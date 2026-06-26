# 引擎注册表

> 引擎清单、调用参数、用途说明见 `SKILL.md §② 标的类型与引擎映射`。
> 此文件只记录 `--output-dir` 的行为和开发备注。

## fund/holdings

**描述：** 获取基金季度前十大持仓（全部披露季度，最新在前）。

**调用：** `python engines/fund/holdings.py <基金代码> [--output-dir <目录>]`

**--output-dir：** 传此参数时结果写 JSON 到目录下的 `<代码>_holdings.json`，只打印文件路径到 stdout。

---

## fund/nav

**描述：** 获取基金净值数据（单位净值走势、累计净值走势、收益率对比、同类排名、资产配置、业绩评价）。

**调用：** `python engines/fund/nav.py <基金代码> [--output-dir <目录>]`

**--output-dir：** 传此参数时结果写 JSON 到目录下的 `<代码>_nav.json`。

---

## fund/scale

**描述：** 获取基金规模变动序列、持有人结构、资产配置数据。

**调用：** `python engines/fund/scale.py <基金代码> [--output-dir <目录>]`

**--output-dir：** 传此参数时结果写 JSON 到目录下的 `<代码>_scale.json`。

---

## fund/managers

**描述：** 获取基金现任基金经理信息（姓名、任职时间、在管规模、任职回报）。

**调用：** `python engines/fund/managers.py <基金代码> [--output-dir <目录>]`

**--output-dir：** 传此参数时结果写 JSON 到目录下的 `<代码>_managers.json`。

---

## fund/search

**描述：** 在全市场基金列表中搜索（按代码 / 名称 / 拼音首字母 / 类型过滤）。

**调用：** `python engines/fund/search.py <关键词> [--type <类型>] [--max <数量>] [--output-dir <目录>]`

**--output-dir：** 传此参数时结果写 JSON 到目录下的 `search_<关键词>.json`。

---

## stock/financials

**描述：** 获取个股财务指标（ROE、营收、净利润、毛利率、资产负债率等，按报告期）。

**调用：** `python engines/stock/financials.py <股票代码> [--output-dir <目录>]`

**--output-dir：** 传此参数时结果写 JSON 到目录下的 `<代码>_financials.json`。

---

## stock/valuation

**描述：** 获取个股估值数据（PE/PB/PS 历史序列 + 当前快照 + 历史百分位）。

**调用：** `python engines/stock/valuation.py <股票代码> [--output-dir <目录>]`

**--output-dir：** 传此参数时结果写 JSON 到目录下的 `<代码>_valuation.json`。

---

## stock/price

**描述：** 获取个股日线行情（开盘/收盘/最高/最低/成交量/成交额/换手率，默认前复权）。

**调用：** `python engines/stock/price.py <股票代码> [--start YYYYMMDD] [--end YYYYMMDD] [--adjust qfq|hfq|] [--output-dir <目录>]`

**--output-dir：** 传此参数时结果写 JSON 到目录下的 `<代码>_price.json`。
