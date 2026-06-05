---
name: illustration-prompt
description: 根据文档或对话上下文，自动判断配图位置、推断视觉风格、生成可直接喂给图像生成模型的完整提示词。每张配图输出一个 `.prompt` 文件。需用户明确要求才触发，不会自动启动。触发词：#illustration
---

# Illustration Prompt Generator

根据文档或上下文，创建可直接喂给图像生成模型的高质量提示词

## Workflow

共 7 个阶段，按顺序执行。Step 2（全文理解）、Step 3（产出形态锚定）、Step 4（风格锚点）和 Step 5（配图规划）产出需经用户确认后方可进入下一步。

### 1. INGEST — 获取输入

接收用户的文档/上下文。支持：文件路径、URL、粘贴文本、对话上下文。

### 2. COMPREHEND — 理解全文

读全文，提取领域、受众、文章类型、语气。标记需要图解的关键节点：抽象概念首次出现、架构说明、对比转折、数据描述、流程步骤、类比隐喻。为每个候选节点标记**概念密度**（高/中/低）。

### 3. OUTPUT FORM ANCHORING — 产出形态锚定

在 COMPREHEND 输出经用户确认后，进入风格推断前，先锚定产出形态。

向用户呈现以下模板确认：

#### 产出形态锚定

请选择本次配图的产出形态：

- [ ] 文章内联插图（文中分散插入，与段落内容对应）
- [ ] 封面图（文章顶部，单张，概括全文主旨）
- [ ] 轮廓图/概览图（单张，展示文章结构骨架）
- [ ] 社交分享卡片（OG 图，16:9，含标题 + 视觉摘要）
- [ ] 演示文稿配图（多张，演讲场景，文字少视觉冲击强）
- [ ] 其他：__________

- 配图数量: [自动推理 / 固定 ___ 张]
- 特殊约束: [如有]

| 产出形态 | 对 PLANNING 的影响 | 对 GENERATE 的影响 |
|---------|------------------|------------------|
| 内联插图 | 按概念密度在各段落间分配 | 标准自然语言段落，含实体/布局/光照描述 |
| 封面图 | 仅 1 张，抽取最高概念密度的核心意象 | 装饰配图策略，≥30% 留白，无技术标注 |
| 轮廓图 | 1 张，全局结构映射 | 信息图/架构图策略，含标注和数据层级描述 |
| 社交卡片 | 1 张，16:9 固定，强调标题 + 视觉冲击 | 装饰配图策略，横纵比 16:9 |
| 演示配图 | 按章节或关键节点分配，每张自包含 | 文字极少，视觉优先，动态感描述 |

### 4. STYLE ANCHOR — 推断风格

从语感/领域/受众推断统一视觉风格，输出结构化风格锚点摘要（色板、渲染风格、氛围、参考方向）。**提交用户确认**，用户可调整色板/渲染风格/氛围/参考方向或整体覆写。

### 5. PLANNING — 规划配图

基于概念密度驱动，输出配图规划（位置、数量、每张的配图类型），每张图自动生成 diagram-slug。**提交用户确认**，用户可增删位置、调整类型、修改 slug、重新排序。

### 6. GENERATE — 生成提示词

严格按以下流程逐张生成。每张输出三个区块：
- Context（位置、摘要、类型——供审阅）
- Style Anchor（风格决策记录——供审阅）
- Prompt（自然语言段落——直接复制投喂图像模型）

### 7. OUTPUT — 写出文件

每张图输出到 `docs/<diagram-slug>.prompt`。

## Input

| 方式 | 说明 |
|------|------|
| 文件路径 | 读取本地文件 |
| URL | 使用 webfetch 获取全文 |
| 粘贴文本 | 直接处理 |
| 对话上下文 | 基于已有对话内容 + 补充要求 |

## Comprehend 理解原则

读取全文时关注以下维度，用于后续步骤：

- **领域**：技术 / 科学 / 人文 / 商业 / 教育 ……
- **受众**：专业读者 / 普通读者 / 决策者 / 学生 ……
- **文章类型**：教程 / 观点 / 报告 / 笔记 / 文档 ……
- **语气**：严肃 / 轻松 / 正式 / 亲切 / 批判 ……
- **关键节点**：以下位置优先标记为配图候选
  - 抽象概念首次出现（纯文字难以理解的）
  - 架构/系统说明
  - 对比或转折（A vs B, 之前 vs 之后）
  - 数据或趋势描述
  - 流程/步骤说明
  - 类比或隐喻（可用插图强化）

