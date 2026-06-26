---
name: article-image-prompt
disable-model-invocation: true
description: 为一个没有配图的文章生产封面图和内联插图（Prompt + 可选图片输出）。用户有文章但不知道怎么配图时使用。
---

# 文章配图 Prompt 生成

一个**视觉翻译器** — 读取文章（文件/URL/粘贴/上下文），产出它需要的配图，不需要用户做自己不会的设计决策。

**翻译器** 是核心概念：忠实读取原文，找到需要翻译的部分，用另一种语言（图像）交付。用户不需要告诉它*怎么*翻译 — 只需要确认目录。

---

## 阶段总览

| # | 阶段 | 做什么 | 用户操作 |
|---|------|-------|---------|
| 1 | **INGEST** | 读取原文 | 无 |
| 2 | **AUDIT** | 扫描配图候选 | 无 |
| 3 | **ALIGN** | 确认目录：TRIAGE 选候选 → REFINE 定风格 | 逐层 + 逐组确认 |
| 4 | **TRANSLATE** | 执行翻译：生成 Prompt | 无 |
| 5 | **RENDER** | 交付译本 | 无 |

---

### 1. INGEST — 读取文章

从文件路径、URL、粘贴文本或对话上下文中获取文章。识别格式（markdown/HTML/纯文本/PDF）。

**完成标准：** 全文已在上下文中，并标注了来源格式。

---

### 2. AUDIT — 扫描配图候选

对全文进行**松扫描** — 标记所有值得配图的内容：

- **抽象概念**（一致性、背压、收敛）
- **系统/架构**（分层、组件、服务）
- **流程**（阶段、状态转换、决策分支）
- **对比或权衡**（vs.、与…相反、对比）
- **量化论断**（X% 的、N×、增长曲线）
- **空间/因果关系**（导致、依赖于、位于…内）
- **数据结构**（树、环、队列、缓冲区）
- **文章核心论点**（整篇文章的主题 — 封面候选）

每个候选按以下三维度打分：

| 分值 | 1 | 2 | 3 | 4 | 5 |
|-----|---|---|---|---|---|
| **清晰度增益** | 配图无帮助 | | 中立 | | 没有配图读者会误解 |
| **视觉适配度** | 无法用图表达 | | 需要高度抽象 | | 能自然映射到具象画面 |
| **叙事权重** | 边缘内容 | | 支撑性细节 | | 核心论点的关键 |

按 `清晰度增益 × 叙事权重` 降序排列。

**无最低频次门槛：** 一个概念只出现一次但承载了文章论点，比出现十次但无关紧要的概念更值得配图。

排序后，为每个候选分配**置信等级**：

| 等级 | 标签 | 条件 | 含义 |
|------|------|------|------|
| A | 高置信度 · 强烈推荐 | 清晰度 ≥ 4 且 权重 ≥ 4 | 有清晰视觉隐喻，强烈推荐 |
| B | 中置信度 · 可接受 | 总分 ≥ 6，非 A | 需要一定抽象，仍可行 |
| C | 低置信度 · 存疑 | 总分 < 6 | 强行可视化，建议跳过除非别无选择 |

候选中表达文章核心论点的、排名最高的，标记为**封面候选**。接下来的 N 个（默认：3 个）为**内联候选**。根据文章长度重载 N：<500 字 → N=1，500-3000 → N=3，>3000 → N=5。

输出中文候选列表，包含评分、置信等级和一句推荐理由。候选名称使用文章原词（中文）。

**完成标准：** 已生成并展示排序后的候选列表。

---

### 3. ALIGN — 确认目录（两轮）

ALIGN 就是确认"翻译目录"：拆为两轮 — **TRIAGE**（选哪些章节进译本）和 **REFINE**（确认每章的设计细节）。将"选什么"和"怎么做"解耦，可以快速接受高置信候选、丢弃存疑候选，无需从头再来。

---

#### 第 1 轮：TRIAGE — 目录确认（挑选候选）

用 AUDIT 输出的分层候选列表逐层展示，从高置信到低置信。默认接受信号从 Y 到 N 递减。

```
🅰 Tier A — 高置信度 · 强烈推荐
  🖼 封面: "两阶段提交共识"                 [清晰度:5 权重:5]
  📄 1. "投票阶段"                         [清晰度:4 权重:5]
是否全部接受 Tier A? [Y/n]
```

```
🅱 Tier B — 中置信度 · 可接受
  📄 2. "崩溃恢复时间线"                   [清晰度:3 权重:4]
是否全部接受 Tier B? [y/N]
```

```
🅲 Tier C — 低置信度 · 存疑
  📄 3. "协调器故障转移状态"                [清晰度:2 权重:3]
是否全部接受 Tier C? [y/N]
```

用户拒绝某层默认值（A 层的 Y，B/C 层的 N）时，指定去留：`保留 1，去掉 2`。封面候选必须用户明确确认才能丢弃 — 它代表文章论点。

