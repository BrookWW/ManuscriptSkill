# Round workflow

The user selects the schedule and starts fresh chats. Codex prepares copies and
saves results within the authorized task; no external runner is required.
Planning-only tasks use the separate segmented guide and do not create a review
handoff.

## Prepare one round

Identify the project root, project-relative entry, mode, and necessary extra
assets. A block review also needs the supplied plan and block number. Infer
unambiguous details from the request and workspace; ask only for missing details
that affect execution. If output is omitted, choose a new named directory
outside the input tree within the available write permissions.

Use a new output directory; do not merge with or overwrite a prior round:

```text
round-001/
  manuscript/       Complete revised project; next-round input
  report.md         Human-facing report; retained for the author
  handoff.json      Delivery status and source manifest
  .audit-work/      Optional notes, downloads, and build products
```

Before copying or editing, write an initial `report.md` identifying the request
and an `incomplete` handoff with the known entry, mode, and block, and an empty
file list. If interrupted, a source directory alone never implies completion.

Copy required source files into `manuscript/`, preserving paths relative to the
project root. Inspect entry/include chains, bibliography resources, figures,
local classes/styles, and evidence files; include explicit user-supplied assets.
Do not copy an enclosing research directory wholesale. Exclude credentials,
agent configuration/state, Git internals, old reports, logs, and build caches.
Do not recursively follow aliases into unrelated locations. Materialize a
required linked dependency only after identifying its authorized target.

Keep real copies, not links to the input. Output must remain outside the input
tree, including after resolving aliases, so future copies cannot absorb prior
rounds. Edit the copied project only. Compilation's working directory is the
copied project root, even when the entry is nested. Put temporary products in
`.audit-work/`; remove only verified generated products from delivery, preserving
necessary input assets.

## Check sources and coverage

Verify local TeX includes, Bib resources, graphics, classes/styles, and explicit
assets resolve from the copied root. Static scanning alone does not establish
closure for macro-generated paths or runtime-generated resources. Resolve an
uncertain required dependency or report an incomplete source handoff; do not
invent a successful dependency check. A missing TeX toolchain is an unavailable
check, not automatically an incomplete handoff when sources are otherwise
complete.

Record reviewed sections and substantive claims, dependencies checked, and
material left unchecked. Full-review coverage includes the complete paper's
substantive material; a block review includes its scope and affected passages.
Do not claim completion from a partial reading. Distinguish a finished review
with unresolved mathematics from an unfinished review or missing source files.
If an author decision is pending, identify the affected claim and options in
the report and final response. A complete handoff may retain that claim pending
the decision; do not describe the manuscript as corrected or ready to submit.

## Report and finalize

Update `report.md` with scope and coverage; changes and unresolved issues with
mathematical reasons; checks actually performed and unavailable/failed checks;
input/output root and relative entry; and delivery status. Keep review history
out of paper sources and bibliography. Source manifests belong in the handoff,
so the report need not repeat a long file list. Report and manuscript languages
are separate choices.
Scale the report to the findings. Give enough evidence to assess each issue,
link to detailed arguments in the manuscript, and avoid repeating the same
proof or check in several report sections.

Write UTF-8 `handoff.json` with exactly these fields:

```json
{
  "format_version": 1,
  "status": "complete",
  "mode": "full",
  "block": null,
  "entry": "paper/main.tex",
  "files": ["paper/main.tex", "references.bib"]
}
```

- `status`: `incomplete` initially; `complete` only after requested coverage,
  source delivery, and the report are finished.
- `mode`: `full` or `segmented`; `block` is null for full, or the positive plan
  block number for segmented review.
- `entry`: the actual entry relative to `manuscript/`, using forward slashes.
- `files`: unique project-relative paths to all delivered files, conventionally
  sorted; include the entry and dependencies. Use forward slashes, no absolute
  paths, parent traversal, aliases, or drive-qualified paths. Do not list files
  outside `manuscript/` or retain scratch files in that tree.

Verify the listed files exist and match the delivered source tree. Update the
handoff last, preferably by replacing a temporary file in the same directory.
If the task cannot finish, retain `incomplete`, update its file list to what
actually exists when possible, and explain the reason. This manifest records
handoff state; it does not certify mathematics or provide transaction isolation.

Return links to the report, handoff, and revised entry, with the status and any
material unresolved issue. A no-change review still needs a complete copy and
report. Do not cancel later user-planned rounds because this round found no
problems.

## Continue or recover

The saved round directory is the file archive. The user normally retains it in
place, starts a fresh chat, and supplies the latest completed `manuscript/` as
the next input. For block reviews, also pass the fixed plan for this pass.
Do not seek older reports, chats, or archive files unless explicitly supplied.
Archiving a chat is optional; it does not delete history or reset memory.

After interruption, keep partial output. Retry from the last completed handoff
in a new directory. A user may explicitly choose to salvage a partial version;
identify it as partial and recheck it before claiming completion. Never silently
promote an incomplete handoff. Starting a new chat or moving folders is a
workflow convention, not a security boundary.
