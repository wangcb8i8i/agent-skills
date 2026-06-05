---
name: illustration-prompt
description: 根据文档或对话上下文，自动判断配图位置、推断视觉风格、生成可直接喂给图像生成模型的完整提示词。每张配图输出一个 `.prompt` 文件。需用户明确要求才触发，不会自动启动。触发词：#illustration
---

# Illustration Prompt Generator

根据文档或上下文，创建可直接喂给图像生成模型的高质量提示词

## Workflow

共 7 个阶段，按顺序执行。Step 2（全文理解）、Step 3（产出形态与模型锚定）、Step 4（风格锚点）和 Step 5（配图规划）产出需经用户确认后方可进入下一步。

| # | 步骤 | 需用户确认 | 概要 |
|---|------|-----------|------|
| 1 | INGEST 获取输入 | 否 | 接收文档/URL/粘贴文本 |
| 2 | COMPREHEND 理解全文 | 是 | 提取领域/受众/关键节点 |
| 3 | OUTPUT FORM + MODEL ANCHORING 产出形态与模型锚定 | 是 | 选择产出形态、目标模型、文字策略 |
| 4 | STYLE ANCHOR 推断风格 | 是 | 输出色板/渲染/氛围/风格参考 |
| 5 | PLANNING 规划配图 | 是 | 输出配图规划 + 信息溯源表 + 元素词典 |
| 6 | GENERATE 生成提示词 | 否 | 逐张生成 Prompt |
| 7 | OUTPUT 写出文件 | 否 | 输出 .prompt 文件 |

### 1. INGEST — 获取输入

接收用户的文档/上下文。

| 方式 | 说明 |
|------|------|
| 文件路径 | 读取本地文件 |
| URL | 使用 webfetch 获取全文 |
| 粘贴文本 | 直接处理 |
| 对话上下文 | 基于已有对话内容 + 补充要求 |

### 2. COMPREHEND — 理解全文

读全文，提取领域、受众、文章类型、语气。标记需要图解的关键节点：抽象概念首次出现、架构说明、对比转折、数据描述、流程步骤、类比隐喻。为每个候选节点记录 原文位置，并标记以下维度：**概念密度**（高/中/低）、**理解增益**（高/中/低）、**叙事重要性**（高/中/低）、**视觉可译性**（高/中/低）、**图内是否需文字**（无文字 / 仅标签 / 仅数字 / 必须精确文字）。候选节点按综合优先级排序，而不是只按概念密度排序。

#### 理解维度

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
- **原文位置**：每个候选节点对应的原文位置（段落、节、小节或引用片段）
- **图内是否需文字**：无文字 / 仅标签 / 仅数字 / 必须精确文字

为每个候选节点标记以下评分，用于综合排序：

| 因子 | 含义 |
|------|------|
| 概念密度 | 信息是否抽象、是否需要图解辅助 |
| 理解增益 | 配图后能否显著降低理解门槛 |
| 叙事重要性 | 是否处于结构总览、关键转折、核心论点 |
| 视觉可译性 | 是否能稳定转化为清晰视觉元素 |
| 复用价值 | 是否会在多张图中重复出现，值得进入 Glossary |
| 传播价值 | 是否适合作为封面图、社交卡片或概览主视觉 |

概念密度高的节点通常需要更细的 Prompt，但配图优先级不只由概念密度决定。

概念密度联动 Prompt 详细度策略：

| 概念密度 | Prompt 详细度 | 应用方式 |
|---------|-------------|---------|
| 高 | 多细节层、丰富标注 | "highly detailed, multi-layered with annotations and callouts" |
| 中 | 结构清晰、中等细节 | "moderate detail, clear structure, focused composition" |
| 低 | 极简、氛围导向 | "minimal detail, atmospheric, clean negative space, sparse elements" |

#### 用户确认模板

将以下摘要提交用户确认：

```
领域：分布式系统
受众：有后端基础的开发者
文章类型：教程
语气：技术性 · 严谨 · 逐步引导

候选配图节点（按综合优先级排序）：

  #1  第 2 节 · Leader Election 概念首次出现
       原文位置：第 2 节第 1-3 段
       综合优先级：高  |  概念密度：高  |  理解增益：高  |  图内是否需文字：无文字

  #2  第 4 节 · Log Replication 架构说明
       原文位置：第 4 节第 1-5 段
       综合优先级：高  |  概念密度：中  |  理解增益：高  |  图内是否需文字：仅标签
```

