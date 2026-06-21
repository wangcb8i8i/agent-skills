# Visual Patterns for explain-it

Use these patterns to choose the clearest terminal-native visual when a visual would help.

Prefer the simplest pattern that reduces cognitive load.
Prefer plain prose when a visual would not add clarity.
Prefer multiple small visuals over one oversized diagram when different concerns need different views.

Choose a pattern only after reading enough material to know what the explanation is really about.
Do not draw from the nearest snippet when the real meaning depends on surrounding flow, ownership, or data movement.
Let the user's question shape what the explanation emphasizes.
When several patterns could work, prefer the one that resolves the dominant confusion most clearly.

Use patterns as tools, not fixed answers.

---

## 按问题类型选择

| 问题类型 | 推荐模式 | 备选模式 |
|----------|----------|----------|
| 识别型 | 无图（纯文字） | Hierarchy / Tree（有嵌套结构时） |
| 流程型 | Call flow | Sequence / State/Transform / Pipeline/DAG |
| 结构型 | Structure | Hierarchy / Tree / Compact table |
| 理由型 | Decision table | Reasoning chain |
| 对比型 | Compact table | Options-compared table |
| 追问型 | 由缺口实质决定初始回答的对应类型 | — |

如果两个模式都能用，选最能消除用户当下困惑的那个。
如果两个问题同样重要，先解决主导的那个，再视需要补第二个模式。

视觉之后，只配最少文字——引导视线、标出边界、提示易误读点。

---

# 视觉模式

## 1. Call flow pattern

### Use when
- execution order matters
- a function dispatches across branches
- a request or command passes through stages
- the main question is "how does input become output?"

### Goal
Show the path through the code in the order it executes.

### Output shape

```
[input]
  ↓
[normalize]
  ↓
[branch]
  ├─→ [path A]
  └─→ [path B]
  ↓
[result]
```

### What to emphasize
- the real entry, not just the first line you saw
- the branch that changes behavior most
- the boundary where control passes to another layer

### Example

```
[HTTP request]
  ↓
[parse params]
  ↓
[build query]
  ↓
[service call]
  ↓
[serialize response]
```

### Common misuse
- Do not use this when the real question is ownership or module boundaries.
- Do not turn a static dependency graph into a fake timeline.
- Do not flatten important branches into a misleading straight line.

---

## 2. Structure pattern

### Use when
- multiple files or layers collaborate
- module ownership matters
- the user needs to understand who depends on whom
- the main question is "what sits where and what is each part responsible for?"

### Goal
Show relationships and responsibilities, not time order.

### Output shape

```
[entry]
  └─→ [orchestrator]
        ├─→ [domain service]
        ├─→ [cache]
        └─→ [repository]
```

### What to emphasize
- the layer that owns the decision
- boundaries between coordination and execution
- dependencies that matter to understanding, not every import

### Example

```
[controller]
  └─→ [search service]
        ├─→ [query builder]
        └─→ [result serializer]
```

### Common misuse
- Do not use this when the confusing part is branch order or runtime progression.
- Do not overload the diagram with every dependency in the file.
- Do not hide the owning layer by giving every node equal visual weight.

---

## 3. State / transform pattern

### Use when
- data shape changes across steps
- parsing, normalization, reduction, or serialization is central
- the main question is "what does this become after each stage?"

### Goal
Show meaningful state or representation changes.

### Output shape

```
raw input
  ↓ validate
trusted input
  ↓ transform
domain object
  ↓ serialize
response shape
```

### What to emphasize
- the before/after shape that actually matters
- the step where data becomes trusted, normalized, or domain-level
- the transformation that explains later behavior

### Example

```
request params
  ↓ coerce
typed filters
  ↓ execute
search result
  ↓ map
API payload
```

### Common misuse
- Do not use this when there is no meaningful transformation.
- Do not list trivial assignments as state transitions.
- Do not confuse state change with mere variable renaming.

---

## 4. Compact table pattern

### Use when
- several objects or parameters have distinct roles
- state fields matter more than call order
- branch differences are easier to compare side by side
- several entities, roles, or concepts have distinct definitions
- a flat comparison is easier to scan than prose

### Goal
Compress key distinctions into a small readable table.

