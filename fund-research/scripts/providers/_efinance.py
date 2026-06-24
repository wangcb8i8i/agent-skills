import efinance as ef
import pandas as pd
import numpy as np
import re
from datetime import datetime

from ._base import _record_status


def _ef_get_fund_code(query: str) -> str:
    df = ef.fund.get_fund_codes()
    df["code"] = df["基金代码"].astype(str)
    exact = df[df["code"] == query]
    if not exact.empty:
        _record_status("fund_basic_info", True, f"精确匹配:{query}", source="efinance")
        return query
    match = df[df["code"].str.startswith(query)]
    if not match.empty:
        code = match.iloc[0]["code"]
        _record_status("fund_basic_info", True, f"前缀匹配:{code}", source="efinance")
        return code
    name_match = df[df["基金简称"].str.contains(query, na=False)]
    if not name_match.empty:
        code = name_match.iloc[0]["code"]
        _record_status("fund_basic_info", True, f"名称匹配:{code}", source="efinance")
        return code
    raise ValueError(f"未找到匹配基金: {query}")


def _ef_get_fund_name(code: str) -> str:
    codes_df = ef.fund.get_fund_codes()
    codes_df["code"] = codes_df["基金代码"].astype(str)
    match = codes_df[codes_df["code"] == code]
    if not match.empty:
        return match.iloc[0]["基金简称"]
    return code


def _ef_get_fund_category(code: str) -> str:
    codes_df = ef.fund.get_fund_codes()
    codes_df["code"] = codes_df["基金代码"].astype(str)
    match = codes_df[codes_df["code"] == code]
    if not match.empty:
        return match.iloc[0].get("基金类型", "未知")
    return "未知"


_FUND_INFO_CACHE_EF = {}


def _ef_get_fund_info(code: str) -> dict:
    if code in _FUND_INFO_CACHE_EF:
        return _FUND_INFO_CACHE_EF[code]
    info = {"code": code, "name": code, "category": "未知"}
    try:
        info["name"] = _ef_get_fund_name(code)
    except Exception:
        pass
    try:
        info["category"] = _ef_get_fund_category(code)
    except Exception:
        pass
    _FUND_INFO_CACHE_EF[code] = info
    return info


def _ef_get_nav_history(code: str) -> pd.DataFrame:
    df = ef.fund.get_quote_history(code)
    df.rename(columns={"日期": "date", "累计净值": "acc_nav"}, inplace=True)
    df["date"] = pd.to_datetime(df["date"])
    df["acc_nav"] = pd.to_numeric(df["acc_nav"], errors="coerce")
    df.sort_values("date", inplace=True)
    df["daily_return"] = df["acc_nav"].pct_change() * 100
    df = df[["date", "acc_nav", "daily_return"]].dropna(subset=["acc_nav"])
    _record_status("nav_history", True, f"{len(df)}条记录", source="efinance")
    return df


def _ef_get_portfolio_holdings(code: str) -> list:
    df = ef.fund.get_invest_position(code)
    if df.empty:
        _record_status("portfolio_holdings", False, "efinance 无持仓数据", source="efinance")
        return []
    df.rename(columns={"持仓占比": "占净值比例"}, inplace=True)
    df["占净值比例"] = pd.to_numeric(df.get("占净值比例", 0), errors="coerce")
    result = df.sort_values("占净值比例", ascending=False).to_dict("records")
    _record_status("portfolio_holdings", True, f"{len(df)}只持仓", source="efinance")
    return result


def _ef_get_market_index_history(symbol: str = "000300", years: int = 10) -> pd.DataFrame:
    end = datetime.now()
    start = end - pd.DateOffset(years=years)
    df = ef.stock.get_quote_history(
        symbol,
        beg=start.strftime("%Y%m%d"),
        end=end.strftime("%Y%m%d"),
    )
    if df.empty:
        _record_status("market_index", False, "efinance 无指数数据", source="efinance")
        return pd.DataFrame()
    df.rename(columns={"日期": "date", "收盘": "close"}, inplace=True)
    df["date"] = pd.to_datetime(df["date"])
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df.sort_values("date", inplace=True)
    _record_status("market_index", True, f"沪深300: {len(df)}条", source="efinance")
    return df


