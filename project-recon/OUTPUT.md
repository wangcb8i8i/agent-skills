# Recon Map 产出规范

> 被 [project-recon](SKILL.md) 引用的披露参考。Recon Map 核心是写给项目新读者看的——让一个人能在最短时间内抓住关键信息。只在你需要写文件或检查格式时查阅本节。

## 读者导航

Recon Map 按阅读优先级组织。建议阅读顺序：

1. **RECON.md — Overview + Module Coverage 表**：项目全貌、解决什么问题、技术栈、模块划分
2. **user-journeys.md**：用户怎么用这个系统，每步涉及哪些模块（→ modules/{m}.md 查看模块职责与 Flow）
3. **glossary.md**：项目专用术语——看不懂领域名词时查阅
4. **选一个最关心的模块，读其 Flow 节**：主功能走通，入口到出口
5. **architecture.md**：模块间关系和核心抽象（聚焦"改哪里影响谁"时读）
6. **dev-loop.md**：搭建环境时查阅

每份文件独立可读——不需要从头到尾读完。

每份产出文件末尾写入一段固定格式的「下一步」导航，降低读者在文件间的跳转成本：

```markdown
---
→ 下一步：{一句指引，说明读完这份后看什么最划算}
```
- RECON.md 尾部：`→ 下一步：制作用户怎么用这个系统？读 user-journeys.md；看不懂领域名词？查 glossary.md`
- user-journeys.md 尾部：`→ 下一步：挑一个出现在最多步骤中的模块，读 modules/{m}.md 的 Flow 节`
- glossary.md 尾部：`→ 下一步：回 RECON.md 的 Overview 看整体定位；或读 user-journeys.md 看用户怎么与这些术语互动`
- modules/{m}.md 尾部：`→ 下一步：想看模块间的依赖关系？读 architecture.md；想深入该模块设计？读 Deep 节`
- architecture.md 尾部：`→ 下一步：想搭建开发环境？读 dev-loop.md；想深入某个模块？读 modules/{m}.md`
- dev-loop.md 尾部：`→ 下一步：回 RECON.md 选一个模块开始探索，从 modules/{m}.md 的 Flow 节入手`
- design-decisions.md 尾部：`→ 下一步：回头看对应模块的 Deep 节理解上下文 → modules/{m}.md`
- entry-points.md 尾部：`→ 下一步：想了解这些入口如何协同完成用户目标？读 user-journeys.md`

## 文件结构

目标项目根目录下 **`.recon/`** 子目录，集中存放所有产出物：

```
{目标项目}/
└── .recon/
    ├── RECON.md                 ← Overview + 覆盖状态表（唯一索引）
    ├── glossary.md              ← 项目专用术语
    ├── architecture.md          ← 模块依赖图（含外部系统）+ 核心抽象 + 数据模型
    ├── user-journeys.md         ← 用户旅程（每步标注涉及模块）
    ├── entry-points.md          ← 运行时入口清单（main、CLI、路由注册、导出API）+ 运行时配置
    ├── dev-loop.md              ← 构建/测试/lint/CI 命令与环境搭建
    ├── design-decisions.md      ← 设计决策（跨模块统一归档，深入了解模块时产出）
    └── modules/                 ← 模块专属文件（Step 3 创建骨架，Step 4/6 增补）
        ├── core.md              ← 职责/上下游 + Flow 节 + Deep 节
        ├── auth.md
        ├── payment.md
        └── {subsystem}/         ← 大型项目：按子系统分组
            └── {module}.md
```

不写 `.gitignore`——Recon Map 默认进入版本控制，可被团队共享和审查。如果决定后续排除，一行 `.recon/` 到 `.gitignore` 即可。

## user-journeys.md 格式

```markdown
# User Journeys: {project-name}

## Personas
- {persona}: {description}

## Journey: {name}

### User Steps
| 步骤 | 用户动作 | 涉及模块（→ modules/{m}.md Flow 节，architecture.md 次级） |
|------|---------|------------------------------|
| Step1 | init    | [core/]                      |
| Step2 | add src | [scanner/], [db/]            |
| Step3 | query   | [api/], [db/], [view/]       |

Steps: Step1 → Step2 → Step3 → done

### Prerequisites
- Step2 依赖 Step1 完成
```

