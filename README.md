**Modular, composable AI agent skills for understanding, revising, and planning work.**  
Works with Claude Code, Codex, OpenCode, and other AI coding agents.

## Skills

| Skill | Description |
|---|---|
| **code-explain** | Build mental models from code with terminal-native ASCII diagrams, flow charts, and state machines. Two modes: quick scan for small features, map-then-navigate for large codebases. |
| **doc-explain** | Same mental-model approach applied to proposals, specs, decision records, and reports. Classifies by document type and question category. |
| **revise-markdown** | Structured review-comment loop — find, analyze, revise, resolve, repeat until approval. Every comment accounted for. |
| **research-plan-driven** | Research → plan → todo → implement pipeline with explicit approval gates at each phase. Advances only on user sign-off. |
| **intent-capture** | Three-phase guided conversation (explore, challenge, capture) to turn vague requests into structured intent briefs. |

## Design

- **One skill per directory** — No cross-skill imports. Each skill is self-contained and independently usable.
- **Markdown-only** — No code runtime. The AI reads and interprets skill instructions on invocation.
- **Trigger by description** — Skill descriptions match user intent semantically, not by exact keyword.
- **Approval gates where needed** — research-plan-driven uses explicit phase gates; code-explain and doc-explain are read-only and gate-free.

## License

MIT
