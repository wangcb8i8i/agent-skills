# Visual Patterns for doc-explain

Use these patterns to choose the clearest terminal-native visual when a visual would help.

Prefer the simplest pattern that reduces cognitive load.
Prefer plain prose when a visual would not add clarity.
Prefer multiple small visuals over one oversized diagram when different concerns need different views.

Choose a pattern only after reading enough of the document to know what the explanation is really about.
Let the user's question shape what the explanation emphasizes.
When several patterns could work, prefer the one that resolves the dominant confusion most clearly.

---

## 1. Reasoning chain pattern

### Use when
- the argument structure matters
- a claim is built from premises, evidence, and inferences
- the main question is "how does this document reach its conclusions?"

### Goal
Show how premises chain into conclusions, and where the chain weakens.

### Output shape

```text
[premise A] ──┐
              ├──▶ [inference] ──▶ [conclusion]
[premise B] ──┘        │
                    [assumption: ...]
```

### What to emphasize
- the premises that carry the most weight
- the inference step where the chain is weakest or most implicit
- assumptions that are stated vs. those that are only implied
- where evidence is cited vs. where the author asserts without support

### Example

```text
[users report confusion] ──┐
                           ├──▶ [UI must be redesigned] ──▶ [allocate 2 sprints]
[competitor X does it]  ──┘        │
                               [assumption: confusion is caused by UI, not workflow]
```

### Common misuse
- Do not use this when the document is a reference or guide with no argument.
- Do not force a linear chain onto a document that argues by accumulation, not deduction.
- Do not treat every sentence as a premise — only the claims that drive the conclusion.

---

## 2. Skeleton map pattern

### Use when
- section organization and responsibility matter
- the user needs to navigate the document efficiently
- the main question is "what is where, and what does each part do?"

### Goal
Show the document's structure with one-line role annotations.

### Output shape

```text
doc-title/
├── §1 Introduction       — problem statement, scope
├── §2 Background         — prior art, constraints
├── §3 Proposal           — the change being advocated
│   ├── §3.1 Design       — how it works
│   └── §3.2 Tradeoffs    — alternatives considered
├── §4 Implementation     — rollout plan
└── §5 Open Questions     — unresolved items
```

### What to emphasize
- the section that carries the core claim or decision
- sections that can be skipped for a given question
- surprising or non-obvious placement ("the budget is in §7, not §2")

### Example

```text
ADR-0042-auth-migration.md/
├── §1 Context            — why the current auth system must change
├── §2 Options            — 3 alternatives evaluated
├── §3 Decision           — chosen approach + rationale
├── §4 Consequences       — what gets easier, what gets harder
└── §5 Migration Plan     — phased rollout
```

### Common misuse
- Do not reproduce the full TOC. Annotate only the sections relevant to the question.
- Do not use this when the user's question is about argument, not navigation.
- Do not leave section roles vague ("§3 = details").

---

## 3. Decision table pattern

### Use when
- the document records one or more decisions
- the user needs to understand who decided what, why, and with what tradeoffs
- the main question is "what was decided and on what basis?"

### Goal
Compress decision records into a scannable table.

### Output shape

```md
| Decision | Who | Rationale | Tradeoff / Cost | Status |
|----------|-----|-----------|-----------------|--------|
| ...      | ... | ...       | ...             | ...    |
```

### What to emphasize
- decisions, not every opinion in the document
- the tradeoff column — what was knowingly sacrificed
- whether the decision is proposed, accepted, or superseded

### Example

```md
| Decision | Who | Rationale | Tradeoff | Status |
|----------|-----|-----------|----------|--------|
| Use OAuth2 not SAML | security team | broader ecosystem support | SAML IdP users need migration | accepted |
| Self-host not SaaS | infra lead | data residency req | increased ops burden | proposed |
```

### Common misuse
- Do not use this for documents that contain no decisions.
- Do not list every technical choice as a "decision" — reserve for tradeoff-bearing choices.
- Do not invent rationale the document doesn't state.

---

## 4. Cross-reference graph pattern

### Use when
- the document depends on or is referenced by other documents
- the user needs to understand the document's context in a larger corpus
- the main question is "how does this fit with everything else?"

### Goal
Show inbound and outbound references with relationship types.

### Output shape

```text
[prerequisite doc] ──▶ [this document] ──▶ [dependent doc]
         (defines terms)              (builds on proposal)
                             │
                             ├──▶ [contradicts: alt-proposal.md]
                             └──▶ [supersedes: old-spec.md]
```

### What to emphasize
- references that materially change how this document should be read
- contradictions that the reader should be aware of
- documents that this one supersedes or deprecates

### Example

```text
[team-charter.md] ──▶ [this spec] ──▶ [implementation-plan.md]
   (defines scope)                     (execution detail)
                  │
                  ├──▶ [obsoletes: v1-spec.md]
                  └──▶ [references: api-contract.md §3]
```

### Common misuse
- Do not map every hyperlink. Only the references that affect understanding.
- Do not use this for a standalone document with no meaningful references.
- Do not guess at relationship types — infer only when the document states it.

