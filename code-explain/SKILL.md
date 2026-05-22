---
name: code-explain
description: Explains code, execution flow, module responsibilities, and implementation details. Prefer terminal-native, visual-first explanations with multiple local visual anchors when helpful. This skill explains; it does not implement. Do not auto-trigger — use only when the user explicitly asks to understand code.
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

## Workflow

This skill has two modes, chosen by scope:
- **Standard**: small to medium features — single-turn, one response and done.
- **Map + navigate**: large features — multi-turn across 3+ responses.

The decision path: **classify → detect scale → read & verify → execute the chosen mode**.

### 1. Classify the question

Before explaining, identify what the user is primarily asking for:
- **responsibility** — what this code, file, or module is for
- **execution flow** — how control moves through it
- **data flow** — how input becomes output
- **structure** — how files or components relate
- **rationale** — why it is written this way
- **nuance** — what is easy to misread or surprising

If the request is ambiguous, ask one clarifying question before explaining.
Do not default to explaining the whole file, module, or subsystem.
Choose the narrowest scope that fully answers the question.

### 2. Detect scale

After classifying, assess whether the target is **small** or **large**.

A feature is **large** when any of these apply:
- 5+ files or modules are involved
- the call chain is 3+ levels deep
- 3+ significant branching paths exist
- complex state management or multi-stage data flow is central
- the user explicitly describes it as large, complex, or hard to follow

When uncertain, default to large. A map is always skimmable; a shallow explanation of a deep feature is useless.

→ small: go to [Standard mode](#4-standard-mode-small-scope).
→ large: go to [Map + Navigate mode](#5-map--navigate-mode-large-scope).

### 3. Read & verify

Applies to both modes.

#### Read enough

Before answering, inspect enough code to identify:
- the real entry point
- the key handoffs
- the meaningful branches
- the observable effect or exit

Follow important calls until the requested behavior is clear enough to explain.
Do not explain from an isolated snippet when the meaning depends on surrounding flow.
Read only as broadly as needed for the user's question.

#### Verification boundary

Only describe behavior as fact when verified in the inspected code. State clearly when:
- behavior was verified directly
- a dependency was only sampled
- a conclusion is inferred rather than confirmed
- surrounding runtime context was not inspected

Do not imply end-to-end certainty from a local snippet.
If the inspected scope is partial, say what was verified and what still needs checking.

### 4. Standard mode (small scope)

Single-turn explanation. Start by directly answering the user's actual question in one sentence.
Answer the user's actual question, not the largest explainable surface area.

#### Output

Add only the sections needed to support that answer, such as:
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

#### Visual guidance

Prefer compact terminal-native visuals when they reduce cognitive load.
If plain prose is clearer, use plain prose.
For concrete visual patterns, see `docs/visual-patterns.md`.
Choose a pattern only after the explanation goal is clear.

Use local visual anchors to clarify:
- structure
- execution flow
- branching
- data mapping
- state transitions
- concurrent interleaving
- pipeline parallelism
- contrasts or misread-prone behavior

Prefer multiple small visuals over one oversized diagram when the explanation spans different concerns.
Do not add visuals that merely decorate or repeat nearby prose.
Choose the simplest visual that makes the point clear.

### 5. Map + Navigate mode (large scope)

When scale detection flags a feature as large, do not attempt a single-pass explanation. Instead, guide the user through three phases: map the territory, navigate selected branches in depth, then synthesize back into a coherent whole. The user controls pacing and branch selection throughout.

**CRITICAL — Multi-turn interaction**: This mode spans 3+ responses. You MUST NOT complete multiple phases in one response. Each phase boundary is a hard stop — output the phase content, emit the user-facing prompt, then wait. A typical interaction: turn 1 = Phase 1 (map) → user reply → turn 2 = Phase 2 (dive into branch A) → user reply → turn 3 = Phase 2 (dive into branch B) → user says "合拢" → turn 4 = Phase 3 (synthesize). Never collapse these boundaries.

#### Phase 1: Map (reconnaissance)

Goal: give the user a global mental model without diving into any single branch.

Read broadly but shallowly — identify entry points, key modules, major branches, and handoff boundaries. Do not trace calls deeply yet.

Output:
- **全局地图**: a structure or hierarchy diagram showing modules, files, or components and their relationships. Use the existing structure or hierarchy/tree visual patterns.
- **分支目录**: a compact table listing each key branch, what it does in one sentence, and its importance (core / important / edge).
- **建议阅读顺序**: the recommended order to explore branches. Default to core → important → edge unless the user has a specific concern.

End Phase 1 by asking the user which branch to dive into first.

```
这里有 N 条值得深入的分支。你想先钻哪条？（输入编号或名称，也可以跳过直接合拢）
```

CRITICAL: After outputting the map, branch catalog, and this prompt, STOP. Do not deep-dive any branch. Do not proceed to Phase 2. Wait for the user to select a branch before continuing.

#### Phase 2: Navigate (deep-dive)

Goal: trace one branch recursively from entry to leaves, matching the quality of the standard small-feature explanation.

When the user selects a branch:
- Trace the call chain for that branch deeply, following important calls to their conclusions.
- Use the same visual patterns, verification boundary, and output contract as the standard explain mode.
- Stay within the scope of one branch. Do not detour into sibling branches.

After each branch, output a brief summary and ask the next move:

```
**已探索**: [branch-name]

下一条钻哪个？还是"合拢"？
```

CRITICAL: After each deep-dive response, STOP. Do not dive into another branch until the user responds with a selection or "合拢".

Accept these user responses:
- a branch number/name → dive into that branch
- "合拢" or "synthesize" → move to Phase 3
- "停" or "pause" → stop here, save progress for next session

#### Phase 3: Synthesize (assemble)

Goal: weave the explored branches back into a single coherent narrative the user can retell.

When the user asks to synthesize:
- Recap the global map, visually marking which branches were explored.
- Show how the explored branches connect — their handoff points, shared state, ordering constraints.
- Present the end-to-end flow: the complete path from input to output, covering all explored branches in their proper relationships.
- List any unexplored branches the user may want to revisit later.

The user should walk away able to explain the full chain to someone else. That is the success criterion.

#### Cross-session

The user may pause and resume across conversations. To support this:
- When the user pauses, summarize what was covered and what remains.
- When the user returns and says "继续解读" or references the same feature, pick up from the last phase and branch.
- Track progress in conversation state — no file persistence needed.

## Hard boundaries

Do not:
- modify, create, or delete any file
- paraphrase the code line by line
- explain more surface area than the user's question requires
- present inference as confirmed behavior
- imply full-path certainty from a partial inspection
- mix explanation with implementation advice unless the user asks
- add visuals that do not clarify structure, flow, mapping, branching, or contrast
- for large features, skip the map and jump straight to deep-dive
- for large features, dive into every branch in one response — let the user choose the pace
- for large features, complete multiple map+navigate phases in a single response — each phase is a separate turn
- add branches to the catalog that don't materially affect understanding
