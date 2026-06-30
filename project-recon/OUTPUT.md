# Recon Map 产出规范

> 被 [project-recon](SKILL.md) 引用的披露参考。Recon Map 核心是写给项目新读者看的——让一个人能在最短时间内抓住关键信息。只在你需要写文件或检查格式时查阅本节。

## 读者导航

Recon Map 按阅读优先级组织。建议阅读顺序：

1. **RECON.md — Overview + Module Coverage 表**：项目全貌、技术栈、模块划分
2. **content-journey.md**：内容在系统中经历的形态变化链（先看全景，再看模块细节）
3. **architecture.md**：模块间关系和核心抽象（聚焦"改哪里影响谁"时读）
3. **选一个最关心的模块，读其 Flow 节**：主功能走通，入口到出口
4. **user-journeys.md**：用户怎么用这个系统（关注"实际怎么用"时读）
5. **dev-loop.md**：搭建环境时查阅

每份文件独立可读——不需要从头到尾读完。

## 文件结构

目标项目根目录下 **`.recon/`** 子目录，集中存放所有产出物：

```
{目标项目}/
└── .recon/
    ├── RECON.md                 ← 覆盖状态表（唯一索引）
    ├── glossary.md              ← 项目专用术语
    ├── architecture.md          ← 模块依赖图 + 核心抽象
    ├── user-journeys.md         ← 用户旅程
    ├── content-journey.md       ← 内容变形记：内容在系统中的形态变化链
    ├── entry-points.md          ← 入口点清单
    ├── dev-loop.md              ← 构建/测试/调试命令
    ├── design-decisions.md      ← 设计决策（跨模块统一归档）
    └── modules/                 ← 模块专属文件
        ├── core.md              ← Flow 节 + Deep 节
        ├── auth.md
        └── payment.md
```

不写 `.gitignore`——Recon Map 默认进入版本控制，可被团队共享和审查。如果决定后续排除，一行 `.recon/` 到 `.gitignore` 即可。

## user-journeys.md 格式

```markdown
# User Journeys: {project-name}

## Personas
- {persona}: {description}

## Journey: {name}
{step1} → {step2} → {step3} → done

### Prerequisites
- {step2} 依赖 {step1} 完成
```

## content-journey.md 格式

```markdown
# 内容变形记：{project-name}

以内容本身为主语，描述它从进入系统到最终产出的完整形态变化链。

---

## 第{N}站：{站名}

一句话描述：{输入形态} → {经过什么处理} → {输出形态}

**输入**：数据来源（表/文件/上游产出）
**处理**：关键处理逻辑（什么 Agent / 什么步骤）
**输出**：写入位置（表/文件）
**下一站**：{下一站名}
```

（Step 4 产出，Full 全部模块追踪完成后写一份完整的。onCover 补全模块后更新相应站。）

每个模块一个 `.recon/modules/{module}.md`，按节（section）递进：

```markdown
# {module}

**职责**：这个模块做什么的、解决什么问题。
**上下游**：上游依赖谁的产出 → [本模块] → 下游谁依赖本模块的产出。

## Flow

从入口到出口的完整功能路径，精确到 `文件::函数`。
（Step 4 产出，Full / onCover 创建，onRevisit 更新）

## Deep

内部抽象、错误处理路径、设计 tradeoffs、Open Questions。
（Step 6 产出，onDig 创建 / onRevisit 更新）
```

## RECON.md 格式

```markdown
# Recon Map: {project-name}
Generated: {date} | HEAD: {commit}

## Module Coverage

| Module | 1.Perim | 2.Entry | 3.Arch | 4.Flow | 5.DevLoop | 6.Deep | Last Visit |
|--------|---------|---------|--------|--------|-----------|--------|------------|
| core/  | ✓       | ✓       | ✓      | ✓      | -         | ✓      | 2026-06-27 |
| auth/  | ✓       | ✓       | ✓      | ✓      | -         | -      | 2026-06-27 |
| payment/ | ✓     | ✓       | ✓      | -      | -         | -      | 2026-06-26 |

### 字段规则

**Module**：以代码目录/模块为粒度。一个模块一次覆盖整块代码。

**里程碑（1-6）**：✓ = 完成该步骤，- = 未完成。Agent 用 `-` 来判断走 onCover 时还需要做什么。

**Depth**：`✓` 的数量（N/6）。1-2 为"扫过"，3-4 为"已跟踪"，5-6 为"深入"。

**Last Visit**：最后一次 revisist 的日期。超过 30 天且有最新 commit 变化则建议 revisit。
