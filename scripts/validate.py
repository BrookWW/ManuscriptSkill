#!/usr/bin/env python3
"""Developer checks for the package and a delivered review-round file manifest.

These static checks establish structure and file consistency, not mathematical
correctness, dependency closure, operating-system isolation, or protection
against concurrent filesystem changes.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
from urllib.parse import unquote, urlsplit


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
MAIN_WORD_BUDGET = 1100
DEFAULT_WORD_BUDGET = 2000
HANDOFF_FIELDS = {"format_version", "status", "mode", "block", "entry", "files"}


class ValidationError(ValueError):
    """A package or handoff violates a documented invariant."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def project_path(value: object, label: str = "path") -> str:
    """Accept canonical relative POSIX paths, including nested project entries."""
    require(isinstance(value, str) and bool(value.strip()), f"{label}: expected a nonempty path")
    assert isinstance(value, str)
    require(not any(c in value for c in ("\\", ":")) and not any(ord(c) < 32 for c in value), f"{label}: forbidden path character")
    require(not value.startswith("/"), f"{label}: absolute paths are forbidden")
    parts = value.split("/")
    require(all(part not in ("", ".", "..") for part in parts), f"{label}: noncanonical or traversing path")
    require(str(PurePosixPath(value)) == value, f"{label}: expected a canonical POSIX path")
    return value


def safe_stat(path: Path, *, directory: bool = False) -> os.stat_result:
    """Use lstat so linked files/directories never become implicit inputs."""
    info = path.lstat()
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    require(not stat.S_ISLNK(info.st_mode), f"linked path is forbidden: {path}")
    require(not getattr(info, "st_file_attributes", 0) & reparse_flag, f"reparse point is forbidden: {path}")
    expected = stat.S_ISDIR if directory else stat.S_ISREG
    require(expected(info.st_mode), f"expected a {'directory' if directory else 'regular file'}: {path}")
    if not directory:
        require(info.st_nlink <= 1, f"hard-linked file is forbidden: {path}")
    return info


def tree_files(root: Path) -> set[str]:
    """Walk without following links; reject aliased directory identities."""
    pending = [root]
    seen: set[tuple[int, int]] = set()
    files: set[str] = set()
    while pending:
        directory = pending.pop()
        info = safe_stat(directory, directory=True)
        identity = (info.st_dev, info.st_ino)
        if info.st_ino:
            require(identity not in seen, f"repeated directory identity: {directory}")
            seen.add(identity)
        with os.scandir(directory) as entries:
            for entry in entries:
                path = Path(entry.path)
                relative = project_path(path.relative_to(root).as_posix())
                item_info = path.lstat()
                if stat.S_ISDIR(item_info.st_mode):
                    safe_stat(path, directory=True)
                    pending.append(path)
                else:
                    safe_stat(path)
                    files.add(relative)
    return files


def unique_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON field: {key}")
        result[key] = value
    return result


def validate_handoff(data: object) -> dict[str, object]:
    """Validate the schema, allowing incomplete state without promoting it."""
    require(isinstance(data, dict), "handoff.json: expected a JSON object")
    assert isinstance(data, dict)
    require(set(data) == HANDOFF_FIELDS, "handoff.json: expected exactly format_version, status, mode, block, entry, files")
    require(type(data["format_version"]) is int and data["format_version"] == 1, "format_version must be 1")
    require(isinstance(data["status"], str) and data["status"] in ("complete", "incomplete"), "status must be complete or incomplete")
    require(isinstance(data["mode"], str) and data["mode"] in ("full", "segmented"), "mode must be full or segmented")
    if data["mode"] == "full":
        require(data["block"] is None, "full mode requires block: null")
    else:
        require(type(data["block"]) is int and data["block"] > 0, "segmented mode requires a positive integer block")
    project_path(data["entry"], "entry")
    require(isinstance(data["files"], list), "files must be a list")
    paths = [project_path(value, "files") for value in data["files"]]
    require(len(paths) == len(set(paths)), "files contains duplicate paths")
    if data["status"] == "complete":
        require(bool(paths), "complete handoff requires manuscript files")
        require(data["entry"] in paths, "entry must appear in files for a complete handoff")
    return data


def validate_round(round_path: Path) -> dict[str, object]:
    """Check schema and exact delivery inventory without reading manuscript logic."""
    round_path = Path(round_path).absolute()
    safe_stat(round_path, directory=True)
    handoff = round_path / "handoff.json"
    safe_stat(handoff)
    data = validate_handoff(json.loads(handoff.read_text(encoding="utf-8"), object_pairs_hook=unique_json_object))
    safe_stat(round_path / "report.md")
    manuscript = round_path / "manuscript"
    if manuscript.exists() or manuscript.is_symlink():
        actual = tree_files(manuscript)
    else:
        require(data["status"] == "incomplete", "complete handoff requires manuscript/")
        actual = set()
    declared = set(data["files"])
    missing = sorted(declared - actual)
    undeclared = sorted(actual - declared)
    require(not missing, f"manifest declares missing files: {', '.join(missing)}")
    require(not undeclared, f"manifest omits delivered files: {', '.join(undeclared)}")
    return data