（首次侦察时产出。后续用户指向具体模块时按需补充 Flow 节。）

每个模块一个 `.recon/modules/{module}.md`，按节（section）递进：

```markdown
# {module}

**职责**：这个模块做什么的、解决什么问题。
**上下游**：上游依赖谁的产出 → [本模块] → 下游谁依赖本模块的产出。

## Flow（按需）

Flow 节整体按需——模块可能没有此节（评估后标记 `○` 即可）。两个子节各自按需——没有数据旅程或代码轨迹的模块不写该子节。

### 数据旅程
（仅在模块有输入输出形态变化或副作用时写）
输入：{输入形态}
处理：{关键处理逻辑}
输出：{输出形态}
输出送入：→ [{下游模块}]

### 代码轨迹
（仅在模块有可追踪的执行路径时写）
{文件}::{函数} → {文件}::{函数} → {文件}::{函数}

（Flow 节：用户指向具体模块时按需创建或更新）

## Deep

内部抽象、错误处理路径、设计 tradeoffs、Open Questions。
末尾加 `→ design-decisions.md#{module}` 反向指针（design-decisions 条目以模块名二级标题归档，使锚点可用）。
（用户要求深入了解指定模块时创建或更新）
```

## 模块拆分

文件内容与文件标题的抽象层次一致。当 Flow 或 Deep 偏离了标题的抽象层（描述"模块内的某个东西"而非"模块本身"），迁到子文件 `modules/{模块}/{子实体}.md`。

拆分不靠行数或实体数量，靠内容与标题的抽象层是否对齐。

## RECON.md 格式

```markdown
# Recon Map: {project-name}
Generated: {date} | HEAD: {commit}

## Overview

- **定位**：{一句话——项目是什么 + 技术栈}
- **问题域**：{这个项目解决用户的什么问题——谁在什么场景下用它来干什么}
- **模块地图**：{module} → 一句话职责（→ modules/{m}.md）；…
- **关键架构决策**：{最值得注意的设计选择，不是全部}
- **快速开始**：{想跑起来做什么 → dev-loop.md}
- **推荐入口**：如果想理解架构，读 {产出/章节}；如果想动手改代码，读 {产出/章节}

## Module Coverage

| Module | 1.Perim | 2.Entry | 3.Arch | 4.Journey | 5.DevLoop | 6.Deep | Last Visit |
|--------|---------|---------|--------|--------|-----------|--------|------------|
| core/  | ✓       | ✓       | ✓      | ✓      | -         | ✓      | 2026-06-27 |
| auth/  | ✓       | ✓       | ✓      | ✓      | -         | -      | 2026-06-27 |
| payment/ | ✓     | ✓       | ✓      | -      | -         | -      | 2026-06-26 |

### 字段规则

**Module**：以代码目录/模块为粒度。一个模块一次覆盖整块代码。

**里程碑（1-6）**：`✓` = 完成该步骤且有内容；`○` = 已评估，无需写（如该模块没有数据旅程或代码轨迹）；`-` = 未完成。Agent 用 `-` 来判断尚未覆盖的工作。

> **4.Journey 列**：`✓` = 已写 Flow 节；`○` = 评估后该模块无需 Flow（无数据旅程或代码轨迹）；`-` = 未评估。读者据符号即可判断，无需追到 `modules/{module}.md` 确认。

**Last Visit**：最后一次 revisit 的日期。超过 30 天且有最新 commit 变化则建议 revisit。

**子表**：大模块可展开为子表——主表该行标记 `→`，子表在同一文件下面另起一节。

```
| core/ | ✓ | ✓ | ✓ | → | - | ✓ | ← 标记 → 表示展开 |
|   skeleton | ✓ | ✓ | ✓ | ✓ | - | ✓ | ← 缩进表示子模块 |
|   adaptation | ✓ | ✓ | ✓ | ✓ | - | ✓ |
```
