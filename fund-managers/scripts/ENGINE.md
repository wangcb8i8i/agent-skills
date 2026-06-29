# 引擎注册表（权威源）

> SKILL.md §② 引用此文件作为引擎映射的权威来源。
> 更新引擎清单时只需改此文件，无需碰 SKILL.md。

标的类型决定调哪个引擎组——基金走 `fund/` 下引擎，个股走 `stock/` 下引擎。
代码未知时先在 ① 阶段通过 websearch 查代码并确认用户，不启动本地搜索。

## 基金标的

| 引擎 | 调用 | 写盘文件名 | 用途 |
|------|------|-----------|------|
| 前十大持仓 | `python engines/fund/holdings.py <代码> --output-dir <dir>` | `<code>_holdings.json` | 持仓、集中度、行业分布 |
| 净值数据 | `python engines/fund/nav.py <代码> --output-dir <dir>` | `<code>_nav.json` | 收益、回撤、同类排名 |
| 规模变动 | `python engines/fund/scale.py <代码> --output-dir <dir>` | `<code>_scale.json` | 申赎趋势、持有人结构 |
| 基金经理 | `python engines/fund/managers.py <代码> --output-dir <dir>` | `<code>_managers.json` | 任职回报、在管规模 |

## 个股标的

| 引擎 | 调用 | 写盘文件名 | 用途 |
|------|------|-----------|------|
| 财务指标 | `python engines/stock/financials.py <代码> --output-dir <dir>` | `<code>_financials.json` | ROE/营收/毛利率/负债率 |
| 估值 | `python engines/stock/valuation.py <代码> --output-dir <dir>` | `<code>_valuation.json` | PE/PB 历史序列+百分位 |
| 行情 | `python engines/stock/price.py <代码> --output-dir <dir>` | `<code>_price.json` | 日线量价换手率 |

---

## 引擎详情

以下仅记录表中未覆盖的额外参数和开发备注。

### stock/price

**额外参数：** `--start YYYYMMDD`（起始日，默认 20000101），`--end YYYYMMDD`（截止日，默认 20500101），`--adjust qfq|hfq|`（前复权/后复权/不复权，默认 qfq）。

**开发备注：**
- 数据层 fallback 链：`scripts/engines/_shared/akshare.py` 中的 `daily_bars()` 编排，走 AKShare → BaoStock → pytdx → None。
