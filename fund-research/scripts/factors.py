import numpy as np
import pandas as pd
from scipy import stats
from config import WINDOWS, PEER_RANK_BINS


def _window_slice(df: pd.DataFrame, days: int):
    cutoff = df["date"].max() - pd.Timedelta(days=days)
    return df[df["date"] >= cutoff].copy()


def _rank_bin(pct: float) -> str:
    if pct is None:
        return "N/A"
    if pct >= 75:
        return "前25%"
    elif pct >= 50:
        return "中位偏上"
    elif pct >= 25:
        return "中位偏下"
    else:
        return "后25%"


def excess_return(nav: pd.DataFrame, peer_median: pd.Series = None) -> dict:
    result = {}
    for label, days in WINDOWS.items():
        w = _window_slice(nav, days)
        if len(w) < 2:
            result[label] = None
            continue
        fund_ret = w["acc_nav"].iloc[-1] / w["acc_nav"].iloc[0] - 1
        peer_ret = None
        if peer_median is not None:
            w_start = w["date"].min()
            w_end = w["date"].max()
            peer_window = peer_median[(peer_median.index >= w_start) & (peer_median.index <= w_end)]
            if len(peer_window) >= 2:
                peer_ret = peer_window.iloc[-1] / peer_window.iloc[0] - 1
        result[label] = {
            "fund_return": round(fund_ret * 100, 2),
            "peer_return": round(peer_ret * 100, 2) if peer_ret is not None else None,
            "excess": round((fund_ret - (peer_ret or 0)) * 100, 2),
        }
    return result


def information_ratio(nav: pd.DataFrame, peer_median: pd.Series = None) -> dict:
    result = {}
    for label, days in WINDOWS.items():
        w = _window_slice(nav, days)
        if len(w) < 20:
            result[label] = None
            continue
        rets = w.set_index("date")["daily_return"].dropna()
        if peer_median is not None:
            w_start = w["date"].min()
            w_end = w["date"].max()
            peer_window = peer_median[(peer_median.index >= w_start) & (peer_median.index <= w_end)]
            peer_rets = peer_window.pct_change().dropna() * 100
            aligned = pd.concat([rets, peer_rets], axis=1, join="inner").dropna()
            if len(aligned) < 20:
                result[label] = None
                continue
            excess = aligned.iloc[:, 0] - aligned.iloc[:, 1]
        else:
            excess = rets
        ir = excess.mean() / (excess.std() + 1e-10)
        result[label] = round(ir * np.sqrt(252), 2)
    return result


def max_drawdown(nav: pd.DataFrame) -> dict:
    result = {}
    for label, days in WINDOWS.items():
        w = _window_slice(nav, days)
        if len(w) < 2:
            result[label] = None
            continue
        peak = w["acc_nav"].cummax()
        dd = (w["acc_nav"] - peak) / peak
        result[label] = round(dd.min() * 100, 2)
    return result


def volatility(nav: pd.DataFrame) -> dict:
    result = {}
    for label, days in WINDOWS.items():
        w = _window_slice(nav, days)
        if len(w) < 20:
            result[label] = None
            continue
        vol = w["daily_return"].dropna().std() * np.sqrt(252)
        result[label] = round(vol, 2)
    return result


def downside_deviation(nav: pd.DataFrame, mar: float = 0.0) -> dict:
    result = {}
    for label, days in WINDOWS.items():
        w = _window_slice(nav, days)
        if len(w) < 20:
            result[label] = None
            continue
        rets = w["daily_return"].dropna()
        mar_daily = mar / 252
        downside = rets[rets < mar_daily]
        if len(downside) < 2:
            result[label] = 0.0
            continue
        dd = np.sqrt((downside.sub(mar_daily) ** 2).mean()) * np.sqrt(252)
        result[label] = round(dd, 2)
    return result


def var_historical(nav: pd.DataFrame, confidence: float = 0.95) -> dict:
    result = {}
    for label, days in WINDOWS.items():
        w = _window_slice(nav, days)
        if len(w) < 20:
            result[label] = None
            continue
        rets = w["daily_return"].dropna()
        result[label] = round(rets.quantile(1 - confidence), 2)
    return result


