---
name: doc-explain
description: Explains documents—proposals, specs, decision records, guides, reports. Prefer terminal-native, visual-first explanations with multiple local visual anchors when helpful. This skill explains; it does not implement, review, or co-author. Do not auto-trigger — use only when the user explicitly asks to understand a document.
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

## Workflow

This skill has two modes, chosen by scope:
- **Standard**: short to medium documents — single-turn, one response and done.
- **Map + navigate**: large documents — multi-turn across 3+ responses.

The decision path: **classify → detect scale → read & verify → execute the chosen mode**.

### 1. Classify the document and question

Before explaining, identify two things:

#### Document type

- **proposal** — advocates for a change or decision
- **spec** — defines what should be built or how it should behave
- **decision-record** — captures a concluded decision, rationale, and alternatives
- **guide** — instructs the reader how to do something
- **reference** — catalogs facts, APIs, or configurations
- **report** — narrates findings, events, or analysis
- **strategy / vision** — sets direction, principles, or goals

#### Question category

- **premise** — what this document claims, proposes, or concludes
- **reasoning chain** — how the argument builds from premises to conclusions
- **skeleton** — how the document is organized and what each section is responsible for
- **context** — what background, problem, or constraint motivated this document
- **relationship** — how this document relates to others (references, extends, contradicts)
- **decision** — what was decided, by whom, on what basis, with what tradeoffs
- **ambiguity / gap** — what is unsaid, assumed, missing, or easy to misread
- **information flow** — how data, evidence, or conclusions move through the document

If the request is ambiguous, ask one clarifying question before explaining.
Do not default to summarizing the whole document.
Choose the narrowest scope that fully answers the question.

### 2. Detect scale

After classifying, assess whether the document is **small** or **large**.

A document is **large** when any of these apply:
- 10+ pages or major sections
- multiple nested arguments or sub-decisions that each deserve independent treatment
- cross-references to 3+ other documents that materially affect understanding
- complex argument structure (premises → sub-conclusions → main conclusion)
- the user explicitly describes it as large, dense, or hard to follow

When uncertain, default to large. A map is always skimmable; a shallow explanation of a deep document is useless.

→ small: go to [Standard mode](#4-standard-mode-small-scope).
→ large: go to [Map + Navigate mode](#5-map--navigate-mode-large-scope).

### 3. Read & verify

Applies to both modes.

#### Read enough

Before answering, inspect enough of the document to identify:
- the central claim or thesis
- the key supporting sections
- the conclusion or call to action
- the boundaries between fact, inference, and opinion
- cross-references that materially affect understanding

Read referenced documents when the meaning of this document depends on them.
Read only as broadly as needed for the user's question.

#### Verification boundary

Only describe document content as fact when verified by direct inspection. State clearly when:
- content was verified directly in the document
- a referenced document was only sampled (e.g., title, abstract, or opening)
- a gap or missing piece is inferred rather than confirmed
- surrounding context (org decisions, prior discussions) was not inspected

Do not imply full-document certainty from a partial read.
If the inspected scope is partial, say what was verified and what still needs checking.

### 4. Standard mode (small scope)

Single-turn explanation. Start by directly answering the user's actual question in one sentence.

#### Output

Add only the sections needed to support that answer, such as:
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

#### Visual guidance

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

### 5. Map + Navigate mode (large scope)

When scale detection flags a document as large, do not attempt a single-pass explanation. Instead, guide the user through three phases: map the argument territory, navigate selected sections in depth, then synthesize back into a coherent whole. The user controls pacing and section selection throughout.

**CRITICAL — Multi-turn interaction**: This mode spans 3+ responses. You MUST NOT complete multiple phases in one response. Each phase boundary is a hard stop — output the phase content, emit the user-facing prompt, then wait. A typical interaction: turn 1 = Phase 1 (map) → user reply → turn 2 = Phase 2 (dive into section A) → user reply → turn 3 = Phase 2 (dive into section B) → user says "合拢" → turn 4 = Phase 3 (synthesize). Never collapse these boundaries.

#### Phase 1: Map (reconnaissance)

Goal: give the user a global mental model of the document without diving into any single section.

Read broadly but shallowly — scan the table of contents, abstract, introduction, section headings, and conclusion. Identify the central thesis, key arguments, and how sections relate.

Output:
- **文档地图**: a structure or hierarchy diagram showing sections, their roles in the argument, and how they relate. Use the existing structure or hierarchy/tree visual patterns.
- **关键章节**: a compact table listing each key section or argument, what it contributes in one sentence, and its importance (core / important / supporting).
- **建议阅读顺序**: the recommended order to explore sections. Default to core thesis → supporting arguments → context/appendices unless the user has a specific question.

End Phase 1 by asking the user which section to dive into first.

```
这份文档有 N 个关键章节。你想先深入哪个？（输入编号或名称，也可以跳过直接合拢）
```

CRITICAL: After outputting the document map, section catalog, and this prompt, STOP. Do not deep-dive any section. Do not proceed to Phase 2. Wait for the user to select a section before continuing.

#### Phase 2: Navigate (deep-dive)

Goal: trace one section or argument chain deeply, matching the quality of the standard small-document explanation.

When the user selects a section:
- Read that section and any referenced material that materially affects its meaning.
- Explain what it claims, how it supports the larger thesis, what evidence it relies on, and what it assumes or omits.
- Use the same visual patterns, verification boundary, and output contract as the standard explain mode.
- Stay within the scope of one section or argument. Do not detour into sibling sections.

After each section, output a brief summary and ask the next move:

```
**已探索**: [section-name]

下一个深入哪个？还是"合拢"？
```

CRITICAL: After each deep-dive response, STOP. Do not dive into another section until the user responds with a selection or "合拢".

Accept these user responses:
- a section number/name → dive into that section
- "合拢" or "synthesize" → move to Phase 3
- "停" or "pause" → stop here, save progress for next session

#### Phase 3: Synthesize (assemble)

Goal: weave the explored sections back into a single coherent understanding the user can retell.

When the user asks to synthesize:
- Recap the document map, visually marking which sections were explored.
- Show how the explored sections connect — how supporting arguments feed the central thesis, where evidence chains converge.
- Present the document's core argument end-to-end, covering all explored sections in their proper relationships.
- List any unexplored sections the user may want to revisit later.

The user should walk away able to explain the document's thesis, argument structure, and key evidence to someone else. That is the success criterion.

#### Cross-session

The user may pause and resume across conversations. To support this:
- When the user pauses, summarize what was covered and what remains.
- When the user returns and says "继续解读" or references the same document, pick up from the last phase and section.
- Track progress in conversation state — no file persistence needed.

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
- modify, create, or delete any file (except [Artifact output](#artifact-output) when explicitly requested)
- paraphrase the document section by section
- explain more surface area than the user's question requires
- present inference as document fact
- imply full-document certainty from a partial inspection
- mix explanation with critique, review, or co-authoring unless the user asks
- add visuals that do not clarify argument, structure, decision, relationship, or gap
- supplement what the document "should have said" — a gap is noted, not filled
- for large documents, skip the map and jump straight to deep-dive
- for large documents, dive into every section in one response — let the user choose the pace
- for large documents, complete multiple map+navigate phases in a single response — each phase is a separate turn
- add sections to the catalog that don't materially affect understanding
