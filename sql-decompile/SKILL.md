---
name: sql-decompile
description: Decode complex SQL or Oracle PL/SQL into business meaning that a technical person can hold in their head. Trigger when the user asks to explain/understand/decode/decompile a SQL query, PL/SQL block, stored procedure, function, package, or trigger. Also when examining code whose business intent is unclear.
---

# SQL / PL/SQL Decompile

将复杂 SQL 或 Oracle PL/SQL **decompile** 为业务含义，让不懂业务的技术人在脑中运行这个心智模型。

**加粗术语** 在 [`GLOSSARY.md`](GLOSSARY.md) 中定义。可视化模式在 [`references/patterns.md`](references/patterns.md) 中定义。

## Input Detection

自动检测输入类型并路由到对应分支：

| 输入特征 | 路由 |
|---|---|
| `SELECT` / `INSERT` / `UPDATE` / `DELETE` / `MERGE` / `WITH` 开头（独立语句） | **Branch A: SQL** |
| `CREATE [OR REPLACE] PROCEDURE\|FUNCTION\|PACKAGE\|TRIGGER` | **Branch B: PL/SQL** |
| `DECLARE` / `DECLARE ... BEGIN ... END` / 裸 `BEGIN ... END`（匿名块） | **Branch B: PL/SQL** |
| `BEGIN` 内含 `SELECT ... INTO` / `EXECUTE IMMEDIATE` | **Branch B: PL/SQL** |
| 混合：CREATE TABLE + INSERT 批量脚本 | 按**主要意图**判断 |
| 不确定（片段不完整） | 提问用户 |

检测输出：`输入识别为 {SQL | PL/SQL}，进入 {Branch A | Branch B} 模式。`

---

## 阶段一 · 分类

#### ① 确定模式（三选一）

| 用户说 | 模式 |
|---|---|
| "在做什么"、"解释这段代码"、裸代码文本 | **Decompile** — 完整业务语义反编译 |
| "数据怎么来的"、"数据血缘" | **Lineage Trace** — 数据流追踪（待实现） |
| "有什么坑"、"检查质量" | **Anomaly Scan** — 反模式扫描（待实现） |

当前实现 **Decompile** 主线；后两者占位。

#### ② 范围确认

| 特征 | 策略 |
|---|---|
| `< 30` 行 | 全量 **decompile**，一次性输出 |
| `≥ 30` 行 | 先输出骨架图，标注"详情逐层展开"；之后每层单独输出 |
| 含外部调用（UDF / 其他过程调用） | 标记 `[外部依赖：{名称}]`，不展开被调用方内部逻辑 |
| 无 DDL 可用且命名无业务线索 | 标注 `推测语义`，低置信度输出 |

**完成标准**：确定模式和分析策略。进入阶段二前输出一条确认。

---

## 阶段二 · Decompile

### Branch A: SQL Decompile

按 SQL **逻辑执行顺序**（FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → CTE）逐层映射。每层填入一行映射。

| # | 层 | SQL 结构 → 业务 | 映射对象 | 完成标准 |
|---|---|---|---|---|
| ① | FROM | 表引用 → **业务实体** | 每张表/视图/CTE → 实体名 + 置信度 | 所有引用映射完毕 |
| ② | JOIN | ON 条件 → **业务关系** | 每对表 + JOIN 类型 → 关系含义 | 能说清"为什么是 LEFT 不是 INNER" |
| ③ | WHERE | 谓词 → **业务过滤规则** | 每个条件 → 业务含义 + 过滤方向 | 能说清"删掉了什么" |
| ④ | GROUP BY | 分组列 → **业务粒度** | → grain 描述句 | 一句话说清"每行代表什么" |
| ⑤ | 聚合 | 函数 → **业务度量** | 每个聚合 → KPI + 单位 | 能说清"SUM 在算什么" |
| ⑥ | HAVING | 条件 → **业务阈值** | → 过滤前后差异 | 无 HAVING 则跳过 |
| ⑦ | SELECT | 列 → 维度/度量 | 每列 → 类型标注 | 能回答"输出是什么" |
| ⑧ | ORDER BY | 排序列 → **业务优先级** | → 排序意图 | 无 ORDER BY 则跳过 |
| ⑨ | CTE/子查询 | 中间结果 → **中间业务概念** | → 业务解释 | 能说清"为什么需要这个中间结果" |

**判断依据（由强到弱，①②③层通用）**：
- DDL 注释或业务文档
- 列名语义（`order_id` → 订单事实，`user_name` → 用户维度）
- 别名惯例（`o` → order, `u` → user, `p` → product）
- Schema 层命名（`ods_` → 原始层, `dim_` → 维度, `fct_` → 事实表）
- CTE / 别名名称含义
- 以上均缺 → `推测：{实体}`，置信度低

**JOIN 类型业务含义**：

| JOIN | 业务含义 |
|---|---|
| `INNER` | 二者均存在的子集 |
| `LEFT` | 左表为主，右表信息可选（NULL = 无匹配） |
| `RIGHT` | 镜像 LEFT，交换左右后同 |
| `FULL` | 全部保留，尽力匹配 |
| `CROSS` | 每对组合 → 枚举/配置展开 |

