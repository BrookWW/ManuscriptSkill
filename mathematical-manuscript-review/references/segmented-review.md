# Segmented review

Use this mode for an organized manuscript that benefits from focused rounds.
One planning chat produces a plan; the user opens a fresh chat for each block
and supplies the latest complete manuscript. This manual workflow does not
enforce independent filesystem or memory boundaries.

## Planning stage

Read the complete manuscript and choose relatively self-contained blocks with
manageable workloads. Group connected arguments, split large proof branches
where useful, and order blocks to support later work. Cover substantive content,
including unnamed claims and appendices. Arrange a closing consistency check in
the last block or a separate block when useful.

Save a short Markdown plan at the user-specified new path, defaulting to
`review-plan.md` in a new planning directory outside the manuscript. Do not
overwrite an existing plan. Use the requested report language, otherwise the
user's conversation language. Use one level-two heading per block, numbered consecutively:
`## 1. Block title`, `## 2. Block title`, and so on. Under each heading identify
scope and review focus; section names, theorem labels, or clear prose suffice.
An optional short overview can precede the blocks. Do not wrap the saved plan
in a code fence.
Use stable labels and project-relative locations, not an old round's absolute
source paths. In every block, the current request's project root is authoritative.

Choose the block count based on the paper. No dependency ledger, formal graph,
token estimate, or trial decomposition is required. Planning changes no
manuscript files, performs no full revision, and does not count as a review
round. Return the saved plan and block count, then stop.

## Review one block

Require the latest manuscript, the fixed plan, a specified block, and a new
output directory. If the request says only "segmented review" and no plan
exists, produce the plan first. If a plan is supplied but the block is unclear,
ask which block to review. Do not execute all blocks in one chat while claiming
independent rounds.

Follow [the round workflow](manual-workflow.md) to copy the complete source
project before editing. Read the plan for orientation, then deeply audit and
revise the selected block. Consult other sections to resolve relevant
definitions, statements, proofs, references, or dependencies; do not routinely
reaudit the entire paper in each block. The plan is navigation, not evidence.

Make justified repairs and update directly affected passages, including those
outside the block. Use the latest text to interpret scope when earlier edits
have moved or renamed material. If the scope can no longer be identified, stop
and report the ambiguity rather than silently changing the plan. Report
unresolved obstacles and unverified dependencies. Optional collaborators receive
focused tasks for this block.

Deliver the complete manuscript and required assets under `manuscript/`, plus
`report.md` and `handoff.json`, as defined in the round workflow. Keep review history out
of manuscript sources. The next block receives the latest sources and the same
plan; prior reports and chat logs are not routine input.

## Finish or repeat a pass

A pass completes after every planned block has a completed review handoff. For
another pass, open a fresh planning chat against the latest manuscript and make
a new plan. For a final whole-paper review, explicitly schedule full mode in a
fresh chat. Neither another pass nor a full review starts automatically.
