# Color Science Reference

按视觉风格基调索引的色板系统。每套色板定义了 9 个语义色值 + 氛围印象，用于 GENERATE 阶段的 Style Anchor 和 Prompt 撰写。

## 使用规则

- 选择视觉风格基调后（Step 4a），直接加载对应色板作为该批次全部配图的配色方案
- 所有 Prompt 中的 hex 值必须来源于已选色板，禁止同义改写
- 跨图复用的同一实体在同一批次中必须使用相同 hex，由 Visual Glossary 保证
- HTML 输入时（Step 2 提取了文档样式基调），优先映射到最接近的色板，而非使用默认

## 色板索引

| 风格基调 | 色板 slug | 行 |
|---------|----------|---|
| 技术手绘风 | tech-handdrawn | ↓ |
| 高对比分析风 | analysis-contrast | ↓ |
| 灰度结构风 | grayscale-structural | ↓ |
| 手记博客风 | blog-handdrawn | ↓ |

---

### tech-handdrawn — 技术手绘风

| 角色 | 色值 | HSL | 用途 |
|------|------|-----|------|
| 主色 | `#3D7EA6` | hsl(204, 45%, 45%) | Primary entity fill |
| 强调色 | `#C47A3D` | hsl(30, 45%, 50%) | Accent / call to action |
| 背景色 | `#F5F3EF` | hsl(35, 30%, 96%) | Canvas background |
| 第二背景 | `#E8E4DC` | hsl(35, 25%, 89%) | Card / panel |
| 成功/确认 | `#4A8C5A` | hsl(130, 30%, 42%) | Confirmation / complete |
| 警告/注意 | `#B8923D` | hsl(42, 50%, 48%) | Warning / pending |
| 错误/拒绝 | `#A64D4D` | hsl(0, 35%, 48%) | Error / denied |
| 中性/次要 | `#6D7A8C` | hsl(210, 15%, 49%) | Secondary entity |
| 文字/标签 | `#2D3A4A` | hsl(210, 25%, 23%) | Label / text |

**氛围印象**: 严谨 · 手绘 · 白板感

---

### analysis-contrast — 高对比分析风

| 角色 | 色值 | HSL | 用途 |
|------|------|-----|------|
| 主色 | `#FF3D00` | hsl(14, 100%, 50%) | Primary entity fill |
| 强调色 | `#00E5FF` | hsl(186, 100%, 50%) | Accent / secondary signal |
| 背景色 | `#1A1A1A` | hsl(0, 0%, 10%) | Canvas background |
| 第二背景 | `#2A2A2A` | hsl(0, 0%, 16%) | Card / panel |
| 成功/确认 | `#00E676` | hsl(151, 100%, 45%) | Confirmation / complete |
| 警告/注意 | `#FFEA00` | hsl(55, 100%, 50%) | Warning / pending |
| 错误/拒绝 | `#FF1744` | hsl(348, 100%, 55%) | Error / denied |
| 中性/次要 | `#616161` | hsl(0, 0%, 38%) | Secondary entity |
| 文字/标签 | `#FFFFFF` | hsl(0, 0%, 100%) | Label / text |

**氛围印象**: 戏剧化 · 高张力 · 分析感

---

### grayscale-structural — 灰度结构风

| 角色 | 色值 | HSL | 用途 |
|------|------|-----|------|
| 主色 | `#4A5568` | hsl(215, 20%, 35%) | Primary entity fill |
| 强调色 | `#1A202C` | hsl(215, 30%, 14%) | Accent / key boundary |
| 背景色 | `#F8F9FA` | hsl(210, 20%, 98%) | Canvas background |
| 第二背景 | `#EDF2F7` | hsl(210, 40%, 95%) | Card / panel |
| 成功/确认 | `#5A7A60` | hsl(130, 15%, 42%) | Confirmation — subtle green cast |
| 警告/注意 | `#8A7A50` | hsl(42, 25%, 43%) | Warning — subtle amber cast |
| 错误/拒绝 | `#7A5050` | hsl(0, 25%, 40%) | Error — subtle red cast |
| 中性/次要 | `#A0AEC0` | hsl(215, 20%, 69%) | Secondary entity |
| 文字/标签 | `#2D3748` | hsl(215, 25%, 23%) | Label / text |

**氛围印象**: 克制 · 结构 · 工程感

---

### blog-handdrawn — 手记博客风

| 角色 | 色值 | HSL | 用途 |
|------|------|-----|------|
| 主色 | `#7986CB` | hsl(231, 42%, 64%) | Primary entity fill |
| 强调色 | `#EC407A` | hsl(338, 82%, 59%) | Accent / highlight |
| 背景色 | `#FFF8E1` | hsl(42, 100%, 94%) | Canvas background |
| 第二背景 | `#FFECB3` | hsl(40, 100%, 85%) | Card / panel |
| 成功/确认 | `#8BC34A` | hsl(88, 50%, 53%) | Confirmation / complete |
| 警告/注意 | `#FFD54F` | hsl(46, 100%, 66%) | Warning / pending |
| 错误/拒绝 | `#FF8A65` | hsl(15, 100%, 70%) | Error / denied |
| 中性/次要 | `#BCAAA4` | hsl(20, 15%, 69%) | Secondary entity |
| 文字/标签 | `#5D4037` | hsl(17, 25%, 29%) | Label / text |

**氛围印象**: 温暖 · 有机 · 手写感
