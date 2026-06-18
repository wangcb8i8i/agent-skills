---
name: sql-decompile
description: Decode complex SQL into business meaning that a technical person can hold in their head. Trigger when the user asks to explain/understand/decode/decompile a SQL query, or pastes SQL text and asks what it does. Also when examining a query whose business intent is unclear.
---

# SQL Decompile

将复杂 SQL **decompile** 为业务含义，让不懂业务的技术人在脑中运行这个心智模型。

**加粗术语** 在 [`GLOSSARY.md`](GLOSSARY.md) 中定义。

## 工作流

### 阶段一 · 输入分类

#### ① 确定模式

当前仅实现 **Decompile** 分支。Lineage Trace、Anomaly Scan、Schema Decode 占位待后续迭代。

| 用户说 / 输入信号 | 模式 |
|---|---|
| "这个 SQL 在做什么"、"解释这个查询"、裸 SQL 文本 | **Decompile** |
| "数据怎么来的"、"数据血缘" | Lineage Trace ✗ |
| "有什么坑"、"检查质量" | Anomaly Scan ✗ |
| "结果集什么意思" | Schema Decode ✗ |

#### ② 范围确认

| SQL 特征 | 策略 |
|---|---|
| `< 30` 行 | 全量 **decompile**，一次性输出完整结构 |
| `≥ 30` 行 | 先输出查询骨架（CTE DAG + 最终 SELECT），标注 "详情逐层展开"；之后每层单独输出 |
| 含 UDF / 存储过程 | 标记 `[外部依赖：{名称}]`，不展开其内部逻辑 |
| 无 DDL 可用且表名列名无业务线索 | 标注 `[推测语义]`，低置信度输出 |

**完成标准**：模式确定，分析策略锁定。进入阶段二前已输出一条确认（"本查询将按 Decompile 模式分析，范围：{全量/分层}"）。

---

### 阶段二 · Decompile

按 SQL **逻辑执行顺序**（FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY）而非书写顺序，逐层解开业务含义。每层以**映射完成**为完成标准。

**核心原则**：每遇到一个 SQL 结构，回答两个问题：

1. 这个结构对应什么**业务概念**？
2. 为什么业务需要这个**操作**？

#### ① FROM → 业务实体

每个表引用（table reference）对应一个**业务实体**。

输出格式：实体映射表

```
| 表 / CTE | 业务实体         | 置信度 | 依据                       |
|----------|------------------|--------|----------------------------|
| t1       | 订单             | 高     | 列含 order_id, order_status |
| t2       | 用户             | 高     | 列含 user_id, user_name     |
| sub      | 活跃付费用户宽表 | 中     | CTE 名 active_paid_users    |
```

判断依据（由强到弱）：
- DDL 注释或业务文档
- 列名语义（`order_id` → 订单事实，`user_name` → 用户维度维度）
- 别名惯例（`o` → order, `u` → user, `p` → product）
- Schema 层命名（`ods_` → 原始层, `dim_` → 维度表, `fct_` → 事实表, `dwd_` → 明细层, `dws_` → 汇总层）
- CTE 名称含义（`active_users` → 活跃用户宽表）
- 以上均缺时 → `推测：{实体}`，置信度低

**完成标准**：每个表引用和 CTE 都有一行实体映射，标注置信度。**每个实体都被赋予一个业务名称**（而不是留空或直接复用表名）。

---

#### ② JOIN → 业务关系

每个 JOIN 编码一条**业务关系**。用关系映射表输出：

```
| 左实体 | 右实体 | JOIN 类型 | 业务含义                                        |
|--------|--------|-----------|-------------------------------------------------|
| 订单   | 用户   | INNER     | 只保留有有效用户的订单（过滤了匿名/已注销用户） |
| 订单   | 支付   | LEFT      | 保留全部订单，支付信息可能为空（未支付订单）    |
```

| JOIN 类型 | 业务含义模板 |
|---|---|
| `INNER JOIN` | 只保留{左}和{右}都有的记录 → 业务上"二者均存在"的子集 |
| `LEFT JOIN` | {左}全部保留，{右}无匹配则为 NULL → 业务上"{左}为主，{右}信息可选" |
| `RIGHT JOIN` | 镜像 LEFT，统一按 LEFT 处理（交换左右顺序后再解释） |
| `FULL JOIN` | 两侧全部保留 → 业务上"所有记录，尽力匹配两侧信息" |
| `CROSS JOIN` | 每对组合 → 通常意味着枚举/配置展开 |

