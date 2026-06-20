import numpy as np
from config import WEIGHTS, WINDOWS


def _rank_to_score(rank_str: str) -> float:
    mapping = {
        "前25%": 0.85,
        "中位偏上": 0.65,
        "中位偏下": 0.35,
        "后25%": 0.15,
        "N/A": 0.5,
    }
    return mapping.get(rank_str, 0.5)


def _percentile_directional_score(pct: float, lower_is_better: bool = False) -> float:
    if pct is None:
        return 0.5
    p = max(0, min(100, pct)) / 100
    if lower_is_better:
        p = 1 - p
    return round(p, 3)


def score_dimension(factors: dict, dim: str) -> dict:
    percentiles = factors.get("_percentiles", {})

    if dim == "return":
        er_pct = percentiles.get("excess_return", {})
        ir_pct = percentiles.get("information_ratio", {})
        er_score = _percentile_directional_score(er_pct.get("pct"))
        ir_score = _percentile_directional_score(ir_pct.get("pct"))
        rank = er_pct.get("rank", "N/A")
        detail_parts = []
        er_val = factors.get("excess_return", {}).get("3y", {})
        if isinstance(er_val, dict) and er_val.get("excess") is not None:
            detail_parts.append(f"超额{er_val['excess']}%")
        if ir_pct.get("pct") is not None:
            detail_parts.append(f"同类{rank}")
        detail = "; ".join(detail_parts) if detail_parts else "无数据"
        score = 0.6 * er_score + 0.4 * ir_score if ir_pct.get("pct") is not None else er_score
        return {"score": round(score, 3), "detail": detail, "rank": rank}

    elif dim == "risk":
        dd_pct = percentiles.get("max_drawdown", {})
        vol_pct = percentiles.get("volatility", {})
        dv_pct = percentiles.get("downside_deviation", {})
        dd_score = _percentile_directional_score(dd_pct.get("pct"), lower_is_better=True)
        vol_score = _percentile_directional_score(vol_pct.get("pct"), lower_is_better=True)
        dv_score = _percentile_directional_score(dv_pct.get("pct"), lower_is_better=True)
        rank = dd_pct.get("rank", "N/A")
        detail_parts = []
        dd_val = factors.get("max_drawdown", {}).get("3y")
        if dd_val is not None:
            detail_parts.append(f"最大回撤{dd_val}%")
        if dd_pct.get("pct") is not None:
            detail_parts.append(f"同类{rank}")
        detail = "; ".join(detail_parts) if detail_parts else "无数据"
        score = 0.5 * dd_score + 0.25 * vol_score + 0.25 * dv_score
        return {"score": round(score, 3), "detail": detail, "rank": rank}

    elif dim == "quality":
        rt_pct = percentiles.get("recovery_time", {})
        score = _percentile_directional_score(rt_pct.get("pct"), lower_is_better=True)
        rank = rt_pct.get("rank", "N/A")
        detail_parts = []
        rt_val = factors.get("recovery_time", {}).get("3y")
        if rt_val is not None:
            detail_parts.append(f"回撤恢复{rt_val}天")
        if rt_pct.get("pct") is not None:
            detail_parts.append(f"同类{rank}")
        detail = "; ".join(detail_parts) if detail_parts else "定量数据不足"
        return {"score": round(score, 3), "detail": detail, "rank": rank}

    elif dim == "flow":
        flow = factors.get("fund_flow", {})
        purchase = flow.get("purchase_status", "未知")
        if "限" in purchase or "暂停" in purchase:
            score = 0.3
            trend = "限购/暂停"
        else:
            score = 0.6
            trend = "正常申购"
        detail = f"申购:{purchase}; 赎回:{flow.get('redeem_status', '未知')}"
        return {"score": round(score, 3), "detail": detail, "rank": "N/A"}

    elif dim == "style":
        conc = factors.get("concentration", {})
        ind = factors.get("industry", {})
        detail_parts = []
        if conc.get("top10_pct") is not None:
            detail_parts.append(f"前10集中度{conc['top10_pct']}%")
        if ind.get("drift") is not None:
            detail_parts.append(f"行业漂移{ind['drift']}%")
        detail = "; ".join(detail_parts) if detail_parts else "定量数据不足"
        return {"score": 0.5, "detail": detail, "rank": "定量数据不足，仅定性参考"}

    elif dim == "fee":
        return {
            "score": 0.5,
            "detail": "定量数据不足（费率需手动查证）",
            "rank": "定量数据不足，仅定性参考",
        }

    return {"score": 0.5, "detail": "未知维度", "rank": "N/A"}


def compute_overall_score(factors: dict, case: str) -> dict:
    weights = WEIGHTS.get(case, WEIGHTS["买入"])
    dim_scores = {}
    total = 0
    applied_weight = 0
    for dim, w in weights.items():
        ds = score_dimension(factors, dim)
        ds["confidence"] = _dim_confidence(factors, dim)
        ds["weight"] = w
        dim_scores[dim] = ds
        total += ds["score"] * w
        applied_weight += w
    overall = round(total / applied_weight, 3) if applied_weight > 0 else 0.5
    return {
        "overall_score": overall,
        "dim_scores": dim_scores,
        "weights_applied": weights,
    }


def _dim_confidence(factors: dict, dim: str) -> str:
    percentiles = factors.get("_percentiles", {})
    if dim == "return":
        vals = factors.get("excess_return", {})
        has_data = sum(1 for v in vals.values() if isinstance(v, dict) and v.get("excess") is not None)
        if percentiles.get("excess_return", {}).get("pct") is not None and has_data >= 1:
            return "高"
        return "中" if has_data >= 1 else "低"
    elif dim == "risk":
        dd = factors.get("max_drawdown", {})
        has_data = sum(1 for v in dd.values() if v is not None)
        if percentiles.get("max_drawdown", {}).get("pct") is not None and has_data >= 1:
            return "高"
        return "中" if has_data >= 1 else "低"
    elif dim == "quality":
        rt_pct = percentiles.get("recovery_time", {})
        return "中" if rt_pct.get("pct") is not None else "低"
    elif dim == "style":
        conc = factors.get("concentration", {})
        return "低" if conc.get("top10_pct") is None else "中"
    elif dim == "flow":
        status = factors.get("fund_flow", {})
        return "低" if status.get("purchase_status") == "未知" else "中"
    elif dim == "fee":
        return "低"
    return "低"
