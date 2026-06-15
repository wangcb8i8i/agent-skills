# Planning

## Purpose

Create a detailed, reviewable, concrete implementation plan based on the approved research

## What to do

1. Base the plan on the latest approved research artifact (or on the shared understanding from Task Clarify if Express Pipeline was chosen).
2. Define the intended implementation approach concretely enough that coding should not require inventing architecture on the fly.
3. Name the exact files, components, interfaces, contracts, or boundaries expected to change.
4. Record the important technical decisions and the rationale behind them.
5. Make risks, trade-offs, scope limits, and unresolved decisions easy to review.
6. Write implementation plan into plan artifact
7. Verify the artifact against common coverage gaps before presenting:
   - Does it name every file expected to change and why?
   - Does it expose key decisions with rationale and alternatives?
   - Does it surface risks, edge cases, and non-goals explicitly?
   - Can a reviewer understand the implementation without filling in gaps?
   If any answer is no, fill the gap. If deliberately skipped, note why.

## Artifact organization

Plan artifacts should follow a top-down reading logic. Each section answers a question the reviewer will ask:

1. **Goal & approach** — Open with the goal, implementation strategy, and a workflow / data flow / architecture skeleton
2. **Change list** — File-by-file: what changes and how
3. **Key decisions** — Important decisions, rationale, and alternatives considered
4. **Risks & boundaries** — Identified risks and explicit non-goals

This order expresses the reading logic, not fixed headings. Skip a section if its conclusion is empty.

**Once the plan artifact written:**

1. Conduct a pre-review of the plan according to the  `guides/pre-review.md` （Do not read before the planned artifact is created）.

1. Ask the user to review the plan artifact. Do not implement yet; wait for explicit approval.

## Review-friendly principles

The artifact must enable the reviewer to confidently answer:
*is this plan safe to implement?*

- **Approach-clarity.** The core strategy — how pieces fit together —
  is the first substantive section, not buried in detail.
- **Scope-explicit.** Every file touched named with intent. Non-goals
  stated so the reviewer can spot scope creep before it happens.
- **Decision-visible.** Key technical decisions surfaced with rationale
  and rejected alternatives. Implicit decisions are a review blocker.
- **Concrete-enough.** Interfaces, contracts, data shapes, and boundary
  conditions named. The reviewer should not need to fill in gaps.
- **Risk-surfaced.** Risks, trade-offs, edge cases, and unresolved
  approval points easy to locate — not buried in prose.
- **Self-contained.** Summary-level understanding possible without
  leaving the artifact. Research referenced but not required reading.

## Floor

A plan needs revision before todo creation when:
- major implementation decisions are still implicit
- affected files or boundaries are not named concretely
- the intended structure of code changes is vague
- validation approach is missing or vague
- key design gaps would need to be solved during implementation

## Constraints

- Do not write implementation code.
- Do not create the todo list in this phase.
- Do not treat plan approval as implementation approval.
- Do not add scope not justified by approved research.
- Do not leave important design gaps to be invented during implementation.

## Completion criteria

Leave this phase only when:

- `docs/<task-slug>.plan.md` exists
- the plan is concrete and reviewable
- all current plan review comments have been handled
- the user has explicitly approved the plan artifact
