---
name: illustration-prompt
description: 根据文档或对话上下文，自动判断配图位置、推断视觉风格、生成可直接喂给 DALL·E 的完整提示词。每张配图输出一个 `.prompt` 文件。需用户明确要求才触发，不会自动启动。触发词：#illustration
---

# Illustration Prompt Generator

根据文档或上下文，创建"可直接喂给LLM用于生成配图/插图的提示词"

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
| 内联插图 | 按概念密度在各段落间分配 | 标准模板，SEPARABILITY 必填 |
| 封面图 | 仅 1 张，抽取最高概念密度的核心意象 | 装饰配图策略，≥30% 负空间，无标注 |
| 轮廓图 | 1 张，全局结构映射 | 信息图/架构图策略，必含 ANNOTATIONS |
| 社交卡片 | 1 张，16:9 固定，强调标题 + 视觉冲击 | 装饰配图策略，FORMAT 固定 16:9 |
| 演示配图 | 按章节或关键节点分配，每张自包含 | 文字极少，视觉优先，MOTION 鼓励动态感 |

### 4. STYLE ANCHOR — 推断风格

从语感/领域/受众推断统一视觉风格，输出结构化风格锚点摘要（色板、渲染风格、氛围、参考方向）。**提交用户确认**，用户可调整色板/渲染风格/氛围/参考方向或整体覆写。

### 5. PLANNING — 规划配图

基于概念密度驱动，输出配图规划（位置、数量、每张的配图类型），每张图自动生成 diagram-slug。**提交用户确认**，用户可增删位置、调整类型、修改 slug、重新排序。

### 6. GENERATE — 生成提示词

严格按模板逐张生成。每张输出三个区块：
- Context（位置、摘要、类型——供审阅）
- Style Anchor（风格决策记录——供审阅）
- Prompt（完整提示词——唯一需要复制的内容）

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

严格按以下模板输出每张图的提示词文件。

文件路径：`docs/<diagram-slug>.prompt`

### 模板

```markdown
## Context

- 所处位置:    [文章中具体位置]
- 内容摘要:     [该段落的核心内容摘要，为理解插图意图提供上下文]
- 配图类型:        [概念示意图 / 架构图 / 流程图 / 信息图 / 装饰配图]
- 视觉角色: [这张图在文章中扮演什么角色：帮助理解/装饰点缀/数据对比/流程说明]

## Style Anchor

- 配色方案:     [主色调 · 辅色调 · 背景色]
- 渲染风格:   [渲染风格]
- 氛围基调:        [氛围关键词]
- 细节密度:     [细节密度]
- 风格参考:   [参考方向]

## Prompt

[SUBJECT]
Scene: <祈使句完整体>

| Role | Entity | Qty | State | Anchor |
|------|--------|-----|-------|--------|
| primary | <实体名> | <精确数量> | <画面状态> | 原文: <术语> |
| secondary | ... | ... | ... | ... |

[Relation]
[<Entity>] —<动作, 方式>→ [<Entity>]

[COMPOSITION]
...布局类型 · 视角 · 排列原则 · 引导线方向 · 画面分层（→分隔）...

[COLOR PALETTE]
...角色: hex — 占比或用途 · 角色: hex — 占比或用途 · BG: hex...

[LIGHTING]
...光源类型 · 方向 · 对比度 · 阴影策略 · 自发光元素列表...

[ATMOSPHERE]
...氛围关键词 2-4 个 · 情绪 1-2 个 · 密度等级...

[PROPORTIONS]
...主体区域占比 · 负空间方位及占比 · 元素相对大小比...

[条件维度：按 Visual Type-Dimension 矩阵启用]

[VIEWPOINT]
...俯仰角 · 方位角 · 距离 · 畸变...

[SCALE & DEPTH]
...层级数 · 前→中→后层内容 · 景深效果...

[TEXTURE]
...材质列表 · 渲染风格...

[MOTION]
...动势方向 · 速度感 · 静态元素...

[FOCUS]
...主焦点位置 · 权重分配 · 引导元素...

[ANNOTATIONS]
...标签类型 · 标注线 · 图例...

[SEPARABILITY]
...间距规则 · 标签位置 · 连接线路由...

[EXCLUSIONS]
...排除元素清单...

[FORMAT]
...横纵比 · 分辨率...
```

### Type-specific Prompt Strategies

按配图类型选择对应的 Prompt 策略。各类型的详细策略表见 `references/type-strategies.md`。

### Prompt 块写作规则

