# Implementation

> **Language note:** All output artifacts must be written in Chinese (see Critical Rules in SKILL.md).  
> References are in English for readability — do not treat them as a style template for artifacts.

## Purpose

Execute the approved todo list exactly enough to preserve the approval-gated workflow.

Implementation follows the approved plan and approved todo list. It does not redefine them.

## What to do

1. Re-read the approved plan and approved todo list in `docs/<task-slug>.plan.md`.
2. Execute the approved todo items in order, from first to last. For each item:
   - Do the work described.
   - When the work is truly complete, update the checkbox: `- [ ]` becomes `- [x]`.
   - The todo list already includes validation items (e.g. run tests, check output). Execute them as part of this sequence.
3. Stop immediately if the approved artifacts no longer support correct execution.
4. When all todo items are checked off, proceed to the verification and feedback phase.

#### Rewind Protocol

When the approved artifacts no longer support correct execution:

1. **Stop immediately**. Do not continue implementing.
2. **Identify the earliest invalid phase**: which artifact (research, plan, or todo) is broken?
3. **Disposition of artifacts**:
   - Artifacts from the invalid phase and all downstream phases are discarded
   - All upstream (previously approved) artifacts are preserved
   - Example: plan is invalid → discard `plan.md` and its todo list; keep `research.md`
4. **Reload**: read the reference for the phase being rewound to
5. **Inform the user**: state which phase you're rewinding to, why, and what artifacts were discarded
6. **Proceed**: re-enter the workflow at the rewound phase, starting with a fresh artifact
7. **Re-approval required**: the newly created artifact must pass the phase's review-approval cycle before advancing. Upstream (preserved) artifacts remain approved.

## Change policy

| Change type | Status |
|---|---|
| Small wiring, imports, test adjustments, minor support edits | OK without reopening earlier phases |
| New scope, unapproved behavior changes, silent redesign, opportunistic refactors | Rewind to earliest invalid phase |
| Approved plan no longer fits the real codebase | Rewind |
| Newly discovered requirement that changes scope or design | Rewind |

If a necessary step is missing from the approved todo list, stop and return to the earliest invalid phase. Do not keep coding once the plan is invalidated.

## Constraints

- Do not add scope, behavior changes, or architecture changes beyond approved work.
- Do not implement work not represented by the approved todo list.
- Do not mark unfinished tasks as completed.
- Do not make new design decisions that should have been captured in approved artifacts.

## Completion criteria

Leave this phase only when:

- every approved todo item is marked as complete (`- [ ]` changed to `- [x]`)
- implementation remains within approved scope
- no unresolved blocker requires rewinding to an earlier phase