def recovery_time(nav: pd.DataFrame) -> dict:
    w = _window_slice(nav, 756)
    if len(w) < 2:
        return {"3y": None}
    peak = w["acc_nav"].cummax()
    dd = (w["acc_nav"] - peak) / peak
    max_dd_idx = dd.idxmin()
    if pd.isna(max_dd_idx):
        return {"3y": None}
    max_dd_row = w.loc[max_dd_idx]
    dd_start = w.loc[:max_dd_idx][w.loc[:max_dd_idx, "acc_nav"] == w.loc[:max_dd_idx, "acc_nav"].max()]
    if dd_start.empty:
        return {"3y": None}
    dd_start_date = dd_start.index[-1] if isinstance(dd_start.index[-1], pd.Timestamp) else None
    if dd_start_date is None:
        dd_start_date = dd_start.iloc[0]["date"]
    recovery_candidates = w.loc[max_dd_idx:]
    recovered = recovery_candidates[recovery_candidates["acc_nav"] >= w.loc[max_dd_idx, "acc_nav"]]
    if recovered.empty:
        return {"3y": None}
    days = (recovered.iloc[0]["date"] - dd_start_date).days
    return {"3y": days}


def fund_flow_score(status: dict, scale_history: list = None,
                    institutional_data: dict = None) -> dict:
    purchase = status.get("申购状态", "未知")
    redeem = status.get("赎回状态", "未知")
    restrictions = []
    if "限" in purchase or "暂停" in purchase:
        restrictions.append(f"申购:{purchase}")
    if "限" in redeem or "暂停" in redeem:
        restrictions.append(f"赎回:{redeem}")

    scale_trend = None
    if scale_history and len(scale_history) >= 2:
        sorted_scales = sorted(scale_history, key=lambda x: x.get("date", ""))
        if len(sorted_scales) >= 2:
            recent = sorted_scales[-1].get("scale", 0)
            prev = sorted_scales[-2].get("scale", 0)
            if prev > 0:
                ratio = recent / prev
                if ratio > 1.5:
                    scale_trend = "暴增"
                elif ratio < 0.7:
                    scale_trend = "锐减"
                else:
                    scale_trend = "稳定"

    institutional_trend = None
    if institutional_data:
        inst_pct = institutional_data.get("institutional_pct")
        internal_pct = institutional_data.get("internal_pct")
    else:
        inst_pct = None
        internal_pct = None

    return {
        "purchase_status": purchase,
        "redeem_status": redeem,
        "restrictions": restrictions if restrictions else "正常",
        "scale_trend": scale_trend,
        "institutional_pct": inst_pct,
        "internal_pct": internal_pct,
        "institutional_trend": institutional_trend,
    }


def concentration_risk(holdings: list) -> dict:
    if not holdings:
        return {"top10_pct": None, "top3_industry": None}
    top10 = holdings[:10]
    top10_pct = sum(h.get("占净值比例", 0) for h in top10)
    return {
        "top10_pct": round(top10_pct, 2),
        "count": len(holdings),
    }


def industry_analysis(industry_data: list) -> dict:
    if not industry_data:
        return {"top3_pct": None, "drift": None, "latest_quarter": None}
    df = pd.DataFrame(industry_data)
    if df.empty:
        return {"top3_pct": None, "drift": None, "latest_quarter": None}
    latest = df[df["截止时间"] == df["截止时间"].max()].sort_values("占净值比例", ascending=False)
    h3_pct = latest.head(3)["占净值比例"].sum() if len(latest) >= 3 else None
    quarters = df["截止时间"].unique()
    if len(quarters) >= 2:
        q0 = df[df["截止时间"] == quarters[-1]].set_index("行业类别")["占净值比例"].fillna(0)
        q1 = df[df["截止时间"] == quarters[-2]].set_index("行业类别")["占净值比例"].fillna(0)
        all_industries = pd.concat([q0, q1], axis=1, join="outer").fillna(0)
        drift = abs(all_industries.iloc[:, 0] - all_industries.iloc[:, 1]).sum() / 2
    else:
        drift = None
    return {
        "top3_pct": round(h3_pct, 2) if h3_pct is not None else None,
        "drift": round(drift, 2) if drift is not None else None,
        "latest_quarter": str(quarters[-1])[:7] if len(quarters) > 0 else None,
    }


def _compute_single_fund_factors(nav: pd.DataFrame, peer_median: pd.Series = None) -> dict:
    if nav.empty:
        return {}
    return {
        "excess_return": excess_return(nav, peer_median),
        "information_ratio": information_ratio(nav, peer_median),
        "max_drawdown": max_drawdown(nav),
        "volatility": volatility(nav),
        "downside_deviation": downside_deviation(nav),
        "var_95": var_historical(nav),
        "recovery_time": recovery_time(nav),
        "calmar_ratio": calmar_ratio(nav),
    }


def _extract_factor_value(factor_result, window="3y") -> float:
    if factor_result is None:
        return None
    if isinstance(factor_result, dict):
        v = factor_result.get(window)
        if isinstance(v, dict):
            return v.get("excess") or v.get("fund_return")
        return v
    return None


def _compute_percentile(fund_val: float, peer_vals: list) -> float:
    if fund_val is None or not peer_vals:
        return None
    valid = [v for v in peer_vals if v is not None]
    if len(valid) < 3:
        return None
    below = sum(1 for v in valid if v <= fund_val)
    return round(below / len(valid) * 100, 1)