标记每个候选节点的**概念密度**（高/中/低），高密度优先配图。

将领域、受众、文章类型、语气及候选节点列表输出摘要提交用户确认。用户可修正领域判断、增删候选节点、调整概念密度。确认后方可进入 Step 3（产出形态锚定）。

概念密度联动 Prompt 详细度策略：

| 概念密度 | Prompt 详细度 | 应用方式 |
|---------|-------------|---------|
| 高 | 多细节层、丰富标注 | "highly detailed, multi-layered with annotations and callouts" |
| 中 | 结构清晰、中等细节 | "moderate detail, clear structure, focused composition" |
| 低 | 极简、氛围导向 | "minimal detail, atmospheric, clean negative space, sparse elements" |

### Article Type → Visual Strategy 映射

根据 COMPREHEND 阶段识别的文章类型，选择视觉策略：

| 文章类型 | 视觉策略建议 |
|---------|------------|
| 教程 | 步骤可视化、截图风格、界面元素、干净矢量、明亮色板 |
| 观点/分析 | 隐喻图、戏剧感光影、抽象拓扑、丰富纹理、高对比度 |
| 技术报告 | 精确几何图、数据可视化、中性色板、冷静精确氛围 |
| 产品文档 | UI/流程导向、简化架构图、干净明亮、信息密度高 |
| 笔记/博客 | 思维导图风格、手绘/线描质感、松散构图、有机形状 |

**使用规则**：上述为建议方向。如果 Style Anchor 用户确认时覆写了风格，以用户覆写为准。

## Style Anchor 风格推断

从文档语感自动推导视觉风格锚点，输出结构化摘要：

```markdown
## Style Anchor

- 配色方案: ■ [中文名1] [角色] · ■ [中文名2] [角色] · ■ [中文名3] [角色]
- 渲染风格:   [当前风格]，可选：写实 · 矢量扁平 · 抽象拓扑 · 等轴测 · 水彩 · 线描 · ……(详见 references/type-strategies.md)
- 氛围基调: [关键词 2-4 个，如 简洁 · 技术感 · 深色 · 极简]
- 细节密度: [精致丰富 / 中等细节 / 极简留白]
- 风格参考: [类比或参考方向，如 深色仪表盘美学 / 复古科学教科书]
```

将结构化摘要呈现给用户，用户确认时，可逐项修改或整体覆写。

## Planning 配图规划

基于概念密度驱动，输出配图规划：

```
建议配图 4 张：

  #1 [concept-intro]         第 2 段 · 概念引入    概念示意图
  #2 [system-architecture]   第 4 节 · 架构说明    架构图
  #3 [comparison-table]      第 5 节 · 方案对比    信息图
  #4 [flow-process]          第 7 节 · 流程步骤    流程图
```

每张图自动生成 diagram-slug（简短英语 kebab-case 标题）。

用户可在此阶段：
- 增删配图位置
- 调整配图类型
- 修改 diagram-slug
- 重新排序

### Visual Glossary（元素词典）

PLANNING 确认后，GENERATE 前，为文章中反复出现的关键概念注册统一视觉标识。

```
元素词典:

- [Candidate node]:  暖琥珀色 #FF6B35, 六边形, 自发光边缘辉光
- [Follower node]:   半透明青色 #00D4FF, 透明度 30%, 圆形
- [RPC message]:     暖琥珀到青色虚线方向箭头
- [consensus]:       绿色 #00FF88 重叠勾选图标
```

**规则**：
- 仅注册跨图复用的概念（单次出现的无需条目）
- 每个条目包含：命名、色值 hex、形状、渲染特征
- 所有 Prompt 引用时使用相同描述，禁止同义改写
- 提交用户确认 PLANNING 时同步确认 Glossary

### Visual Role → Prompt Strategy 映射

每张图的 Visual Role 决定 Prompt 的侧重方向：

