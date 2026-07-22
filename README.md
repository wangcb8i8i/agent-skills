**Modular, composable AI agent skills for understanding, revising, and planning work.**  
Works with Claude Code, Codex, OpenCode, and other AI coding agents.

👉 [**Interactive Presentations**](https://wangcb8i8i.github.io/agent-skills/) — 技能介绍与演示文稿索引页

## Skills

| Skill | Description | Trigger |
|---|---|---|
| **article-image-prompt** | Visual translator — read an article and generate cover + inline illustration prompts (and optionally the images). For when the user has content but doesn't know how to illustrate it. | Article needs illustrations |
| **article-retelling** | Deconstruct and rebuild source text (URL/file/paste) into a publishable article in the user's own voice. Full pipeline: ingestion, analysis, structure proposal, narrative reconstruction, output. | `#retelling` |
| **breakout** | When you're stuck, quickly surface multiple possible directions. | `#breakout` |
| **explain-code** | Build mental models from code — terminal-native ASCII diagrams, flow charts, state machines. Quick scan for small features, map-then-navigate for large codebases. | "解释" "讲讲" "怎么工作" |
| **explain-concept** | Navigate concept space — start from the user's concept as origin, explore along multiple dimensions, then converge. | User throws out a concept |
| **explain-sql** | Decompile SQL or Oracle PL/SQL into business narrative — not what the code does, but why it exists. | SQL explanation request |
| **fund-managers** | Analyze funds or stocks through the independent lenses of 6 top Chinese fund managers. Side-by-side narrative, no scoring, no synthesis. | Fund/stock analysis request |
| **illustration-prompt** | Auto-detect illustration opportunities in content, infer visual style, generate detailed prompts ready for image generation models. Outputs `.prompt` files. | `#illustration` |
| **inspiration** | Generate inspiration from any understood context. | "有什么启发" "能联想到什么" `#灵感` |
| **intent-capture** | Multi-phase guided conversation to turn vague ideas, complaints, or optimization goals into structured intent briefs with success criteria. | Vague / incomplete ideas |
| **project-cognitive-tree** | Build and persist a cognitive tree of an unfamiliar project — root to leaf, top-down, user chooses the path. | User-invoked, new project |
| **project-recon** | Quick reconnaissance of an unfamiliar project — systematic understanding and mastery. Also serves as the project-context entry point for other skills. | New project exploration |
| **research-plan-driven** | Research → plan → todo → implement → verification pipeline with explicit approval gates at each phase. Advances only on user sign-off. | "plan driven", "research and plan" |
| **research-report** | Automated deep research engine. Give a direction, get conclusions — fully automatic after scope confirmation. Support 10+ analysis lenses. | `/research [topic]` |
| **revise-markdown** | Structured review-comment loop — find, analyze, revise, resolve inline `COMMENT:` markers, repeat until explicit approval. Every comment accounted for. | "revise the doc", "address the comments" |
| **wechat-format** | Convert Markdown to WeChat Official Account (公众号) HTML+CSS with themes, semantic components (callouts, info grids, badges), and WeChat-compatible rendering. | WeChat article / 公众号 |

## Design

- **One skill per directory** — No cross-skill imports. Each skill is self-contained and independently usable.
- **Markdown-only** — No code runtime. The AI reads and interprets skill instructions on invocation.
- **Trigger by description** — Skill descriptions match user intent semantically, not by exact keyword.
- **Approval gates where needed** — research-plan-driven uses explicit phase gates; explain-code and explain-concept are read-only and gate-free.

## License

MIT
