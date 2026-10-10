# ManuscriptSkill

[English](README.md) | [简体中文](README.zh-CN.md)

[![Validation](https://github.com/BrookWW/ManuscriptSkill/actions/workflows/ci.yml/badge.svg)](https://github.com/BrookWW/ManuscriptSkill/actions/workflows/ci.yml)

Review and revise mathematical LaTeX manuscripts in Codex with one reusable skill. Each review saves a complete source revision, a separate report, and a small handoff record. Use full-paper rounds or plan a segmented pass and review one block per fresh chat.

ManuscriptSkill is designed for GPT-6-class Codex models. You choose the model and reasoning effort in your client; the skill does not select or enforce them. It contains instructions and reference files, with no runtime scripts, Python service, or Linux requirement. Literature access, PDF reading, compilation, and subagent review depend on the tools available in your Codex environment.

The core states scope, scientific constraints, and completion conditions once; mode-specific guidance and the optional style profile load only when needed. Explicit user instructions take precedence over skill defaults. These choices follow the [official GPT-6 instruction-following guidance](https://developers.openai.com/api/docs/guides/latest-model#instruction-following); they are design choices, not a measured accuracy claim.

The [review skill](mathematical-manuscript-review/SKILL.md) covers mathematical reasoning, justified repairs, theorem design, literature verification, and exposition. It preserves the author's research objective, manuscript language, and existing journal format. The bundled [style preferences](mathematical-manuscript-review/references/personal-style.md) and [LaTeX template](mathematical-manuscript-review/assets/tex_template.tex) are an optional BrookWW style profile. Enable them by requesting "Use the bundled author style"; explicit author instructions and a supplied journal template take precedence. These preferences are not official journal requirements.

## Install

In Codex, ask the skill installer to install the skill folder from this repository:

```text
Use $skill-installer to install the skill from:
https://github.com/BrookWW/ManuscriptSkill/tree/main/mathematical-manuscript-review
Install the complete folder, including references, assets, and agents.
If the same skill is already installed, compare versions before replacing it.
Tell me the actual installation location and how to invoke it in a new chat.
```

The current [Codex skills documentation](https://learn.chatgpt.com/docs/build-skills) lists `~/.agents/skills/` for personal skills. Some existing clients and installers use `~/.codex/skills/`. Follow your client's installer and actual discovery directory; installing the same skill in both locations can create ambiguity.

For a local copy, clone or download the repository:

```sh
git clone https://github.com/BrookWW/ManuscriptSkill.git
cd ManuscriptSkill
```

Copy the entire `mathematical-manuscript-review/` folder into your client's confirmed skill directory. Do not copy only `SKILL.md` or merge it into an existing version. If the skill does not appear, restart Codex and check its discovery directory.

You can also try it before installation: ask Codex to read the local `mathematical-manuscript-review/SKILL.md` and its referenced files, then give a review request. Installed invocation uses `$mathematical-manuscript-review`.

## Prepare the manuscript

Give Codex the project root, the entry file relative to that root, and any required assets that include discovery may miss. Supply the TeX/Bib sources, figures, local classes and styles, and computational evidence needed to assess the claims. For a nested entry such as `paper/main.tex`, keep that path throughout the workflow. On Windows, use drive-qualified absolute roots and output paths; entry and asset paths remain relative to the project.

Every review needs a new output directory outside its input tree. Codex copies the complete required project before editing, so you can keep the original and earlier revisions. It excludes old review reports, credentials, agent state, and build caches. Required external or linked dependencies must be identified and materialized within the authorized project copy.

The following paths are examples, not bundled review results:

```text
paper-original/
  paper/main.tex
  bibliography/references.bib
  figures/
paper-reviews/
  full-001/
    manuscript/              Complete editable project for the next round
      paper/main.tex
      bibliography/references.bib
      figures/
    report.md                Findings, revisions, and actual checks
    handoff.json             Delivery status and source locations
    .audit-work/             Optional temporary material
  planning-001/review-plan.md
  pass-001-block-001/
  pass-001-block-002/
  final-full-001/
```

Deliverables are source files and required assets. Compiled manuscript PDFs are temporary checks; input PDFs used as figures or evidence remain part of the project when needed.

## Full-paper review

Open a new Codex chat, replace the placeholders, and send:

```text
Use $mathematical-manuscript-review for one full review, revision, and recheck.
Input project root: <absolute path to the current complete manuscript project>
Entry file: <project-relative path, for example paper/main.tex>
Output round directory: <new absolute path, for example paper-reviews/full-001>
Extra required assets: <project-relative paths, or none>
Report language: English. Preserve the manuscript's language.

Copy the complete required project to manuscript/ before editing.
Save report.md and handoff.json outside manuscript/.
Do this round only. Do not read previous reports or other chats.
```

Read the report and check the handoff before continuing. A `complete` handoff means that the requested round and source delivery finished; unresolved mathematics must still appear in the report. Completion does not certify correctness or publication readiness.

For another round, open a new chat and use the last completed round's `manuscript/` as the input root. Keep the actual relative entry path and required asset paths, and choose another new output directory. Pass only the latest complete manuscript, the current request, and any currently needed evidence. Earlier reports and chat transcripts are not normal next-round inputs.

The round directory is your file archive. You may archive its chat to organize the sidebar, but this does not delete files, clear memory, or restrict access. A fresh chat follows the review convention; it does not establish filesystem isolation. A round that finds no changes still delivers the full source copy and report.

## Segmented review

A segmented pass starts with planning and then chains the latest complete revision through every block. Planning does not count as a review round.

### Plan the pass

Open a fresh chat:

```text
Use $mathematical-manuscript-review in segmented mode for planning only.
Project root: <absolute path to the latest complete manuscript project>
Entry file: <actual project-relative entry path>
Plan destination: <new planning directory>/review-plan.md
Plan language: English. Preserve the manuscript's language.

Read the complete manuscript and divide the substantive arguments and appendices
into numbered review blocks. Specify their scope and order.
Produce only the plan. Do not revise sources or start block reviews.
```

Keep this plan fixed throughout the pass. Read it before starting, and note the block count.

### Review one block

Open a new chat for each block:

```text
Use $mathematical-manuscript-review in segmented mode to review one block.
Input project root: <absolute path to the latest complete manuscript project>
Entry file: <actual project-relative entry path>
Fixed plan: <absolute path to review-plan.md>
Block: 1
Output round directory: <new absolute path, for example pass-001-block-001>
Extra required assets: <project-relative paths, or none>
Report language: English. Preserve the manuscript's language.

Copy the complete required project before reviewing the assigned block.
Consult other passages and repair directly affected material as needed.
Deliver the complete manuscript/, report.md, and handoff.json.
Do this block only. Do not read earlier review reports.
```

For block 2, use block 1's delivered `manuscript/`, keep the same plan, increment the block number, and choose a new output directory. Continue this chain through all blocks. Starting every block from the initial manuscript would discard earlier revisions.

Another segmented pass needs a new plan based on the latest complete manuscript. A final full-paper review runs only when you request it. See the [segmented mode guide](mathematical-manuscript-review/references/segmented-review.md) and [round workflow](mathematical-manuscript-review/references/manual-workflow.md) for the complete conventions.

## Multi-round workflows and recovery

You can combine modes, for example:

| Stage | Chats | Input |
|---|---|---|
| Three full rounds | One fresh chat per round | Original project, then the latest complete revision |
| One segmented plan | One fresh planning chat | Third round's complete revision |
| One segmented pass | One fresh chat per planned block | Latest revision plus the fixed plan |
| One final full round | One fresh chat | Last block's complete revision |

For a plan with N blocks, this example uses N+5 chats, including one planning chat. Counts are configurable; this sequence has not been shown to produce optimal quality or cost. Skills can run longer tasks, but this workflow deliberately stops at each handoff so you control the next input and review scope.

If a review stops or required source dependencies are missing, keep the partial output and retry from the last completed manuscript in a new directory. Do not use an `incomplete` handoff as a completed revision. You may explicitly ask Codex to salvage partial work, identifying it as partial input. Unresolved mathematical questions belong in the report and can remain after an otherwise completed review.

The report must distinguish checks performed from checks unavailable or failed. A source the model could not read remains unverified. Missing subagent tools do not prevent a direct review, and TeX compilation is optional; neither reviewer agreement nor successful compilation proves the mathematics.

## Relationship to ManuscriptAgent

This skill derives from [ManuscriptAgent](https://github.com/BrookWW/BrookWW-ManuscriptAgent). It keeps the review method and source handoff while letting you manage rounds in Codex.

| Capability | ManuscriptSkill | ManuscriptAgent runner |
|---|---|---|
| Mathematical review instructions | Standalone skill | Bundled skill |
| Round sequencing | User starts fresh chats and selects inputs | Runner schedules sessions and revisions |
| Operating environment | Client and tools that can read and edit files | macOS runner with its documented requirements |
| Isolation | Client permissions and workflow conventions | Runner enforces its sandbox and access boundaries |
| Credentials, network, process cleanup | Client controls | Runner supplies dedicated controls |
| Review results | Complete sources, report, handoff record | Complete sources and run records |

ManuscriptSkill supplies no kernel sandbox, automatic scheduling, separate credentials, network allowlist, or guaranteed process cleanup. Its behavior depends on client permissions, project instructions, accessible files, and model choices. No controlled study establishes review quality equal to the runner or a guaranteed advantage from GPT-6-class models.

## Development and validation

The installed skill has no package dependency. Repository validation uses Python 3.11+ and PyYAML as development tools:

```sh
python -m pip install -r requirements-dev.txt
python scripts/validate.py
python -m unittest discover -s tests -v
```

On systems where Python 3 is named `python3`, use that command. You can optionally check a delivered round with `python scripts/validate.py --round <absolute-round-path>`. That check validates the handoff and delivered file tree, not the paper's mathematics.

CI checks the package, metadata, referenced files, and cross-platform test cases. These checks cover packaging and workflow contracts; they do not measure research-level mathematical reliability or prove that a model follows every instruction. Real manuscript evaluation requires a separate run with the chosen model and tools, followed by human assessment of findings and revisions. Keep private manuscripts, generated review archives, and authentication material out of this repository.

The [validation record](docs/validation.md) documents the audit and small behavioral smoke checks. The deliberately defective [synthetic fixture](examples/regularity/README.md) is available for reproducing basic workflow checks.

## Repository layout

```text
mathematical-manuscript-review/
  SKILL.md
  agents/openai.yaml
  references/
    manual-workflow.md
    segmented-review.md
    personal-style.md
  assets/tex_template.tex
README.md
README.zh-CN.md
```

## License

[MIT](LICENSE).
