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

`docs/<task-slug>.plan.md` should contain:

- Clear and concise title
- summary of what will be built and why, referencing the research artifact it is based on
- concise outline of the plan
- list of file paths to be created or modified and the intent of each change （excluding the name of the planning artifact itself）
- Detailed approach with rationale for key decisions
- Code snippets showing the actual planned changes (not pseudocode — real code shapes)
- Important interfaces, schemas, contracts, or data-shape changes
- Trade-offs considered and why this approach was chosen
- Anything that was intentionally left out and why
- Scope boundaries and explicit non-goals
- Risks, edge cases, and unresolved approval points

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