def unfenced_markdown(text: str) -> str:
    """Remove fenced examples before interpreting documentation links."""
    output: list[str] = []
    marker = ""
    length = 0
    for line in text.splitlines():
        fence = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        if fence:
            token = fence.group(1)
            if not marker:
                marker, length = token[0], len(token)
            elif token[0] == marker and len(token) >= length and not fence.group(2).strip():
                marker = ""
            continue
        if not marker:
            output.append(line)
    return "\n".join(output)


def markdown_targets(text: str) -> list[str]:
    text = unfenced_markdown(text)
    # Handle ordinary links/images and reference definitions; inline examples
    # containing code are removed so placeholder commands are not read as links.
    text = re.sub(r"(`+).*?\1", "", text)
    pattern = r"!?\[[^\]\n]*\]\(\s*(<[^>\n]+>[^\s)]*|[^\s)]+)(?:\s+[^)]*)?\)"
    targets = re.findall(pattern, text)
    targets.extend(re.findall(r"^\s{0,3}\[[^\]\n]+\]:\s*(<[^>\n]+>[^\s)]*|\S+)", text, re.MULTILINE))
    return targets


def validate_links(document: Path, package_root: Path) -> None:
    for raw in markdown_targets(document.read_text(encoding="utf-8")):
        target = raw[1:-1] if raw.startswith("<") and raw.endswith(">") else raw
        if any(marker in target for marker in ("<", ">", "{", "}")):
            continue
        if raw.startswith("<") and re.fullmatch(r"(?:path|project|repo|round|file|directory|skill)(?:[-_](?:path|root|name))?", target, re.IGNORECASE):
            continue
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        require(not parsed.path.startswith("/"), f"{document.name}: absolute local link: {target}")
        linked = (document.parent / unquote(parsed.path)).resolve()
        require(linked.is_relative_to(package_root.resolve()), f"{document.name}: link leaves package: {target}")
        require(linked.exists(), f"{document.name}: broken relative link: {target}")


def yaml_mapping(text: str, label: str) -> dict[str, object]:
    try:
        import yaml
    except ImportError as error:
        raise ValidationError("package checks need PyYAML; install requirements-dev.txt") from error
    try:
        class UniqueSafeLoader(yaml.SafeLoader):
            pass

        def unique_mapping(loader, node, deep=False):
            pairs = loader.construct_pairs(node, deep=deep)
            result = {}
            for key, value in pairs:
                try:
                    require(key not in result, f"{label}: duplicate YAML key")
                    result[key] = value
                except TypeError as error:
                    raise ValidationError(f"{label}: YAML keys must be scalar") from error
            return result

        UniqueSafeLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)
        data = yaml.load(text, Loader=UniqueSafeLoader)
    except yaml.YAMLError as error:
        raise ValidationError(f"{label}: invalid YAML") from error
    require(isinstance(data, dict), f"{label}: expected a YAML mapping")
    return data


def validate_skill_metadata(skill: Path) -> str:
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", text, re.DOTALL)
    require(match is not None, "SKILL.md: missing YAML frontmatter")
    assert match is not None
    metadata = yaml_mapping(match.group(1), "SKILL.md")
    require(set(metadata) <= {"name", "description", "license", "allowed-tools", "metadata"}, "SKILL.md: unsupported frontmatter key")
    name = metadata.get("name")
    require(isinstance(name, str) and bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name)), "SKILL.md: invalid name")
    require(len(name) <= 64 and name == skill.name, "skill folder must match name (maximum 64 characters)")
    description = metadata.get("description")
    require(isinstance(description, str) and bool(description.strip()) and len(description) <= 1024, "SKILL.md: invalid description")
    require(not any(c in description for c in "<>"), "SKILL.md: description cannot contain angle brackets")
    if "metadata" in metadata:
        require(isinstance(metadata["metadata"], dict), "SKILL.md: metadata must be a mapping")
    if "license" in metadata:
        require(isinstance(metadata["license"], str), "SKILL.md: license must be a string")
    if "allowed-tools" in metadata:
        allowed = metadata["allowed-tools"]
        require(isinstance(allowed, str) or (isinstance(allowed, list) and all(isinstance(item, str) for item in allowed)), "SKILL.md: invalid allowed-tools")
    require(not re.search(r"^\s*\[TODO:[^\n]*\]\s*$", unfenced_markdown(text), re.MULTILINE), "SKILL.md: unfinished scaffold placeholder")
    return text


