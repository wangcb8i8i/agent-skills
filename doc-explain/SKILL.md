---
name: doc-explain
description: Explains documents—proposals, specs, decision records, guides, reports. Use this skill when the user explicitly asks to understand a document. Prefer terminal-native, visual-first explanations with multiple local visual anchors when helpful. This skill explains; it does not implement, review, or co-author.
---

# Doc Explain

Turn a document into a mental model the user can repeat back.

## Purpose

Help the user understand:
- what the document claims or proposes
- how the argument is constructed
- what evidence, assumptions, and gaps sit behind each conclusion
- how sections relate to each other and to other documents
- what is easy to misread, missing, or ambiguous

## When to use

Use this skill only when the user's primary intent is to understand an existing document.

Examples:
- "Explain this doc"
- "What does this spec actually propose?"
- "Walk me through the argument in this decision record"
- "How are these two docs related?"
- "What's the structure of this report?"
- "What does this doc assume but never state?"
- "Summarize the key decisions in this proposal"

## When not to use

Do not use this skill for:
- co-authoring or editing documents
- reviewing or critiquing documents
- comparing documents to code
- debugging
- implementation planning
- code explanation

This is an explanation skill, not a writing or review workflow.

## First classify the document and the question

Before explaining, identify two things:

### Document type

- proposal — advocates for a change or decision
- spec — defines what should be built or how it should behave
- decision-record — captures a concluded decision, rationale, and alternatives
- guide — instructs the reader how to do something
- reference — catalogs facts, APIs, or configurations
- report — narrates findings, events, or analysis
- strategy / vision — sets direction, principles, or goals

### Question category

- premise — what this document claims, proposes, or concludes
- reasoning chain — how the argument builds from premises to conclusions
- skeleton — how the document is organized and what each section is responsible for
- context — what background, problem, or constraint motivated this document
- relationship — how this document relates to others (references, extends, contradicts)
- decision — what was decided, by whom, on what basis, with what tradeoffs
- ambiguity / gap — what is unsaid, assumed, missing, or easy to misread
- information flow — how data, evidence, or conclusions move through the document

If the request is ambiguous, ask one clarifying question before explaining.
Do not default to summarizing the whole document.
Choose the narrowest scope that fully answers the question.

## Read enough to explain truthfully

Before answering, inspect enough of the document to identify:
- the central claim or thesis
- the key supporting sections
- the conclusion or call to action
- the boundaries between fact, inference, and opinion
- cross-references that materially affect understanding

Read referenced documents when the meaning of this document depends on them.
Read only as broadly as needed for the user's question.

## Verification boundary

Only describe document content as fact when it has been verified by direct inspection.

State clearly when:
- content was verified directly in the document
- a referenced document was only sampled (e.g., title, abstract, or opening)
- a gap or missing piece is inferred rather than confirmed
- surrounding context (org decisions, prior discussions) was not inspected

Do not imply full-document certainty from a partial read.
If the inspected scope is partial, say what was verified and what still needs checking.

## Output contract

Start by directly answering the user's actual question in one sentence.

Then add only the sections needed to support that answer, such as:
- What it claims
- How it is organized
- How the argument builds
- What evidence supports it
- What it assumes or omits
- How it relates to other documents
- Key decisions and their rationale
- Where to start reading
- Things that are easy to misread

Do not expand to every section by default.
Prefer the smallest complete explanation that the user can build on.
Use sections only when they help the reader orient, navigate, or verify the explanation.

## Visual guidance

Prefer compact terminal-native visuals when they reduce cognitive load.
If plain prose is clearer, use plain prose.
For concrete visual patterns, see `docs/visual-patterns.md`.
Choose a pattern only after the explanation goal is clear.

Use local visual anchors to clarify:
- argument structure
- section organization and responsibility
- decision records and tradeoffs
- cross-document relationships
- claims vs. evidence vs. gaps
- timelines of events, versions, or decisions
- comparisons between alternatives

Prefer multiple small visuals over one oversized diagram when the explanation spans different concerns.
Do not add visuals that merely decorate or repeat nearby prose.
Choose the simplest visual that makes the point clear.

## Artifact output

By default, this skill does not produce files. Explanations live in the conversation.

When the user explicitly asks to persist the explanation ("save as read-notes", "write that to docs/", "create a reading note"):

- Write to the path the user specifies, or suggest `docs/read-notes/<doc-name>.md` if none given
- Use richer visual formats when the target is a markdown file (mermaid diagrams, full-width tables) since the output renders in a viewer, not a terminal
- Include a header block with source document path, date, and scope of reading
- Do not re-explain in the conversation after writing; confirm the file path and let the user open it

This is an opt-in extension, not the default behavior.

## Hard boundaries

Do not:
- paraphrase the document section by section
- explain more surface area than the user's question requires
- present inference as document fact
- imply full-document certainty from a partial inspection
- mix explanation with critique, review, or co-authoring unless the user asks
- add visuals that do not clarify argument, structure, decision, relationship, or gap
- supplement what the document "should have said" — a gap is noted, not filled
