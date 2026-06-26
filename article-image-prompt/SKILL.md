---
name: article-image-prompt
disable-model-invocation: true
description: 为一个没有配图的文章生产封面图和内联插图（Prompt + 可选图片输出）。用户有文章但不知道怎么配图时使用。
---

# Article Image Prompt

A **visual translator** for articles — reads an article (file/URL/paste/context) and produces the images it needs, without requiring you to make design decisions you don't know how to make.

The **translator** metaphor is the leading concept: it reads source material faithfully, finds what should be translated, and delivers output in another language (images). You don't tell it *how* to translate — you just confirm the table of contents.

---

## Stages

| # | Stage | What happens | User input |
|---|-------|-------------|-----------|
| 1 | **INGEST** | Read the article | None |
| 2 | **AUDIT** | Scan for all illustration candidates; recommend strategy | None |
| 3 | **ALIGN** | Review the full plan, adjust or accept | Confirm once |
| 4 | **TRANSLATE** | Generate grounded prompts | None |
| 5 | **RENDER** | Save `.prompt` file | None |

---

### 1. INGEST — Read the article

Accept the article from: file path, URL, pasted text, or conversation context. Detect format (markdown/HTML/plaintext/PDF).

**Completion criterion:** Full article text is in context, with source format noted.

---

### 2. AUDIT — Find what to illustrate

Scan the entire article for every node worth illustrating. This is a **loose scan** — flag anything that describes:

- An **abstract concept** (consistency, backpressure, convergence)
- A **system/architecture** (layers, components, services)
- A **process flow** (stages, state transitions, decision branches)
- A **comparison or trade-off** (vs., as opposed to, contrasted with)
- A **quantitative claim** (X% of, N×, growth curve)
- A **spatial/causal relationship** (leads to, depends on, sits within)
- A **data structure** (tree, ring, queue, buffer)
- The **article's core thesis** (what the whole thing is about — cover candidate)

For each candidate, assign:

| Score | 1 | 2 | 3 | 4 | 5 |
|-------|---|---|---|---|---|
| **Clarity gain** | Visual adds nothing | | Neutral | | Readers will misunderstand without it |
| **Visual fit** | Impossible to depict | | Needs heavy abstraction | | Maps naturally to concrete imagery |
| **Narrative weight** | Tangential | | Supporting detail | | Central to the article's argument |

Then rank by `clarity_gain × narrative_weight` (descending).

**No minimum frequency threshold.** A concept that appears once but carries the article's thesis is a better illustration target than one that appears ten times but is incidental.

The top-ranked candidate that expresses the article's core thesis is flagged as **cover candidate**. The next N (default: 3) are **inline candidates**. Override N based on article length: <500 words → N=1, 500-3000 → N=3, >3000 → N=5.

Output a ranked candidate list with scores and one-line rationale per entry.

**Completion criterion:** Ranked candidate list produced and presented.

---

### 3. ALIGN — Confirm the plan

Present everything in one view: candidates, styles, compositions. This is a single confirmation step — the **translator** has already done the thinking.

**Style** is recommended automatically from article type:

| Article type | Recommended style | Palette slug |
|-------------|-------------------|-------------|
| Tutorial | tutorial-warm 温暖教程风 |
| Analysis/opinion | analysis-contrast 高对比分析风 |
| Technical report | grayscale-structural 灰度结构风 |
| Product documentation | product-doc 产品文档风 |
| Notes/blog | blog-handdrawn 手记博客风 |
| Mixed/other | tech-clean 简洁技术风 |

Present as a compact block:

```text
I scanned the article and recommend:

  🖼 Cover: "Two-phase commit consensus"
     Style: analysis-contrast · 高对比分析风
     Composition: split-screen between coordinator
     and cohorts, green/red status indicators

  📄 3 inline illustrations:
    1. "Phase 1 voting" — flow diagram
       Style: tech-clean  · after § "Prepare phase"
    2. "Phase 2 commit/abort" — state machine
       Style: tech-clean  · after § "Commit phase"
    3. "Crash recovery" — timeline diagram
       Style: analysis-contrast  · after § "Failure scenarios"

  [accept all]  [adjust]  [reject and retry]
```

The user picks one of three responses:

- **accept all** → proceed to TRANSLATE.
- **adjust** → user modifies any aspect (add/remove images, change style, override palette, tweak composition, or set per-image in-image text strategy). After adjustment, proceed to TRANSLATE.
- **reject and retry** → user provides new guidance (e.g. "fewer diagrams, more conceptual"), re-run AUDIT with adjusted criteria.

**In-image text strategy** is handled here as an optional per-image adjustment — it has a sensible default per illustration type and only needs explicit attention when the user disagrees with the default:

| Illustration type | Default text strategy |
|------------------|----------------------|
| Cover | 尽量无字 |
| Diagram (概念示意图) | 无文字 或 仅标签 |
| Flowchart | 仅标签 |
| Infographic | 仅数字 |
| Decorative | 无文字 |

**Completion criterion:** Every illustration candidate has an agreed type + style + composition note. No pending questions.

---

### 4. TRANSLATE — Generate prompts

For each confirmed illustration, generate two outputs per image:

1. **Visual Thesis** — one sentence declaring what a reader should understand from seeing only this image, without reading the article. The thesis must contain a verifiable claim, not just a topic description:
   - ✓ "Reader should understand **why AP is preferred over CP in social feeds**" — contains claim + stance
   - ✗ "Reader should understand **the difference between AP and CP**" — topic only, no claim

2. **Prompt** — the image generation prompt, with its first sentence grounded in the Visual Thesis.

