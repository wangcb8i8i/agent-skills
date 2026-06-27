# Output Quality Checklist

Before saving the final HTML, verify every item below.

- [ ] **Paragraph spacing**: Controlled by `<style>` block — `#output p { margin: 1.5em 8px }`, `#output blockquote > p { margin: 0 }`. No inline `margin` on any `<p>`.
- [ ] **No inline styles on body elements**: Every `<p>`, `<h1>`–`<h6>`, `<blockquote>`, `<img>` gets its styles from the `<style>` block, NOT from inline `style=""`. Body HTML uses clean semantic tags without inline style pollution.
- [ ] **Image styling**: Every `<img>` has `max-width: 100%; border-radius: 6px; display: block; margin: 0.1em auto 0.5em` (from `<style>` block). No `!important` on content images.
- [ ] **Remote images preserved**: No remote image URL was replaced with a lazy-load placeholder or SVG. Images from `http://` were upgraded to `https://`.
- [ ] **Heading margins**: `<h2>` uses `margin: {top} auto {bottom}` or `{top} 0 {bottom}` — never `8px` or other arbitrary values for left/right margins.
- [ ] **List rendering**: Ordered lists use CSS counters (`counter-increment` in `<style>`). No manual `<span>` text markers. No empty `<li>` elements.
- [ ] **Cover image**: If a cover image is identified, verify `<!--wechat-cover:...-->` is injected with the correct path. **Verify the cover image is NOT present in the article body** — it's an API field, not content imagery.
- [ ] **Figcaption**: Every `<figure>` has a non-empty `<figcaption>`, with `font-size ≥ 0.85em` and `color ≥ rgba(51,51,51,0.70)` (from `<style>` block).
- [ ] **No empty elements**: No empty `<li>`, `<p>`, or other block-level elements with `textContent.trim() === ""` in the output.
- [ ] **`<style>` block completeness**: The `<style>` block covers: `#output p`, `#output h1`–`h6`, `#output blockquote`, `#output blockquote > p`, `#output ol/ul/li`, `#output ol > li::before`, `#output figure/figcaption`, `#output img`, `#output a`, `#output code`, `#output pre`, `#output hr`, and `@media (prefers-color-scheme: dark)`.
- [ ] **WeChat compatibility only**: Inline `style=""` is only used for compatibility transforms (Mermaid SVG wrap `max-width:100%;overflow-x:auto`, table scroll wrapper `<section style="max-width:100%;overflow:auto">`, tspan fill colors). Each is minimal and element-specific.