def _ef_get_industry_allocation(code: str) -> list:
    dates = ef.fund.get_public_dates(code)
    if not dates:
        _record_status("industry_allocation", False, "efinance 无行业数据", source="efinance")
        return []
    recent_dates = [d for d in dates if d.startswith(str(datetime.now().year)) or d.startswith(str(datetime.now().year - 1))]
    if not recent_dates:
        recent_dates = dates[:2]
    all_dfs = []
    for d in recent_dates:
        try:
            df = ef.fund.get_industry_distribution(code, dates=[d])
            if not df.empty:
                all_dfs.append(df)
        except Exception:
            continue
    if not all_dfs:
        _record_status("industry_allocation", False, "未获取到行业配置数据", source="efinance")
        return []
    combined = pd.concat(all_dfs, ignore_index=True)
    combined.rename(columns={
        "行业名称": "行业类别",
        "持仓比例": "占净值比例",
        "公布日期": "截止时间",
    }, inplace=True)
    combined["占净值比例"] = pd.to_numeric(combined.get("占净值比例", 0), errors="coerce")
    combined["截止时间"] = pd.to_datetime(combined.get("截止时间", "2025-01-01"))
    _record_status("industry_allocation", True, f"{len(all_dfs)}季度行业配置", source="efinance")
    return combined.to_dict("records")


def _ef_get_manager_info(code: str) -> dict:
    df = ef.fund.get_fund_manager(code)
    if df.empty:
        _record_status("manager_info", False, "efinance 无经理信息", source="efinance")
        return {"managers": [], "tenure_years": None, "count": 0}
    result = []
    max_tenure = 0.0
    for _, r in df.iterrows():
        tenure_str = str(r.get("基金经理任职日期", "未知"))
        tenure_years = None
        try:
            start = pd.to_datetime(tenure_str)
            tenure_years = round((datetime.now() - start).days / 365, 1)
        except (ValueError, TypeError):
            try:
                nums = re.findall(r"[\d.]+", tenure_str)
                if nums:
                    tenure_years = float(nums[0])
            except (ValueError, IndexError):
                pass
        if tenure_years and tenure_years > max_tenure:
            max_tenure = tenure_years
        result.append({
            "name": str(r.get("基金经理", "未知")),
            "tenure_years": tenure_years,
            "tenure_raw": tenure_str,
        })
    _record_status("manager_info", True, f"{len(result)}位经理, 最长{max_tenure}年", source="efinance")
    return {"managers": result, "tenure_years": max_tenure, "count": len(result)}


def _ef_get_peer_nav_history(category: str, max_peers: int = 15) -> dict:
    df = ef.fund.get_fund_codes()
    df["code"] = df["基金代码"].astype(str)

    candidates = df[df["基金类型"] == category]
    match_method = "精确匹配"

    if len(candidates) < 5:
        prefix = category.split("-")[0] if "-" in category else category
        candidates = df[df["基金类型"].str.contains(prefix, na=False)]
        match_method = f"前缀匹配({prefix}), 精确匹配池不足"

    if candidates.empty:
        _record_status("peer_nav_history", False, f"分类'{category}'未找到同类基金", source="efinance")
        return {}

    if len(candidates) > max_peers:
        candidates = candidates.sample(n=max_peers, random_state=42)
        match_method += ", 随机抽样"

    codes = candidates["code"].tolist()
    _record_status("peer_nav_history", True, f"{match_method}: 备选{len(codes)}只, 分类'{category}'", source="efinance")

    result = {}
    fetch_success = 0
    for code in codes:
        try:
            result[code] = _ef_get_nav_history(code)
            fetch_success += 1
        except Exception:
            continue
        if len(result) >= max_peers:
            break

    _record_status("peer_nav_history", fetch_success > 0, f"实际拉取{fetch_success}/{len(codes)}只同类净值, 分类'{category}'", source="efinance")
    return result