### Output shape

```
| Item   | Role | Changes when | Why it matters |
|--------|------|--------------|----------------|
| state  | ...  | ...          | ...            |
```

### What to emphasize
- only the fields or objects needed to read the code correctly
- the contrast the reader is most likely to miss
- stable, narrow columns that scan quickly in a terminal

### Example

```
| Name    | Role                  | Changes when             |
|---------|-----------------------|--------------------------|
| state   | current reducer state | after each action        |
| action  | transition trigger    | once per dispatch        |
| error   | failure payload       | only on error branches   |
```

### Common misuse
- Do not build wide tables that wrap badly in terminal output.
- Do not include fields that are not necessary for understanding.
- Do not use a table when sequence or transformation is the real mental model.

---

## 5. Hierarchy / tree pattern

### Use when
- the main question is about containment, nesting, or ownership
- the code is easier to understand as a directory, module, or parent-child hierarchy
- the user needs to see what lives inside what

### Goal
Show containment and nesting clearly.

### Output shape

```
package/
├── entry/
│   └── handler
├── domain/
│   ├── service
│   └── model
└── infra/
    └── repository
```

### What to emphasize
- the parent-child structure that matters to understanding
- which node owns or contains the important behavior
- only the branches needed to answer the question

### Example

```
search/
├── controller
├── service
├── query_builder
└── serializer
```

### Common misuse
- Do not use this when runtime order matters more than containment.
- Do not turn a call graph into a tree.
- Do not include every sibling if only one branch matters.

---

## 6. Sequence pattern

### Use when
- multiple actors or layers exchange messages over time
- request/response back-and-forth is central
- the user needs to see who sends what to whom, and in what order

### Goal
Show interaction order across participants.

### Output shape

```
Client        Server        Database
  │             │               │
  │── request ─▶│               │
  │             │── query ─────▶│
  │             │◀── rows ──────│
  │◀── response │               │
```

### What to emphasize
- the actors that matter to the interaction
- the order of exchanges
- boundaries where responsibility changes hands

### Example

```
Browser       API           Cache
  │             │              │
  │── GET /x ──▶│              │
  │             │── lookup ───▶│
  │             │◀── hit ──────│
  │◀── 200 ─────│              │
```

### Common misuse
- Do not use this for single-function local control flow.
- Do not use this when structure or transformation is the real question.
- Do not add actors that do not affect the explanation.

---

## 7. State machine pattern

### Use when
- an object has a defined lifecycle with legal state transitions
- multiple paths can lead to different terminal states
- incorrect transition ordering is a common bug vector
- the main question is "what states exist and what causes transitions between them?"

### Goal
Show the legal state space and transition triggers compactly.

### Output shape

```
     ┌── cancel ──▶ [cancelled]
     │
[init] ──▶ [pending] ──▶ [running] ──▶ [done]
           │                │
           └── error ───────▶ [failed]
```

### What to emphasize
- the legal transitions between states
- the trigger or condition on each edge when it is non-obvious
- states that cannot transition into each other (the absent edges)
- the transition most likely to be missed or misapplied

### Example

```
           ┌── timeout ──▶ [expired]
           │
[idle] ──▶ [active] ──▶ [completed]
           │    │
           │    └── abort ──▶ [aborted]
           │
           └── evict ──▶ [evicted]
```

### Common misuse
- Do not use this when there is no meaningful lifecycle — a flag toggle is not a state machine.
- Do not draw every field value change as a state.
- Do not confuse with state/transform, which models data shape, not legal transitions.

---

## 8. Concurrency / interleaving pattern

### Use when
- multiple goroutines, threads, or async tasks overlap in time
- a race condition, deadlock, or ordering ambiguity is central to understanding
- the main question is "who can run when, and what interleavings are dangerous?"

### Goal
Show concurrent execution units and the points where they interact or conflict.

### Output shape

```
goroutine A:  lock(m) ── read(x) ── write(x) ── unlock(m) ──
goroutine B:  ── wait(m) ─────────────────────── lock(m) ── read(x)
```

### What to emphasize
- the shared resource or critical section
- the ordering constraints (who waits on whom)
- which interleavings are safe and which are not
- the one interaction that is easiest to get wrong