The Visual Thesis is written first, anchors the prompt, and is included in the output file before the prompt. This gives you a visible intent declaration inside the `.prompt` file—a baseline you can check the generated image against.

**Output structure per image:**
```markdown
# <diagram-slug>

## Visual Thesis
[One sentence: reader should understand ___ from seeing this image]

## Context
- Position: [section / paragraph]
...

## Style Anchor
...

## Prompt
[Narrative declaration — first sentence must align with Visual Thesis]
...
```

Write prompts in **English**. Use precise **hex colors** from the selected palette. Ground every visual element to the source article (原文依据 → 合理推导 → 视觉转化方案).

Output is a single `{article-dir}/illustration-prompt/{slug}.prompt` file, all prompts separated by `# <diagram-slug>`. `slug` is inferred from the article's topic (kebab-case). If the file exists, append `-2`, `-3` etc. When input is a file path, `article-dir` is that file's directory; when input is a URL or pasted text, `article-dir` is the current working directory. Create the directory if it doesn't exist.

See `references/color-science.md` for palette hex values, `references/metaphor-guide.md` for concept→visual metaphor mapping, and `references/type-strategies.md` for type-specific wording patterns.

**Completion criterion:** One prompt per confirmed illustration, each complying with the spec and quality checks. File structure verified.

---

### 5. RENDER — Save the output

Save the `.prompt` file (already accumulated during TRANSLATE). Report the file path to the user.

**Completion criterion:** File path reported.

---

## Reference

### Prompt spec

```markdown
# <diagram-slug>

## Visual Thesis

[One sentence: what the reader should understand from seeing only this image.
Must contain a verifiable claim, not just a topic label.]

## Context

- Position: [section / paragraph]
- Illustration type: [cover / diagram / flowchart / infographic / decorative]
- Target model: [Generic / GPT Image / Midjourney / Flux / SDXL / Ideogram]
- In-image text: [none / labels only / numbers only / exact text / minimal]
- Text language: [Chinese (default)]

## Style Anchor

- Palette: <slug>
- Rendering: [vector flat / gradient / hand-drawn / realistic / etc.]
- Atmosphere: [2-4 mood keywords]
- Detail density: [rich / moderate / minimal]

## Prompt

[Narrative declaration — medium/style + Visual Thesis anchoring, first sentence]
[Aspect ratio]
[Exclusions: "No..." negative sentences]
[Entities: position + shape + #hex + size/state, one per sentence]
[Relationships: connection type + direction + endpoints]
[Reading order: start → path → end]
[Semantic binding (optional): representing block at end]
```

### Composition layers (7-layer order)

1. **Narrative declaration** — medium/style + Visual Thesis anchoring. The first sentence must answer "what claim does this image express?" not just "what topic does this image show?" (`A split-screen comparison: left side shows user waiting with loading spinner (CP — consistent but slow), right side shows smooth scrolling with stale-data badge (AP — fast but eventually consistent). The AP side is visually favored — brighter, larger, warmer.`)
2. **Canvas** — background color (hex) + aspect ratio
3. **Constraints** — exclusions as `No...` statements (at least 2)
4. **Entities** — one sentence per entity: position, shape, `#hex`, size/state
5. **Relationships** — connections: type, direction, endpoints
6. **Path** — reading-order guidance (`Reading order: start at..., then...`)
7. **Semantics (optional)** — `representing`/`indicating`/`depicting` block at the very end, never inline

### Governing rules

- **Visual Thesis first**: Every image must have a `## Visual Thesis` written before its prompt. The thesis must contain a verifiable claim — not just a topic label ("the trade-off between AP and CP" ✗, "why AP wins for social feeds" ✓).
- **Narrative anchoring**: The prompt's first sentence must align with the Visual Thesis. If the thesis says "AP is preferred," the first sentence must express that preference visually (brighter/warmer/larger), not stay neutral.
- **Hex fidelity**: All color values use exact hex from the selected palette. No synonym substitution (`#FF6B35` is `#FF6B35`, not `amber` or `orange`).
- **Grounding**: Every visual element must trace back to the article. Three-source grounding: 原文依据 (verbatim fact) → 合理推导 (light inference) → 视觉转化方案 (visual translation).
- **Reading order**: Must guide the eye explicitly. No prompt omits it.
- **Narrative focus**: The visually most prominent element must be the core concept's protagonist. No "core element in the corner, decoration at center."
- **In-image text**: Default language is Chinese. Follow the agreed strategy per image.
- **Block representing**: `representing`/`indicating`/`depicting` sentences go only in the final semantics block. Never embed in entity or relationship sentences.

### Quality checks

Before delivering the file:

- [ ] **Thesis check**: Every image has a `## Visual Thesis` section with a verifiable claim
- [ ] **Narrative alignment**: The prompt's first sentence aligns with the Visual Thesis (if thesis says "AP preferred," first sentence does not stay neutral)
- [ ] Every entity from the composition note appears in the prompt
- [ ] All hex values are from the selected palette (no synonym substitution)
- [ ] Reading order is explicitly specified
- [ ] Exclusions are applied (no elements from "禁止添加" or equivalent)
- [ ] Visual elements trace to article grounding
- [ ] `representing`/`indicating` only in the final block, never inline
- [ ] Narrative focus is aligned (most prominent element = protagonist concept)
- [ ] The prompt is a single coherent paragraph, not a list
- [ ] In-image text follows the agreed strategy and language (default: Chinese)
- [ ] Cross-image consistency: same concept uses same visual description in every image
