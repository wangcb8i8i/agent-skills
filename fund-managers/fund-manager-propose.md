# 数据层增强提议

> 对标 a-stock-data（A 股全栈数据工具包 V3.2.4）的数据层设计，对 fund-managers 当前数据层做三项可落地的增强。只加不删，不改变现有调用签名。

## 汇总

| # | 改动 | 文件 | 代码量 | 风险 |
|---|------|------|--------|------|
| P0 | 东财 HTTP 请求统一节流 | `scripts/engines/_shared/eastmoney.py` | ≈5 行 | 无 |
| P1 | 腾讯财经作为行情第二 fallback | `scripts/engines/stock/price.py` + `_shared/tencent.py` | ≈50 行 | 无 |
| P2 | 个股财务/三表直连 fallback | `scripts/engines/_shared/` 下加 `mootdx.py` + `sina.py` | ≈120 行 | 无 |

---

## P0 — 东财 HTTP 统一节流

### 现状

fund-managers 的 `eastmoney.py` 中，`get()` 函数有 3 次重试（间隔 1.5s），但**请求之间没有最小间隔控制**。当 AI 多子代理并行分析多位经理时，各引擎脚本（holdings/nav/scale/managers）**同时**向 `fund.eastmoney.com` 和 `fundf10.eastmoney.com` 发请求，可能触发东财风控（并发 ≥10 / 每秒 >5 次 → 临时封 IP）。

此外，`holdings.py` 中年份循环的 `time.sleep(0.4)` 由调用方自行控制，不是统一的——新引擎脚本可能忘记加、或加了不符合东财阈值。

### 方案

在 `eastmoney.py` 的 `get()` 函数开头增加一个模块级节流，**3 行**，不改任何现有调用：

```python
# 在 eastmoney.py 的 _S = requests.Session() 之后添加

_LAST_EM_CALL = [0.0]          # 模块级时间戳（list 绕 Python 闭包）
EM_MIN_INTERVAL = 0.5          # 两次东财请求最小间隔（秒）

def _throttle():
    """东财请求前节流：保证请求间隔 ≥ EM_MIN_INTERVAL"""
    wait = EM_MIN_INTERVAL - (time.time() - _LAST_EM_CALL[0])
    if wait > 0:
        time.sleep(wait)
    _LAST_EM_CALL[0] = time.time()
```

然后在 `get()` 第一行插入：

```python
def get(url, referer=None, tries=3):
    _throttle()                     # ← 新增
    h = {"Referer": referer} if referer else {}
    ...
```

### 效果

- 所有走 `eastmoney.py::get()` 的请求自动间隔 ≥0.5s
- 即使 AI 子代理并发跑 6 个引擎，第一个调用锁定时间戳，后续排队等
- `holdings.py` 中已有的 `time.sleep(0.4)` 可以保留（双保险），或后续统一移除
- **无任何外部依赖或开销**——`time.time()` + `time.sleep()` 都是标准库

### 不做的理由

不把 `EM_MIN_INTERVAL` 做成可配置参数（如 a-stock-data），因为 fund-managers 引擎是在子进程中独立执行的，没有全局状态传参通道。模块级常量足够。

---

## P1 — 腾讯财经作为行情第二 fallback

### 现状

`_shared/akshare.py::spot_snapshot()` 的 fallback 链：

```
AKShare stock_zh_a_spot_em() ─→ 失败 ─→ Eastmoney push2 直调 ─→ None
```

问题：
1. AKShare 全市场快照（`stock_zh_a_spot_em()`）每次拉 5000+ 只股票，只为了取 1 只的实时价——高频场景下浪费带宽和 API 配额
2. Eastmoney push2 有风控风险（即使直调）
3. 缺少一个"轻量、不封 IP"的中间层

### 方案

新增 `_shared/tencent.py`，实现 `tencent_quote()`，插入到 fallback 链中间：

```
AKShare → 腾讯财经(新增) → Eastmoney push2 → None
```

#### 腾讯财经 API 特征

| 属性 | 值 |
|------|-----|
| 协议 | HTTP GET，GBK 编码 |
| 端点 | `qt.gtimg.cn/q={sh/sz/bj}{code}` |
| 不封 IP | 社区长期验证 |
| 响应字段 | 88 个 `~` 分隔字段（实时价/昨收/PE/PB/市值/换手率/涨跌停价等） |
| 单次请求 | 支持批量：逗号拼接多只股票，一次返回全部 |

#### 代码