Write in English. Prompt 块由**标记词 tag** 组织为结构化段落，每个 tag 独立一行，首行以 `[TAG_NAME]` 开头。Tags 按固定顺序排列，条件 tag 仅在启用时出现（参见 Visual Type-Dimension 矩阵）。

#### Tag 定义

| Tag | Required | 规范 |
|-----|----------|------|
| `[SUBJECT]` | **必填** | 三段式结构：① `Scene:` 祈使句总述 → ② Entity Table → ③ Relation Graph。Entity Table 列：`Role / Entity / Qty / State / Anchor`。Relation Graph 格式：`[Entity] —<动作, 方式>→ [Entity]`。实体 ≥ 2 时 Entity Table 必填，实体间有交互时 Relation Graph 必填。Entity 名称与 Visual Glossary 严格一致。 |
| `[COMPOSITION]` | **必填** | 必须声明：布局类型（水平/垂直/径向/网格/自由）、视角（俯视/平视/仰视/等轴测/特写）、排列原则（对称/黄金分割/三分法/居中/不对称）、引导线方向。如有画面分层，用 `→` 分隔。例：`horizontal L→R layout, isometric 3/4 view, asymmetric with focal point at left-third, foreground: nodes → midground: lines → background: gradient` |
| `[COLOR PALETTE]` | **必填** | 格式：`<角色描述>: <hex> — <占比或用途>`，多条用 `·` 分隔。所有 hex 值与 Style Anchor Palette 严格一致，禁止同义改写（如 "amber" 替换 "#FF6B35"）。例：`Primary nodes: #00D4FF at 40% · Accent arrows: #FF6B35 — directional flow · BG: #1A1A2E` |
| `[LIGHTING]` | **必填** | 必须声明：光源类型（自然光/自发光/环境光/边缘光/体积光）+ 方位（top-down / side / backlit / rim）+ 对比度（高/中/低）+ 阴影策略（硬阴影/软阴影/无阴影）。自发光元素需单独列出。例：`self-illuminated nodes as primary source, dark ambient backlight, high contrast, soft drop shadows on containers, no hard rim light` |
| `[ATMOSPHERE]` | **必填** | 格式：氛围关键词 2-4 个 · 情绪关键词 1-2 个 · 密度等级（精致丰富/中等细节/极简留白）。三者缺一不可。例：`precise · minimal · technical · analytical · mood: neutral and systematic · density: moderate detail, no visual noise` |
| `[PROPORTIONS]` | **必填** | 格式：`主体 <区域> <百分比> · 负空间 <方位> <百分比> · 主元素:次元素 大小比 <x:y>`。例：`central 60% active content · right-edge 15% negative space · primary:secondary element size ratio 3:1` |
| `[VIEWPOINT]` | 条件必填 | 架构图/流程图/信息图必须启用。格式：`<角度>° elevation · <角度>° azimuth · <景别> · <畸变>`。例：`30° elevation, 315° azimuth, medium shot, orthographic projection, no distortion` |
| `[SCALE & DEPTH]` | 条件必填 | 画面含 3+ 深度层次时必填。格式：`<层级数> layers: foreground: <内容> → midground: <内容> → background: <内容> · depth effect: <浅景深/全景深/渐变焦>` |
| `[TEXTURE]` | 条件必填 | 非"矢量扁平"渲染风格时必填。格式：`材质 1 · 材质 2 · ... · rendering base: <矢量扁平/水彩/线描/等轴测/抽象拓扑>` |
| `[MOTION]` | 条件必填 | 流程图/数据流/动态对比图必填。格式：`flow direction: <L→R/T→B/radial> · speed: <静止/有方向动势/动态模糊> · static elements: <列表>` |
| `[FOCUS]` | 条件必填 | 信息密度高或有 3+ 视觉焦点时必填。格式：`primary focal point: <位置, 属性> · weight: <主% / 次%> · guiding elements: <列表>` |
| `[ANNOTATIONS]` | 条件必填 | 信息图/架构图必填。格式：`text labels: <yes/no> · style: <sans-serif/serif> · leader lines: <实线/虚线/无> · legend: <yes/no> · hierarchy: <n levels>` |
| `[SEPARABILITY]` | **必填** | 装饰配图除外。规定元素间距、标签位置、连接线路由，防止重叠遮挡。格式：`<规则1> · <规则2> · <规则3>`，至少 3 条。例：`semantic elements separated with visible whitespace · text labels placed outside visual elements · lines and arrows routed around shapes without crossing through them` |
| `[EXCLUSIONS]` | **必填** | 明确列出不应出现的元素，以 `no` 开头，逗号分隔。≥2 个排除项。例：`no human figures, no realistic textures, no UI chrome, no logos`。信息图/架构图如需标签则删除 `no text labels`。 |
| `[FORMAT]` | **必填** | 自然语言描述横纵比 + 分辨率。**禁止**使用 Midjourney 风格参数（`--ar`、`--v`、`--s`、`--style` 等）。例：`16:9 wide landscape format, high resolution` |