| Visual Role | Prompt 策略 |
|-------------|------------|
| 帮助理解 | 标注/箭头/标签/图例清晰，结构优先于美感 |
| 装饰点缀 | 氛围优先，隐喻表达，>30% 负空间，不包含技术标注 |
| 数据对比 | 精确图形（柱/饼/折线），数值标注，色阶分类，图例 |
| 流程说明 | 时序布局（L→R / T→B），箭头连线，状态标注，多面板 |

## Generate 提示词生成

严格按以下流程和模板输出每张图的提示词文件。

文件路径：`docs/<diagram-slug>.prompt`

### 模板

```markdown
## Context

- 所处位置: [文章中具体位置]
- 内容摘要: [该段落的核心内容摘要，为理解插图意图提供上下文]
- 配图类型: [概念示意图 / 架构图 / 流程图 / 信息图 / 装饰配图]
- 视觉角色: [帮助理解 / 装饰点缀 / 数据对比 / 流程说明]

## Style Anchor

- 配色方案: [#hex1 角色 · #hex2 角色 · #hex3 角色]
- 渲染风格: [渲染风格]
- 氛围基调: [氛围关键词 2-4 个]
- 细节密度: [精致丰富 / 中等细节 / 极简留白]
- 风格参考: [参考方向]

## Prompt

[自然语言段落。第一句祈使句总述场景。随后依次：Primary 实体（形状、#hex、状态）→ Secondary 实体+差异 → 关系/连接 → 空间布局/视角 → 光照/氛围 → No... 排除项 → Aspect ratio... 格式]
```

### Type-specific Prompt Strategies

按配图类型选择对应的 Prompt 策略。各类型的详细策略表见 `references/type-strategies.md`。

### 生成流程

1. **构建内部追踪数据**（不输出，用于校验）

   为每张图整理：

   ```
   实体表: 所有实体、数量、色值 hex、形状、渲染特征、角色(primary/secondary)
   关系图: 实体间连接方式、方向、线型
   色板:   该图涉及的所有 hex 值
   决策:   布局类型 · 视角 · 排版 · 光照 · 氛围 · 格式
   ```

   元数据填写完整后才进入下一步。

2. **按写作规则撰写** — 将追踪数据自然融入段落

3. **语义扫描校验** — 对照 Quality Checks 逐项扫描。不通过则重写

### 写作规则

#### 句子结构

- 第一句以祈使句总述场景（`Create a...` / `Show a...` / `Illustrate a...`）
- Primary 实体先出场，描述最详细（形状、色值 `#hex`、大小、发光状态）
- Secondary 实体紧随其后，用 `while`、`in contrast to` 等标识与 Primary 的差异
- 关系/连接用动作动词表达（`radiate outward from`、`connect through`、`flow from...to`）
- 布局、视角、透视自然融入空间描述，不单独成句列表
- 光照作为段落过渡自然插入
- 排除项以 `No...` 否定句收尾
- 格式以收束句指定（`Aspect ratio...`）

#### 数值精确

- 实体数量用精确英文数字：`a single`、`four`、`three of them`
- 颜色值使用 hex 格式精确指定：`#FF6B35`
- 所有 hex 必须来自内部追踪色板，禁止同义改写（不允许用 `amber` 代替 `#FF6B35`）

#### 长度与语言

- 长度自由，根据概念密度自定：高密度节点多细节层（丰富实体描述、空间层次、光照过渡
- Write in English
- 使用自然连贯的段落，不分割为列表或要点

### 产出语义

最终输出应该是 `## Prompt` 下方的一个完整自然语言段落，不加额外说明或包装。用户只复制 `## Prompt` 下面这一段即可。

### 概念→视觉隐喻指南

抽象概念必须翻译为图像生成模型可理解的视觉元素。常见领域的隐喻映射表见 `references/metaphor-guide.md`。

**使用规则**：优先匹配源文中出现的术语，选择最贴合的隐喻。避免强行套用——如果源文有自带的比喻（如 `think of it as a highway`），优先使用原文比喻而非表内映射。

### 输出示例

