---
name: wechat-format
description: >
  Converts Markdown to self-contained HTML for WeChat Official Account (微信公众号).
  Triggers on content destined for mp.weixin.qq.com, 微信排版, or 公众号风格 content.
  Parameters: --preview (default, open browser) or --publish (upload images, create draft).
---

# WeChat Format (微信排版)

Converts Markdown → self-contained HTML styled for WeChat Official Account articles, with optional illustration embedding.

## Input / Output

| | |
|---|---|
| **Input** | Markdown text (standard + WeChat extensions) |
| **Parameters** | `--preview` (default): local image paths + open browser. `--publish`: run `scripts/publish.py`. |
| **Output** | Single `.html`, CSS embedded in `<style>`, ready to paste into 微信公众号编辑器. Written to `web-chat-artifacts/<name>.html`. |

## Leading Words

| Word | Meaning |
|------|---------|
| `juiced` | Class names on elements anchor styles in `<style>` block. juice2 reads the `<style>`, matches selectors to DOM, writes matching properties into `style=""`, then removes `<style>` — no LLM CSS→inline bugs. |
| `compat-wrap` | WeChat compatibility transforms (Mermaid SVG wrap, tspan color, dominant-baseline→dy, image sizing) still applied as inline `style=""` at Phase 3 step 5. These survive juicing. |
| `three-gate` | Illustration matching algorithm with 3 branches (auto-match, sequential pair, manual). All converge to user-confirmed mapping table. |
| `cover-out` | Cover image is API metadata, not article content. Never inserted into body HTML. |

## Workflow

5 phases, sequential.

```
Phase 1 ─ Target Recognition (参数解析)
              ↓
Phase 2 ─ Illustration Matching (may skip)
              ↓
Phase 3 ─ Generate HTML (with <style> + class names)
              ↓
Phase 4 ─ Illustration Embedding (may skip)
              ↓
Phase 4.5 ─ Inline Conversion (juice2: <style> → inline)
              ↓
Phase 5 ─ Consume (preview / publish) — pure inline HTML
```

### Phase 1 — Target Recognition

| Parameter | Mode | Behavior |
|-----------|------|----------|
| `--preview` | Preview | Local image paths; save HTML then `open` browser |
| `--publish` | Publish | Local paths; save HTML then run `scripts/publish.py` |
| (none) | Preview | Same as `--preview` |

### Phase 2 — Illustration Matching

#### 2a. Ask user

- **Need illustrations** → user provides illustration directory path, go to 2b
- **No illustrations** → skip to Phase 3

#### 2b. Three-Gate Matching (`three-gate`)

Read `.prompt` files (extract `diagram-slug` list, preserve order) and image files (sorted by name).

```
Step 1: Parse .prompt → slugs (ordered)
Step 2: Scan images → filenames (sorted)
Step 3: Auto-match by filename → three gates:
```

| Condition | Gate |
|-----------|------|
| **≥1 auto-match** | Keep matches; pair remaining images & slugs in order 1:1 |
| **0 match, count(img) == count(slug)** | All paired 1:1 in order (skip filename matching entirely) |
| **0 match, count(img) ≠ count(slug)** | Fallback: ask user per image which slug it maps to |

All branches converge to mapping table → user confirmation:

```
📄 配图映射确认（共 N 张图）
  顺序 │ 图片             │ 匹配方式  │ 插入位置
  ─────┼──────────────────┼──────────┼───────────────────────
   1   │ leader-election  │ 自动匹配  │ 第 2 节 · Leader Election

  Enter      → confirm all
  swap 1 3   → swap images
  move 2 4   → move image
  remove 3   → remove image
  done       → confirm and proceed
```

#### 2c. Build Mapping Table

```json
[{"slug": "leader-election", "img_path": "/abs/path.png", "prompt_location": "...", "match_method": "auto"}]
```

`match_method`: `"auto"` / `"paired"` / `"manual"`