每个候选节点至少包含：原文位置、综合优先级、概念密度、理解增益、图内是否需文字。用户可修正领域判断、增删候选节点、调整评分和图内是否需文字。确认后方可进入 Step 3（产出形态与模型锚定）。

#### Article Type → Visual Strategy 映射

根据 COMPREHEND 阶段识别的文章类型，选择视觉策略：

| 文章类型 | 视觉策略建议 |
|---------|------------|
| 教程 | 步骤可视化、截图风格、界面元素、干净矢量、明亮色板 |
| 观点/分析 | 隐喻图、戏剧感光影、抽象拓扑、丰富纹理、高对比度 |
| 技术报告 | 精确几何图、数据可视化、中性色板、冷静精确氛围 |
| 产品文档 | UI/流程导向、简化架构图、干净明亮、信息密度高 |
| 笔记/博客 | 思维导图风格、手绘/线描质感、松散构图、有机形状 |

**使用规则**：上述为建议方向。如果 Style Anchor 用户确认时覆写了风格，以用户覆写为准。

### 3. OUTPUT FORM + MODEL ANCHORING — 产出形态与模型锚定

在 COMPREHEND 输出经用户确认后，进入风格推断前，先锚定产出形态、目标模型和全局图内文字策略。

#### 用户确认模板

以下默认值由技能基于 COMPREHEND 阶段分析结果生成，提交用户确认：

```
请选择本次配图的产出形态：

- [x] 文章内联插图（文中分散插入，与段落内容对应）  ← 默认
- [ ] 封面图（文章顶部，单张，概括全文主旨）
- [ ] 轮廓图/概览图（单张，展示文章结构骨架）
- [ ] 社交分享卡片（OG 图，16:9，含标题 + 视觉摘要）
- [ ] 演示文稿配图（多张，演讲场景，文字少视觉冲击强）
- [ ] 其他：__________

- 配图数量: 3 (可选：自动推理 / 固定 ___ 张)
- 目标模型: Midjourney (可选：Generic / GPT Image / Flux / SDXL / Ideogram / 其他)
- 优先目标: 语义准确 (可选：图表清晰 / 排字能力 / 写实质感 / 风格冲击)
- 全局图内文字策略: 无文字 (可选：仅标签 / 仅数字 / 必须精确文字 / 尽量无字)
- 特殊约束: [如有]
```

| 产出形态 | 对 PLANNING 的影响 | 对 GENERATE 的影响 |
|---------|------------------|------------------|
| 内联插图 | 按综合优先级在各段落间分配 | 标准自然语言段落，含实体/布局/光照描述 |
| 封面图 | 仅 1 张，抽取传播价值最高的核心意象 | 装饰配图策略，≥30% 留白，无技术标注 |
| 轮廓图 | 1 张，全局结构映射 | 信息图/架构图策略，含标注和数据层级描述 |
| 社交卡片 | 1 张，16:9 固定，强调标题 + 视觉冲击 | 装饰配图策略，横纵比 16:9，按图内文字策略处理标题 |
| 演示配图 | 按章节或关键节点分配，每张自包含 | 文字极少，视觉优先，动态感描述 |

#### Target Model Anchor

在 Step 3 锚定以下全局约束：

```markdown
## Target Model Anchor

- Target model: [Generic / GPT Image / Midjourney / Flux / SDXL / Ideogram / 其他]
- Priority: [semantic fidelity / diagram clarity / typography / photorealism / stylistic impact]
- 全局图内文字策略: [无文字 / 仅标签 / 仅数字 / 必须精确文字 / 尽量无字]
```

使用规则：

- 未指定时默认 `Generic`，保持模型无关的高质量自然语言 Prompt。
- 指定目标模型后，Prompt 用词可偏向该模型更稳定理解的表达，但仍优先保证语义准确。
- 图内文字策略默认全局生效；单图如需例外，在 PLANNING 阶段显式覆写。
- 当策略为 `Exact text required` 时，必须逐字引用文案；如果目标模型排字能力弱，优先建议生成无字底图，将文案转移到图外后期叠加。

### 4. STYLE ANCHOR — 推断风格

从语感/领域/受众推断统一视觉风格，并结合目标模型、优先目标和全局图内文字策略调整风格表达，输出结构化风格锚点摘要（色板、渲染风格、氛围、参考方向）。**提交用户确认**，用户可调整色板/渲染风格/氛围/参考方向或整体覆写。