**聚合关注点**：
- 窗口函数 → 不改变 grain，只做排名/分组内排序
- `COUNT(*)` vs `COUNT(col)` → 后者排除 NULL → 可能是"有效值计数"
- `SUM(CASE WHEN ...)` → 条件计数，拆开解释

---

### Branch B: PL/SQL Decompile

**核心视角转变**：SQL decompile 问"数据如何变换"；PL/SQL decompile 问"业务过程如何执行"——决策点、循环、异常处理是核心。

#### ① Interface → 业务入口

| PL/SQL 结构 | 业务对应 |
|---|---|
| 过程名 `process_refund` | 业务操作：处理退款 |
| 入参 `p_order_id` | 业务入参：订单 ID |
| 出参 `p_status OUT` | 业务结果：处理状态码 |
| 函数返回值 | 业务度量 / 状态码 |
| `CREATE OR REPLACE PACKAGE` | 业务模块边界 |

**完成标准**：每个参数标注了业务含义。能说清"这个入口在业务上触发什么操作"。

---

#### ② Declarations → 业务状态

| 声明 | 业务含义 |
|---|---|
| 变量 `v_total_refund NUMBER` | 中间值：累计退款金额 |
| 游标 `CURSOR c_pending IS ...` | 数据集：待处理退款的订单 |
| 异常 `e_insufficient_balance` | 业务异常：余额不足 |
| 集合/记录类型 | 业务结构体 |

PL/SQL 命名前缀映射：

| 前缀 | 含义 | 示例 |
|---|---|---|
| `v_` / `l_` | 变量 / 局部 | `v_count` |
| `p_` | 参数 | `p_order_id` |
| `c_` | 游标 | `c_active_users` |
| `c_` (常量) | 常量 | `c_max_retry` |
| `t_` / `type_` | 自定义类型 | `t_order_rec` |
| `e_` | 异常 | `e_not_found` |

**完成标准**：关键变量有业务含义映射，游标关联了对应的数据集描述。

---

#### ③ Main Flow → 业务步骤序列

将执行体分解为 **业务步骤序列**。扫描方法：先定位结构关键字（`IF` / `CASE` / `LOOP` / `FOR` / `WHILE` / `BEGIN..EXCEPTION..END` / `COMMIT` / `ROLLBACK` / 独立 DML），这些是步骤的分界，再对每段标注业务含义。

```
| # | 位置 | 业务步骤                           | 类型     | 业务影响              |
|---|------|-----------------------------------|----------|-----------------------|
| 1 | L10  | 查询待处理退款订单                 | 数据集   | 打开退款数据窗口      |
| 2 | L12  | 遍历每笔待处理退款                 | 循环     | 逐笔处理              |
| 3 | L14  | 判断余额是否足够                   | 决策     | 足额→退款；不足→报错  |
| 4 | L20  | 扣减余额，插入退款记录             | DML      | 余额−, 退款+1         |
| 5 | L30  | 异常处理：余额不足                 | 异常     | 记录日志，不回滚      |
```

| 步骤类型 | 判定 | 输出特征 |
|---|---|---|
| **数据集** | 含 `SELECT INTO` / `FETCH` / 游标操作 | 附 SQL 摘要 |
| **决策** | `IF` / `ELSIF` / `CASE` | 附分支数 + 各分支业务含义 |
| **循环** | `LOOP` / `FOR` / `WHILE` / 游标 `FOR LOOP` | 附每次迭代处理的业务单位 |
| **DML** | `INSERT` / `UPDATE` / `DELETE` / `MERGE` | 附影响的实体和列 |
| **调用** | 调用其他过程/函数 | 标注被调方名称 |
| **事务** | `COMMIT` / `ROLLBACK` / `SAVEPOINT` | 附事务边界含义 |
| **异常** | `EXCEPTION` / `WHEN ... THEN` | 附触发条件和恢复策略 |

**完成标准**：执行体被分解为业务步骤序列，每步有类型标签和业务解释。**没有遗漏 IF / LOOP / DML**。

---

#### ④ Decision Tree → 业务决策

从 `IF` / `CASE` / `ELSIF` 分支提取决策树。展示**业务上在什么条件下做什么**，而非复现代码。

```
源码：
  IF v_balance >= p_amount THEN
    process_refund(...);
  ELSE
    log_error('insufficient');
    RAISE e_insufficient_balance;
  END IF;

决策树：
余额 ≥ 退款金额？
  ├─ 是 → 执行退款
  └─ 否 → 记录"余额不足"错误，抛出异常
```

**完成标准**：每个条件分支标注了业务含义。能说清"什么情况下走哪条路"。

---

#### ⑤ Dependencies → 业务依赖

| 被依赖对象 | 类型 | 使用方式 |
|---|---|---|
| orders | TABLE | SELECT / UPDATE |
| refunds | TABLE | INSERT |
| check_balance | FUNCTION | 条件判断 |
| log_utils | PACKAGE | 日志记录 |

**完成标准**：所有被引用的表 / 视图 / 函数 / 过程已列举。

---

