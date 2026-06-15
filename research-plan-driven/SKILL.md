---
name: research-plan-driven
description: Use this skill only when the user explicitly asks for a research-plan-driven workflow. Trigger only for explicit requests such as phrases like “plan driven”, “research and plan”, or “research-plan”.
---

# Research-Plan-Driven

## Workflow

```
   Task Clarify
        │
        ▼
┌─────────────────┐
│    Research     │──<<review-revise Repeat>>──► until approved
└───────┬─────────┘
        │ approved
        ▼
┌─────────────────┐
│    Planning     │──<<review-revise Repeat>>──► until approved
└───────┬─────────┘
        │ approved
        ▼
┌─────────────────┐
│   Todo List     │──<<review-revise Repeat>>──► until approved
└───────┬─────────┘
        │ approved
        ▼
┌─────────────────┐
│  Implementation │
└───────┬─────────┘
        │
        ▼
┌─────────────────┐
│  Verification   │────► feedback final report
└─────────────────┘
													                
 ```

## Workflow Variants

### Full Pipeline (default)
All 5 phases (Research → Planning → Todo List → Implementation → Verification) with approval gates. Use when the task involves material unknowns, cross-module changes, or significant design decisions.

### Express Pipeline
Skip Research when the task is narrow, well-understood, and the user already has sufficient context. Flow: Task Clarify → Planning → Todo List → Implementation → Verification.

**Rules:**
- Suggest Express only during Task Clarify, after understanding the task scope
- The user must explicitly approve the shortcut
- If Express is chosen, skip Research and proceed directly to Planning
- If uncertainty emerges during Planning, recommend switching to Full Pipeline

## Critical Rules

| Non-Negotiable-Rule | Applies to phases |
| ---- | ----------------- |
| Require explicit approval before advancing to the next phase | Research , Planning , Todo List |
| Treat each approved artifact as the contract for the next phase | Research , Planning , Todo List |
| Every review revision requires critical thought to maintain contextual and logical alignment. | Research, Planning, Todo List |
| Do not read unrelated files under `docs/` unless the user explicitly asks | All phases |
| Read the corresponding reference first When the user approves to proceed to the next phase | All phases |
| Questions must focus to sharpen the real requirements | Task Clarify |
| Socratic question,for each question, provide your recommended answer. | Task Clarify |
| Proceed without stopping for approval during execution | Implementation, Verification |
| All output artifacts use Chinese as the primary language | All phases |

## Task Naming

Generate a short, stable, readable `task-slug` for the task and use it throughout the workflow.

> If resuming from an artifact the user provided, reuse its `task-slug`.

`task-slug` is used for name the required artifacts:

- `docs/<task-slug>.research.md`  

- `docs/<task-slug>.plan.md`

**Rule:** use the `docs` directory in Project root, create it if does not exist

## Task Clarify

Turn raw task/idea into **clear, accurate, and specific** shared understanding through structured dialogue **before research begins**. 

**Rules:**

- Ask **1-3 questions per message**; batch related questions together
- Prefer **multiple-choice questions** when possible
- Use open-ended questions only when necessary
- If a aspect of the task needs depth, split it into multiple questions

**Focus on understanding:**

- purpose  
- concrete deliverables or success criteria
- constraints 
- Boundaries
- explicit non-goals 

This step is meaningful and crucial for the quality of subsequent research and planning.

## Resume rules

Resume only from an artifact the user explicitly identifies.

| Artifact provided | Resume phase |
|---|---|
| `<task-slug>.research.md` | Research |
| `<task-slug>.plan.md` without `## Todo List` | Planning |
| `<task-slug>.plan.md` with `## Todo List` | Todo list |

**Important**: Before resuming, read all predecessor artifacts back to the identified one. If any predecessor is missing or insufficient, return to the earliest invalid phase instead of guessing.

## Phase references

**Note**: Read on demand

| File | Read when |
|---|---|
| `references/phase-1-research.md` | When Research becomes the active phase. |
| `references/phase-2-planning.md` | When Planning becomes the active phase. |
| `references/phase-3-todo-list.md` | When Todo list becomes the active phase. |
| `references/phase-4-implementation.md` | When Implementation becomes the active phase. |
| `references/phase-5-verification.md` | When Final verification becomes the active phase. |

## Review-Revise Repeat

**Purpose**: Through multiple rounds of review and revision, ensure the artifact achieves a shared understanding and is sufficiently correct to 

avoid rework in subsequent work caused by prior errors.

### What to do

* Find all review comments annotated by user
* Analyze each one and evaluate them comprehensively before responding
* Revise the artifact to address each comment, removing resolved comments sections
* **Before re-submission, run the self-check below** (see Before Re-submission Check)
* Ask the user to review the updated artifact again.
* Repeat until the user explicitly approves that artifact.

#### Before Re-submission Check

Before asking the user to re-review, verify all three:

1. **Content anchor check.** For each resolved comment, confirm the fix exists in the artifact by reading the exact line. Do not rely on memory ("I think I fixed it").
2. **Regression check.** Re-read the full artifact to confirm that fixes did not break consistency in other sections.
3. **Honest unresolved.** If any comment was only partially fixed, or you are unsure if the fix is correct, state it explicitly. Do not skip or silently downgrade.

#### Stuck Escalation

If after 2+ rounds the user's core concern is still unresolved:

1. Stop fixing individual comments
2. Ask the user: *"What is the single core issue that still isn't right?"*
3. Focus the next revision on that one issue only

### How to find comments

Check for inline comments and end-of-document review sections, including markers such as `COMMENT`  or `Review Comments`

Comments should follow this format:

> `COMMENT: <text> [on: "<anchor text>"]`
>
> The `on:` field is optional and points to the specific content the comment refers to. If present, use it to locate the referenced section before revising.

### Constraints

- Do not treat comments as approval.
- Do not ignore, silently drop, or partially address a comment.
- Don't mechanize and mindlessly resolve comments
- Don't jump out of the repetitive process of 'review-revise' without the explicit approval



## Workflow Complete

This skill is complete only when all implementations have been verified and fed back, and confirmed by the user.
