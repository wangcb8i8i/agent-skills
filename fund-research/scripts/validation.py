import numpy as np
import pandas as pd
from factors import max_drawdown, volatility, WINDOWS


def stability_check(nav: pd.DataFrame) -> dict:
    if len(nav) < 504:
        return {"status": "数据不足", "detail": "历史少于2年，无法做稳定性检验"}
    mid = nav["date"].max() - pd.Timedelta(days=756)
    h1 = nav[nav["date"] < mid].copy()
    h2 = nav[nav["date"] >= mid].copy()
    if len(h1) < 20 or len(h2) < 20:
        return {"status": "数据不足", "detail": "子窗口样本不足"}
    dd1 = min(max_drawdown(h1).values())
    dd2 = min(max_drawdown(h2).values())
    vol1 = volatility(h1).get("3y", 0)
    vol2 = volatility(h2).get("3y", 0)
    dd_change = abs((dd2 or 0) - (dd1 or 0))
    vol_change = abs((vol2 or 0) - (vol1 or 0))
    issues = []
    if dd_change > 15:
        issues.append(f"回撤特征变化较大({dd_change:.0f}%)")
    if vol_change > 10:
        issues.append(f"波动特征变化较大({vol_change:.0f}%)")
    if issues:
        return {"status": "预警", "issues": issues}
    return {"status": "通过", "detail": "前后两年因子特征基本一致"}


def scenario_analysis(nav: pd.DataFrame, market_index: pd.DataFrame = None) -> dict:
    if len(nav) < 252 or "daily_return" not in nav.columns:
        return {"status": "数据不足",
                "_note": "情景回测基于沪深300均线形态简化分类，非精确市场周期判定，仅供参考"}

    if market_index is None or market_index.empty:
        return {"status": "无市场指数数据",
                "_note": "情景回测基于沪深300均线形态简化分类，非精确市场周期判定，仅供参考"}

    idx = market_index.copy()
    idx["ma120"] = idx["close"].rolling(120).mean()
    idx["ma60"] = idx["close"].rolling(60).mean()
    idx["pct_6m"] = idx["close"].pct_change(periods=120).fillna(0)

    idx["market_phase"] = "震荡"
    idx.loc[(idx["close"] > idx["ma120"]) & (idx["pct_6m"] > 0.15), "market_phase"] = "牛市"
    idx.loc[(idx["close"] < idx["ma120"]) & (idx["pct_6m"] < -0.15), "market_phase"] = "熊市"

    phase_map = idx[["date", "market_phase"]].dropna()
    nav = nav.merge(phase_map, on="date", how="left")
    nav["market_phase"] = nav["market_phase"].fillna("震荡")

    phases = {}
    for phase in ["牛市", "熊市", "震荡"]:
        subset = nav[nav["market_phase"] == phase]
        if len(subset) < 20:
            phases[phase] = None
            continue
        ret = subset["daily_return"].dropna()
        n_days = len(ret)
        total_ret = (1 + ret / 100).prod() - 1
        ann_ret = (1 + total_ret) ** (252 / n_days) - 1 if n_days > 0 else 0
        phases[phase] = {
            "return_ann": round(ann_ret * 100, 2),
            "total_return": round(total_ret * 100, 2),
            "days": n_days,
            "period": f"{subset['date'].iloc[0].strftime('%Y%m')}-{subset['date'].iloc[-1].strftime('%Y%m')}",
            "volatility": round(ret.std() * np.sqrt(252), 2),
        }

    phases["_note"] = "情景回测基于沪深300均线形态简化分类（120日均线+6个月趋势），非精确市场周期判定。仅适用于股票型/偏股混合型基金，对债基/QDII/商品基金无参考意义。"
    return phases


def sensitivity_analysis(nav: pd.DataFrame) -> dict:
    mid = len(nav) // 2
    if mid < 100:
        return {"status": "数据不足"}
    h1 = nav.iloc[:mid].copy()
    h2 = nav.iloc[mid:].copy()
    dd1 = min(max_drawdown(h1).values()) or 0
    dd2 = min(max_drawdown(h2).values()) or 0
    vol1 = volatility(h1).get("3y", 0) or 0
    vol2 = volatility(h2).get("3y", 0) or 0
    flips = []
    if abs(dd2 - dd1) > 20:
        flips.append(f"回撤前后半段差异{abs(dd2-dd1):.0f}%")
    if abs(vol2 - vol1) > 15:
        flips.append(f"波动前后半段差异{abs(vol2-vol1):.0f}%")
    return {"flips": flips} if flips else {"flips": []}


def run_all_checks(nav: pd.DataFrame, market_index: pd.DataFrame = None) -> dict:
    return {
        "stability": stability_check(nav),
        "scenario": scenario_analysis(nav, market_index),
        "sensitivity": sensitivity_analysis(nav),
    }
