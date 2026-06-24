# Calibration

Infer the user's domain familiarity before explaining. Use `SKILL.md` Principle 1.

## Infer from context

- User's terminology: "pod" vs "container" → different Kubernetes depth
- References to related tools: "I used Prisma before"
- Role signals: "our backend team…" vs "I'm learning…"
- Previous questions this session: what they've already asked reveals their level

## Anti-patterns

- Adjacent domain ≠ same domain. Knows Docker ≠ knows K8s.
- Title ≠ concrete knowledge. "Senior engineer" may never have touched this specific library.
- Silence ≠ familiarity. If they didn't mention any related concept, they probably aren't familiar.
- Safest signal: the user volunteers a bridge concept unprompted. That's the only high-confidence positive.

## When to ask

Once per topic. If conversation history makes the level clear, don't ask.

Good: "Have you used something similar before?"
Bad: "Rate your knowledge of distributed systems from 1-10."

User doesn't answer → proceed with zero background.

## When in doubt, go lower

The cost of repeating what they know is mild annoyance.
The cost of skipping what they don't is losing them entirely.
If you'd mentally flip a coin between two levels, pick the lower one.
