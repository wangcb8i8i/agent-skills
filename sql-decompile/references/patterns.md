# 可视化模式 —— SQL / PL/SQL Decompile 输出图集

SQL 分支使用数据流向图（CTE Chain / Join Tree / Aggregation Pipeline）。
PL/SQL 分支使用过程流向图（Process Flow / Decision Tree / State Transition / Dependency Graph）。

---

# SQL 模式

## CTE Chain（CTE 链）

展示数据在 CTE 之间的流动。适合以 `WITH ... SELECT` 结构为主的查询。

```
                    ┌──────────────────────┐
                    │  ods_order           │  ← 源表 1（订单原始数据）
                    └────────┬─────────────┘
                             │
                    ┌────────▼─────────────┐
                    │  dwd_order_clean     │  ← CTE 1（清洗：去重、标准化）
                    └────────┬─────────────┘
                             │ LEFT JOIN
                    ┌────────▼─────────────┐
                    │  dim_user            │  ← 源表 2（用户维度）
                    └────────┬─────────────┘
                             │
                    ┌────────▼─────────────┐
                    │  paid_orders         │  ← CTE 2（过滤：已支付）
                    └────────┬─────────────┘
                             │
                    ┌────────▼─────────────┐
                    │  final               │  ← 最终 SELECT（按用户聚合）
                    └──────────────────────┘
```

### 何时用
- ≥2 个 CTE
- 嵌套子查询（可展开为扁平链）
- 线性或近乎线性的数据流

### 规则
- 每层标注实体或操作类型
- 箭头 = 数据流动方向

---

## Join Tree（JOIN 树）

展示多表 JOIN 关系。适合星型/雪花型。

```
                    ┌─────────────┐
                    │   订单      │  ← 事实表（核心）
                    └──────┬──────┘
                           │
          INNER ┌──────────┼──────────┐ LEFT
                │          │          │
       ┌────────▼───┐ ┌───▼────────┐ ┌▼──────────┐
       │   用户     │ │   商品     │ │   支付    │
       │ (维度表)   │ │ (维度表)   │ │ (事实表)  │
       └────────────┘ └────────────┘ └───────────┘
```

### 何时用
- 一张事实表 JOIN 多张维度表
- JOIN 数量 ≥3
- 需展示 INNER vs LEFT 差异

---

## Aggregation Pipeline（聚合管道）

展示从明细到聚合的变换。

```
[明细层]
  dwd_order                        ← 每行 = 一笔订单
      │
      │ GROUP BY user_id
      ▼
[聚合层]
  user_order_stats                 ← 每行 = 一个用户
      │
      │ COUNT(*)     → 订单量（笔）
      │ SUM(amount)  → 总金额（元）
      │ AVG(score)   → 均分（分）
      │
      │ HAVING COUNT(*) > 5
      ▼
[输出层]
  final                            ← 只保留订单量 >5 的用户
```

### 何时用
- 含 GROUP BY + 多个聚合
- 需要展示 grain 变化
- 含 HAVING

---

## 单表过滤流

```
[dwd_order] ── WHERE status='paid' ──> [输出：已支付订单]
                │
                │ AND created_at >= '2024-01-01'
                │
                └──> 结果：2024 年后的已支付订单
```

### 何时用
- 单表查询，WHERE 条件 ≤3

---

## 子查询展开

```
SELECT * FROM orders o
WHERE EXISTS (
  SELECT 1 FROM payments p
  WHERE p.order_id = o.id AND p.status = 'success'
)

     ──── 等价于 ────

[orders] ── INNER JOIN ──> [payments (status='success')]
                                │
                                └── 只保留有成功支付记录的订单
```

---

# PL/SQL 模式

## Process Flow（业务流程图）

展示 PL/SQL 执行体的业务步骤序列和流程控制。

```
[入口] process_refund(p_order_id)
  │
  │ ① 查询待处理退款订单
  ▼
[数据集] c_pending (curs)
  │
  ▼
 ╔══════════════════════════════════╗
 ║ ② FOR cur IN c_pending LOOP     ║
 ║    逐笔处理退款                   ║
 ╚══════════════════════════════════╝
  │
  │ ③ 余额 ≥ 退款金额？
  ├────── 是 ────> ④ 执行退款（扣余额 + 插入退款记录）
  │                   │
  │                   ▼
  │               [DML] orders: SET balance-
  │               [DML] refunds: INSERT
  │                   │
  │                   ▼
  │               ⑤ 更新订单状态为已退款
  │
  └────── 否 ────> ⑥ 记录错误日志
                      │
                      ▼
                   RAISE e_insufficient_balance
                           │
                           ▼
                  [EXCEPTION] 记录日志，不回滚
```

### 何时用
- 含多个业务步骤的 PL/SQL 块
- 有 IF/CASE 分支
- 有循环处理
- 含异常处理

### 规则
- 步骤标号 + 类型标签（数据集 / 决策 / DML / 异常）
- 循环用边框做视觉标记
- 分支线标注分支含义

---

## Decision Tree（决策树）

展示 IF/CASE 分支的业务决策逻辑。

```
退单金额 > 1000？
  ├─ 是 → 需要经理审批
  │         ├─ 经理已审批 → 执行退款
  │         └─ 经理未审批 → 挂起待审
  │
  └─ 否 → 自动退款
           ├─ 余额足够 → 实时退款
           └─ 余额不足 → 转人工处理
```

### 何时用
- 多层嵌套 IF / CASE
- ELSIF 链
- 复杂 CASE WHEN

### 规则
- 叶子节点标注最终操作
- 深度 ≤5 级，超过则分多图
- 分支条件都标注业务含义

---

## State Transition（状态变迁）

展示关键变量在流程中的变化。

```
v_refund_total := 0              → 0
  │
  │ 循环每笔退款
  ▼
v_refund_total := v_refund_total + amount
  │                                → 累计中...
  │ 循环结束
  ▼
v_refund_total := v_refund_total  → 最终累计值（写入日志）

═══ 事务边界 ═══

v_processed := FALSE              → 初始
  │
  │ COMMIT
  ▼
v_processed := TRUE               → 已持久化
  │
  │ 异常 ROLLBACK
  ▼
v_processed := FALSE              → 回滚
```

### 何时用
- 关键变量的值变化是理解业务逻辑的关键
- 变量在流程的不同阶段代表不同含义
- 需展示事务的前后状态对比

---

## Dependency Graph（依赖图）

展示过程/函数之间的调用关系。

```
[入口] process_refund
  │
  ├──> check_balance (FUNCTION)      ← 余额检查
  │         └──> get_account (FUNCTION)
  │
  ├──> deduct_balance (PROCEDURE)    ← 扣款
  │         └──> lock_account (PROCEDURE)
  │
  ├──> insert_refund_record (PROCEDURE) ← 记录退款
  │
  └──> log_utils.log_info (PROCEDURE)   ← 日志
```

### 何时用
- 主过程调用多个子过程/函数
- 依赖链条是关键理解障碍
- 需理解模块边界

### 规则
- 只展示一级调用（不递归展开子过程的子过程）
- 标注每个被调方的基本职责
