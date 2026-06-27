# Custom Components & Content Structuring

## Custom Components (JSX-style)

Syntax: `<ComponentName prop="value" />` (PascalCase, self-closing or open-close).

| Component | Purpose | Key props |
|-----------|---------|-----------|
| `<MpProfile />` | WeChat account card | `mpId` `nickname` `headimg` `signature` `serviceType` `verifyStatus` |
| `<QRCodeBlock />` | QR code image | `url` `text="扫码访问"` `size=150` |
| `<AuthorBlock />` | Author info card | `name` `avatar` `bio` |
| `<TipBlock />` | Info/warning box | `type=info/success/warning/danger` `title` `content` |
| `<TableBlock />` | Advanced table | `headers='["A","B"]'` `rows='[["a","b"]]'` `striped=true` `caption` |
| `<InfoGrid />` | Key-value grid | `items='[{"label":"","value":""}]'` `cols=2` |
| `<BadgeGroup />` | Tag badges | `tags='["tag1","tag2"]'` `color="#07c160"` |

Components use CSS variables for colors (fallbacks provided). **TipBlock** has 4 color variants:

- `info` → blue `#1890ff`
- `success` → green `#52c41a`
- `warning` → yellow `#faad14`
- `danger` → red `#ff4d4f`

Component templates use `--md-comp-*` CSS variables (resolved before output):

| Variable | Default | Description |
|----------|---------|-------------|
| `--md-comp-bg` | `#fff` | Component background |
| `--md-comp-bg-secondary` | `#f5f5f5` | Secondary background |
| `--md-comp-bg-stripe` | `#fafafa` | Stripe background |
| `--md-comp-text-primary` | `#333` | Primary text |
| `--md-comp-text-secondary` | `#666` | Secondary text |
| `--md-comp-text-tertiary` | `#999` | Tertiary text |
| `--md-comp-border-default` | `#e0e0e0` | Border |
| `--md-comp-border-light` | `#eee` | Light border |

## Content Structuring Guide

After theme is selected, analyze the Markdown body to identify key semantic units beyond standard GFM.

### Component Mapping Table

| When you find... | Use this component | Example |
|------------------|-------------------|---------|
| Core thesis or central question | `.callout` with `.callout-label` | "当编码不再是稀缺资源，靠编码吃饭的人该怎么办？" |
| Critical warning, urgent risk | `.card.card-danger` | "不是 AI 会取代你，而是 AI 产出了一堆你理解不了的东西" |
| Key quote worth emphasizing | `.card.card-filled` with larger serif text | "LLM 不会恐惧复杂度。而且它是史上最高产的程序员。" |
| Sequential steps, principles, action items | `<ol class="flow-list">` with `.flow-step` + `.flow-num` | 四条行动原则 / 三步操作指南 |
| Final takeaways, conclusions | `<ul class="insight-list">` with `.insight-marker` | 结尾两个金句收束 |

### Rules

- **Do not overuse**: Each `<section>` at most one special component (callout or card). If everything is emphasized, nothing is.
- **Ordinary narrative stays as `<p>`**: Only elevate the 2–5 most critical information nodes in the entire article.
- **Flow list for numbered sequences only**: Use `.flow-list` when the ordered list represents sequential steps. When the list represents principles or core capabilities that need step-like emphasis, prefer `.flow-list` over plain `<ol>` with text markers.
- **Plain ordered list**: Use CSS counters in `<style>` block. No `<span>` text markers — CSS counters are more reliable, accessible, and avoid empty `<li>` spacers. The `<style>` block must contain `ol { counter-reset: item; } li.listitem { counter-increment: item; } li.listitem::before { content: counter(item); }` (styled per theme).
- **Insight list for takeaways only**: Use at end of an article or major section for conclusions.
- **Never nest components** inside each other.