> 完整 Tag 速查表（必填类型、段内顺序、最小内容示例）见 `references/tag-quick-reference.md`。

#### Tag 顺序规则

必须按上表顺序排列：SUBJECT / COMPOSITION / COLOR PALETTE / LIGHTING / ATMOSPHERE / PROPORTIONS → Conditional（VIEWPOINT / SCALE & DEPTH / TEXTURE / MOTION / FOCUS / ANNOTATIONS）→ SEPARABILITY → EXCLUSIONS → FORMAT。SEPARABILITY 在装饰配图时删除，其余类型必填。Conditional tag 若不适用则整行删除，不保留空标记。必填标签合计：非装饰配图 9 个，装饰配图 8 个。

#### 维度内部顺序规则

以下 tag 的内容有严格的段内顺序，不得随意排列：

| Tag | 段内顺序 |
|-----|---------|
| SUBJECT | ① Scene 祈使句 → ② Entity Table（Role / Entity / Qty / State / Anchor）→ ③ Relation Graph |
| COMPOSITION | ① 布局类型 → ② 视角 → ③ 排列原则 → ④ 引导线 → ⑤ 分层（→ 分隔）|
| COLOR PALETTE | ① 主色 → ② 辅色 → ③ 强调色 → ④ 背景色 |
| LIGHTING | ① 光源类型 → ② 方位 → ③ 对比度 → ④ 阴影策略 → ⑤ 自发光元素 |
| ANNOTATIONS | ① 文字标签类型 → ② 标注线 → ③ 图例 → ④ 字号层级 |

#### 语言规范

| 维度 | 规则 |
|------|------|
| 语气 | 祈使句优先（`Create a detailed visualization of...` / `Show...` / `Illustrate...`）|
| tag 内长度 | 每个 tag 1-3 行，不应跨 2+ 段落。FORMAT 限 1 行。 |
| 总长度 | 不含 tag 名称的正文部分 150-300 词。Required 8 个 tag 约 100-150 词，条件 tag 按需叠加。 |
| 质量词 | 使用 `ultra-detailed`、`highly detailed`、`sharp focus`（❌ `8K`、`photorealistic` 对 DALL·E 无效）|
| 排除项 | 必须通过 `[EXCLUSIONS]` tag 显式声明，禁止在非 EXCLUSIONS tag 中写排除描述 |
| 一致性 | 多张图共用视觉词典（见 Visual Glossary），相同概念复用相同视觉描述。禁止同义改写。 |
| 禁止重复 | 同一信息不得在两个 tag 中重复描述。如 COMPOSITION 已声明视角，VIEWPOINT 中不允许再写角度。 |

#### Type-Dimension 映射矩阵

决定 Conditional tags 的启用：

| 类型 | Required tags | 强制启用 | 按需启用 |
|------|---------------|---------|---------|
| 概念示意图 | 9 | VIEWPOINT, FOCUS | SCALE & DEPTH, TEXTURE |
| 架构图 | 9 | VIEWPOINT, ANNOTATIONS, MOTION | SCALE & DEPTH, TEXTURE |
| 流程图 | 9 | VIEWPOINT, MOTION, SCALE & DEPTH | FOCUS, ANNOTATIONS |
| 信息图 | 9 | VIEWPOINT, ANNOTATIONS, FOCUS | MOTION, SCALE & DEPTH |
| 装饰配图 | 8（PROPORTIONS 中负空间 ≥30%） | TEXTURE, FOCUS | — |

#### 产出语义

最终输出应该是 `## Prompt` 下方的一个完整 Prompt 块，不加额外说明或包装。用户只复制 `## Prompt` 下面这一段即可。

### 概念→视觉隐喻指南

抽象概念必须翻译为 DALL·E 可理解的视觉元素。常见领域的隐喻映射表见 `references/metaphor-guide.md`。