**完成标准：** 每个候选已标记为保留或丢弃。保留列表不为空。

---

#### 第 2 轮：REFINE — 为保留候选确定风格与构图

按文章类型推荐**风格**：

| 文章类型 | 推荐风格 | 色板标识 |
|---------|---------|---------|
| 教程 | tutorial-warm 温暖教程风 |
| 分析/观点 | analysis-contrast 高对比分析风 |
| 技术报告 | grayscale-structural 灰度结构风 |
| 产品文档 | product-doc 产品文档风 |
| 笔记/博客 | blog-handdrawn 手记博客风 |
| 混合/其他 | tech-clean 简洁技术风 |

对保留候选展示推荐风格：

```text
🖼 封面: "两阶段提交共识"
   风格: analysis-contrast · 高对比分析风
   构图: 分屏对比，协调器 vs 参与者，绿/红状态指示

📄 1. "投票阶段" — 流程图
   风格: tech-clean · 位于 § "准备阶段" 后
📄 2. "崩溃恢复" — 时间线图
   风格: analysis-contrast · 位于 § "故障场景" 后

  [accept all]  [adjust]  [reject and retry]
```

用户从三种回应中选择：

- **accept all** → 直接进入 TRANSLATE 阶段生成 Prompt
- **adjust** → 用户修改风格、替换色板、调整构图，或设置每张图的文字策略。调整后进入 TRANSLATE
  - ⚠ 如果用户要求增删配图 → 回 TRIAGE 重新确认候选集，不在本轮处理
- **reject and retry** → 用户提供新方向（如"少用图表，多用概念图"），重新执行 AUDIT。TRIAGE 保留的候选作为初始约束带入

**图中文字策略**有默认值，按插图类型自动推荐，只需在用户不同意时调整：

| 插图类型 | 默认文字策略 |
|---------|------------|
| 封面 | 尽量无字 |
| 示意图 | 无文字 或 仅标签 |
| 流程图 | 仅标签 |
| 信息图 | 仅数字 |
| 装饰图 | 无文字 |

**完成标准：** 每个保留候选已确认风格 + 构图 + 文字策略。无待解决问题。

---

### 4. TRANSLATE — 执行翻译（生成 Prompt）

把目录确认后的方案"翻译"为图片模型能理解的语言。每张已确认的插图生成两项内容：

1. **Visual Thesis** — 一句话说明读者只看到这张图（不读文章）时应该理解什么。必须包含可验证的主张，不只是话题标签（用中文）：
   - ✓ "读者应该理解 **为什么社交 Feed 选用 AP 优于 CP**" — 包含主张 + 立场
   - ✗ "读者应该理解 **AP 和 CP 的区别**" — 只有话题，没有主张

2. **Prompt** — 图片生成 Prompt，首句锚定在 Visual Thesis 上。

Visual Thesis 先写，锚定 Prompt，包含在输出文件的 Prompt 之前。这样 `.prompt` 文件里有一条可追溯的意图声明 — 可以用它来检验生成的图片是否符合预期。

**语言策略：** 在 `.prompt` 文件中，只有 `## Prompt` 段是英文（实际的图片生成文本）。其他所有段使用中文 — 用户通过中文来理解和验证意图。

**每张图的输出结构** — 完整字段列表见 Reference → Prompt spec：

```markdown
# <diagram-slug>

## Visual Thesis
[一句话：含可验证主张，不只是话题标签]

## Context
[位置、插图类型、目标模型、图中文字策略]

## Style Anchor
[色板、渲染风格、氛围、细节密度]

## Prompt
[English — narrative declaration + Visual Thesis anchoring + colors + layout + exclusions]
```

五个段标题（`# <slug>`、`## Visual Thesis`、`## Context`、`## Style Anchor`、`## Prompt`）是规范结构。所有字段级细节只在一个地方：Reference 的 Prompt spec。

`## Prompt` 正文**仅限英文**。使用所选色板的精确 **hex 颜色**。每个视觉元素必须追溯到原文（原文依据 → 合理推导 → 视觉转化方案）。

输出为单个 `{article-dir}/illustration-prompt/{slug}.prompt` 文件，多个 Prompt 用 `# <diagram-slug>` 分隔。`slug` 从文章主题推断（kebab-case）。如果文件已存在，追加 `-2`、`-3` 等。输入为文件路径时，`article-dir` 为该文件所在目录；输入为 URL 或粘贴文本时，`article-dir` 为当前工作目录。如目录不存在则创建。

参考 `references/color-science.md` 获取色板 hex 值、`references/metaphor-guide.md` 获取概念→视觉隐喻映射、`references/type-strategies.md` 获取各类文章的措辞模式。

**完成标准：** 每张已确认插图都有一个符合规范和质检要求的 Prompt。文件结构已校验。