### Example

```
producer:  write(ch) ────────────────── write(ch) ── close(ch) ──
consumer:  ── read(ch) ── process ── read(ch) ── process ── read(ch) → done
```

### Common misuse
- Do not use this for synchronous, single-threaded call flow.
- Do not draw every goroutine in the program — only the ones whose interleaving matters.
- Do not use this when structure or ownership is the real question.

---

## 9. Pipeline / DAG pattern

### Use when
- data flows through parallel stages that fan out and merge
- independent branches converge at a join point
- the main question is "what runs in parallel and where do results combine?"

### Goal
Show parallelism boundaries and merge points without over-specifying ordering.

### Output shape

```
         ┌── [stage A] ──┐
[input] ──┤               ├── [merge] ── [output]
         └── [stage B] ──┘
```

### What to emphasize
- which stages are independent and could run in parallel
- the merge point where results reunite
- dependencies that force sequential execution
- the stage that is the bottleneck or error boundary

### Example

```
              ┌── [fetch db] ──┐
[user query] ──┤                ├── [rank] ── [response]
              └── [fetch cache] ┘
```

### Common misuse
- Do not use this when execution is actually sequential.
- Do not turn a simple call chain into a DAG just because the code imports two modules.
- Do not hide the merge logic — if the join is non-trivial, it often deserves its own prose note.

---

## 10. Reasoning chain pattern

### Use when
- the argument structure matters
- a claim is built from premises, evidence, and inferences
- the main question is "how does this document reach its conclusions?"

### Goal
Show how premises chain into conclusions, and where the chain weakens.

### Output shape

```
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

```
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

## 11. Skeleton map pattern

### Use when
- section organization and responsibility matter
- the user needs to navigate the document efficiently
- the main question is "what is where, and what does each part do?"

### Goal
Show the document's structure with one-line role annotations.

### Output shape

```
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

```
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

## 12. Decision table pattern

### Use when
- the document records one or more decisions
- the user needs to understand who decided what, why, and with what tradeoffs
- the main question is "what was decided and on what basis?"

### Goal
Compress decision records into a scannable table.

### Output shape

```
| Decision | Who | Rationale | Tradeoff / Cost | Status |
|----------|-----|-----------|-----------------|--------|
| ...      | ... | ...       | ...             | ...    |
```

### What to emphasize
- decisions, not every opinion in the document
- the tradeoff column — what was knowingly sacrificed
- whether the decision is proposed, accepted, or superseded

### Example

```
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

## 13. Cross-reference graph pattern

### Use when
- the document depends on or is referenced by other documents
- the user needs to understand the document's context in a larger corpus
- the main question is "how does this fit with everything else?"

### Goal
Show inbound and outbound references with relationship types.

### Output shape

```
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

```
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

## 14. Gap matrix pattern

### Use when
- the document's omissions matter as much as its content
- the user needs to see what was promised vs. what was delivered
- the main question is "what does this document leave out?"

### Goal
Surface mismatches between scope claims and actual coverage, plus unstated assumptions.

### Output shape

```
| Claim / Expectation | Covered? | Notes |
|---------------------|----------|-------|
| ...                 | ✔ / ✘ / ⚡ | ...   |
```

### What to emphasize
- claims the document makes about its own scope that it doesn't fulfill
- topics a reader would reasonably expect that are absent
- assumptions that would change the reading if they were false

### Example

```
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

## 15. Timeline pattern

### Use when
- the document narrates events, versions, or decisions over time
- chronological order matters to understanding
- the main question is "what happened when, and in what order?"

### Goal
Show events in time sequence with causal or dependency links.

### Output shape

```
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

```
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

## 16. Options-compared table pattern

### Use when
- the document evaluates multiple alternatives
- the user needs to understand tradeoffs between options
- the main question is "what were the choices and why was this one picked?"

### Goal
Show alternatives side by side with the criteria that drove selection.

### Output shape

```
| Criterion | Option A | Option B | Option C (chosen) |
|-----------|----------|----------|--------------------|
| ...       | ...      | ...      | ...                |
```

### What to emphasize
- the criterion that was decisive
- options that were close contenders vs. strawmen
- criteria that were considered but not weighted

### Example

```
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


