# Visual Patterns for code-explain

Use these patterns to choose the clearest terminal-native visual when a visual would help.

Prefer the simplest pattern that reduces cognitive load.
Prefer plain prose when a visual would not add clarity.
Prefer multiple small visuals over one oversized diagram when different concerns need different views.

Choose a pattern only after reading enough code to know what the explanation is really about.
Do not draw from the nearest snippet when the real meaning depends on surrounding flow, ownership, or data movement.
Let the user's question shape what the explanation emphasizes.
When several patterns could work, prefer the one that resolves the dominant confusion most clearly.
Use patterns as tools, not fixed answers.

---

## 1. Call flow pattern

### Use when
- execution order matters
- a function dispatches across branches
- a request or command passes through stages
- the main question is "how does input become output?"

### Goal
Show the path through the code in the order it executes.

### Output shape

```text
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

```text
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

```text
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

```text
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

```text
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

```text
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

### Goal
Compress key distinctions into a small readable table.

### Output shape

```md
| Item   | Role | Changes when | Why it matters |
|--------|------|--------------|----------------|
| state  | ...  | ...          | ...            |
```

### What to emphasize
- only the fields or objects needed to read the code correctly
- the contrast the reader is most likely to miss
- stable, narrow columns that scan quickly in a terminal

### Example

```md
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

```text
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

```text
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

```text
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

```text
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

## Pattern selection shortcut

- "What runs in what order?" → call flow
- "What talks to what over time?" → sequence
- "What is responsible for what?" → structure
- "How is this organized?" → structure or hierarchy / tree
- "How does this relate to surrounding code?" → structure or sequence
- "What owns what, and what gets delegated?" → structure or compact table
- "Where should I start reading?" → hierarchy / tree or structure with an entry-point anchor
- "How does the data change?" → state / transform
- "What are the important roles or differences?" → compact table
- "What contains what?" → hierarchy / tree
- "What is easy to misread?" → compact table, or the dominant structural / flow pattern with a short contrast callout

If two questions matter equally, pick the dominant one first and add a second pattern only if it genuinely improves clarity.

After the visual, add only the minimum prose needed to orient the reader, highlight the governing boundary, and call out likely misreads.