#### ⑥ Error + Transaction → 异常恢复与事务边界

| 异常 | 触发条件 | 恢复策略 |
|---|---|---|
| `NO_DATA_FOUND` | SELECT INTO 无结果 | 设默认值继续 |
| `OTHERS` | 其他异常 | 记录日志并重新 RAISE |

| 位置 | 语句 | 业务含义 |
|---|---|---|
| L35 | COMMIT | 批次处理完成，持久化变更 |
| L40 | SAVEPOINT before_refund | 回滚锚点：在退款操作前 |
| L42 | ROLLBACK TO before_refund | 退款失败，回滚到此前的状态 |

**完成标准**：EXCEPTION handler 全部标注触发条件和恢复策略。COMMIT/ROLLBACK 标注事务边界含义。

---

## 阶段三 · 输出

### SQL Decompile 输出结构

1. **一句话摘要** — `{主体} 在 {条件范围} 下的 {度量}`
2. **实体映射表** — FROM / JOIN 中每个表 → 业务实体
3. **数据流图** — 使用 `references/patterns.md` 中的 SQL 模式
4. **逐层分解** — 按逻辑执行顺序，每层一句业务解释
5. **关键业务规则清单** — WHERE / HAVING / CASE WHEN 中的逻辑，每行一条

### PL/SQL Decompile 输出结构

1. **一句话摘要** — 这个存储过程 / 块完成什么业务操作
2. **接口映射** — 参数 → 业务含义
3. **流程图** — 使用 `references/patterns.md` 中的 Process Flow / Decision Tree 模式
4. **步骤分解表** — 类型标注 + 业务解释（⑥步产出）
5. **决策树** — IF/CASE 分支的树形表示（④步产出）
6. **依赖清单** — 被引用的表 / 函数 / 过程（⑤步产出）

### 共享约束

- 对话输出 ASCII 图，禁 mermaid。写文件时才用 mermaid
- SQL 关键字保留英文，业务映射用中文
- **不给出** 修改建议、优化建议、批评或审查
- **不输出** "根据分析"、"我注意到"、"总的来说" 等填充语
- **不输出** 自检过程
- **不输出** 内部流程标签（"阶段二"、"③" 等是说明，不是输出内容）
- 类比必须附带失效声明：`这个类比在 {映射点} 上成立，但在 {失效处} 不成立`
- 任何推断必须标注置信度

### 最少图形门槛

- SQL 分支：必须含 ≥1 张数据流图；例外：≤15 行且无子查询
- PL/SQL 分支：必须含 ≥1 张业务流程图；例外：≤20 行

---

## 阶段四 · 追问循环

| 用户说 | 处理 |
|---|---|
| "X 部分再细点" | 同概念深度输出更细粒度 |
| "那 Y 呢" | 范围迁移，重新分类 |
| "继续" | 输出下一个未展示的块 |

**规则**：
- 追问无深度上限。第 3 次递归起，末尾附方向提示：`继续往下是 {边界条件/极端情况/错误路径}，要继续吗？`
- 用户说"继续" → 解除提示
- 用户沉默 → 结束。不主动问"还有问题吗"

---

## 实体推断参考

### 表名 → 业务实体

```
order, orders, t_order               → 订单
user, users, t_user                  → 用户
product, products, sku               → 商品
payment, payments, pay               → 支付
refund, refunds                      → 退款
invoice, invoices                    → 发票
member, members, membership          → 会员
coupon, coupons, promo               → 优惠券
category, categories, catalog        → 分类
address, addresses                   → 地址
log, audit_log, history              → 日志 / 审计
config, configs, setting, parameter  → 配置
dim_date                             → 日期维度
dim_xxx                              → xxx 维度表
fct_xxx                              → xxx 事实表
ods_xxx                              → ODS 原始数据
dwd_xxx                              → DWD 明细层
dws_xxx                              → DWS 汇总层
ads_xxx                              → ADS 应用层
```

### 列名 → 业务属性

```
xxx_id, xxx_no, xxx_code            → 业务标识符
xxx_name, xxx_desc, xxx_nm          → 名称 / 描述
xxx_at, xxx_date, xxx_time          → 时间戳
xxx_status, xxx_state               → 状态
xxx_type, xxx_category              → 分类 / 类型
xxx_amount, xxx_price, xxx_fee      → 金额
xxx_qty, xxx_quantity               → 数量
xxx_cnt, xxx_count                  → 计数
xxx_rate, xxx_pct, ratio_xxx        → 比率 / 百分比
is_xxx, has_xxx, xxx_flag           → 布尔标志
xxx_by, create_by, update_by        → 操作人
xxx_rank, xxx_seq, xxx_order        → 序号 / 排名
xxx_level, xxx_grade, xxx_tier      → 层级 / 等级
```

---

## 硬边界

不得：
- 输出修改建议、优化建议、批评或审查
- 在未读取代码文本的情况下作答
- 输出填充语、自检过程、内部流程标签
- 将推断呈现为已确认的事实——必须标注置信度
- 解释超出用户要求范围的内容
- 回答后主动评价（"理解了吗"）
- 按行复述代码——必须按业务逻辑块组织
