# Validation record

## 2026-10-10 publication audit

The standalone skill was audited against its source ManuscriptAgent skill,
then reviewed again after revision. The audit addressed forced personal
formatting, runner-only requirements, repeated instructions, ambiguous partial
delivery, and missing coverage information. User instructions now take
precedence over defaults; the author profile is optional; input copies and
`incomplete`/`complete` handoffs are explicit. The mathematical safeguards for
proof gaps, counterexamples, citations, and substantive theorem changes remain.

The installed skill contains six instruction/resource files and requires no
runtime package installation. The repository's Python validator and tests are
developer tools. Word budgets limit instruction growth; these are project
maintenance limits, not measured model-token counts or accuracy metrics.

### Deterministic checks

Local environment: macOS ARM64, Python 3.12.13, and cached PyYAML. At this stage,
40 unit tests passed with no skipped tests. They cover metadata and local links,
handoff schema, malformed and duplicate fields, source manifests, nested entry
paths, incomplete-state rejection, path traversal, and link aliases. Windows
reparse attributes are simulated locally; Windows execution is a separate CI
check. CI is configured for Ubuntu, macOS, and Windows with Python 3.11 and 3.12.

The round validator reads a static file tree. It does not prove dependency
closure, prevent concurrent replacement, establish sandbox isolation, or assess
mathematical correctness. Tests using synthetic files do not measure model
adherence.

### Behavioral smoke checks

Independent development agents applied the skill to the public
[regularity fixture](../examples/regularity/README.md) in temporary workspaces.
They received the request, skill, and raw source; no expected finding was
supplied. Each evaluation used a fresh agent context. No personal manuscript or
credentials were part of the fixture.

- **Full review:** detected that continuity on a compact interval does not imply
  Lipschitz continuity, with the square-root counterexample. The agent supplied
  a proved uniform-continuity replacement and explained the change in the main
  conclusion and a stronger-hypothesis alternative. It preserved the valid
  affine theorem, class, custom macro, language, and relative paths. The missing
  `amsfonts` dependency was repaired. The available TeX toolchain compiled the
  final candidate, and both check-PDF pages were inspected. A complete two-file
  handoff passed the static validator. Input hashes were unchanged; no empty
  bibliography or compiled PDF entered source delivery.
- **Planning only:** saved one numbered review block covering the small
  manuscript and its closing consistency check. It produced no manuscript copy
  or review handoff; input hashes remained unchanged. One block is appropriate
  for this small fixture and does not test multi-block scheduling.
- **Segmented block review:** followed that one-block plan, detected the same
  false theorem, preserved the valid affine result and supplied format, and
  fixed the definition/font-package defects. It retained the refuted main claim
  pending an author choice, with the claim, counterexample, and alternatives
  explicitly reported. Source delivery was complete and passed the validator;
  mathematics remained unresolved and the report did not deem the paper ready
  for submission. Compilation and visual inspection succeeded.

The full-review report repeated some proof/check details, so the workflow was
refined to keep the report proportional and point to detailed manuscript
arguments. The plan included its input's absolute root, so the guide now directs
plans to use stable labels and project-relative locations, with the current
request's root taking precedence. These were narrow changes supported by the
observed behavior.
The two review agents made different editorial choices about the refuted
conclusion: one documented a replacement that answered the stated objective;
the other retained it pending a decision. The workflow now explicitly permits
the latter as a completed review handoff with unresolved mathematics. This
latitude requires human assessment and is not a repeatability claim.

This is a small engineering smoke evaluation, not a research-mathematics
benchmark. It does not establish repeatability, hard-problem proof reliability,
literature verification, multi-round quality, GPT-6 performance superiority, or
equivalence to the original isolated runner. Client installation and tool access
can differ; use the chosen model and representative manuscripts for further
evaluation.