---

## 5. Gap matrix pattern

### Use when
- the document's omissions matter as much as its content
- the user needs to see what was promised vs. what was delivered
- the main question is "what does this document leave out?"

### Goal
Surface mismatches between scope claims and actual coverage, plus unstated assumptions.

### Output shape

```md
| Claim / Expectation | Covered? | Notes |
|---------------------|----------|-------|
| ...                 | ✔ / ✘ / ⚡ | ...   |
```

### What to emphasize
- claims the document makes about its own scope that it doesn't fulfill
- topics a reader would reasonably expect that are absent
- assumptions that would change the reading if they were false

### Example

```md
| Expectation | Covered? | Notes |
|-------------|----------|-------|
| Problem statement | ✔ | §1 |
| Alternatives considered | ✘ | mentions "other options" but never names them |
| Rollback plan | ✘ | not addressed |
| Performance targets | ⚡ | mentioned in passing, no numbers |
```

### Common misuse
- Do not use this to list everything the document isn't. Only gaps relevant to the user's question.
- Do not confuse "I wish it said X" with "a reasonable reader would expect X."
- The ⚡ (partial) marker is for content that is mentioned but not substantiated.

---

## 6. Timeline pattern

### Use when
- the document narrates events, versions, or decisions over time
- chronological order matters to understanding
- the main question is "what happened when, and in what order?"

### Goal
Show events in time sequence with causal or dependency links.

### Output shape

```text
2024-01    2024-03       2024-06       2024-09
   │          │             │             │
   ▼          ▼             ▼             ▼
[event A]──▶[event B]────▶[decision]───▶[outcome]
               │                          │
               └── [parallel event C] ────┘
```

### What to emphasize
- the event or decision that changed direction
- events whose order is surprising or consequential
- parallel tracks that intersect

### Example

```text
Q1                  Q2                    Q3
 │                   │                     │
 ▼                   ▼                     ▼
[incident #42]──▶[postmortem]──▶[ADR-0042 adopted]──▶[migration starts]
                      │
                      └── [parallel: vendor evaluation]
```

### Common misuse
- Do not use this when the document is not organized around time.
- Do not invent a timeline from a document that only implies one.
- Do not add dates the document doesn't provide.

---

## 7. Options-compared table pattern

### Use when
- the document evaluates multiple alternatives
- the user needs to understand tradeoffs between options
- the main question is "what were the choices and why was this one picked?"

### Goal
Show alternatives side by side with the criteria that drove selection.

### Output shape

```md
| Criterion | Option A | Option B | Option C (chosen) |
|-----------|----------|----------|--------------------|
| ...       | ...      | ...      | ...                |
```

### What to emphasize
- the criterion that was decisive
- options that were close contenders vs. strawmen
- criteria that were considered but not weighted

### Example

```md
| Criterion | OAuth2 | SAML | Custom (chosen for phase 1) |
|-----------|--------|------|---------------------------|
| Time to implement | 2 wk | 4 wk | 1 wk |
| Ecosystem support | strong | moderate | none |
| Migration cost later | low | low | high |
```

### Common misuse
- Do not invent criteria the document doesn't mention.
- Do not use this when only one option was seriously considered.
- Do not guess at why an option was rejected if the document doesn't say.

---

## 8. Compact table pattern

### Use when
- several entities, roles, or concepts have distinct definitions
- a flat comparison is easier to scan than prose
- the document is a reference or glossary

### Goal
Compress key distinctions into a small readable table.

### Output shape

```md
| Item       | Definition | Scope / Boundary | Why it matters |
|------------|------------|------------------|----------------|
| ...        | ...        | ...              | ...            |
```

### What to emphasize
- only the terms or entities needed to read the document correctly
- the contrast the reader is most likely to miss
- stable, narrow columns that scan quickly in a terminal

### Example

```md
| Term       | Definition                              | Boundary                     |
|------------|-----------------------------------------|------------------------------|
| workspace  | a tenant-isolated project container     | 1 workspace = 1 billing unit |
| project    | a git repo + config + collaborators     | lives inside a workspace     |
| deployment | a running instance of a project branch  | tied to a single environment |
```

### Common misuse
- Do not build wide tables that wrap badly in terminal output.
- Do not include entries that are not necessary for understanding.
- Do not use a table when sequence or argument is the real mental model.

---

## Pattern selection shortcut

- "What does this doc claim?" → reasoning chain
- "How is the argument built?" → reasoning chain
- "How is this document organized?" → skeleton map
- "What was decided and why?" → decision table
- "How does this relate to other docs?" → cross-reference graph
- "What's missing or assumed?" → gap matrix
- "What happened in what order?" → timeline
- "What were the alternatives?" → options-compared table
- "What do these terms mean?" → compact table
- "What is easy to misread?" → gap matrix, or the dominant pattern with a short contrast callout

If two questions matter equally, pick the dominant one first and add a second pattern only if it genuinely improves clarity.

After the visual, add only the minimum prose needed to orient the reader, highlight the governing boundary, and call out likely misreads.