def compute_percentiles(fund_factors: dict, peer_navs: dict, peer_median: pd.Series = None) -> dict:
    peer_factor_values = {
        "excess_return_3y": [],
        "information_ratio_3y": [],
        "max_drawdown_3y": [],
        "volatility_3y": [],
        "downside_deviation_3y": [],
        "var_95_3y": [],
        "recovery_time_3y": [],
        "calmar_ratio_3y": [],
    }

    for code, pnav in peer_navs.items():
        if pnav is None or pnav.empty:
            continue
        pfactors = _compute_single_fund_factors(pnav, peer_median)
        er = _extract_factor_value(pfactors.get("excess_return"))
        if er is not None:
            peer_factor_values["excess_return_3y"].append(er)
        ir_val = pfactors.get("information_ratio", {}).get("3y")
        if ir_val is not None:
            peer_factor_values["information_ratio_3y"].append(ir_val)
        dd_val = pfactors.get("max_drawdown", {}).get("3y")
        if dd_val is not None:
            peer_factor_values["max_drawdown_3y"].append(dd_val)
        vol_val = pfactors.get("volatility", {}).get("3y")
        if vol_val is not None:
            peer_factor_values["volatility_3y"].append(vol_val)
        dv_val = pfactors.get("downside_deviation", {}).get("3y")
        if dv_val is not None:
            peer_factor_values["downside_deviation_3y"].append(dv_val)
        var_val = pfactors.get("var_95", {}).get("3y")
        if var_val is not None:
            peer_factor_values["var_95_3y"].append(var_val)
        rt_val = pfactors.get("recovery_time", {}).get("3y")
        if rt_val is not None:
            peer_factor_values["recovery_time_3y"].append(rt_val)
        cr_val = pfactors.get("calmar_ratio", {}).get("3y")
        if cr_val is not None:
            peer_factor_values["calmar_ratio_3y"].append(cr_val)

    percentiles = {}
    fund_er = _extract_factor_value(fund_factors.get("excess_return"))
    percentiles["excess_return"] = {
        "pct": _compute_percentile(fund_er, peer_factor_values["excess_return_3y"]),
        "rank": _rank_bin(_compute_percentile(fund_er, peer_factor_values["excess_return_3y"])),
    }
    fund_ir = fund_factors.get("information_ratio", {}).get("3y")
    percentiles["information_ratio"] = {
        "pct": _compute_percentile(fund_ir, peer_factor_values["information_ratio_3y"]),
        "rank": _rank_bin(_compute_percentile(fund_ir, peer_factor_values["information_ratio_3y"])),
    }
    fund_dd = fund_factors.get("max_drawdown", {}).get("3y")
    dd_pct = _compute_percentile(fund_dd, peer_factor_values["max_drawdown_3y"])
    percentiles["max_drawdown"] = {
        "pct": dd_pct,
        "rank": _rank_bin(100 - dd_pct if dd_pct is not None else None),
    }
    fund_vol = fund_factors.get("volatility", {}).get("3y")
    vol_pct = _compute_percentile(fund_vol, peer_factor_values["volatility_3y"])
    percentiles["volatility"] = {
        "pct": vol_pct,
        "rank": _rank_bin(100 - vol_pct if vol_pct is not None else None),
    }
    fund_dv = fund_factors.get("downside_deviation", {}).get("3y")
    dv_pct = _compute_percentile(fund_dv, peer_factor_values["downside_deviation_3y"])
    percentiles["downside_deviation"] = {
        "pct": dv_pct,
        "rank": _rank_bin(100 - dv_pct if dv_pct is not None else None),
    }
    fund_var95 = fund_factors.get("var_95", {}).get("3y")
    var_pct = _compute_percentile(fund_var95, peer_factor_values["var_95_3y"])
    percentiles["var_95"] = {
        "pct": var_pct,
        "rank": _rank_bin(100 - var_pct if var_pct is not None else None),
    }
    fund_rt = fund_factors.get("recovery_time", {}).get("3y")
    rt_pct = _compute_percentile(fund_rt, peer_factor_values["recovery_time_3y"])
    percentiles["recovery_time"] = {
        "pct": rt_pct,
        "rank": _rank_bin(100 - rt_pct if rt_pct is not None else None),
    }
    fund_cr = fund_factors.get("calmar_ratio", {}).get("3y")
    cr_pct = _compute_percentile(fund_cr, peer_factor_values["calmar_ratio_3y"])
    percentiles["calmar_ratio"] = {
        "pct": cr_pct,
        "rank": _rank_bin(cr_pct if cr_pct is not None else None),
    }

    return percentiles


