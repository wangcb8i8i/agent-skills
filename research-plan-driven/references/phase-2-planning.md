# Planning

## Purpose

Create a detailed, reviewable, concrete implementation plan based on the approved research

## What to do

1. Base the plan on the latest approved research artifact.
2. Define the intended implementation approach concretely enough that coding should not require inventing architecture on the fly.
3. Name the exact files, components, interfaces, contracts, or boundaries expected to change.
4. Record the important technical decisions and the rationale behind them.
5. Make risks, trade-offs, scope limits, and unresolved decisions easy to review.
6. Write implementation plan into plan artifact



**Once the plan artifact written:**

1. Conduct a pre-review of the plan according to the  `guides/pre-review.md` （Do not read before the planned artifact is created）.

1. Ask the user to review the plan artifact, do not implementation yet, wait user explicy approval.

## What the artifact should contain

`docs/<task-slug>.plan.md` should follow a **coarse-to-fine, progressive disclosure** structure. The reader should be able to grasp the full picture at the top level, then dive into details as needed.

### Required structure (top-to-bottom order)

Each section in this order, each level providing only what the previous level couldn't convey:

| Level | Section | Purpose | Max length |
|---|---|---|---|
| 1 | **Title & Summary** | What we're building and why. Reference the research artifact. | 2-3 sentences |
| 2 | **Change Inventory** | File paths to create/modify, and **the intent of each change**. Exclude the planning artifact itself. | Bullet list, 1-2 lines each |
| 3 | **Top-Level Approach** | The high-level strategy — how the pieces fit together. Not pseudocode, but a conceptual architecture. | 3-5 sentences |
| 4 | **Resulting Shape** | What the codebase looks like after this plan is executed. Use a structural diagram (tree, module map, or relationship sketch) so the reviewer can visualize the outcome at a glance. | 1 visual block + brief caption |
| 5 | **Key Decisions** | Important technical decisions and the rationale behind them. Trade-offs considered, why this approach was chosen. | Per decision: 2-4 sentences |
| 6 | **Detailed Approach** | Concrete implementation details organized by weight/importance. Lead with what's novel or risky; routine wiring goes later. Include code snippets (real code shapes, not pseudocode), interfaces, schemas, contracts, data-shape changes. | As needed |
| 7 | **Scope & Risks** | Explicit non-goals, scope boundaries, risks, edge cases, unresolved approval points. Anything intentionally left out and why. | Bullet list |

### Key principles

- **Progressive disclosure**: Each level is a summary/abstraction of what follows. The reviewer can stop after any level and make a decision.
- **Resulting Shape is mandatory**: This is the most commonly missing piece. Show the end state — don't make the reviewer infer it from a pile of diffs.
- **Weight before order, not order before weight**: In Detailed Approach, lead with the most novel, risky, or consequential implementation details. Routine wiring and boilerplate go last.
- **Navigation aids**: Use clear headings and, where helpful, cross-reference ("see §Detailed Approach for the full implementation of X").

## What is not sufficient plan

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
