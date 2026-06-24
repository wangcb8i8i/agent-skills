---
name: explain-it
description: Explain code, modules, or architecture. Use when the user asks to "explain", "understand", "how does X work", "what is X", or "why is X this way".
---

# explain-it

Build a **mental model** — the user should predict behaviour of code they haven't seen, not recite what they were told.

## Principles

1. **Calibrate before explaining.** Infer the user's domain familiarity from conversation history — what terms they use, what tools they reference, what role they signal. If unclear, ask once: "Have you used something similar before?" No answer → assume newcomer. When in doubt between two levels, go lower. See `calibration.md`.
2. **Bridge from the known.** An explanation is a delta, not a full description. Anchor on what the user already knows, then only explain the difference. No known concept to bridge from → find the closest everyday analogy → state where the analogy breaks.
3. **Start with why it exists.** Lead with the problem it solves. If you can't find it, say so.
4. **Read only what answers the question.** Skip setup, config, error handlers, tests — unless they *are* the question.
5. **Scaffold, don't dump.** Give the skeleton before details. With a bridge: "X vs [known Y] — what X adds, what X drops, where X behaves differently." Without a bridge: what problem, how it solves it (one sentence), what it explicitly doesn't do.
6. **Use the user's language, not the code's.** Introduce jargon only after defining it in plain terms. If every word you use isn't one the user knows, they can't retell it.

## Output shapes

If you found a bridge concept, anchor every output on it — frame as delta from the known, not as introduction.

| User asks | Give them |
|-----------|-----------|
| What is X | Problem it solves → one-line definition → most common misuse |
| How does X work | One-line why → ASCII flow → who/what at each node |
| How is X organized | Why this structure → ASCII nesting → one-line per module role |
| Why X this way | Options → chosen → rejected and why (decisive factor) |
| X vs Y | Decisive differences only → when to use which |
| A specific follow-up | Only the new piece. Zero recap unless ≤2 sentences for context |

## Visual patterns

**Pick the simplest that works.** Downgrade whenever possible — if a call flow does it, don't draw a sequence diagram.

| Scenario | Use | Example |
|----------|-----|---------|
| Single-thread execution | Call flow | `A → B → C → result` |
| Multi-party message exchange | Sequence | `Client → Server → DB` with arrows |
| Independent branches merging | Pipeline | `[A]─┬─[merge]─[out]` with parallel lanes |
| Object with lifecycle states | State machine | `[init] → [running] → [done]`, mark impossible transitions |
| Module roles and nesting | Nesting diagram | `[entry] └─ [service] ├─ [cache] └─ [db]`, each with one-line role |
| Design decisions | Decision table | `| Option | Chosen? | Why | Tradeoff |` |
| Options comparison (vs) | Compact table | Only decisive differences, ≤5 rows |

## Cold start

When pointed at a project or module without a specific question:

1. Check conversation history for domain familiarity. Unclear → ask once. No answer → assume newcomer.
2. Find the motivation: README → package metadata → entry imports → directory name → ask. Stop at the first clear signal.
3. Output: bridge (if found) + 3-piece skeleton + 2-3 natural next questions.

```
It solves mapping objects to SQL without raw queries.
How: decorators define schema, query builder generates SQL.
Doesn't handle: schema migrations, connection pooling.
You might want to know: how queries get built, how relations work, or how transactions work.
```

## Done when

User can explain the thing back in their own words — not parrot your phrasing, but describe what it is, why it exists, and where it bites.

After finishing a topic, offer one adjacent piece or stay quiet. Don't ask "is that clear?"

To persist an explanation → `output.md`
