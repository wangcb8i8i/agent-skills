import time
import akshare as ak
import pandas as pd
import numpy as np
import re
from datetime import datetime

from ._base import _record_status


_FUND_INFO_CACHE = {}


def _ak_get_fund_code(query: str) -> str:
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
    _record_status("fund_basic_info", False, "未找到匹配基金")
    raise ValueError(f"未找到匹配基金: {query}")


def _ak_get_fund_name(code: str) -> str:
    df = ak.fund_name_em()
    df["code"] = df["基金代码"].astype(str)
    match = df[df["code"] == code]
    return match.iloc[0]["基金简称"] if not match.empty else code


def _ak_get_fund_category(code: str) -> str:
    df = ak.fund_name_em()
    df["code"] = df["基金代码"].astype(str)
    match = df[df["code"] == code]
    return match.iloc[0].get("基金类型", "未知") if not match.empty else "未知"


def _ak_get_fund_info(code: str) -> dict:
    if code in _FUND_INFO_CACHE:
        return _FUND_INFO_CACHE[code]
    info = {"code": code, "name": code, "category": "未知"}
    try:
        info["name"] = _ak_get_fund_name(code)
    except Exception:
        pass
    try:
        info["category"] = _ak_get_fund_category(code)
    except Exception:
        pass
    _FUND_INFO_CACHE[code] = info
    return info


def _ak_get_nav_history(code: str) -> pd.DataFrame:
    # 累计净值 — 用于区间总收益计算（excess_return 等）
    df_acc = ak.fund_open_fund_info_em(symbol=code, indicator="累计净值走势", period="成立来")
    df_acc.rename(columns={"净值日期": "date", "累计净值": "acc_nav"}, inplace=True)

    # 单位净值 + 日增长率 — 用于日收益率计算（volatility、VaR、IR 等）
    time.sleep(0.3)
    df_unit = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势", period="成立来")

    df = pd.merge(df_acc, df_unit, on="净值日期", how="outer")
    df["date"] = pd.to_datetime(df["date"])
    df.sort_values("date", inplace=True)
    df["acc_nav"] = pd.to_numeric(df["acc_nav"], errors="coerce")
    # 日增长率来自东方财富，即 unit_nav.pct_change()，是正确的日收益率
    df["daily_return"] = pd.to_numeric(df["日增长率"], errors="coerce")
    _record_status("nav_history", True, f"{len(df)}条记录")
    return df[["date", "acc_nav", "daily_return"]].dropna(subset=["acc_nav"])


def _ak_get_portfolio_holdings(code: str) -> list:
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


def _ak_get_fund_latest_status(code: str) -> dict:
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


def _ak_get_market_index_history(symbol: str = "000300", years: int = 10) -> pd.DataFrame:
    end = datetime.now().strftime("%Y%m%d")
    start = (datetime.now() - pd.DateOffset(years=years)).strftime("%Y%m%d")
    df = ak.stock_zh_index_hist_csindex(symbol=symbol, start_date=start, end_date=end)
    df.rename(columns={"日期": "date", "收盘": "close"}, inplace=True)
    df["date"] = pd.to_datetime(df["date"])
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df.sort_values("date", inplace=True)
    _record_status("market_index", True, f"沪深300: {len(df)}条")
    return df


def _ak_get_industry_allocation(code: str) -> list:
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


def _ak_get_fund_scale(code: str) -> dict:
    df = ak.fund_scale_em()
    row = df[df["基金代码"].astype(str) == code]
    if row.empty:
        _record_status("fund_scale", False, "代码未在规模列表中找到")
        return {"scale": None, "unit": "亿元", "category": None}
    r = row.iloc[0]
    scale_cols = [c for c in df.columns if "规模" in c or "净值" in c]
    scale = None
    for col in scale_cols:
        try:
            scale = float(r[col])
            break
        except (ValueError, TypeError):
            continue
    if scale is None and "基金规模" in r:
        scale = float(r["基金规模"])
    _record_status("fund_scale", scale is not None, f"规模: {scale}亿元" if scale else "解析失败")
    return {
        "scale": scale,
        "unit": "亿元",
        "category": str(r.get("基金类型", "")) if not row.empty else None,
    }