def validate_ui_metadata(skill: Path) -> None:
    metadata = yaml_mapping((skill / "agents" / "openai.yaml").read_text(encoding="utf-8"), "openai.yaml")
    require(set(metadata) <= {"interface", "policy", "dependencies"}, "openai.yaml: unsupported top-level key")
    interface = metadata.get("interface")
    require(isinstance(interface, dict), "openai.yaml: interface mapping required")
    require(set(interface) <= {"display_name", "short_description", "default_prompt", "icon_small", "icon_large", "brand_color"}, "openai.yaml: unsupported interface key")
    for field in ("display_name", "short_description", "default_prompt"):
        require(isinstance(interface.get(field), str) and bool(interface[field].strip()), f"openai.yaml: {field} must be a nonempty string")
    require(25 <= len(interface["short_description"]) <= 64, "openai.yaml: short_description must be 25–64 characters")
    require(f"${skill.name}" in interface["default_prompt"], "openai.yaml: default_prompt must mention the skill")
    for field in ("icon_small", "icon_large"):
        if field in interface:
            require(isinstance(interface[field], str), f"openai.yaml: {field} must be a string")
            icon = (skill / interface[field]).resolve()
            require(icon.is_relative_to(skill.resolve()) and icon.is_file(), f"openai.yaml: missing or external {field}")
    if "brand_color" in interface:
        require(isinstance(interface["brand_color"], str) and bool(re.fullmatch(r"#[0-9A-Fa-f]{6}", interface["brand_color"])), "openai.yaml: invalid brand_color")
    if "policy" in metadata:
        policy = metadata["policy"]
        require(isinstance(policy, dict) and set(policy) <= {"allow_implicit_invocation"}, "openai.yaml: invalid policy")
        if "allow_implicit_invocation" in policy:
            require(type(policy["allow_implicit_invocation"]) is bool, "openai.yaml: invocation policy must be boolean")
    if "dependencies" in metadata:
        require(isinstance(metadata["dependencies"], dict), "openai.yaml: dependencies must be a mapping")


def forbidden_artifact(path: str) -> bool:
    parts = [part.lower() for part in PurePosixPath(path).parts]
    forbidden = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".venv", "venv", "node_modules", ".codex", ".agents", "runs", "rounds", "review-runs", "credentials", "secrets"}
    if any(part in forbidden or re.fullmatch(r"round-\d+", part) for part in parts):
        return True
    name = parts[-1] if parts else ""
    return (name in {".ds_store", "auth.json", "handoff.json", "credentials.json", "credentials.yaml", "credentials.yml"}
            or name == ".env" or name.startswith(".env.")
            or name.endswith((".pyc", ".pyo", ".pem", ".key", ".p12", ".pfx", ".zip", ".tar", ".gz")))


def tracked_package_files(package_root: Path) -> list[str]:
    """Inspect the index when available; installation directories are not repositories."""
    try:
        result = subprocess.run(["git", "-C", str(package_root), "ls-files", "-z", "--", "."], capture_output=True, check=False)
    except FileNotFoundError:
        return []
    if result.returncode:
        return []
    return [path for path in result.stdout.decode("utf-8", errors="strict").split("\0") if path]


def validate_package(package_root: Path) -> dict[str, int]:
    package_root = Path(package_root).absolute()
    skills = [path for path in package_root.iterdir() if path.is_dir() and (path / "SKILL.md").is_file()]
    require(len(skills) == 1, "package must contain exactly one installable skill folder")
    skill = skills[0]
    files = tree_files(skill)
    for relative in files:
        require(not forbidden_artifact(relative), f"private/runtime artifact in skill: {relative}")
    for relative in tracked_package_files(package_root):
        require(not forbidden_artifact(relative), f"private/runtime artifact tracked by Git: {relative}")
    main = validate_skill_metadata(skill)
    validate_ui_metadata(skill)
    main_words = len(main.split())
    manual = skill / "references" / "manual-workflow.md"
    safe_stat(manual)
    default_words = main_words + len(manual.read_text(encoding="utf-8").split())
    require(main_words <= MAIN_WORD_BUDGET, f"SKILL.md exceeds project word budget: {main_words} > {MAIN_WORD_BUDGET}")
    require(default_words <= DEFAULT_WORD_BUDGET, f"default instructions exceed project word budget: {default_words} > {DEFAULT_WORD_BUDGET}")
    documents = [skill / path for path in files if path.endswith(".md")]
    documents.extend(package_root.glob("README*.md"))
    documents.extend((package_root / "docs").glob("*.md"))
    documents.extend((package_root / "examples").rglob("*.md"))
    for document in documents:
        validate_links(document, package_root)
    return {"main_words": main_words, "default_words": default_words, "skill_files": len(files)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", nargs="?", type=Path, default=PACKAGE_ROOT)
    parser.add_argument("--round", dest="round_path", type=Path, help="check one review round; incomplete rounds return nonzero")
    args = parser.parse_args(argv)
    try:
        if args.round_path:
            handoff = validate_round(args.round_path)
            if handoff["status"] == "incomplete":
                print("Incomplete round: file manifest checked; do not promote or count this round.")
                return 1
            print(f"Round structure valid (static check): {len(handoff['files'])} manuscript files; mathematics and dependency closure not checked.")
        else:
            result = validate_package(args.package)
            print(f"Package valid: {result['skill_files']} skill files; {result['main_words']} main words, {result['default_words']} default words (project budgets).")
    except (ValidationError, OSError, json.JSONDecodeError, UnicodeError) as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