```
# docs/raft-leader-election.prompt

## Context

- 所处位置: 第 3 节 · 第 2 段
- 内容摘要: Candidate 发起选举，RequestVote RPC 广播到所有 Peer，收到多数派确认后成为 Leader
- 配图类型: 概念示意图
- 视觉角色: 帮助读者理解 Raft Leader Election 的核心消息流程

## Style Anchor

- 配色方案: #FF6B35 强调色 · #00D4FF 辅色 · #1A1A2E 背景色
- 渲染风格: 抽象拓扑，矢量扁平加微渐变
- 氛围基调: 简洁 · 极简 · 技术感
- 细节密度: 中等细节，无视觉噪音
- 风格参考: 深色仪表盘美学，半透明自发光节点

## Prompt

Create an abstract topology diagram of a Raft cluster leader election
process. At the center, a single Candidate node with a hexagonal core
glows in #FF6B35 with a self-illuminated edge halo. Around it in a
radial ring arrangement, four Follower nodes float as translucent
circles in #00D4FF at 30% opacity; three of them display a #00FF88
confirmation overlay indicating they have acknowledged the vote
request, while the fourth remains dark. Dashed directional arrows in
#00D4FF radiate outward from the Candidate to each Follower, tracing
the RequestVote RPC broadcast path. The scene sits against a deep
#1A1A2E gradient background, viewed from a 30° elevated isometric 3/4
perspective with the Candidate node slightly elevated above the ring
plane to establish visual hierarchy. Lighting comes from the
self-illuminated Candidate as the primary source against a dark
ambient with high contrast. The atmosphere is precise, minimal,
technical, and analytical, with moderate detail and clean negative
space occupying the outer 20% of the composition. No human figures,
no realistic textures, no UI chrome, no logos, no visible text labels,
no decorative elements. Aspect ratio 16:9 wide landscape, high
resolution.
```

## Output 文件规范

- 每张图一个文件：`docs/<diagram-slug>.prompt`
- diagram-slug 由 Skill 自动生成，简短描述性英语 kebab-case
- 文件包含完整的 Context + Style Anchor + Prompt 三个区块
- Prompt 区块为自然语言段落，直接复制即可投喂图像生成模型

## Quality Checks

交付前逐项语义扫描：

### 实体覆盖
- [ ] Primary 实体在 Prompt 中出现（实体名匹配内部追踪数据）
- [ ] 所有 secondary 实体在 Prompt 中出现
- [ ] 每个实体的数量词与内部追踪一致（`a single` / `four` / `three of them`）

### 色值精确
- [ ] 所有 hex 值在 Prompt 中出现且与内部色板一致
- [ ] 无同义颜色描述（禁止用 `amber` 代替 `#FF6B35`）

### 关系表达
- [ ] 实体间关系通过动作/连接词表达
- [ ] 关系方向正确（`from X to Y` / `radiate outward from`）

### 空间布局
- [ ] 布局类型已表达（径向/水平/垂直/网格/自由）
- [ ] 视角/透视已表达
- [ ] 构图原则已表达（对称/不对称/三分法等）

### 光照氛围
- [ ] 光源类型+方位已描述
- [ ] 对比度已描述（高/中/低）
- [ ] 氛围关键词 2-4 个

### 格式与排除
- [ ] 横纵比已指定
- [ ] 排除项 ≥2 个
- [ ] 无图像模型专用参数（`--ar`、`--v` 等）

### Visual Glossary 一致性
- [ ] 跨图复用概念使用相同视觉描述（形状、hex、渲染特征）
- [ ] 元素词典已锁定且被引用

### 上下文一致性
- [ ] Context 中的位置/摘要与原文一致
- [ ] 概念密度高的节点有更多细节层级

## Anti-Patterns

- ❌ Prompt 块包含说明文字（如"你可以这样使用"、"以下是提示词"）—— 只有提示词本身
- ❌ Prompt 块用中文写（英文提示词对图像模型理解更好）
- ❌ Prompt 块包含图像模型专用参数（`--ar`、`--v`、`--s`、`--style` 等）
- ❌ 风格锚点前后矛盾（如色板写深色模式但提示词要求白色背景）
- ❌ diagram-slug 使用中文或过长
- ❌ 输出多张图时全部塞到一个文件里（每张图独立文件）
- ❌ 不经过风格确认直接生成提示词
- ❌ 使用颜色名称而非 hex 值（如使用 "amber" 而非 "#FF6B35"）
- ❌ 内部追踪数据中的实体未全部写入 Prompts
