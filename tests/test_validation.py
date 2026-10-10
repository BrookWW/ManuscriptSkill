"""Portable structural tests; no model calls, credentials, or manuscript data."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate.py"
SPEC = importlib.util.spec_from_file_location("manuscript_validation", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
validation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validation)


class RoundTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.round = Path(self.temp.name) / "round-01"
        self.round.mkdir()
        (self.round / "report.md").write_text("Checks and unresolved issues.\n", encoding="utf-8")
        manuscript = self.round / "manuscript"
        (manuscript / "paper" / "sections").mkdir(parents=True)
        (manuscript / "paper" / "main.tex").write_text("\\input{sections/proof}\n", encoding="utf-8")
        (manuscript / "paper" / "sections" / "proof.tex").write_text("A synthetic proof.\n", encoding="utf-8")
        (manuscript / "references.bib").write_text("", encoding="utf-8")
        self.handoff = {
            "format_version": 1,
            "status": "complete",
            "mode": "full",
            "block": None,
            "entry": "paper/main.tex",
            "files": ["paper/main.tex", "paper/sections/proof.tex", "references.bib"],
        }
        self.write_handoff()

    def write_handoff(self) -> None:
        (self.round / "handoff.json").write_text(json.dumps(self.handoff), encoding="utf-8")

    def assert_invalid(self, message: str) -> None:
        with self.assertRaisesRegex(validation.ValidationError, message):
            validation.validate_round(self.round)

    def cli(self) -> tuple[int, str]:
        output = io.StringIO()
        with redirect_stdout(output), redirect_stderr(output):
            result = validation.main(["--round", str(self.round)])
        return result, output.getvalue()

    def test_complete_nested_full_round(self) -> None:
        result = validation.validate_round(self.round)
        self.assertEqual(result["entry"], "paper/main.tex")
        code, output = self.cli()
        self.assertEqual(code, 0)
        self.assertIn("3 manuscript files", output)
        self.assertIn("dependency closure not checked", output)

    def test_complete_segmented_round(self) -> None:
        self.handoff.update(mode="segmented", block=2)
        self.write_handoff()
        self.assertEqual(validation.validate_round(self.round)["block"], 2)

    def test_incomplete_is_valid_state_but_never_promoted(self) -> None:
        self.handoff["status"] = "incomplete"
        self.write_handoff()
        self.assertEqual(validation.validate_round(self.round)["status"], "incomplete")
        code, output = self.cli()
        self.assertEqual(code, 1)
        self.assertIn("do not promote or count", output)

    def test_incomplete_empty_delivery(self) -> None:
        shutil.rmtree(self.round / "manuscript")
        self.handoff.update(status="incomplete", files=[])
        self.write_handoff()
        self.assertEqual(validation.validate_round(self.round)["files"], [])
        self.assertEqual(self.cli()[0], 1)

    def test_missing_entry_in_manifest(self) -> None:
        self.handoff["files"].remove("paper/main.tex")
        self.write_handoff()
        self.assert_invalid("entry must appear")

    def test_missing_declared_file(self) -> None:
        (self.round / "manuscript" / "paper" / "main.tex").unlink()
        self.assert_invalid("missing files")

    def test_undeclared_delivery(self) -> None:
        (self.round / "manuscript" / "extra.tex").write_text("Unexpected.", encoding="utf-8")
        self.assert_invalid("omits delivered files")

    def test_duplicate_manifest_path(self) -> None:
        self.handoff["files"].append("paper/main.tex")
        self.write_handoff()
        self.assert_invalid("duplicate paths")

    def test_missing_report(self) -> None:
        (self.round / "report.md").unlink()
        self.assertEqual(self.cli()[0], 1)

    def test_report_must_be_regular_file(self) -> None:
        (self.round / "report.md").unlink()
        (self.round / "report.md").mkdir()
        self.assert_invalid("regular file")

    def test_missing_manuscript(self) -> None:
        shutil.rmtree(self.round / "manuscript")
        self.assert_invalid("requires manuscript/")

    def test_schema_has_exact_fields(self) -> None:
        self.handoff["unexpected"] = "do not interpret me"
        self.write_handoff()
        self.assert_invalid("exactly")

    def test_bad_schema_values(self) -> None:
        for field, values in {
            "format_version": [True, 2, "1"],
            "status": ["finished", None, []],
            "mode": ["block", None],
            "block": [1, False, "1"],
            "entry": [None, "", "   "],
            "files": ["paper/main.tex", None],
        }.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    bad = dict(self.handoff, **{field: value})
                    with self.assertRaises(validation.ValidationError):
                        validation.validate_handoff(bad)

    def test_segmented_block_positive_integer(self) -> None:
        for block in (None, 0, -1, True, "2", 1.5):
            with self.subTest(block=block), self.assertRaises(validation.ValidationError):
                validation.validate_handoff(dict(self.handoff, mode="segmented", block=block))

    def test_path_boundaries(self) -> None:
        for value in ("/main.tex", "../main.tex", "paper/../main.tex", "./main.tex", "paper//main.tex", "paper/main.tex/", "C:/main.tex", "C:main.tex", "\\\\server\\main.tex", "paper\\main.tex", "//server/main.tex", "paper:main.tex", "main\x00.tex"):
            with self.subTest(value=value), self.assertRaises(validation.ValidationError):
                validation.project_path(value)

    def test_manifest_paths_validate_even_when_incomplete(self) -> None:
        self.handoff.update(status="incomplete", files=["../source.tex"])
        self.write_handoff()
        self.assert_invalid("traversing")

    def test_duplicate_json_field(self) -> None:
        text = json.dumps(self.handoff)
        text = text[:-1] + ', "status": "complete"}'
        (self.round / "handoff.json").write_text(text, encoding="utf-8")
        self.assert_invalid("duplicate JSON field")

    def test_malformed_json_returns_cli_error(self) -> None:
        (self.round / "handoff.json").write_text('{"format_version":', encoding="utf-8")
        code, output = self.cli()
        self.assertEqual(code, 1)
        self.assertIn("Validation failed:", output)
        self.assertNotIn("Traceback", output)

    def test_all_malformed_field_types_are_validation_errors(self) -> None:
        for field in validation.HANDOFF_FIELDS:
            for value in ({}, [], None, True):
                with self.subTest(field=field, value=value):
                    data = dict(self.handoff, **{field: value})
                    if field == "block" and value is None:
                        continue
                    with self.assertRaises(validation.ValidationError):
                        validation.validate_handoff(data)

    def make_symlink(self, target: Path, link: Path, *, directory: bool = False) -> None:
        try:
            link.symlink_to(target, target_is_directory=directory)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"symlinks unavailable: {error}")

    def test_symlink_file_is_rejected(self) -> None:
        target = Path(self.temp.name) / "external.tex"
        target.write_text("External source.", encoding="utf-8")
        entry = self.round / "manuscript" / "paper" / "main.tex"
        entry.unlink()
        self.make_symlink(target, entry)
        self.assert_invalid("linked path|reparse point")

    def test_symlink_directory_cycle_is_rejected(self) -> None:
        root = self.round / "manuscript"
        self.make_symlink(root, root / "cycle", directory=True)
        self.assert_invalid("linked path|reparse point")

    def test_symlink_report_is_rejected(self) -> None:
        target = Path(self.temp.name) / "external-report.md"
        target.write_text("External report.", encoding="utf-8")
        report = self.round / "report.md"
        report.unlink()
        self.make_symlink(target, report)
        self.assert_invalid("linked path|reparse point")

    def test_hardlink_alias_is_rejected(self) -> None:
        source = self.round / "manuscript" / "paper" / "main.tex"
        try:
            os.link(source, self.round / "manuscript" / "alias.tex")
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"hard links unavailable: {error}")
        self.assert_invalid("hard-linked")

    def test_windows_reparse_attribute_is_rejected(self) -> None:
        fake = SimpleNamespace(st_mode=0o100644, st_file_attributes=0x400, st_nlink=1)
        with patch.object(Path, "lstat", return_value=fake):
            with self.assertRaisesRegex(validation.ValidationError, "reparse point"):
                validation.safe_stat(Path("synthetic-junction"))


class PackageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / "synthetic-review"
        (self.skill / "agents").mkdir(parents=True)
        (self.skill / "references").mkdir()
        (self.skill / "SKILL.md").write_text(
            '---\nname: synthetic-review\ndescription: "Review synthetic manuscripts."\nmetadata:\n  version: "1"\n---\n'
            "# Synthetic review\n\nRead the [workflow](references/manual-workflow.md).\n",
            encoding="utf-8",
        )
        (self.skill / "references" / "manual-workflow.md").write_text("Save the revised sources.\n", encoding="utf-8")
        (self.skill / "agents" / "openai.yaml").write_text(
            'interface:\n  display_name: "Synthetic review"\n'
            '  short_description: "Review a synthetic manuscript round"\n'
            '  default_prompt: "Use $synthetic-review to review this manuscript."\n'
            "policy:\n  allow_implicit_invocation: true\n",
            encoding="utf-8",
        )
        (self.root / "README.md").write_text("[Skill](synthetic-review/SKILL.md)\n", encoding="utf-8")

    def test_valid_metadata_links_and_budgets(self) -> None:
        result = validation.validate_package(self.root)
        self.assertEqual(result["skill_files"], 3)
        self.assertLess(result["main_words"], validation.MAIN_WORD_BUDGET)

    def test_folder_must_match_metadata_name(self) -> None:
        self.skill.rename(self.root / "other-name")
        with self.assertRaisesRegex(validation.ValidationError, "folder must match"):
            validation.validate_package(self.root)

    def test_unsupported_frontmatter(self) -> None:
        path = self.skill / "SKILL.md"
        path.write_text(path.read_text().replace("metadata:", "unsupported:\n  value: 1\nmetadata:"), encoding="utf-8")
        with self.assertRaisesRegex(validation.ValidationError, "unsupported frontmatter"):
            validation.validate_package(self.root)

    def test_invalid_yaml(self) -> None:
        (self.skill / "SKILL.md").write_text("---\nname: [broken\n---\n", encoding="utf-8")
        with self.assertRaisesRegex(validation.ValidationError, "invalid YAML"):
            validation.validate_package(self.root)

    def test_duplicate_yaml_key_is_rejected(self) -> None:
        path = self.skill / "SKILL.md"
        path.write_text(path.read_text().replace("name: synthetic-review", "name: synthetic-review\nname: synthetic-review"), encoding="utf-8")
        with self.assertRaisesRegex(validation.ValidationError, "duplicate YAML key"):
            validation.validate_package(self.root)

    def test_default_prompt_requires_skill_mention(self) -> None:
        path = self.skill / "agents" / "openai.yaml"
        path.write_text(path.read_text().replace("$synthetic-review", "the skill"), encoding="utf-8")
        with self.assertRaisesRegex(validation.ValidationError, "must mention"):
            validation.validate_package(self.root)

    def test_ui_description_length(self) -> None:
        path = self.skill / "agents" / "openai.yaml"
        path.write_text(path.read_text().replace("Review a synthetic manuscript round", "Short"), encoding="utf-8")
        with self.assertRaisesRegex(validation.ValidationError, "25–64"):
            validation.validate_package(self.root)

    def test_readme_broken_link(self) -> None:
        (self.root / "README.zh-CN.md").write_text("[Missing](missing.md)\n", encoding="utf-8")
        with self.assertRaisesRegex(validation.ValidationError, "broken relative link"):
            validation.validate_package(self.root)

    def test_repository_docs_broken_link(self) -> None:
        for parent in (self.root / "docs", self.root / "examples" / "regularity"):
            with self.subTest(parent=parent.relative_to(self.root).as_posix()):
                parent.mkdir(parents=True, exist_ok=True)
                document = parent / "validation.md"
                document.write_text("[Missing report](missing-report.md)\n", encoding="utf-8")
                try:
                    with self.assertRaisesRegex(validation.ValidationError, "broken relative link"):
                        validation.validate_package(self.root)
                finally:
                    document.unlink()

    def test_links_skip_fences_web_and_placeholders(self) -> None:
        (self.root / "README.md").write_text(
            "```markdown\n[Missing](missing.md)\n```\n"
            "~~~text\n[Also missing](also-missing.md)\n~~~\n"
            "[Web](https://example.org/page)\n[Placeholder](<project>/main.tex)\n"
            "[Anchor](#usage)\n[Skill](<synthetic-review/SKILL.md>)\n",
            encoding="utf-8",
        )
        validation.validate_package(self.root)

    def test_reference_definition_is_checked(self) -> None:
        (self.root / "README.md").write_text("[Guide][guide]\n\n[guide]: missing.md\n", encoding="utf-8")
        with self.assertRaisesRegex(validation.ValidationError, "broken relative link"):
            validation.validate_package(self.root)

    def test_link_cannot_leave_package(self) -> None:
        (self.root / "README.md").write_text("[Outside](../outside.md)\n", encoding="utf-8")
        with self.assertRaisesRegex(validation.ValidationError, "leaves package"):
            validation.validate_package(self.root)

    def test_main_word_budget(self) -> None:
        path = self.skill / "SKILL.md"
        path.write_text(path.read_text() + "word " * validation.MAIN_WORD_BUDGET, encoding="utf-8")
        with self.assertRaisesRegex(validation.ValidationError, "SKILL.md exceeds"):
            validation.validate_package(self.root)

    def test_default_word_budget(self) -> None:
        path = self.skill / "references" / "manual-workflow.md"
        path.write_text("word " * validation.DEFAULT_WORD_BUDGET, encoding="utf-8")
        with self.assertRaisesRegex(validation.ValidationError, "default instructions exceed"):
            validation.validate_package(self.root)

    def test_private_or_runtime_artifacts_in_installable_folder(self) -> None:
        for name in ("auth.json", ".env", "archive.zip", "__pycache__/file.pyc", "round-01/handoff.json"):
            with self.subTest(name=name):
                path = self.skill / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("synthetic", encoding="utf-8")
                try:
                    with self.assertRaisesRegex(validation.ValidationError, "private/runtime artifact"):
                        validation.validate_package(self.root)
                finally:
                    path.unlink()

    def test_tracked_private_artifacts(self) -> None:
        with patch.object(validation, "tracked_package_files", return_value=["private/.env"]):
            with self.assertRaisesRegex(validation.ValidationError, "tracked by Git"):
                validation.validate_package(self.root)


if __name__ == "__main__":
    unittest.main()