def _ak_get_manager_info(code: str) -> dict:
    df = ak.fund_manager_em()
    managers = df[df["基金代码"].astype(str) == code]
    if managers.empty:
        _record_status("manager_info", False, "未找到经理信息")
        return {"managers": [], "tenure_years": None, "count": 0}
    result = []
    max_tenure = 0.0
    for _, r in managers.iterrows():
        tenure_str = str(r.get("任职日期", "") or r.get("任职时间", "") or "未知")
        tenure_years = None
        try:
            nums = re.findall(r"[\d.]+", tenure_str)
            if "年" in tenure_str and len(nums) >= 1:
                tenure_years = float(nums[0])
            elif nums:
                tenure_years = float(nums[0])
        except (ValueError, IndexError):
            pass
        if tenure_years and tenure_years > max_tenure:
            max_tenure = tenure_years
        result.append({
            "name": str(r.get("基金经理", "") or r.get("姓名", "") or "未知"),
            "tenure_years": tenure_years,
            "tenure_raw": tenure_str,
        })
    _record_status("manager_info", True, f"{len(result)}位经理, 最长{max_tenure}年")
    return {"managers": result, "tenure_years": max_tenure, "count": len(result)}


def _ak_get_institutional_ratio(code: str) -> dict:
    df = ak.fund_hold_structure_em(symbol=code)
    if df.empty:
        _record_status("inst_ratio", False, "无持有人结构数据")
        return {"institutional_pct": None, "internal_pct": None}
    inst_cols = [c for c in df.columns if "机构" in c]
    internal_cols = [c for c in df.columns if "内部" in c or "管理人" in c]
    inst_pct = None
    internal_pct = None
    if inst_cols:
        latest = df.iloc[-1]
        inst_pct = float(latest[inst_cols[0]]) if inst_cols[0] in latest else None
    if internal_cols:
        latest = df.iloc[-1]
        internal_pct = float(latest[internal_cols[0]]) if internal_cols[0] in latest else None
    _record_status("inst_ratio", inst_pct is not None, f"机构: {inst_pct}%")
    return {"institutional_pct": inst_pct, "internal_pct": internal_pct}


def _ak_get_turnover_rate(code: str) -> dict:
    df = ak.fund_portfolio_turnover_em(symbol=code)
    if df.empty:
        _record_status("turnover", False, "无换手率数据")
        return {"turnover_rate": None, "period": None}
    rate_cols = [c for c in df.columns if "换手" in c]
    if not rate_cols:
        _record_status("turnover", False, "未识别到换手率列")
        return {"turnover_rate": None, "period": None}
    latest_rate = float(df.iloc[-1][rate_cols[0]])
    _record_status("turnover", True, f"换手率: {latest_rate}%")
    return {
        "turnover_rate": latest_rate,
        "period": str(df.iloc[-1].get("截止时间", df.iloc[-1].get("date", ""))),
    }


def _ak_get_fee_rate(code: str) -> dict:
    df = ak.fund_name_em()
    row = df[df["基金代码"].astype(str) == code]
    if row.empty:
        _record_status("fee_rate", False, "代码未找到")
        return {"management_fee": None, "custodian_fee": None, "total_fee": None}
    r = row.iloc[0]
    mgmt_str = str(r.get("管理费率", "0") or "0").replace("%", "")
    cust_str = str(r.get("托管费率", "0") or "0").replace("%", "")
    try:
        mgmt = float(mgmt_str)
    except ValueError:
        mgmt = None
    try:
        cust = float(cust_str)
    except ValueError:
        cust = None
    total = (mgmt or 0) + (cust or 0)
    _record_status("fee_rate", True, f"管理{mgmt}%+托管{cust}%={total}%")
    return {"management_fee": mgmt, "custodian_fee": cust, "total_fee": total}


def _ak_get_scale_history(code: str) -> list:
    df = ak.fund_scale_change_em()
    rows = df[df["基金代码"].astype(str) == code]
    if rows.empty:
        _record_status("scale_history", False, "无规模历史数据")
        return []
    result = []
    for _, r in rows.iterrows():
        try:
            scale = float(str(r.get("基金规模", "0")).replace(",", ""))
            date = str(r.get("日期", r.get("截止时间", "")))
            result.append({"date": date, "scale": scale})
        except (ValueError, TypeError):
            continue
    _record_status("scale_history", True, f"{len(result)}期规模数据")
    return result


def _ak_get_peer_nav_history(category: str, max_peers: int = 15) -> dict:
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

    result = {}
    fetch_success = 0
    for code in codes:
        try:
            result[code] = _ak_get_nav_history(code)
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
