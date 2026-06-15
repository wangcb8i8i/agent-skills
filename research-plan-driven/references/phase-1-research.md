# Research

## Purpose

Build a deep understanding of all task-relevant information, based on both user-provided materials and the task-relevant parts of the codebase, so that later phases can proceed with comprehensive, reliable context.

## What to do

1. Define the task in concrete, researchable terms and split the investigation into focused questions or subsystems that can be researched without overlap.
2. Delegate codebase explore or investigate for those focused areas by default, and handle a check directly only when it is clearly narrower and faster than delegating it.
3. Treat all delegated findings as unverified input, then review them together, resolve conflicts, and read directly only where needed to verify critical claims or close material gaps.
4. Ask the user only for decisions, requirements, or facts that the codebase and delegated investigation cannot answer.
5. Write a readable/reviewable research artifact that contains verified task-relevant codebase reality and constraints, and any explicitly unresolved non-repository questions.
6. Verify the artifact against common coverage gaps before presenting:
   - Does it describe how data moves through the affected paths?
   - Does it document the relevant codebase patterns and conventions?
   - Does it surface gotchas or constraints that materially affect planning?
   - Does it check for existing reusable functionality?
   - Does it note what was NOT found (e.g. queried but absent)?
   - Does it contain any proposals, solutions, or recommendations that go beyond factual findings?
   If any answer is no, fill the gap. If deliberately skipped, note why.

## Artifact organization

Research artifacts should follow a top-down reading logic. Each section answers a question the reviewer will ask:

1. **Scope alignment** — Open with the research goal and scope so the reviewer can confirm "this matches the task"
2. **Key findings** — Follow immediately with 2–3 most critical findings (evidence anchor + confidence label). The reviewer can stop here or dive deeper
3. **Detailed findings** — Organize by subsystem or research question, each claim traceable to source
4. **Context** — Codebase patterns, conventions, data flows, and constraints that affect planning
5. **Unresolved questions** — Explicitly list open items that block planning decisions

This order expresses the reading logic, not fixed headings. Skip a section if its conclusion is empty.

## Research delegation

Launch 1-3 focused subagents in parallel when that improves coverage or speed. Split work by focused question or subsystem, and avoid overlapping tasks.

The prompt to each subagent must include:

* What to investigate and why (the task context)
* Specific files or patterns to look at
* What kind of findings to return (actual implementations,patterns, data flows, conventions, edge cases)
* Constraint: investigate facts only — do not propose solutions, architectures, or feature ideas

A good prompt for subagent should:

* Tell trace through the code or file comprehensively and focus on getting a comprehensive understanding of abstractions, architecture and flow of control (understand how things work)
* Tell clear constraints and boundaries
* Give enough context about the surrounding problem that the agent can make judgment calls rather than just following a narrow instruction.

The coordinator reviews subagent findings, fills important gaps, resolves gaps and conflicts from repository evidence, and synthesizes `docs/<task-slug>.research.md`. 

Do not merge conflicting claims silently, and surface unresolved ambiguity explicitly. Always verify:
- conflicting findings
- low-confidence or ambiguity findings

## Review-friendly principles

The artifact must enable the reviewer to confidently answer:
*is this research complete and accurate enough to plan against?*

- **Scope-aligned.** Every major finding traces back to the agreed task scope.
  Off-track exploration is surfaced as supplementary, not mixed in.
- **Scope-complete.** The reviewer can see what was investigated, what was
  found, and what remains unanswered. Material gaps exposed, not hidden.
- **Evidence-anchored.** Each non-obvious finding includes a source citation
  `[src: path:line]`. Conflicting findings surfaced, not merged silently.
- **Certainty-labeled.** Confidence labeled for non-trivial findings
  (high / medium / low). Speculation is not research.
- **Planning-actionable.** The artifact ends with a clear picture of what
  is known well enough to plan, and what is not.

## Floor

The following do not count as completed research on their own:

- a file list without behavioral understanding
- grep output without synthesis
- design proposals presented as facts
- proposals or solutions presented as research findings
- findings from a single source without cross-verification
- unanswered questions that materially affect planning

Prefer compact tables or diagrams — they reduce scanning effort and make the artifact easier to review.

## Constraints

- Do not include proposed implementation decisions as research facts.
- Do not include new feature ideas, architecture proposals, or solution suggestions in the research artifact.
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