def calmar_ratio(nav: pd.DataFrame) -> dict:
    result = {}
    for label, days in WINDOWS.items():
        w = _window_slice(nav, days)
        if len(w) < 2:
            result[label] = None
            continue
        ann_ret = (w["acc_nav"].iloc[-1] / w["acc_nav"].iloc[0]) ** (252 / max(len(w), 1)) - 1
        peak = w["acc_nav"].cummax()
        dd_series = (w["acc_nav"] - peak) / peak
        max_dd = abs(dd_series.min()) if len(dd_series) > 0 else 0
        if max_dd > 0:
            calmar = ann_ret / max_dd
        else:
            calmar = None
        result[label] = round(calmar, 2) if calmar is not None else None
    return result


def factor_exposure_stability(nav: pd.DataFrame) -> dict:
    if len(nav) < 504:
        return {"status": "数据不足", "detail": "少于2年历史，无法做因子暴露稳定性检验"}
    mid = nav["date"].max() - pd.Timedelta(days=756)
    h1 = nav[nav["date"] < mid].copy()
    h2 = nav[nav["date"] >= mid].copy()
    if len(h1) < 60 or len(h2) < 60:
        return {"status": "数据不足", "detail": "子窗口样本不足"}
    rets1 = h1["daily_return"].dropna()
    rets2 = h2["daily_return"].dropna()
    mean1, std1 = rets1.mean(), rets1.std()
    mean2, std2 = rets2.mean(), rets2.std()
    drift_detail = {}
    if std1 > 0 and std2 > 0:
        return_shift = abs(mean1 - mean2)
        vol_ratio = max(std1, std2) / min(std1, std2) if min(std1, std2) > 0 else 1
        drift_detail["return_shift"] = round(return_shift * 100, 2)
        drift_detail["vol_ratio"] = round(vol_ratio, 2)
        skw1 = rets1.skew()
        skw2 = rets2.skew()
        skew_shift = abs(skw1 - skw2)
        drift_detail["skew_shift"] = round(skew_shift, 2)
        issues = []
        if abs(return_shift * 100) > 0.05:
            issues.append(f"收益均值偏移{return_shift*100:.2f}bp")
        if vol_ratio > 1.5:
            issues.append(f"波动率比{vol_ratio:.2f}x")
        if skew_shift > 1.0:
            issues.append(f"偏度偏移{skew_shift:.2f}")
        if issues:
            return {"status": "预警" if len(issues) <= 2 else "漂移", "issues": issues, "drift_detail": drift_detail}
        return {"status": "稳定", "detail": "前后两期收益分布特征基本一致", "drift_detail": drift_detail}
    return {"status": "数据不足", "detail": "波动率异常"}


def compute_all_factors(nav: pd.DataFrame, peer_navs: dict = None,
                        holdings: list = None, status: dict = None,
                        industry_data: list = None,
                        scale_history: list = None,
                        institutional_data: dict = None) -> dict:
    if nav.empty:
        return {}

    peer_median = None
    peer_pool_size = 0
    peer_codes = []
    if peer_navs and len(peer_navs) > 0:
        fund_date_range = (nav["date"].min(), nav["date"].max())
        peers_aligned = []
        for code, pn in peer_navs.items():
            if pn is not None and len(pn) > 0 and "acc_nav" in pn.columns:
                p_start = pn["date"].min()
                p_end = pn["date"].max()
                overlap_days = (min(fund_date_range[1], p_end) - max(fund_date_range[0], p_start)).days
                if overlap_days > 180:
                    peers_aligned.append(pn.set_index("date")["acc_nav"])
                    peer_codes.append(code)
        peer_pool_size = len(peers_aligned)
        if len(peers_aligned) >= 3:
            peer_df = pd.concat(peers_aligned, axis=1, join="outer")
            peer_median = peer_df.median(axis=1)

    fund_factors = _compute_single_fund_factors(nav, peer_median)

    factors = {}
    factors.update(fund_factors)
    factors["fund_flow"] = fund_flow_score(status or {}, scale_history, institutional_data)
    factors["concentration"] = concentration_risk(holdings or [])
    factors["industry"] = industry_analysis(industry_data or [])
    factors["factor_exposure"] = factor_exposure_stability(nav)
    factors["calmar_ratio"] = calmar_ratio(nav)

    percentiles = {}
    if peer_pool_size >= 3:
        percentiles = compute_percentiles(fund_factors, peer_navs or {}, peer_median)
    factors["_percentiles"] = percentiles

    factors["_peer_pool"] = {
        "size": peer_pool_size,
        "codes": peer_codes,
        "representativeness": (
            "较好" if peer_pool_size >= 10 else
            "一般" if peer_pool_size >= 5 else
            "不足" if peer_pool_size >= 3 else "无同类数据"
        ),
    }

    return factors
