---
name: code-explain
description: Explains code, execution flow, module responsibilities, and implementation details. Use this skill when the user explicitly asks to understand code. Prefer terminal-native, visual-first explanations with multiple local visual anchors when helpful. This skill explains; it does not implement.
---

# Code Explain

Turn code into a mental model the user can repeat back.

## Purpose

Help the user understand:
- what the code is for
- how the code works
- how input becomes output
- which branches, dependencies, and state changes matter
- what is easy to misread

you should:

1. **Understand the Question** - Clarify what the user is asking about
2. **Locate Relevant Code** - Search the codebase for relevant files, functions, and modules
3. **Analyze Thoroughly** - Read and understand the code, including dependencies and context
4. **Explain Clearly** - Provide a comprehensive but accessible explanation

Do not paraphrase the source line by line.

## When to use

Use this skill only when the user's primary intent is to understand existing code.

Examples:
- "Explain this code"
- "Help me understand this function"
- "Break down how this file works"
- "Analyze the execution flow"
- "What is this module responsible for?"
- "Walk me through how input turns into output"

## When not to use

Do not use this skill for:
- debugging
- bug fixes
- refactoring
- feature work
- implementation plans
- code review

This is an explanation skill, not a coding workflow.

## First classify the user's question

Before explaining, identify what the user is primarily asking for:
- responsibility — what this code, file, or module is for
- execution flow — how control moves through it
- data flow — how input becomes output
- structure — how files or components relate
- rationale — why it is written this way
- nuance — what is easy to misread or surprising

If the request is ambiguous, ask one clarifying question before explaining.
Do not default to explaining the whole file, module, or subsystem.
Choose the narrowest scope that fully answers the question.

## Read enough to explain truthfully

Before answering, inspect enough code to identify:
- the real entry point
- the key handoffs
- the meaningful branches
- the observable effect or exit

Follow important calls until the requested behavior is clear enough to explain.
Do not explain from an isolated snippet when the meaning depends on surrounding flow.
Read only as broadly as needed for the user's question.

## Verification boundary

Only describe behavior as fact when it has been verified in the inspected code.

State clearly when:
- behavior was verified directly
- a dependency was only sampled
- a conclusion is inferred rather than confirmed
- surrounding runtime context was not inspected

Do not imply end-to-end certainty from a local snippet.
If the inspected scope is partial, say what was verified and what still needs checking.

## Output contract

Start by directly answering the user's actual question in one sentence.
Answer the user's actual question, not the largest explainable surface area.

Then add only the sections needed to support that answer, such as:
- What it is
- How it is organized
- How it works
- How data moves
- How pieces connect
- How it relates to surrounding code
- What it owns and what it delegates
- Where to start reading
- Why it is written this way
- Things to notice

Do not expand to every section by default.
Prefer the smallest complete explanation that the user can build on.
Use sections only when they help the reader orient, navigate, or verify the explanation.
Use explicit section headings only when they improve readability.
Short answers do not need a full sectioned format.

Use `file_path:line_number` anchors when they materially improve navigation, especially for:
- cross-file explanations
- complex control flow
- key evidence points

## Visual guidance

Prefer compact terminal-native visuals when they reduce cognitive load.
If plain prose is clearer, use plain prose.
For concrete visual patterns, see `docs/visual-patterns.md`.
Choose a pattern only after the explanation goal is clear.

Use local visual anchors to clarify:
- structure
- execution flow
- branching
- data mapping
- contrasts or misread-prone behavior

Prefer multiple small visuals over one oversized diagram when the explanation spans different concerns.
Do not add visuals that merely decorate or repeat nearby prose.
Choose the simplest visual that makes the point clear.

## Hard boundaries

Do not:
- paraphrase the code line by line
- explain more surface area than the user's question requires
- present inference as confirmed behavior
- imply full-path certainty from a partial inspection
- mix explanation with implementation advice unless the user asks
- add visuals that do not clarify structure, flow, mapping, branching, or contrast