---

### 5. RENDER — 交付译本

保存 `.prompt` 文件（TRANSLATE 阶段已逐步生成）。向用户报告文件路径。

**完成标准：** 已报告文件路径。

---

## Reference

### Prompt spec

```markdown
# <diagram-slug>

## Visual Thesis

[一句话：读者从这张图应该理解什么。必须包含可验证的主张，不只是话题标签。]

## Context

- 位置: [所在章节 / 段落]
- 插图类型: [cover / diagram / flowchart / infographic / decorative]
- 目标模型: [Generic / GPT Image / Midjourney / Flux / SDXL / Ideogram]
- 图中文字: [none / labels only / numbers only / exact text / minimal]
- 文字语言: 中文（默认）

## Style Anchor

- 色板: <slug>
- 渲染风格: [vector flat / gradient / hand-drawn / realistic / etc.]
- 氛围: [2-4 个氛围关键词]
- 细节密度: [rich / moderate / minimal]

## Prompt

[English only — Narrative declaration + Visual Thesis anchoring + colors + layout + exclusions]
[Aspect ratio]
[Exclusions: "No..." negative sentences]
[Entities: position + shape + #hex + size/state, one per sentence]
[Relationships: connection type + direction + endpoints]
[Reading order: start → path → end]
[Semantic binding (optional): representing / indicating / depicting block at end]
```

### 构图七层

1. **叙事声明** — 媒介/风格 + Visual Thesis 锚定。首句必须回答"这张图表达了什么主张？"，而不是"这张图展示了什么主题？"（例如：`A split-screen comparison: left side shows user waiting with loading spinner (CP — consistent but slow), right side shows smooth scrolling with stale-data badge (AP — fast but eventually consistent). The AP side is visually favored — brighter, larger, warmer.`）
2. **画布** — 背景色（hex）+ 宽高比
3. **约束** — 排除项，以 `No...` 语句表达（至少 2 条）
4. **实体** — 每个实体一句话：位置、形状、`#hex`、大小/状态
5. **关系** — 连接类型、方向、端点
6. **视线引导** — 阅读顺序指导（`Reading order: start at..., then...`）
7. **语义绑定（可选）** — `representing`/`indicating`/`depicting` 写在结尾单独一段，决不可嵌入实体或关系句中

### 核心规则

- **Visual Thesis 先行**：每张图必须先写 `## Visual Thesis`。主张必须包含可验证论断 — 不只是话题标签（"AP 和 CP 的权衡" ✗ → "为什么社交 Feed 更适合 AP" ✓）。
- **叙事锚定**：Prompt 首句必须与 Visual Thesis 对齐。如果 thesis 说"AP 更优"，首句必须在视觉上表达这种偏好（更亮/更大/更暖），而非保持中立。
- **Hex 色彩精准**：所有颜色值使用所选色板的精确 hex。不允许同义词替换（`#FF6B35` 就是 `#FF6B35`，不是 `amber` 或 `orange`）。
- **原文依据**：每个视觉元素必须追溯到原文。三层溯源：原文依据（事实）→ 合理推导 → 视觉转化方案。
- **视线引导**：必须明确引导视线方向。不允许省略。
- **叙事焦点**：视觉上最突出的元素必须是核心概念的"主角"。不允许"核心元素放角落、装饰居中"。
- **图中文字**：默认为中文，按每张图已确认的策略执行。
- **Block representing**：`representing`/`indicating`/`depicting` 只写在尾部语义绑定段。不可嵌入实体或关系句。
- **中英分界**：在 `.prompt` 文件中，`Visual Thesis`、`Context`、`Style Anchor` 等元数据段使用中文。只有 `## Prompt` 正文是英文（发给图片模型的生成文本）。

### 质检清单

交付前检查：

- [ ] **Thesis 检查**：每张图都有 `## Visual Thesis`，且包含可验证主张
- [ ] **叙事对齐**：Prompt 首句与 Visual Thesis 一致（如 thesis 认为"AP 更优"，首句不保持中立）
- [ ] 构图注中每个实体都出现在 Prompt 中
- [ ] 所有 hex 值来自所选色板（无同义词替换）
- [ ] 视线引导已明确指定
- [ ] 约束已应用（"禁止添加"等排除项）
- [ ] 视觉元素追溯到原文
- [ ] `representing`/`indicating` 只出现在尾部，不嵌入中间
- [ ] 叙事焦点对齐（最突出元素 = 核心概念）
- [ ] Prompt 为一个连贯段落，非列表
- [ ] 图中文字遵循已确认的策略和语言（默认中文）
- [ ] 跨图一致性：同一概念在所有图中使用相同的视觉描述
- [ ] **语言检查**：`## Visual Thesis`、`## Context`、`## Style Anchor` 使用中文；仅 `## Prompt` 正文为英文
