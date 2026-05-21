# Research

## Purpose

Build a deep understanding of all task-relevant information, based on both user-provided materials and the task-relevant parts of the codebase, so that later phases can proceed with comprehensive, reliable context.

## What to do

1. Define the task in concrete, researchable terms and split the investigation into focused questions or subsystems that can be researched without overlap.
2. Delegate codebase explore or investigate for those focused areas by default, and handle a check directly only when it is clearly narrower and faster than delegating it.
3. Treat all delegated findings as unverified input, then review them together, resolve conflicts, and read directly only where needed to verify critical claims or close material gaps.
4. Ask the user only for decisions, requirements, or facts that the codebase and delegated investigation cannot answer.
5. Write a readable/reviewable research artifact that contains verified task-relevant codebase reality and constraints, and any explicitly unresolved non-repository questions.

## Research delegation

Launch 1-3 focused subagents in parallel when that improves coverage or speed. Split work by focused question or subsystem, and avoid overlapping tasks.

The prompt to each subagent must include:

* What to investigate and why (the task context)
* Specific files or patterns to look at
* What kind of findings to return (actual implementations,patterns, data flows, conventions, edge cases)

A good prompt for subagent should:

* Tell trace through the code or file comprehensively and focus on getting a comprehensive understanding of abstractions, architecture and flow of control (understand how things work)
* Tell clear constraints and boundaries
* Give enough context about the surrounding problem that the agent can make judgment calls rather than just following a narrow instruction.

The coordinator reviews subagent findings, fills important gaps, resolves gaps and conflicts from repository evidence, and synthesizes `docs/<task-slug>.research.md`. 

Do not merge conflicting claims silently, and surface unresolved ambiguity explicitly. Always verify:
- conflicting findings
- low-confidence or ambiguity findings

## What the artifact should contain

- Clear and concise title
- Overview of the relevant system/module/package
- Key files and their responsibilities
- Data flow (how data moves through the system), control flow, timing diagrams, etc
- Existing patterns and conventions the codebase follows
- Dependencies and integrations
- Potential gotchas or constraints discovered
- Any existing similar functionality that could be reused or extended

Each non-obvious finding should include a source citation: `[src: path:line]`. This lets reviewers verify claims without re-searching the codebase.

Prefer compact tables or diagrams when they improve reviewability.

## What is not sufficient research

The following do not count as completed research on their own:

- a file list without behavioral understanding
- grep output without synthesis
- design proposals presented as facts
- findings from a single source without cross-verification
- unanswered questions that materially affect planning

## Constraints

- Do not include proposed implementation decisions as research facts.
- Do not write implementation code.
- Do not turn the research artifact into a plan.
- Do not finalize the artifact while material research questions remain unresolved.

## Completion criteria

Leave this phase only when:

- `docs/<task-slug>.research.md` exists
- the artifact is grounded in repository evidence
- material ambiguities affecting planning have been resolved or surfaced
- all current research review comments have been handled
- the user has explicitly approved the research artifact for planning