```markdown
## Style Anchor

- 配色方案: ■ [中文名1] [角色] · ■ [中文名2] [角色] · ■ [中文名3] [角色]
- 渲染风格:   [当前风格]，可选：写实 · 矢量扁平 · 抽象拓扑 · 等轴测 · 水彩 · 线描 · ……(详见 references/type-strategies.md)
- 氛围基调: [关键词 2-4 个，如 简洁 · 技术感 · 深色 · 极简]
- 细节密度: [精致丰富 / 中等细节 / 极简留白]
- 风格参考: [类比或参考方向，如 深色仪表盘美学 / 复古科学教科书]
```

将结构化摘要呈现给用户，用户确认时，可逐项修改或整体覆写。风格锚点必须与 Target Model Anchor 和全局图内文字策略一致。配色方案默认可参考 `references/tag-quick-reference.md`；按配图类型的写法细节见 `references/type-strategies.md`。

### 5. PLANNING — 规划配图

基于综合优先级驱动，输出配图规划（位置、数量、每张的配图类型），每张图自动生成 diagram-slug，并为每张图建立 信息溯源表。**提交用户确认**，用户可增删位置、调整类型、修改 slug、重新排序，也可覆盖单图的图内文字策略。

```
建议配图 4 张：

  #1 [concept-intro]         第 2 段 · 概念引入    概念示意图
  #2 [system-architecture]   第 4 节 · 架构说明    架构图
  #3 [comparison-table]      第 5 节 · 方案对比    信息图
  #4 [flow-process]          第 7 节 · 流程步骤    流程图
```

每张图自动生成 diagram-slug（简短英语 kebab-case 标题）。

每张图规划时都要附带最小 信息溯源表：

```markdown
- 原文位置: [原文位置]
- 原文依据: [只写原文直接陈述的事实]
- 合理推导: [允许做的轻量推断]
- 视觉转化方案: [抽象概念对应的视觉隐喻]
- 禁止添加: [不得擅自加入的元素]
- 图内文字策略: [继承全局 / 单图覆写]
```

如果某张图需要把抽象概念翻译为视觉主意象，优先参考 `references/metaphor-guide.md` 选择隐喻，再写入 `视觉转化方案` 字段。

用户可在此阶段：
- 增删配图位置
- 调整配图类型
- 修改 diagram-slug
- 重新排序
- 覆写单图的图内文字策略

#### Visual Glossary（元素词典）

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

#### Visual Role → Prompt Strategy 映射

每张图的 Visual Role 决定 Prompt 的侧重方向：

| Visual Role | Prompt 策略 |
|-------------|------------|
| 帮助理解 | 标注/箭头/标签/图例清晰，结构优先于美感 |
| 装饰点缀 | 氛围优先，隐喻表达，>30% 负空间，不包含技术标注 |
| 数据对比 | 精确图形（柱/饼/折线），数值标注，色阶分类，图例 |
| 流程说明 | 时序布局（L→R / T→B），箭头连线，状态标注，多面板 |

#### 图内文字策略 → Prompt 策略

| 图内文字策略 | Prompt 策略 |
|-------------|------------|
| 无文字 | 明确排除标题、标签、段落文字、UI 文案 |
| 仅标签 | 只允许极少量结构标签，避免整句文案 |
| 仅数字 | 允许数值、百分比、坐标或序号，不允许长文本 |
| 必须精确文字 | 逐字引用所需文字，并在 Prompt 中强调 exact wording |
| 尽量无字 | 优先生成无字底图；如必须表达文案，建议转移到图外 |

### 6. GENERATE — 生成提示词

严格按以下流程和模板输出每张图的提示词文件。

文件路径：`docs/<diagram-slug>.prompt`

#### 模板

```markdown
## Context

- 所处位置: [文章中具体位置]
- 内容摘要: [该段落的核心内容摘要，为理解插图意图提供上下文]
- 配图类型: [概念示意图 / 架构图 / 流程图 / 信息图 / 装饰配图]
- 视觉角色: [帮助理解 / 装饰点缀 / 数据对比 / 流程说明]
- 目标模型: [Generic / GPT Image / Midjourney / Flux / SDXL / Ideogram / 其他]
- 图内文字策略: [无文字 / 仅标签 / 仅数字 / 必须精确文字 / 尽量无字]

## Style Anchor

- 配色方案: [#hex1 角色 · #hex2 角色 · #hex3 角色]
- 渲染风格: [渲染风格]
- 氛围基调: [氛围关键词 2-4 个]
- 细节密度: [精致丰富 / 中等细节 / 极简留白]
- 风格参考: [参考方向]

## Prompt

[自然语言段落。第一句祈使句总述场景。随后依次：Primary 实体（形状、#hex、状态）→ Secondary 实体+差异 → 关系/连接 → 空间布局/视角 → 光照/氛围 → No... 排除项 → Aspect ratio... 格式]
```

