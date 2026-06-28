# Output Quality Checklist

Before running inline.js, verify every item below. juice2 can only inline what's correctly class-anchored.

- [ ] **Paragraph spacing**: Controlled by `<style>` block — `#output p { margin: 0.75em 8px }`, `#output blockquote > p { margin: 0 }`.
- [ ] **Image styling**: Every `<img>` has `max-width: 100%; border-radius: 6px; display: block; margin: 0.1em auto 0.5em` (from `<style>` block). No `!important` on content images.
- [ ] **Remote images preserved**: No remote image URL was replaced with a lazy-load placeholder or SVG. Images from `http://` were upgraded to `https://`.
- [ ] **Heading margins**: `<h2>` uses `margin: {top} auto {bottom}` or `{top} 0 {bottom}` — never `8px` or other arbitrary values for left/right margins.
- [ ] **List rendering**: Ordered lists use `<span class="list-num">` for manual numbering (CSS counters can't be inlined). Verify numbers are sequential and match the source Markdown. No empty `<li>` elements.
- [ ] **Cover image**: If a cover image is identified, verify `<!--wechat-cover:...-->` is injected with the correct path. **Verify the cover image is NOT present in the article body** — it's an API field, not content imagery.
- [ ] **Figcaption**: Every `<figure>` has a non-empty `<figcaption>`, with `font-size ≥ 0.85em` and `color ≥ rgba(51,51,51,0.70)` (from `<style>` block).
- [ ] **No empty elements**: No empty `<li>`, `<p>`, or other block-level elements with `textContent.trim() === ""` in the output.
- [ ] **Class-selector parity**: Every content element carries a class name that matches a selector in the `<style>` block. juice2 matches on selectors; an element without a matching class gets no inline style. Verify the `<style>` block covers: `#output p`, `#output h1`–`h6`, `#output blockquote`, `#output blockquote > p`, `#output ol/ul/li`, `#output figure/figcaption`, `#output img`, `#output a`, `#output code`, `#output pre`, `#output hr`.
