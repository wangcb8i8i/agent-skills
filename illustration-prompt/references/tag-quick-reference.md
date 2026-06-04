# Tag Quick Reference

## 写作速查表

| Tag | 必填 | 段内顺序 | 最小内容 |
|-----|------|---------|---------|
| `[SUBJECT]` | ✅ | Scene → Entity Table → Relation Graph | `Scene: Create... \| Entity Table 5-col \| [Rel]` |
| `[COMPOSITION]` | ✅ | 布局 → 视角 → 排列 → 引导线 → 分层 | `horizontal L→R, isometric 3/4 view, asymmetric` |
| `[COLOR PALETTE]` | ✅ | 主色 → 辅色 → 强调色 → 背景色 | `role: #hex — usage` |
| `[LIGHTING]` | ✅ | 光源 → 方位 → 对比度 → 阴影 → 自发光 | `ambient backlight, high contrast, soft shadows` |
| `[ATMOSPHERE]` | ✅ | 氛围词 → 情绪 → 密度 | `technical · neutral · moderate detail` |
| `[PROPORTIONS]` | ✅ | 主体 → 负空间 → 大小比 | `60% central, 20% edge negative space` |
| `[VIEWPOINT]` | ❖ | 角度 → 景别 → 畸变 | `30° elevation, 315° azimuth, orthographic` |
| `[SCALE & DEPTH]` | ❖ | 层数 → 各层内容 → 景深 | `3 layers: fore/mid/background, shallow DOF` |
| `[TEXTURE]` | ❖ | 材质 1 · 材质 2 · 渲染基底 | `glass, core glow, vector flat with gradients` |
| `[MOTION]` | ❖ | 流向 → 速度 → 静态元素 | `L→R directional, static elements fixed` |
| `[FOCUS]` | ❖ | 主焦点 → 权重 → 引导 | `center-left, 60/40 weight, arrows guiding` |
| `[ANNOTATIONS]` | ❖ | 标签 → 标注线 → 图例 → 层级 | `sans-serif, dashed leader lines, legend yes` |
| `[EXCLUSIONS]` | ✅ | 逗号分隔排除项 | `no human figures, no logos, no UI chrome` |
| `[FORMAT]` | ✅ | 横纵比 · 分辨率 | `16:9 wide landscape, high resolution` |

- ✅ = always required · ❖ = conditional（见 Type-Dimension 矩阵）

## 常用色彩科学对照

| 概念 | 推荐色值 | HSL |
|------|---------|-----|
| 主信息/数据 | #00D4FF cyan | hsl(190, 100%, 50%) |
| 强调/告警/注意 | #FF6B35 warm amber | hsl(18, 100%, 60%) |
| 确认/通过 | #00FF88 green | hsl(155, 100%, 50%) |
| 错误/拒绝 | #FF4444 red | hsl(0, 100%, 63%) |
| 暗色背景 | #1A1A2E deep navy | hsl(240, 25%, 14%) |
| 中性灰底 | #2D2D3F dark gray | hsl(240, 12%, 21%) |
| 次要半透明 | #4A4A6E muted indigo | hsl(240, 20%, 36%) |
| 标签文字 | #FFFFFF white | hsl(0, 0%, 100%) |