**使用规则**：优先匹配源文中出现的术语，选择最贴合的隐喻。避免强行套用——如果源文有自带的比喻（如 "think of it as a highway" ），优先使用原文比喻而非表内映射。

### 输出示例

```
# docs/raft-leader-election.prompt

## Context

- 所处位置:     第 3 节 · 第 2 段
- 内容摘要:      Candidate 发起选举，RequestVote RPC 广播到所有 Peer，收到多数派确认后成为 Leader
- 配图类型:         概念示意图
- 视觉角色:  帮助读者理解 Raft Leader Election 的核心消息流程

## Style Anchor

- 配色方案:     ■ 暖琥珀色 主色 · ■ 青色 辅色 · ■ 深蓝黑 背景色
- 渲染风格:   抽象拓扑，矢量扁平加微渐变，可选：写实 · 矢量扁平 · 抽象拓扑 · 等轴测 · 水彩 · 线描 · ……
- 氛围基调:        简洁 · 极简 · 技术感
- 细节密度:     中等细节，无视觉噪音
- 风格参考:   深色仪表盘美学，半透明自发光节点

## Prompt

[SUBJECT]
Scene: Create an abstract topology diagram of a Raft cluster leader election process.

| Role | Entity | Qty | State | Anchor |
|------|--------|-----|-------|--------|
| primary | Candidate node | 1 | 发起选举, self-illuminated, edge glow | 原文: Leader Election |
| secondary | Follower node | 4 | 3 已确认(acknowledged), 1 待回复 | 原文: RequestVote RPC |
| secondary | Consensus indicator | 3 | activated, green glow overlay | 原文: majority consensus |
| context | Network partition | 1 | dark isolation background, navy gradient | 原文: cluster |

[Relation]
[Candidate node] —<emit, dashed cyan #00D4FF arrows>→ [Follower node]
[Follower node: 3 of 4 acknowledged] —<display>→ [Consensus indicator: green glow]

[COMPOSITION]
Radial ring layout with nodes at slightly varying Z depths for depth effect, isometric 3/4 view, asymmetric composition with Candidate node slightly elevated above the ring plane, 20% negative space at outer edges.

[COLOR PALETTE]
Candidate: #FF6B35 self-illuminated · Follower: #00D4FF at 30% opacity translucent · Consensus glow: #00FF88 overlay · Background: #1A1A2E solid · Arrows: #00D4FF dashed at 60% opacity

[LIGHTING]
Self-illuminated Candidate node as primary light source, dark ambient backlight, high contrast between nodes and background, soft ambient glow on acknowledged Follower nodes, no hard shadows or rim light.

[ATMOSPHERE]
precise · minimal · technical · analytical · mood: neutral and systematic · density: moderate detail, no visual noise, clean negative space

[PROPORTIONS]
central 60% occupied by the ring · 20% negative space at edges · Candidate:Follower size ratio 1.3:1 for visual hierarchy

[VIEWPOINT]
30° elevation, 315° azimuth, medium shot framing the entire ring, orthographic projection without perspective distortion

[SCALE & DEPTH]
3 depth layers: foreground Candidate node · midground Follower ring at varying Z depths · background infinite navy gradient · depth effect: shallow focus with Candidate in sharpest detail

[TEXTURE]
Smooth semi-transparent glass for Follower nodes · self-illuminated core with subtle gradient falloff for Candidate · rendering base: vector flat with dimensional depth via opacity and gradient layers

[MOTION]
flow direction: radial out from Candidate to Followers via dashed arrow lines · speed: static but directional implied by arrowheads · static elements: all node positions and state indicators fixed

[FOCUS]
primary focal point: Candidate node center-elevated, highest luminance · secondary: acknowledged Follower nodes with green glow pull eye radially · guiding elements: dashed arrows radiate outward from center to periphery

[EXCLUSIONS]
no human figures, no realistic textures, no UI chrome, no logos, no visible text labels, no decorative elements

[FORMAT]
16:9 wide landscape format, high resolution
```

## Output 文件规范

- 每张图一个文件：`docs/<diagram-slug>.prompt`
- diagram-slug 由 Skill 自动生成，简短描述性英语 kebab-case
- 文件包含完整的 Context + Style Anchor + Prompt 三个区块

## Quality Checks

交付前验证：

### 结构完整性

