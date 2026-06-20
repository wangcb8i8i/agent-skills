import akshare as ak
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta


_DATA_STATUS = {}


def _record_status(key: str, success: bool, detail: str = "", source: str = "AKShare"):
    _DATA_STATUS[key] = {"success": success, "detail": detail, "source": source}


def get_data_status() -> dict:
    return dict(_DATA_STATUS)


def get_fund_code(query: str) -> str:
    try:
        df = ak.fund_name_em()
        df["code"] = df["基金代码"].astype(str)
        exact = df[df["code"] == query]
        if not exact.empty:
            _record_status("fund_basic_info", True, f"精确匹配:{query}")
            return query
        match = df[df["code"].str.startswith(query)]
        if not match.empty:
            code = match.iloc[0]["code"]
            _record_status("fund_basic_info", True, f"前缀匹配:{code}")
            return code
        name_match = df[df["基金简称"].str.contains(query, na=False)]
        if not name_match.empty:
            code = name_match.iloc[0]["code"]
            _record_status("fund_basic_info", True, f"名称匹配:{code}")
            return code
    except Exception as e:
        _record_status("fund_basic_info", False, str(e))
        raise RuntimeError(f"基金代码查询失败: {e}")
    _record_status("fund_basic_info", False, "未找到匹配基金")
    raise ValueError(f"未找到匹配基金: {query}")


def get_fund_name(code: str) -> str:
    df = ak.fund_name_em()
    df["code"] = df["基金代码"].astype(str)
    match = df[df["code"] == code]
    return match.iloc[0]["基金简称"] if not match.empty else code


def get_fund_category(code: str) -> str:
    df = ak.fund_name_em()
    df["code"] = df["基金代码"].astype(str)
    match = df[df["code"] == code]
    return match.iloc[0].get("基金类型", "未知") if not match.empty else "未知"


_FUND_INFO_CACHE = {}


def get_fund_info(code: str) -> dict:
    if code in _FUND_INFO_CACHE:
        return _FUND_INFO_CACHE[code]
    info = {"code": code, "name": code, "category": "未知"}
    try:
        info["name"] = get_fund_name(code)
    except Exception:
        pass
    try:
        info["category"] = get_fund_category(code)
    except Exception:
        pass
    _FUND_INFO_CACHE[code] = info
    return info


def get_nav_history(code: str) -> pd.DataFrame:
    try:
        df = ak.fund_open_fund_info_em(symbol=code, indicator="累计净值走势", period="成立来")
        df.rename(columns={"净值日期": "date", "累计净值": "acc_nav"}, inplace=True)
        df["date"] = pd.to_datetime(df["date"])
        df.sort_values("date", inplace=True)
        df["acc_nav"] = pd.to_numeric(df["acc_nav"], errors="coerce")
        df["daily_return"] = df["acc_nav"].pct_change() * 100
        _record_status("nav_history", True, f"{len(df)}条记录")
        return df
    except Exception as e:
        _record_status("nav_history", False, str(e))
        raise RuntimeError(f"净值数据获取失败 {code}: {e}")


def get_portfolio_holdings(code: str) -> list:
    years = [datetime.now().year, datetime.now().year - 1]
    for y in years:
        try:
            df = ak.fund_portfolio_hold_em(symbol=code, date=str(y))
            if not df.empty:
                df["占净值比例"] = pd.to_numeric(df.get("占净值比例", 0), errors="coerce")
                result = df.sort_values("占净值比例", ascending=False).to_dict("records")
                _record_status("portfolio_holdings", True, f"{len(df)}只持仓（{y}年）")
                return result
        except Exception:
            continue
    _record_status("portfolio_holdings", False, "未获取到持仓数据")
    return []


def get_fund_latest_status(code: str) -> dict:
    try:
        df = ak.fund_open_fund_daily_em()
        row = df[df["基金代码"].astype(str) == code]
        if row.empty:
            _record_status("fund_status", False, "代码未在日行情列表中找到")
            return {}
        r = row.iloc[0]
        result = {}
        for col in r.index:
            val = r[col]
            if isinstance(val, str) and val.replace(".", "").replace("-", "").isdigit():
                result[col] = float(val)
            else:
                result[col] = str(val)
        _record_status("fund_status", True, "已获取申购/赎回状态")
        return result
    except Exception as e:
        _record_status("fund_status", False, str(e))
        return {}


def get_market_index_history(symbol: str = "000300", years: int = 10) -> pd.DataFrame:
    try:
        end = datetime.now().strftime("%Y%m%d")
        start = (datetime.now() - pd.DateOffset(years=years)).strftime("%Y%m%d")
        df = ak.stock_zh_index_hist_csindex(symbol=symbol, start_date=start, end_date=end)
        df.rename(columns={"日期": "date", "收盘": "close"}, inplace=True)
        df["date"] = pd.to_datetime(df["date"])
        df["close"] = pd.to_numeric(df["close"], errors="coerce")
        df.sort_values("date", inplace=True)
        _record_status("market_index", True, f"沪深300: {len(df)}条")
        return df
    except Exception as e:
        _record_status("market_index", False, str(e))
        return pd.DataFrame()


def get_industry_allocation(code: str) -> list:
    years = [datetime.now().year, datetime.now().year - 1]
    all_dfs = []
    for y in years:
        try:
            df = ak.fund_portfolio_industry_allocation_em(symbol=code, date=str(y))
            if not df.empty:
                all_dfs.append(df)
        except Exception:
            continue
    if not all_dfs:
        _record_status("industry_allocation", False, "未获取到行业配置数据")
        return []
    combined = pd.concat(all_dfs, ignore_index=True)
    combined["占净值比例"] = pd.to_numeric(combined.get("占净值比例", 0), errors="coerce")
    combined["截止时间"] = pd.to_datetime(combined.get("截止时间", combined.get("date", "2025-01-01")))
    _record_status("industry_allocation", True, f"{len(all_dfs)}季度行业配置")
    return combined.to_dict("records")


def get_peer_nav_history(category: str, max_peers: int = 15) -> dict:
    try:
        df = ak.fund_name_em()
        df["code"] = df["基金代码"].astype(str)

        candidates = df[df["基金类型"] == category]
        match_method = "精确匹配"

        if len(candidates) < 5:
            prefix = category.split("-")[0] if "-" in category else category
            candidates = df[df["基金类型"].str.contains(prefix, na=False)]
            match_method = f"前缀匹配({prefix}), 精确匹配池不足"

        if candidates.empty:
            _record_status("peer_nav_history", False, f"分类'{category}'未找到同类基金")
            return {}

        if len(candidates) > max_peers:
            candidates = candidates.sample(n=max_peers, random_state=42)
            match_method += ", 随机抽样"

        codes = candidates["基金代码"].astype(str).tolist()

        _record_status(
            "peer_nav_history",
            True,
            f"{match_method}: 备选{len(codes)}只, 分类'{category}'",
        )
    except Exception as e:
        _record_status("peer_nav_history", False, str(e))
        return {}

    result = {}
    fetch_success = 0
    for code in codes:
        try:
            result[code] = get_nav_history(code)
            fetch_success += 1
        except Exception:
            continue
        if len(result) >= max_peers:
            break

    _record_status(
        "peer_nav_history",
        fetch_success > 0,
        f"实际拉取{fetch_success}/{len(codes)}只同类净值, 分类'{category}'",
    )
    return result
