**Modular, composable AI agent skills for understanding, revising, and planning work.**  
Works with Claude Code, Codex, OpenCode, and other AI coding agents.

👉 [**Interactive Presentations**](https://wangcb8i8i.github.io/agent-skills/) — 技能介绍与演示文稿索引页

## Skills

| Skill | Description | Trigger |
|---|---|---|---|
| **article-retelling** | Deconstruct and rebuild source text (URL/file/paste) into a publishable article in the user's own voice. Full pipeline: ingestion, analysis, structure proposal, narrative reconstruction, output. | `#retelling` |
| **code-explain** | Build mental models from code with terminal-native ASCII diagrams, flow charts, and state machines. Quick scan for small features, map-then-navigate for large codebases. | Explicit code explanation request |
| **doc-explain** | Same mental-model approach applied to proposals, specs, decision records, guides, and reports. Classifies by document type and question category. | Explicit document explanation request |
| **illustration-prompt** | Auto-detect illustration opportunities in content, infer visual style, generate detailed prompts ready for image generation models. Outputs `.prompt` files. | `#illustration` |
| **intent-capture** | Multi-phase guided conversation to turn vague ideas, complaints, or optimization goals into structured intent briefs with success criteria. | Vague / incomplete ideas |
| **research-plan-driven** | Research → plan → todo → implement → verification pipeline with explicit approval gates at each phase. Advances only on user sign-off. | "plan driven", "research and plan" |
| **research-report** | Automated deep research engine. Give a direction, get conclusions — fully automatic after scope confirmation. Support 10+ analysis lenses. | `/research [topic]` |
| **revise-markdown** | Structured review-comment loop — find, analyze, revise, resolve inline `COMMENT:` markers, repeat until explicit approval. Every comment accounted for. | "revise the doc", "address the comments" |
| **wechat-format** | Convert Markdown to WeChat Official Account (公众号) HTML+CSS with themes, semantic components (callouts, info grids, badges), and WeChat-compatible rendering. | WeChat article / 公众号 |

## Design

- **One skill per directory** — No cross-skill imports. Each skill is self-contained and independently usable.
- **Markdown-only** — No code runtime. The AI reads and interprets skill instructions on invocation.
- **Trigger by description** — Skill descriptions match user intent semantically, not by exact keyword.
- **Approval gates where needed** — research-plan-driven uses explicit phase gates; code-explain and doc-explain are read-only and gate-free.

## License

MIT
