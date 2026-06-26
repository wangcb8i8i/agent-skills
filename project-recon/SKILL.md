---
name: project-recon
description: 快速侦察（recon）陌生项目——系统化了解、掌握项目工程。当用户说"上手这个项目""看看这个项目""快速了解熟悉""recon""侦察""我应该读什么""怎么快速开始"时使用。同时也是其他 skill 在需要项目上下文时的调用入口。
---

# project-recon

对陌生项目做系统化**侦察**——目标不是"读代码"，而是持续产出一份可分享的 **Recon Map**。

核心假设：你不知道那里有什么。每次侦察都从外围到核心逐层推进，每层有明确完成标准阻止过早宣称"懂了"。

> Bold terms → 见 [GLOSSARY.md](GLOSSARY.md)

## 入口判断

调用时先做**三叉判断**，决定走哪条 Branch：

```
用户说"看看这个项目"/第一次 → Full
用户说"看看其他模块"        → onCover
用户说"深入看下 X 模块"    → onDig
用户说"再看下 X 模块"      → onRevisit
无明确信号，项目已有 RECON.md → onCover
无明确信号，没有 RECON.md    → Full
```

`onDig` 和 `onRevisit` 的区别：depth < 3 是 onDig（深入新领域），depth ≥ 3 是 onRevisit（重新建立已遗忘的心智模型）。

## Branches

### Full — 首次全流程侦察

按 1→6 的顺序执行所有步骤，产出 Recon Map。

### onCover — 补漏未覆盖模块

1. 读 RECON.md，找 Step1-6 有任何 `-`（未完成）的模块
2. 如果全部 `✓` → 告知用户所有模块已覆盖，建议用 `onDig` 或 `onRevisit`
3. 如果有未完成模块 → 对每个 X 走对应步骤（通常是 Step 4 Flow），完成后更新里程碑

### onDig — 深入指定模块

1. 读 RECON.md 确认目标模块
2. 如果 depth ≥ 3 → 告知用户这个模块已深度覆盖，建议用 `onRevisit` 如果遗忘了
3. 执行 Step 6（Deep Recon）于该模块
4. 更新 RECON.md + 产出对应的 `.recon/` 文件

### onRevisit — 复盘指定模块

1. 读 RECON.md 中该模块的现有记录（作为钩子）
2. 读完之后**必须回到代码重新执行 Step 4 + 6**，不允许直接从 RECON.md 复述
3. 更新模块的 `Last Visit` 时间

## 汇报规则

**问题：** Agent 埋头做侦察写文件，但对话输出的内容很少——用户感觉在围观一个静默运转的黑箱。

**规则——每步都要在对话中给反馈，而不是只写文件：**

| 时机 | 汇报什么 | 长度 |
|------|---------|------|
| 每步完成时 | 该步的 2-3 句关键发现（不是完整内容，是"你该知道什么"） | 2-3 句 |
| Full 分支结束时 | 项目的"电梯演讲"——一句话概述 + 技术栈 + 架构风格 + 值得注意的设计决策 | 一段话 |
| onCover 结束时 | 这次补漏了哪些模块 + 一句总结每块的核心职责 | 每个模块 1-2 句 |
| onDig / onRevisit 结束时 | 该模块的内部设计一句话概括 + 关键 tradeoff + 是否有令人意外的东西 | 3-5 句 |

**不要做：**
- 不要 dump `.recon/` 文件内容到对话中（文件就是为了存完整内容才存在的）
- 不要只说"已完成"或"已写入 .recon/glossary.md"——说发现了什么
- 不要等全部 6 步跑完才开口——每步完成时都应该告知

**目的：** 让对话输出成为 **"我知道了你该知道什么"** 的指引，而不是"文件已生成"的通知。用户读完汇报后，对这个项目已经有方向感；细节去 `.recon/` 里找。

## 六大步

### 1. Perimeter — 外围侦察

| 动作 | 具体内容 |
|------|---------|
| 读 | README, CONTRIBUTING, CHANGELOG, LICENSE |
| 读 | 项目元数据 (package.json, Cargo.toml, pyproject.toml, go.mod 等) |
| 扫 | 目录树 2 层深（`tree -L 2` 或等价操作） |
| 录 | 项目专用术语，写入 `.recon/glossary.md` |

**完成标准**：能回答——项目做什么？什么语言/框架？构建系统？每个顶层目录一句话职责？项目独有的术语列出并解释了。

**陷阱**：README 可能过时。交叉验证 README 说的 vs 代码实际暴露的。

### 2. Entry — 入口侦察

| 动作 | 具体内容 |
|------|---------|
| 找 | main 函数、CLI 入口、HTTP 路由注册、导出 API |
| 找 | CI 配置（.github/workflows, .gitlab-ci.yml）——它告诉你哪些入口是"生产重要"的 |
| 列 | 所有入口点的清单，写入 `.recon/entry-points.md` |

**完成标准**：能列出所有入口点，知道启动流程中最先执行的是什么。

### 3. Architecture — 架构侦察

| 动作 | 具体内容 |
|------|---------|
| 给 | 每个目录/模块贴上"职责标签" |
| 画 | 模块间的依赖方向，写入 `.recon/architecture.md`（Mermaid 或 ASCII） |
| 找 | 核心抽象——traits、interfaces、abstract base classes、核心数据结构 |
| 量 | 文件数、模块规模分布 |

