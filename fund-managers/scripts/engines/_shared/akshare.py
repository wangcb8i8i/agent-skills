# -*- coding: utf-8 -*-
"""AKShare 公共封装层：个股财务、估值、行情数据。

回退链路（每层失败自动尝试下一层）：
  主源 → AKShare
           └→ 失败 → BaoStock（自有服务器，日线/财务）
                        └→ 失败 → pytdx（通达信协议，日线/实时行情）
                                    └→ 失败 → 直调东方财富 HTTP（仅实时快照）
                                                └→ 失败 → 返回 None（降级容忍）

所有 stock 引擎脚本通过此模块访问数据，不直接调 AKShare / BaoStock / pytdx。
"""

import sys

try:
    import akshare as ak
    _HAVE_AK = True
except ImportError:
    _HAVE_AK = False

import pandas as pd


def market_suffix(code):
    """为股票代码添加市场后缀（AKShare 部分接口需要）。

    600/601/603/605/688/689 → .SH
    000/001/002/003/300/301/920 → .SZ
    4xx/8xx → .BJ
    """
    prefix = code[:3]
    if prefix in ("600", "601", "603", "605", "688", "689"):
        return f"{code}.SH"
    elif prefix in ("000", "001", "002", "003", "300", "301", "920"):
        return f"{code}.SZ"
    elif prefix in ("430", "830", "831", "832", "833", "834", "835", "836",
                    "837", "838", "839", "870", "871", "872", "873", "874",
                    "920", "870", "873"):
        return f"{code}.BJ"
    return code


# ─── 财务指标 ────────────────────────────────────────────────


def financial_indicators(symbol):
    """获取个股财务分析指标。

    回退链路：AKShare → BaoStock → None

    返回 DataFrame（列按报告期），失败返回 None。
    """
    # 第 1 层：AKShare
    if _HAVE_AK:
        try:
            df = ak.stock_financial_analysis_indicator_em(
                symbol=market_suffix(symbol), indicator="按报告期"
            )
            if df is not None and not df.empty:
                return df
        except Exception as e:
            print(f"    AKShare financial_indicators({symbol}) 失败: {e}", file=sys.stderr)

    # 第 2 层：BaoStock
    try:
        from engines._shared.baostock_wrapper import financial_indicators as bs_fin
        df = bs_fin(symbol)
        if df is not None and not df.empty:
            return df
    except Exception as e:
        print(f"    BaoStock financial_indicators({symbol}) 失败: {e}", file=sys.stderr)

    return None


# ─── 估值历史序列 ────────────────────────────────────────────


def valuation_history(symbol):
    """获取个股历史估值数据（PE/PB/PS 日线序列）。

    回退链路：AKShare stock_value_em → BaoStock daily_bars（含 peTTM/pbMRQ）→ None

    返回 DataFrame（列：日期, pe, pb, ps, 或对应的中文列名），失败返回 None。
    """
    # 第 1 层：AKShare
    if _HAVE_AK:
        try:
            df = ak.stock_value_em(symbol=symbol).copy()
            if df is not None and not df.empty:
                rename = {"date": "日期", "pe": "市盈率",
                          "pb": "市净率", "ps": "市销率",
                          "pe_ttm_weighted": "市盈率(TTM加权)",
                          "pb_ttm_weighted": "市净率(TTM加权)"}
                df.rename(columns={k: v for k, v in rename.items() if k in df.columns}, inplace=True)
                return df
        except Exception as e:
            print(f"    AKShare valuation_history({symbol}) 失败: {e}", file=sys.stderr)

    # 第 2 层：BaoStock 日线自带 PE/PB
    try:
        from engines._shared.baostock_wrapper import daily_bars as bs_bars
        df = bs_bars(symbol)
        if df is not None and not df.empty:
            # 只保留估值相关列
            keep = [c for c in ["日期", "市盈率", "市净率", "市销率"] if c in df.columns]
            if len(keep) >= 2:
                return df[keep]
    except Exception as e:
        print(f"    BaoStock valuation_history({symbol}) 失败: {e}", file=sys.stderr)

    return None


# ─── 日线行情 ────────────────────────────────────────────────


def daily_bars(symbol, start_date="20000101", end_date="20500101", adjust="qfq"):
    """获取个股日线行情。

    回退链路：AKShare → BaoStock → pytdx → None

    参数：
      symbol   — 股票代码（纯数字，无需后缀）
      start_date — 起始日 "YYYYMMDD"
      end_date   — 截止日 "YYYYMMDD"
      adjust     — 复权："" 不复权, "qfq" 前复权, "hfq" 后复权

    返回 DataFrame（列：日期, 开盘, 收盘, 最高, 最低, 成交量, 成交额, 换手率, ...），
    失败返回 None。
    """
    # 第 1 层：AKShare
    if _HAVE_AK:
        try:
            df = ak.stock_zh_a_hist(
                symbol=symbol, period="daily",
                start_date=start_date, end_date=end_date,
                adjust=adjust,
            )
            if df is not None and not df.empty:
                return df
        except Exception as e:
            print(f"    AKShare daily_bars({symbol}) 失败: {e}", file=sys.stderr)

    # 第 2 层：BaoStock
    try:
        from engines._shared.baostock_wrapper import daily_bars as bs_bars
        df = bs_bars(symbol, start_date=start_date, end_date=end_date, adjust=adjust)
        return df
    except Exception as e:
        print(f"    BaoStock daily_bars({symbol}) 失败: {e}", file=sys.stderr)

    # 第 3 层：pytdx（通达信协议，不复权数据）
    try:
        from engines._shared.pytdx_wrapper import daily_bars as tdx_bars
        df = tdx_bars(symbol, start_date=start_date, end_date=end_date)
        if df is not None and not df.empty:
            return df
    except Exception as e:
        print(f"    pytdx daily_bars({symbol}) 失败: {e}", file=sys.stderr)

    return None


