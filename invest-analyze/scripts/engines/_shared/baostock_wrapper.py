# -*- coding: utf-8 -*-
"""BaoStock 公共封装层：个股财务、日线行情、估值数据的回退源。

当 AKShare 主源失败时，此模块作为第一回退。BaoStock 有自有数据服务器，
不依赖第三方网站 HTML 结构——可靠性优于爬虫类数据源。

BaoStock 覆盖：
  - 日线行情（含 peTTM/pbMRQ/psTTM 估值字段） → daily_bars()
  - 财务指标（ROE/毛利率/净利率/营收）       → financial_indicators()
  - 股票基本资料（名称/上市日/状态）          → stock_basic_info()

不覆盖：实时行情快照（BaoStock 无实时数据）。
"""

import sys

try:
    import baostock as bs
    import pandas as pd

    _HAVE_BS = True
except ImportError:
    _HAVE_BS = False


def _check_bs():
    if not _HAVE_BS:
        print("需要安装 baostock：pip install baostock", file=sys.stderr)
        return False
    return True


def _market_code(symbol):
    """将纯数字股票代码转为 BaoStock 格式（带 sh/sz/bj 前缀）。"""
    prefix = symbol[:3]
    if prefix in ("600", "601", "603", "605", "688", "689"):
        return f"sh.{symbol}"
    elif prefix in ("000", "001", "002", "003", "300", "301"):
        return f"sz.{symbol}"
    elif prefix in ("430", "830", "831", "832", "833", "834", "835", "836",
                    "837", "838", "839", "870", "871", "872", "873", "874",
                    "920"):
        return f"bj.{symbol}"
    return symbol


def _login():
    """登录 BaoStock。每次调用独立登录，避免连接过期。"""
    lg = bs.login()
    return lg.error_code == "0"


def _logout():
    bs.logout()


def daily_bars(symbol, start_date="20000101", end_date="20500101", adjust="qfq"):
    """获取个股日线行情（BaoStock 版本）。

    与 akshare.daily_bars() 接口签名对齐，作为回退源。

    返回 DataFrame（列：日期, 开盘, 收盘, 最高, 最低, 成交量, 成交额, 换手率,
    涨跌幅, peTTM, pbMRQ, psTTM），失败返回 None。
    """
    if not _check_bs():
        return None

    code = _market_code(symbol)
    fields = ("date,code,open,high,low,close,preclose,volume,amount,"
              "adjustflag,turn,pctChg,peTTM,pbMRQ,psTTM,isST")

    # adjustflag: 1=向后复权, 2=向前复权, 3=不复权
    adj_map = {"qfq": "2", "hfq": "1", "": "3"}
    adj_flag = adj_map.get(adjust, "2")

    # 日期格式转换
    sd = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}"
    ed = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}"

    if not _login():
        return None
    try:
        rs = bs.query_history_k_data_plus(
            code, fields, start_date=sd, end_date=ed, frequency="d", adjustflag=adj_flag
        )
        if rs.error_code != "0":
            return None
        data_list = []
        while rs.next():
            data_list.append(rs.get_row_data())
        if not data_list:
            return None
        df = pd.DataFrame(data_list, columns=rs.fields)
        df.rename(columns={
            "date": "日期", "open": "开盘", "close": "收盘",
            "high": "最高", "low": "最低", "volume": "成交量",
            "amount": "成交额", "turn": "换手率", "pctChg": "涨跌幅",
            "peTTM": "市盈率", "pbMRQ": "市净率", "psTTM": "市销率",
        }, inplace=True)
        # 数值类型转换
        for col in df.columns:
            if col == "日期":
                continue
            df[col] = pd.to_numeric(df[col], errors="coerce")
        return df
    except Exception as e:
        print(f"    baostock.daily_bars({symbol}) 异常: {e}", file=sys.stderr)
        return None
    finally:
        _logout()


def financial_indicators(symbol):
    """获取个股财务指标（BaoStock 版本）。

    返回 DataFrame（列：报告期, ROE, 销售毛利率, 销售净利率, 营业总收入,
    净利润），失败返回 None。
    """
    if not _check_bs():
        return None

    code = _market_code(symbol)

    if not _login():
        return None
    try:
        rows = []
        # 取最近 8 个季度（2 年）+ 4 个年度
        for year in range(2020, 2027):
            for quarter in [4, 2]:  # 年报 + 中报
                rs = bs.query_profit_data(code, year=year, quarter=quarter)
                if rs.error_code == "0":
                    d = rs.get_data()
                    if d is not None and not d.empty:
                        rows.append(d)
        if not rows:
            return None
        df = pd.concat(rows, ignore_index=True)
        # 保留有用字段
        keep = ["pubDate", "statDate", "roeAvg", "saleGPM", "saleNPM",
                "operRevenue", "netProfit", "epsTTM"]
        available = [c for c in keep if c in df.columns]
        df = df[available]
        df.rename(columns={
            "pubDate": "发布日期", "statDate": "报告期",
            "roeAvg": "ROE", "saleGPM": "销售毛利率",
            "saleNPM": "销售净利率", "operRevenue": "营业总收入",
            "netProfit": "净利润", "epsTTM": "每股收益",
        }, inplace=True)
        for col in df.columns:
            if col in ("报告期", "发布日期"):
                continue
            df[col] = pd.to_numeric(df[col], errors="coerce")
        return df.sort_values("报告期", ascending=False)
    except Exception as e:
        print(f"    baostock.financial_indicators({symbol}) 异常: {e}", file=sys.stderr)
        return None
    finally:
        _logout()


def stock_basic_info(symbol):
    """获取股票基本资料（名称、上市状态）。

    返回 dict {"code_name": str, "ipoDate": str, "status": str} 或 None。
    """
    if not _check_bs():
        return None

    code = _market_code(symbol)
    if not _login():
        return None
    try:
        rs = bs.query_stock_basic(code)
        if rs.error_code != "0":
            return None
        row = rs.get_data()
        if row is None or row.empty:
            return None
        r = row.iloc[0]
        return {
            "code_name": r.get("code_name", symbol),
            "ipoDate": r.get("ipoDate", ""),
            "status": r.get("status", ""),
        }
    except Exception as e:
        print(f"    baostock.stock_basic_info({symbol}) 异常: {e}", file=sys.stderr)
        return None
    finally:
        _logout()