**完成标准**：能绘制模块依赖图，说出每个模块的单一职责，知道"如果改 X 会影响到谁"。核心抽象有清单。

### 4. Flow — 数据流侦察

**最重要的步骤。** 选一个主要功能，**从入口到出口完整追踪**，产出到 `.recon/flow-{module}.md`。

| 动作 | 具体内容 |
|------|---------|
| 选 | 最简单的 primary feature（不是错误处理路径） |
| 跟 | 从用户输入/HTTP 请求/CLI 参数到最终输出/数据库写入 |
| 记 | 沿途经过的每一层、每个文件、每个关键函数 |

**完成标准**：能精确说出完整路径——"用户发 POST /api/orders → router → OrderController.create → OrderService.place → PaymentGateway.charge → OrderRepository.save"，每个跳转精确到 `文件名::函数名`。

**如果 Agent 只能说出"用户发请求，然后数据被处理，然后保存到数据库"——不达标。** 必须精确到文件名和函数名。

### 5. Dev Loop — 开发回路侦察

| 动作 | 具体内容 |
|------|---------|
| 找 | 构建设置、测试框架、lint 配置 |
| 录 | 写入 `.recon/dev-loop.md` |
| 验 | 确认已知构建+测试+lint 命令（不一定要跑，除非用户要求） |

**完成标准**：能列出从 clean checkout 到跑通测试的全部命令序列。

### 6. Deep — 纵深侦察

只在指定模块上执行（`onDig` / `onRevisit`）：

| 动作 | 具体内容 |
|------|---------|
| 读 | 该模块的所有核心文件（不是全部，是核心） |
| 找 | 隐藏抽象——继承链、trait bounds、依赖注入 |
| 看 | 错误处理路径（不只 happy path） |
| 问 | 为什么这么设计——记录到 `.recon/design-decisions.md` |

**完成标准**：能解释模块的内部设计、关键 tradeoffs、和"为什么这么设计"（真正的动机，不是事后编的）。同时更新术语表 `.recon/glossary.md`。

## Recon Map

技能的核心产出。既是 Agent 的**状态数据库**，也是你的**回忆索引**。

### 文件结构

目标项目根目录下 **`.recon/`** 子目录，集中存放所有产出物：

```
{目标项目}/
└── .recon/
    ├── RECON.md                 ← 打开即见覆盖状态 + 快速跳转
    ├── glossary.md              ← 项目专用术语
    ├── architecture.md          ← 模块依赖图 + 核心抽象
    ├── entry-points.md          ← 入口点清单
    ├── dev-loop.md              ← 构建/测试/调试命令
    ├── design-decisions.md      ← 设计决策 + tradeoffs + Open Questions
    └── flow-{module}.md         ← 每个 traced 模块一条 flow trace
```

不写 `.gitignore`——Recon Map 默认进入版本控制，可被团队共享和审查。如果决定后续排除，一行 `.recon/` 到 `.gitignore` 即可。

### RECON.md 格式

```markdown
# Recon Map: {project-name}
Generated: {date} | HEAD: {commit}

## Module Coverage

| Module | 1.Perim | 2.Entry | 3.Arch | 4.Flow | 5.DevLoop | 6.Deep | Last Visit |
|--------|---------|---------|--------|--------|-----------|--------|------------|
| {name}  | ✓       | ✓       | ✓      | ✓      | -         | ✓      | {date}     |

## Artifacts

- [术语表](.recon/glossary.md)
- [架构概览](.recon/architecture.md)
- [入口清单](.recon/entry-points.md)
- [设计决策](.recon/design-decisions.md)
- [开发回路](.recon/dev-loop.md)
- {module} · [Flow Trace](.recon/flow-{module}.md)
```

### 字段规则

**Module**：以代码目录/模块为粒度。一个模块一次覆盖整块代码。

**里程碑（1-6）**：✓ = 完成该步骤，- = 未完成。Agent 用 `-` 来判断走 onCover 时还需要做什么。

**Depth**：`✓` 的数量（N/6）。1-2 为"扫过"，3-4 为"已跟踪"，5-6 为"深入"。

**Last Visit**：最后一次 revisist 的日期。超过 30 天且有最新 commit 变化则建议 revisit。

## 失败模式

| 问题 | 症状 | 防御 |
|------|------|------|
| 前置完成 | 读了 README 就说"懂了" | 每步有可检查的完成标准 |
| 幸存者偏差 | 只读了主流程，没看错误处理 | Step 4 强约束"每一层都要精确到文件名" |
| 地图≠疆域 | 代码结构和运行时架构不一致 | Step 3 + 4 一起防：架构图 + 运行时追踪 |
| 分析瘫痪 | 在某个工具函数里深挖出不来 | 时间盒约束，Step 6 只对指定模块 |
| 虚假熟悉 | 能复述 RECON.md 但不能从代码重新走 | Step 4 完成标准精确到文件::函数，不能泛泛描述 |
| 复盘变复述 | onRevisit 时直接读 RECON.md 了事 | onRevisit 明确规则：读完钩子后必须重新 trace 代码 |

## 输出语言

默认中文。用户用其他语言时跟随。