#### 2d. Cover Detection (`cover-out`)

Cover is API metadata, not body content:

1. Check for independent cover file (`cover.png` / `cover.jpg` / etc.)
2. If none, mark first mapped image as cover candidate and **remove from mapping table**
3. Show to user for confirmation/replacement

Output (cover path separate from mapping):

```json
{"mapping": [/* body images only */], "cover_img_path": "/abs/path/cover.png"}
```

Cover path written as `<!--wechat-cover:...-->` in HTML (Phase 3) for publish.py.

### Phase 3 — Generate HTML

**`juiced` approach**: semantic HTML + class names, all styles in `<style>` block via class selectors. juice2 (Phase 4.5) inlines them mechanically. Inline `style=""` only for `compat-wrap` transforms.

1. Understand content tone → recommend [theme](references/themes.md) (user confirms)
2. Analyze structure → identify semantic units — see [components guide](references/components.md)
3. Render Markdown → semantic HTML with classes — see [syntax reference](references/syntax-reference.md)
4. Load theme CSS → resolve all CSS functions (`var()`, `hsl()`, `color-mix()`, `calc()`) to concrete values → output `<style>` block
   - **Every content element must carry a class name that matches a selector in `<style>`** — juice2 (Phase 4.5) converts via selector matching, not element type
   - `<style>` is **intermediate**: Phase 4.5 will inline its properties, then delete the block
5. Apply [compatibility transforms](references/compatibility.md) (Mermaid SVG wrap, tspan color, dominant-baseline→dy, image sizing)
6. Post-process: clean empty elements, validate class-selector parity against [quality checklist](references/quality-checklist.md)

**Image handling**: Remote URLs pass through, `http://` → `https://`. No lazy-load placeholders. Local paths marked for Phase 4.

**Metadata comments** in `<head>`:

```html
<!--wechat-title:{title (first h1, max 64 chars)}-->
<!--wechat-digest:{first 120 chars of body, stripped of markup}-->
<!--wechat-cover:{path}--><!-- only if Phase 2d found a cover -->
```

### Phase 4 — Illustration Embedding

Only runs if Phase 2 produced a mapping. Skip otherwise.

#### 4a. LLM Infers Insertion Positions

Input: full HTML + mapping table (no cover image).

Process: read `.prompt` position presets → cross-reference HTML structure → infer insertion points.

Constraints:
- Don't modify original text
- Each image: `<figure><img src="local-path"><figcaption>caption</figcaption></figure>`
- `figcaption`: font-size ≥ 0.85em, color ≥ rgba(51,51,51,0.70), centered
- **Cover never inserted** (`cover-out`)

#### 4b. Confirmation

```
📄 已为 3 张配图定位并插入 HTML：
  ✓ leader-election  → 插入在「## Leader Election」段落后
  ✓ log-replication  → 插入在「## Log Replication」段落后

  全部确认 → 进入消费阶段
```

### Phase 4.5 — Inline Conversion

Run `scripts/inline.js` on the HTML to convert `<style>` → inline.

**Input**: HTML with `<style>` block (from Phase 3-4).

**Process**:
1. Run: `node scripts/inline.js web-chat-artifacts/<name>.html`
2. juice2 parses `<style>`, matches selectors to DOM elements
3. Each element gets `style=""` with matching properties
4. `<style>` block is removed

**Output**: Pure inline HTML, no `<style>` blocks.

**Error handling**: If script fails (non-zero exit), show error and stop.

### Phase 5 — Consume

| Mode | Behavior |
|------|----------|
| `--preview` | Save inlined HTML to `web-chat-artifacts/<name>.html`, then open browser |
| `--publish` | 1. Save inlined HTML to `web-chat-artifacts/<name>.html`<br>2. Run `scripts/publish.py <html_path>`<br>3. publish.py uploads images → creates draft → **deletes HTML file** |

## Output Path

