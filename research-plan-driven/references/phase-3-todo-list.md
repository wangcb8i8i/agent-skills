# Todo List

## Purpose

Turn the approved plan into a concrete, reviewable execution checklist before any implementation begins.

## What to do

1. Start from the latest approved version of `docs/<task-slug>.plan.md`.
2. Append a `## Todo List` section to the same file.
3. Break the approved work into concrete, objectively completable steps.
4. Order the todo items by real execution order and dependencies.
5. Include explicit validation tasks.
6. After the todo list, append a `## Things to note` section.
7. Ask the user to review and explicitly approve the embedded todo list before implementation begins.
8. If the user comments on the todo list, apply `references/review-guide.md` within the todo phase until the embedded todo list is explicitly approved.

## Todo structure

The todo list must:

- fully cover the approved implementation work
- break work into concrete, objectively completable steps
- reflect real execution order and dependencies
- include explicit validation tasks 

Use checkbox-based markdown items inside a `## Todo List` section in `docs/<task-slug>.plan.md`. 

**Todo example**

```markdown
## Todo List

### 1. Entry Points <!-- ref§Core Logic -->
- [ ] Add the new route registration in `src/api/notifications/routes.ts`
- [ ] Add the request handler in `src/api/notifications/controller.ts`
### 2. Core Behavior <!-- ref § SectionB-->
- [ ] Add the service method for listing notifications for the current user in `src/api/notifications/controller.ts`
- [ ] Add the repository query with the approved pagination and sort behavior in `src/api/notifications/controller.ts`
- [ ] Return the response in the existing API response shape
### 3. Safety and Edge Cases <!-- ref  § SectionC-->
- [ ] Reject unauthenticated requests using the existing auth flow 
- [ ] Handle invalid pagination input according to existing conventions
- [ ] Return an empty list correctly when the user has no notifications
### 4. Validation <!-- ref  § Approach C -->
- [ ] Add or update API tests for the happy path
- [ ] Add or update tests for auth failure and user isolation
- [ ] Run typecheck
- [ ] Run lint
- [ ] Run the relevant test suite
```

## Things to note

After the todo list, append a `## Things to note` section.

This section must answer these questions for the current task:

* In the implementation phase of current workflow, what constraints or specifications must/should be concerned with

Use this structure:

```markdown
## Things to note
<The organized answers of questions above here>
```

## Constraints

- Do not write implementation code in this phase.
- Do not create the todo list until the plan is explicitly approved.
- Keep the todo list practical and easy to execute mechanically.

## Completion criteria

Leave this phase only when:

- the embedded todo list has been added into `docs/<task-slug>.plan.md`
- the `## Things to note` section has been added after the todo list
- no unresolved review comments left in artifact
- the embedded todo list has been explicitly approved