#### Type-specific Prompt Strategies

按配图类型选择对应的 Prompt 策略。各类型的详细策略表见 `references/type-strategies.md`。

#### 生成流程

1. **构建内部追踪数据**（不输出，用于校验）

   为每张图整理：

   ```
    实体表: 所有实体、数量、色值 hex、形状、渲染特征、角色(primary/secondary)
    关系图: 实体间连接方式、方向、线型
    色板:   该图涉及的所有 hex 值
    Grounding: 原文位置 · 原文依据 · 合理推导 · 视觉转化方案 · 禁止添加
    文字策略: 图内文字策略 · exact wording（如有）
    决策:   target model · 优先目标 · 布局类型 · 视角 · 排版 · 光照 · 氛围 · 格式
   ```

   元数据填写完整后才进入下一步。

2. **按写作规则撰写** — 将追踪数据自然融入段落

3. **语义扫描校验** — 对照 Quality Checks 逐项扫描。不通过则重写

#### 写作规则

##### 句子结构

- 第一句以祈使句总述场景（`Create a...` / `Show a...` / `Illustrate a...`）
- Primary 实体先出场，描述最详细（形状、色值 `#hex`、大小、发光状态）
- Secondary 实体紧随其后，用 `while`、`in contrast to` 等标识与 Primary 的差异
- 关系/连接用动作动词表达（`radiate outward from`、`connect through`、`flow from...to`）
- 布局、视角、透视自然融入空间描述，不单独成句列表
- 光照作为段落过渡自然插入
- 排除项以 `No...` 否定句收尾
- 格式以收束句指定（`Aspect ratio...`）

##### 数值精确

- 实体数量用精确英文数字：`a single`、`four`、`three of them`
- 颜色值使用 hex 格式精确指定：`#FF6B35`
- 所有 hex 必须来自内部追踪色板，禁止同义改写（不允许用 `amber` 代替 `#FF6B35`）

##### 长度与语言

- 长度自由，根据概念密度和理解增益自定：高密度节点使用更多实体描述、空间层次和光照过渡；低密度节点保持简洁，避免无关细节
- Write in English
- 使用自然连贯的段落，不分割为列表或要点

##### 真实性约束

- Prompt 中的视觉元素必须能回溯到 信息溯源表：属于原文依据、合理推导或视觉转化方案三者之一
- `禁止添加` 中列出的元素禁止出现在 Prompt 中
- 当目标模型已指定时，优先使用该模型更稳定理解的表述方式，但不得牺牲语义准确性
- 当图内文字策略不是 `必须精确文字` 时，避免在 Prompt 中要求大段可读文本

#### 产出语义

最终输出应该是 `## Prompt` 下方的一个完整自然语言段落，不加额外说明或包装。用户只复制 `## Prompt` 下面这一段即可。

#### 概念→视觉隐喻指南

抽象概念的隐喻选择、grounding 风险和类型限制见 `references/metaphor-guide.md`；此处不重复展开。

#### 输出示例

```
# docs/raft-leader-election.prompt

## Context

- 所处位置: 第 3 节 · 第 2 段
- 内容摘要: Candidate 发起选举，RequestVote RPC 广播到所有 Peer，收到多数派确认后成为 Leader
- 配图类型: 概念示意图
- 视觉角色: 帮助读者理解 Raft Leader Election 的核心消息流程
- 目标模型: Generic
- 图内文字策略: 无文字

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

### 7. OUTPUT — 写出文件

每张图输出到 `docs/<diagram-slug>.prompt`。

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

### Source Grounding
- [ ] Prompt 中的关键视觉元素可回溯到 信息溯源表
- [ ] 原文依据、合理推导、视觉转化方案 三者未混淆
- [ ] `禁止添加` 中的元素未出现在 Prompt 中

### 模型与图内文字策略
- [ ] Prompt 写法与目标模型相匹配，未依赖未声明的模型特性
- [ ] 图内文字策略已落实：无字、少量标签、仅数字或精确文字要求一致
- [ ] 当要求精确文字但目标模型排字能力弱时，已优先建议无字底图方案

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
- ❌ 只因概念密度高就强行配图，忽略理解增益、叙事重要性和视觉可译性
- ❌ 没有 原文位置 和 grounding 约束，直接凭印象脑补视觉元素
- ❌ 未声明图内文字策略，却在 Prompt 中要求标题、长段文字或大量标签