| | |
|---|---|
| **Directory** | `web-chat-artifacts/` — sibling to the input Markdown file |
| **Filename** | `{input-stem}.html` |
| **Auto-create** | Create directory if it does not exist |

## Output Template

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{article title}</title>
<!--wechat-title:{标题}--><!-- publish.py extracts and removes these -->
<!--wechat-digest:{摘要}-->
<!--wechat-cover:{封面路径}--><!-- only if Phase 2d -->
</head>
<body>
<div id="output">
  <section>
    <!-- first h1 stripped: title managed by WeChat editor -->
    {rendered content}
  </section>
</div>
</body>
</html>
```

### Footnotes Block

```html
<h4>引用链接</h4>
<p class="footnotes">
  <code style="font-size:90%;opacity:0.6;">[1]</code>: <i>title</i><br/>
  ...
</p>
```

## Caveats Summary

WeChat's X5 Blink kernel has specific behaviors. Key constraints:

| # | Rule |
|---|------|
| 1 | **No CSS functions at runtime**: resolve `var()`, `hsl()`, `color-mix()`, `calc()` before output |
| 2 | **No external resources**: all inline `<style>`, no `@import`, no webfonts |
| 3 | **`<style>` deleted before publish**: Phase 3 generates `<style>`, Phase 4.5 (juice2) inlines and deletes it. No `<style>` reaches WeChat's editor. |
| 4 | **Tables need scroll wrapper**: `<section style="max-width:100%;overflow:auto;-webkit-overflow-scrolling:touch">` |
| 5 | **`color-mix()` unsupported**: pre-compute to `rgba()` — see [method](references/caveats.md#color-mix-resolution) |

See [full caveats](references/caveats.md) for all 11 items (dark mode, code block copy safety, link handling, image sizing, etc.).

## Reference Files

| When you need... | File |
|------------------|------|
| GFM + WeChat extension syntax (text markup, alerts, diagrams, etc.) | [syntax-reference.md](references/syntax-reference.md) |
| Custom components (JSX-style) + content structuring guide | [components.md](references/components.md) |
| Theme selection, CSS variables, customization options | [themes.md](references/themes.md) |
| WeChat compatibility transforms (SVG wrap, tspan, etc.) | [compatibility.md](references/compatibility.md) |
| All 11 WeChat caveats + color-mix resolution | [caveats.md](references/caveats.md) |
| Output quality checklist | [quality-checklist.md](references/quality-checklist.md) |

## Scripts

### inline.js

`scripts/inline.js` — converts `<style>` blocks to inline `style=""` via juice2.

```
$ node scripts/inline.js <html_path>
```

Called by Phase 4.5 after LLM generates HTML with `<style>` block. Reads the file, matches selectors to DOM, writes properties as `style=""`, removes `<style>` block. Overwrites in place.

Dependencies: Node.js, juice (in `scripts/node_modules/`).

### publish.py

`scripts/publish.py` — upload images via WeChat API, create draft.

```
$ python scripts/publish.py <html_path>               # overwrite original
$ python scripts/publish.py <html_path> -o out.html   # output to new file
$ python scripts/publish.py <html_path> --dry-run     # preview only
```

Workflow:
1. Read `WECHAT_APP_ID` / `WECHAT_APP_SECRET` from `.env`
2. Scan HTML for local `<img src="...">` paths
3. Auto-compress images to ≤1MB (WeChat upload limit)
4. Upload via WeChat API, get `https://mmbiz.qpic.cn/...` URL
5. Replace local src paths, write output

Dependencies: `httpx` (required), `Pillow` (optional, auto-compress), `python-dotenv` (optional)

### .env

`scripts/.env` (gitignored):

```
WECHAT_APP_ID=wx_xxx
WECHAT_APP_SECRET=xxx
WECHAT_AUTHOR=作者名
WECHAT_PROXY=http://127.0.0.1:7890    # proxy (optional)
```

Template file: `scripts/.env.example` (no real keys)