```python
# scripts/engines/_shared/tencent.py
import urllib.request
import json

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

def get_prefix(code: str) -> str:
    """6 位股票代码 → 腾讯 API 市场前缀"""
    if code.startswith(("6", "9")):
        return "sh"
    elif code.startswith("8"):
        return "bj"
    else:
        return "sz"

def tencent_quote(codes: list[str]) -> dict[str, dict]:
    """
    批量拉取腾讯财经实时行情。
    返回: {code: {name, price, pe_ttm, pb, mcap, turnover, ...}}
    失败返回空 dict。
    """
    prefixed = [f"{get_prefix(c)}{c}" for c in codes]
    url = "https://qt.gtimg.cn/q=" + ",".join(prefixed)
    req = urllib.request.Request(url)
    req.add_header("User-Agent", UA)
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        data = resp.read().decode("gbk")
    except Exception:
        return {}

    result = {}
    for line in data.strip().split(";"):
        if not line.strip() or "=" not in line or '"' not in line:
            continue
        key = line.split("=")[0].split("_")[-1]
        vals = line.split('"')[1].split("~")
        if len(vals) < 53:
            continue
        code = key[2:]
        result[code] = {
            "name":       vals[1],
            "price":      float(vals[3]) if vals[3] else 0,
            "pe_ttm":     float(vals[39]) if vals[39] else 0,
            "pb":         float(vals[46]) if vals[46] else 0,
            "mcap":       float(vals[44]) if vals[44] else 0,
            "turnover":   float(vals[38]) if vals[38] else 0,
            "high":       float(vals[33]) if vals[33] else 0,
            "low":        float(vals[34]) if vals[34] else 0,
        }
    return result
```

#### 接入现有代码

`scripts/engines/_shared/akshare.py` 的 `spot_snapshot()`：

```python
def spot_snapshot(symbol):
    # 第 1 层：AKShare（不变）
    if _HAVE_AK:
        try:
            ...
            return {c: r.get(c) for c in cols if c in r}
        except Exception:
            pass

    # 第 2 层：腾讯财经（新增 fallback）
    try:
        from engines._shared.tencent import tencent_quote
        tq = tencent_quote([symbol])
        if symbol in tq:
            return tq[symbol]
    except Exception:
        pass

    # 第 3 层：Eastmoney push2 直调（原第 2 层）
    result = _eastmoney_spot_direct(symbol)
    return result
```

### 效果

- AKShare 正常时：行为完全不变
- AKShare 挂了时：走腾讯财经（轻量、不封 IP），比 Eastmoney push2 更可靠
- 腾讯也挂了时：回退到原 Eastmoney push2，无退化

---

## P2 — 个股财务直连 fallback

### 现状

`_shared/akshare.py::financial_indicators()` 的 fallback 链：

```
AKShare stock_financial_analysis_indicator_em() ─→ BaoStock ─→ None
```

| 源 | ROE | 营收 | 毛利率 | 净利率 | 净利润 | 三表 | EPS | 季报37字段 |
|---|-----|------|--------|--------|--------|------|-----|-----------|
| AKShare | ✓ | ✓ | ✓ | ✓ | ✓ | ✘ | ✓ | ✘ |
| BaoStock | ✓ | ✓ | ✓ | ✓ | ✓ | ✘ | ✓ | ✘ |
| **缺口** | | | | | | **缺三表** | | **缺 37 字段** |

赵丹/姜诚要看资产负债表稳健度（负债率/现金/应收），张坤要看自由现金流——这些当前 fallback 链无法提供。

### 方案

加两个直连接口作为 BaoStock 之后的 fallback，只覆盖 `akshare.py` 当前缺失的数据，不改变现有主链路。

#### 2a. 新浪财报三表（资产负债表/利润表/现金流量表）

```python
# scripts/engines/_shared/sina.py
import requests
import json

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
_S = requests.Session()
_S.headers.update({"User-Agent": UA})

def sina_financial_report(code: str, num: int = 8) -> dict[str, list[dict]]:
    """
    新浪财报三表（直连 quotes.sina.cn）。

    参数:
      code: 6 位股票代码
      num:  返回期数（默认 8 期）

    返回: { "lrb": [...], "fzb": [...], "llb": [...] }
    每张表是「按报告期记录」列表：
      [{"报告期": "20260331", "净利润": 123.45, "净利润_同比": 12.3, ...}, ...]

    失败返回空 dict。
    """
    # 利润表
    pass  # 实现见 a-stock-data §6.4，签名对齐
    # 现金流量表
    # 资产负债表
```

> 注：具体实现可引用 a-stock-data SKILL.md §6.4 的 `sina_financial_report()`（直连 `quotes.sina.cn`，零鉴权，已在 V3.2.1 修复解析逻辑）

#### 2b. mootdx 37 字段季报快照（可选，需国内网络）

