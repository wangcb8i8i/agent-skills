# 流程型

用户想知道"怎么运作"——需要追踪执行路径。

---

## 读取边界

读取范围：执行路径上的关键函数、转手点、分支点。

跳过：setup / import / error handler / 配置加载 / 测试代码 等非主线。
只读主路径。分支读最具决定性的那个。

---

## 输出形状

```
一句话动机 → [ASCII 流程图] → 各节点标注谁在做、什么进、什么出
```

顺序：先解释"为什么需要这个流程"，再给图，再逐节点标注。

---

## 视觉模式

### 选择规则

| 场景 | 使用 |
|------|------|
| 单线执行，一个控制流 | Call flow |
| 多参与方来回交换消息 | Sequence |
| 独立分支并行后合并 | Pipeline/DAG |
| 对象有明确生命周期，状态间有合法转移 | State machine |
| 多个执行单元交错运行，共享资源/临界区 | Concurrency / Interleaving |

选参与者最少的那个。如果用 Call flow 够了，就不要上 Sequence。

### Call flow

```
[input]
  ↓
[normalize]
  ↓
[branch]
  ├─→ [path A]
  └─→ [path B]
  ↓
[result]
```

### Sequence

```
Client        Server        Database
  │             │               │
  │── request ─▶│               │
  │             │── query ─────▶│
  │             │◀── rows ──────│
  │◀── response │               │
```

### Pipeline / DAG

```
         ┌── [stage A] ──┐
[input] ──┤               ├── [merge] ── [output]
         └── [stage B] ──┘
```

### State machine

对象有生命周期时，画合法状态转移和触发条件。标注"不可能发生的转移"比画全图更重要。

```
     ┌── cancel ──▶ [cancelled]
     │
[init] ──▶ [pending] ──▶ [running] ──▶ [done]
           │                │
           └── error ───────▶ [failed]
```

### Concurrency / Interleaving

多个执行单元交错运行时，画时间轴上的共享资源访问。重点标注临界区和竞态边界，不画无关的 goroutine。

```
goroutine A:  lock(m) ── read(x) ── write(x) ── unlock(m) ──
goroutine B:  ── wait(m) ─────────────────────── lock(m) ── read(x)
```

---

## 隐含邻接

见 SKILL.md §1b。

## 完成标志

用户能复述输入从哪进、中间经过哪些关键转手、最终从哪出。