**复合条件**：ON 有多个条件时，每个条件是一个独立约束，分别映射。

**完成标准**：每对表之间的 JOIN 至少有一行映射。**能回答"为什么是 LEFT 而不是 INNER"**（即 NULL 出现的业务含义）。

---

#### ③ WHERE → 业务过滤规则

每个谓词是业务选型的一个**筛选规则**。逐条翻译。

```
| 谓词                                   | 业务含义                             | 方向     |
|----------------------------------------|--------------------------------------|----------|
| status = 'active'                      | 只取激活状态的记录                   | 排除非激活 |
| created_at >= '2024-01-01'             | 只取 2024 年及之后的数据             | 排除历史   |
| user_id IN (SELECT ...)                | 只取满足子查询条件的用户             | 条件准入   |
```

关注点：
- AND 组合 → 层层收紧；OR 组合 → 条件并集
- `IN` / `NOT IN` → 显式的业务集合（或子查询返回的集合）
- `LIKE` / 正则 → 通常符合某种业务编码模式
- `EXISTS` / `NOT EXISTS` → 基于关联表的业务存在性判断
- `BETWEEN` → 业务范围的闭区间
- 条件中出现的字面值（如 `'active'`、`'paid'`、`2024-01-01`）→ 是业务域的枚举值或时间边界

**完成标准**：每个 WHERE 条件都被赋予了业务含义。**能回答"删掉了什么"**（即哪些记录被过滤掉了）。

---

#### ④ GROUP BY → 业务粒度

GROUP BY 定义了结果集的**业务粒度**（grain）：每一行代表业务上的一个什么单位。

```
GROUP BY user_id, status
→ 每行 = 一个用户在一种状态下的汇总
```

解释模板：`每行 = {每个 GROUP BY 键的业务含义} 的{度量}汇总`。

**完成标准**：能用一句话说清 grain。**注意**：如果 GROUP BY 多个列，说明这是"多维度的组合粒度"，而非单一维度。

---

#### ⑤ 聚合函数 → 业务度量

每个聚合函数是一个**业务 KPI**。

```
| 聚合                          | 业务含义 | 单位  |
|-------------------------------|----------|-------|
| COUNT(*)                      | 记录条数 | 条    |
| SUM(o.amount)                 | 订单金额 | 元    |
| AVG(r.score)                  | 平均评分 | 分    |
| COUNT(DISTINCT user_id)       | 独立用户数 | 人  |
```

关注点：
- 窗口函数（`ROW_NUMBER() OVER(...)` 等）→ 不改变 grain，只做排序/分组内排名
- `COUNT(*)` vs `COUNT(col)` → 前者包括 NULL，后者排除 → 业务上可能意味着"有效值计数"
- 聚合中嵌套的条件（`SUM(CASE WHEN ... THEN 1 ELSE 0 END)`）→ 是条件计数，拆开解释

**完成标准**：每个聚合都有业务含义映射。**能回答"这个 SUM 在算什么"** 而不是仅复述 SUM。

---

#### ⑥ HAVING → 业务阈值

HAVING 是对聚合后结果的**业务门槛**。

```
HAVING COUNT(*) > 5
→ 只保留订单量超过 5 笔的用户
```

**完成标准**：能说清"过滤前 vs 过滤后"的业务差异。无 HAVING → 跳过。

---

#### ⑦ SELECT → 输出列

SELECT 的每一列要么是**维度**（直接引用或 GROUP BY 键），要么是**度量**（聚合结果）。标注每列类型。

```
| 列                | 类型   | 业务含义     |
|-------------------|--------|--------------|
| user_id           | 维度   | 用户标识     |
| status            | 维度   | 订单状态     |
| COUNT(*)          | 度量   | 订单数量     |
| SUM(o.amount)     | 度量   | 订单金额总和 |
```

**完成标准**：每列标注了维度/度量类型。**可回答"这个查询输出的是什么"**。

---

#### ⑧ ORDER BY → 业务优先级

ORDER BY 反映业务**最关心的排序维度**。

```
ORDER BY amount DESC
→ 按金额从高到低排列，关注大额订单
ORDER BY created_at DESC, id DESC
→ 按时间倒排，相同时按创建序号——展示最新记录
```

**完成标准**：无 ORDER BY → 跳过。有 → 一句话描述排序的业务意图。

---

#### ⑨ 子查询 / CTE → 中间业务概念

每个命名 CTE 或子查询通常包装了一个**中间业务概念**——是业务的自然分解步骤。