# ─── 实时快照（含当前 PE/PB/市值） ──────────────────────────


def _eastmoney_spot_direct(symbol):
    """直调东方财富实时行情 API（单只股票，不依赖 AKShare 全量下载）。

    返回 dict，包含名称、PE、PB、市值等 pytdx 不返回的字段。
    """
    try:
        import requests
        market = f"1.{symbol}" if symbol[:3] in ("600", "601", "603", "605", "688", "689") else f"0.{symbol}"
        url = "https://push2.eastmoney.com/api/qt/stock/get"
        params = {
            "secid": market,
            "fields": "f43,f44,f45,f46,f57,f58,f60,f116,f117,f162,f167",
            "invt": "2",
        }
        headers = {
            "User-Agent": "Mozilla/5.0 Chrome/120.0",
            "Referer": "https://quote.eastmoney.com/",
        }
        r = requests.get(url, params=params, headers=headers, timeout=10)
        d = r.json().get("data", {})
        if not d or "f43" not in d:
            return None

        price = d["f43"] / 100
        last_close = d.get("f60", d["f43"]) / 100

        result = {
            "代码": d.get("f57", symbol),
            "名称": d.get("f58", ""),
            "最新价": price,
            "涨跌幅": round((price - last_close) / last_close * 100, 2) if last_close else 0,
            "涨跌额": round(price - last_close, 2) if last_close else 0,
            "开盘": d.get("f46", 0) / 100,
            "最高": d.get("f44", 0) / 100,
            "最低": d.get("f45", 0) / 100,
        }
        if "f162" in d:
            result["市盈率-动态"] = d["f162"] / 100
        if "f167" in d:
            result["市净率"] = d["f167"] / 100
        if "f116" in d:
            result["总市值"] = float(d["f116"])
        if "f117" in d:
            result["流通市值"] = float(d["f117"])
        return result
    except Exception as e:
        print(f"    direct eastmoney spot({symbol}) 失败: {e}", file=sys.stderr)
        return None


def _spot_merge(symbol, base_dict):
    """从 东财HTTP 补充缺少的字段（名称/PE/PB/市值等）到 base_dict。"""
    try:
        supp = _eastmoney_spot_direct(symbol)
        if supp:
            for k, v in supp.items():
                if k not in base_dict or base_dict.get(k) in (None, 0, ""):
                    base_dict[k] = v
    except Exception:
        pass
    return base_dict


def spot_snapshot(symbol):
    """获取个股实时行情快照（含 PE-动态、PB、总市值）。

    回退链路：
      1. pytdx（通达信协议，~1s，无 HTTP 代理依赖）
         → 成功后异步补充名称/PE/PB/市值（东财 HTTP 单只查询）
      2. 东财 HTTP 直接查询（单只，~2s）
      3. AKShare 全量下载（~65s，最慢回退）

    返回 dict 或 None。
    """
    # 第 1 层：pytdx（通达信协议直连，不受 HTTP 代理影响）
    try:
        from engines._shared.pytdx_wrapper import spot_snapshot as tdx_spot
        result = tdx_spot(symbol)
        if result is not None:
            # 补充名称/PE/PB/市值（如果 pytdx 没有）
            return _spot_merge(symbol, result)
    except Exception as e:
        print(f"    pytdx spot_snapshot({symbol}) 失败: {e}", file=sys.stderr)

    # 第 2 层：东财 HTTP 单只查询
    result = _eastmoney_spot_direct(symbol)
    if result is not None:
        return result

    # 第 3 层：AKShare 全量下载（最慢回退）
    if _HAVE_AK:
        try:
            df = ak.stock_zh_a_spot_em()
            row = df[df["代码"] == symbol]
            if not row.empty:
                r = row.iloc[0]
                cols = ["代码", "名称", "最新价", "涨跌幅", "涨跌额",
                        "成交量", "成交额", "换手率", "市盈率-动态",
                        "市净率", "总市值", "流通市值", "量比",
                        "60日涨跌幅", "5日涨跌幅", "60日换手率"]
                return {c: r.get(c) for c in cols if c in r}
        except Exception as e:
            print(f"    AKShare spot_snapshot({symbol}) 失败: {e}", file=sys.stderr)

    return None