```python
# scripts/engines/_shared/mootdx.py
def quarterly_snapshot(code: str) -> dict | None:
    """
    mootdx 财务快照（37 字段季报数据）。
    包含: EPS / ROE / 净利润 / 主营收入 / 营业利润 / 毛利率 / 资产负债率 / 现金流等。
    走 TCP 7709，不封 IP。

    返回 dict 或 None。
    海外 IP 通常超时（TCP 7709 通达信服务器仅限国内）。
    """
    pass  # 实现见 a-stock-data §6.1
```

**注意：** mootdx 走 TCP 7709，海外 IP 全部超时。这个 fallback 只对国内环境生效。作为可选回退，不强制。

#### 接入现有代码

在 `_shared/akshare.py::financial_indicators()` 增加两层 fallback：

```python
def financial_indicators(symbol):
    # 第 1 层：AKShare（不变）
    if _HAVE_AK:
        try:
            ...
            return df
        except Exception:
            pass

    # 第 2 层：BaoStock（不变）
    try:
        ...
    except Exception:
        pass

    # 第 3 层：新浪三表（新增——只返回当期快照，不替代完整指标）
    try:
        from engines._shared.sina import sina_financial_report
        reports = sina_financial_report(symbol, num=1)
        if reports.get("lrb"):
            return reports  # 调用方自行提取
    except Exception:
        pass

    # 第 4 层：mootdx 财务快照（新增——TCP fallback，国内可用）
    try:
        from engines._shared.mootdx import quarterly_snapshot
        snap = quarterly_snapshot(symbol)
        if snap:
            return snap
    except Exception:
        pass

    return None
```

### 效果

- AKShare 正常时：行为完全不变
- AKShare + BaoStock 都挂了时：仍然能拿到新浪三表或 mootdx 财务快照
- 覆盖 AKShare 缺失的三表维度（资产负债表/现金流），为张坤/姜诚的分析框架补充数据

---

## 影响分析

| 现有模块 | P0 影响 | P1 影响 | P2 影响 |
|----------|---------|---------|---------|
| `eastmoney.py` | `get()` 结构不变，首行加 `_throttle()` | 无 | 无 |
| `akshare.py` | 无 | `spot_snapshot()` 加第 2 层 fallback 调用 | `financial_indicators()` 加第 3/4 层 fallback 调用 |
| 现有引擎 | 不感知（继承 `get()` 的节流行为） | 不感知（`spot_snapshot` 返回格式不变） | 不感知（`financial_indicators` 返回格式兼容现有逻辑） |
| `_shared/` 目录 | 无新增文件 | 新增 `tencent.py` | 新增 `sina.py`（可选加 `mootdx.py`） |
| `requirements.txt` | 无变化 | 无变化 | 可选加 `mootdx` |
| AI 子代理工作流 | 无变化 | 无变化 | 无变化 |

---

## 未纳入的范围

以下考虑过但排在当前三项之外：

| 提议 | 排除原因 |
|------|---------|
| 移除 akshare 依赖 | 破坏性改动，且 akshare 在 fund 基金数据方面仍是字段最全的源 |
| `em_get()` 风格的随机抖动 | fund 场景频率远低于 stock 高频场景，固定间隔足够 |
| 数据源优先级文档化 | 纯文档收益，不阻塞代码改动，可随时单独加 |
| 信号层新引擎（龙虎榜/北向/股东户数） | 本质是新功能而非数据层增强，建议作为独立提案 |
| Ticker 归一化收敛 | 建议只改，但当前 3 处各有细微差异，收敛需验证 40+ 前缀的边界情况，可另开 PR |

---

## 测试方案

每项改动后需验证：

**P0 节流：**
- `eastmoney.py` 加载后 `get()` 相邻两次的 `time.time()` 差值 ≥ `EM_MIN_INTERVAL`（手动观察日志或加 `print` 时间戳验证）
- 不影响 `get()` 的原有重试逻辑和返回值

**P1 腾讯 fallback：**
- `from engines._shared.tencent import tencent_quote; tencent_quote(["600519"])` 返回非空
- `spot_snapshot("600519")` 在 akshare 未装时（临时 `pip uninstall akshare`）自动走腾讯财经并返回正确的结构
- 腾讯 API 全挂时的模拟：断网或改错域名，验证退化到 Eastmoney push2

**P2 财务 fallback：**
- `sina_financial_report("600519", num=1)` 返回非空三个表
- 可选：`quarterly_snapshot("600519")` 国内网络下返回 37 字段
- `financial_indicators("600519")` 在 akshare + baostock 均不可用时走通新浪/mootdx