- [ ] Prompt 块包含全部 required tag（SUBJECT / COMPOSITION / COLOR PALETTE / LIGHTING / ATMOSPHERE / PROPORTIONS / SEPARABILITY / EXCLUSIONS / FORMAT），其中 SEPARABILITY 在装饰配图时除外
- [ ] Conditional tags 的启用与 Type-Dimension 映射矩阵一致，无遗漏无多余
- [ ] Tag 顺序符合规范：SUBJECT / COMPOSITION / COLOR PALETTE / LIGHTING / ATMOSPHERE / PROPORTIONS → Conditional → SEPARABILITY → EXCLUSIONS → FORMAT
- [ ] 每个 tag 的内容在 1-3 行内，未跨 2+ 段落
- [ ] FORMAT tag 仅 1 行

### SUBJECT 专项

- [ ] SUBJECT 首行是 `Scene:` 祈使句完整体，非元素清单开头
- [ ] Entity Table 列完整（Role / Entity / Qty / State / Anchor 五列不缺）
- [ ] Role 列有且仅有一个 primary，不可多个或缺失
- [ ] Qty 使用精确数字或 `x of y` 格式，不含模糊词（many / several / some）
- [ ] Anchor 列包含 ≥1 个原文具体术语引用
- [ ] Entity 名称与 Visual Glossary 严格一致
- [ ] Relation Graph 中所有 `[Entity]` 引用与 Entity Table 中的 Entity 列一字不差
- [ ] 实体 ≥ 2 时 Entity Table 非空，缺则报错
- [ ] 实体间有交互关系时 Relation Graph 非空，缺则报错
- [ ] 实体 = 1 且无状态变化时允许退化省略 Entity Table

### SEPARABILITY 专项

- [ ] 装饰配图以外的类型均包含 SEPARABILITY tag
- [ ] SEPARABILITY 包含 ≥3 条分离规则
- [ ] 规则覆盖：元素间距、标签位置、连接线路由（或对应类型的关键分离维度）
- [ ] 规则可执行（非抽象描述，有具体方位或动作指令）
- [ ] 不与 COMPOSITION 中的分层声明矛盾

### 内容正确性

- [ ] COLOR PALETTE 中所有 hex 值与 Style Anchor Palette 严格一致，无同义改写
- [ ] Visual Glossary 中的概念在所有 Prompt 中复用相同视觉描述
- [ ] Prompt 中 ≥2 个关键元素直接来自原文具体术语/数据（原文锚定）
- [ ] 插图情感基调（Vibe）匹配文章语气（严肃/轻松/正式/亲切）
- [ ] 概念密度高的位置在 Prompt 中有相应的细节层级（高密→多细节层）

### 格式合规

- [ ] 不含 Midjourney 专用参数（`--ar`、`--v`、`--s`、`--style` 等）
- [ ] EXCLUSIONS 列出 ≥2 个排除项
- [ ] PROPORTIONS 声明了主体占比和负空间占比
- [ ] 装饰配图的 PROPORTIONS 中负空间 ≥30%

### 上下文一致性

- [ ] 每张图的 Visual Role 清晰，与文章段落匹配
- [ ] diagram-slug 简短且描述准确
- [ ] Context 中的 Position/Summary 正确反映原文内容
- [ ] 如果有指定配图数量，与实际输出数量一致

## Anti-Patterns

- ❌ Prompt 块包含说明文字（如"你可以这样使用"、"以下是提示词"）—— 只有提示词本身
- ❌ Prompt 块用中文写（DALL·E 对英文提示词理解更好）
- ❌ Prompt 块包含 Midjourney 风格参数（`--ar`、`--v`、`--s`、`--style` 等）—— DALL·E 不识别，会导致 AI 回复对话而非直接出图
- ❌ 风格锚点前后矛盾（如色板写 dark mode 但提示词要求白色背景）
- ❌ diagram-slug 使用中文或过长
- ❌ 输出多张图时全部塞到一个文件里（每张图独立文件）
- ❌ 不经过风格确认直接生成提示词
- ❌ Tag 顺序错乱（如 EXCLUSIONS 放在 SUBJECT 之前）
- ❌ SUBJECT 首句以元素清单开头而非祈使句（如 `[SUBJECT] A warm amber node...` ❌）
- ❌ Conditional tag 在不应启用的类型中出现（如装饰配图使用 VIEWPOINT + ANNOTATIONS）
- ❌ COLOR PALETTE 使用颜色名称而非 hex 值（如使用 "amber" 而非 "#FF6B35"）
- ❌ SUBJECT Entity Table 的 Entity 列名称与 Visual Glossary 不一致
- ❌ SUBJECT Relation Graph 中 `[Entity]` 引用了 Entity Table 中不存在的名称