```
WITH paid_orders AS (
  SELECT * FROM orders WHERE status = 'paid'
)
→ paid_orders = "已支付的订单"——先过滤出已支付订单，后续在此基础上计算
```

**完成标准**：每层 CTE/子查询都被赋予一个业务解释。**能回答"为什么先算这个中间结果"**——即它在业务上是一个什么自然步骤。

---

### 阶段三 · 输出

#### 输出结构

每份解释的固定结构（5 块，按顺序）：

1. **一句话摘要** — 本查询计算了什么。格式：`{主体} 在 {条件范围} 下的 {度量}`。不加前缀。
2. **实体映射表** — FROM / JOIN 中每个表→业务实体
3. **数据流图** — 使用 [`references/patterns.md`](references/patterns.md) 中的模式，展示 CTE/子查询/表之间的数据流
4. **逐层分解** — 按逻辑执行顺序，每层给出一句业务解释 +（可选）关键代码引用
5. **关键业务规则清单** — WHERE / HAVING / CASE WHEN 中的业务逻辑，每条一行，格式 `{规则} → {业务含义}`

#### 格式约束

- 对话中输出 ASCII 图，禁 mermaid。写文件时才用 mermaid。
- 图使用 `references/patterns.md` 中的模式
- SQL 关键字保留英文，业务映射用中文
- **不给出** 修改建议、优化建议、批评或审查（仅 Anomaly Scan 分支解禁，当前未实现）
- **不输出** "根据分析"、"我注意到"、"总的来说" 等填充语
- **不输出** 自检过程
- **不输出** 阶段标签（"阶段二"、"③" 等是流程说明，不是输出内容）

#### 最少图形门槛

- Decompile 输出必须包含至少一张数据流图
- 例外：查询 ≤15 行且无子查询

#### 类比规则

使用类比时附带失效声明：`这个类比在 {映射点} 上成立，但在 {失效处} 不成立，因为 {理由}`。

---

### 阶段四 · 追问循环

用户发起缺口信号后的处理：

| 用户说 | 处理 |
|---|---|
| "X 部分再细点" | 同概念深度，输出该层的更细粒度实现 |
| "那 Y 呢" | 范围迁移，新目标概念进入阶段一重新分类 |
| "为什么那步要这样处理" | 纵深进入理由型解释 |
| "继续" | 输出下一个未展示的块 |

**规则**：
- 追问无深度上限。但从第 3 次递归起，末尾附一句方向提示：`继续往下是 {边界条件/极端情况/错误路径}，要继续吗？`
- 用户说"继续" → 解除方向提示
- 用户沉默 → 结束。不主动问"还有问题吗"

---

## 实体推断参考

### 常见表名 → 业务实体

```
order, orders, t_order               → 订单
user, users, t_user                  → 用户
product, products, sku, t_product    → 商品 / SKU
payment, payments, pay               → 支付
refund, refunds                      → 退款
invoice, invoices                    → 发票
shipment, shipment, delivery         → 发货 / 配送
member, members, membership          → 会员
coupon, coupons, promo               → 优惠券 / 促销
category, categories, catalog        → 分类
address, addresses                   → 地址
log, audit, audit_log, history        → 日志 / 审计
config, configs, setting, parameter  → 配置
dim_date, date_dim                   → 日期维度
dim_xxx                              → xxx 维度表
fct_xxx                              → xxx 事实表
ods_xxx                              → ODS 原始数据
dwd_xxx                              → DWD 明细层
dws_xxx                              → DWS 汇总层
ads_xxx                              → ADS 应用层
```

### 常见列名 → 业务属性

```
xxx_id, xxx_no, xxx_code            → 业务标识符
xxx_name, xxx_desc, xxx_nm          → 名称 / 描述
xxx_at, xxx_date, xxx_time          → 时间戳
xxx_status, xxx_state               → 状态
xxx_type, xxx_category              → 分类 / 类型
xxx_amount, xxx_price, xxx_fee      → 金额
xxx_qty, xxx_quantity, num_xxx      → 数量
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
- 输出修改建议、优化建议、批评或审查（仅 Anomaly Scan 分支解禁，当前未实现）
- 在未读取 SQL 文本的情况下作答
- 输出 "根据分析"、"我注意到" 等填充语
- 输出自检过程
- 将推断呈现为已确认的事实——必须标注置信度
- 解释超出用户要求范围的内容
- 回答后主动评价（"理解了吗"）
- 按行复述 SQL——必须按业务逻辑块组织
