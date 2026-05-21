---
name: revise-markdown
description: Revise a markdown document through a structured review-comment loop — find, analyze, and address inline comments, then repeat until the user explicitly approves. Trigger only when the user explicitly requests it, e.g. "revise the doc", "address the comments", "review and revise", "update the markdown based on comments". Do not auto-trigger.
---

# Revise Markdown

## Purpose

Iteratively revise a markdown artifact by finding, analyzing, and addressing embedded review comments until the user explicitly approves the result.

This is a **review-revise loop**, not a one-shot edit. It ensures every comment is accounted for and no feedback is silently dropped.

## Workflow

```
   Read artifact
        │
        ▼
┌──────────────────┐
│  Find & analyze  │
│    all comments  │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Revise artifact │
│ (address each)   │
│ (remove resolved)│
└──────┬───────────┘
       │
       ▼
   Ask for review
   ┌──────────────┐
   │ User review  │── comments exist ──► loop back
   └──────┬───────┘
          │ explicit approval
          ▼
         Done
```

## Comment Format

Comments must follow this format:

> `COMMENT: <text> [on: "<anchor text>"]`

- `COMMENT:` is the marker that identifies a review comment.
- `on:` is an optional field pointing to the specific content the comment refers to. Use it to locate the referenced section before revising.

Comments can appear:
- Inline within sections
- In a dedicated `## Review Comments` section at the end of the document
- Using variations like `REVIEW COMMENT:` or other obvious review markers

## What to do

1. **Find** all review comments in the artifact. Check both inline and end-of-document review sections.
2. **Analyze** each comment comprehensively before responding. Understand what change is being requested and why.
3. **Evaluate** all comments together — some may interact or conflict. Resolve conflicts before revising.
4. **Revise** the artifact to address each comment fully.
5. **Remove** resolved comment sections from the artifact. A comment stays only if it remains open.
6. **Ask** the user to review the updated artifact.
7. **Repeat** until the user explicitly approves.

## Constraints

| Rule | Rationale |
|---|---|
| Do not treat comments as approval | A comment is feedback, not a sign-off |
| Do not silently drop or partially address a comment | Every comment must be accounted for |
| Do not mechanize — think critically about each comment | Comments may interact, conflict, or miss context |
| Do not exit the review-revise loop without explicit approval | "Looks good" with unresolved comments is not approval |
| If a comment is unclear, ask for clarification before revising | Guessing wastes iterations |
| Remove resolved comment blocks after addressing them | Keeps the artifact clean for the next review round |

## Handling ambiguous comments

If a comment is genuinely ambiguous or its intent is unclear:

1. Surface the ambiguity explicitly: "Comment #3 says 'make this better' — what dimension should I improve: clarity, accuracy, completeness, or conciseness?"
2. Offer a recommended interpretation and let the user confirm.
3. Keep the comment in place until resolved.

## Completion criteria

The loop ends only when:

- All review comments have been addressed and removed from the artifact
- The user has explicitly approved the artifact (e.g. "approved", "LGTM", "proceed")
