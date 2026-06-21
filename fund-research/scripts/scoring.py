from config import WEIGHTS, EXCLUSION_RULES, BEHAVIOR_BOOST, BEHAVIOR_CASE_MODIFIER


def _percentile_directional_score(pct: float, lower_is_better: bool = False):
    if pct is None:
        return None
    p = max(0, min(100, pct)) / 100
    if lower_is_better:
        p = 1 - p
    return round(p, 3)


def _weighted_normalized(scores: list, weights: list) -> float:
    valid = [(s, w) for s, w in zip(scores, weights) if s is not None]
    if not valid:
        return None
    total_w = sum(w for _, w in valid)
    return round(sum(s * w for s, w in valid) / total_w, 3) if total_w > 0 else None


def check_exclusion(code: str, info: dict, scale: dict, manager: dict,
                    inst_ratio: dict, turnover: dict) -> dict:
    reasons = []
    is_index = "指数" in info.get("category", "") or "ETF" in info.get("category", "")
    min_scale = EXCLUSION_RULES["min_scale_index"] if is_index else EXCLUSION_RULES["min_scale_active"]
    scale_val = scale.get("scale")
    if scale_val is not None and scale_val < min_scale:
        reasons.append(f"规模不足: {scale_val}亿 < {min_scale}亿{'（指数）' if is_index else '（主动）'}")
    tenure = manager.get("tenure_years")
    if tenure is not None and tenure < EXCLUSION_RULES["min_manager_years"]:
        reasons.append(f"经理从业年限不足: {tenure}年 < {EXCLUSION_RULES['min_manager_years']}年")
    inst = inst_ratio.get("institutional_pct")
    if inst is not None and inst > EXCLUSION_RULES["max_institutional_pct"]:
        reasons.append(f"机构占比过高: {inst}% > {EXCLUSION_RULES['max_institutional_pct']}%")
    if inst is not None and inst == 0 and EXCLUSION_RULES["min_institutional_pct"] > 0:
        reasons.append(f"纯散户盘（机构占比0%）")
    tr = turnover.get("turnover_rate")
    if tr is not None and tr > EXCLUSION_RULES["max_turnover_rate"]:
        reasons.append(f"换手率过高: {tr}%/年 > {EXCLUSION_RULES['max_turnover_rate']}%/年")
    return {
        "blocked": len(reasons) > 0,
        "reasons": reasons,
        "detail": {
            "scale": scale_val,
            "manager_tenure": tenure,
            "institutional_pct": inst,
            "turnover_rate": tr,
            "is_index": is_index,
        },
    }


def score_dimension(factors: dict, dim: str) -> dict:
    percentiles = factors.get("_percentiles", {})

    if dim == "return":
        er_pct = percentiles.get("excess_return", {})
        ir_pct = percentiles.get("information_ratio", {})
        er_score = _percentile_directional_score(er_pct.get("pct"))
        ir_score = _percentile_directional_score(ir_pct.get("pct"))
        score = _weighted_normalized([er_score, ir_score], [0.6, 0.4])
        rank = er_pct.get("rank", "N/A")
        detail_parts = []
        er_val = factors.get("excess_return", {}).get("3y", {})
        if isinstance(er_val, dict) and er_val.get("excess") is not None:
            detail_parts.append(f"超额{er_val['excess']}%")
        if ir_pct.get("pct") is not None:
            detail_parts.append(f"同类{rank}")
        detail = "; ".join(detail_parts) if detail_parts else ("无数据" if score is None else "无同类对比")
        return {"score": score, "detail": detail, "rank": rank}

    elif dim == "risk":
        dd_pct = percentiles.get("max_drawdown", {})
        vol_pct = percentiles.get("volatility", {})
        dv_pct = percentiles.get("downside_deviation", {})
        cr_pct = percentiles.get("calmar_ratio", {})
        dd_score = _percentile_directional_score(dd_pct.get("pct"), lower_is_better=True)
        vol_score = _percentile_directional_score(vol_pct.get("pct"), lower_is_better=True)
        dv_score = _percentile_directional_score(dv_pct.get("pct"), lower_is_better=True)
        cr_score = _percentile_directional_score(cr_pct.get("pct"))
        score = _weighted_normalized(
            [dd_score, vol_score, dv_score, cr_score],
            [0.35, 0.20, 0.15, 0.30])
        rank = dd_pct.get("rank", "N/A")
        detail_parts = []
        dd_val = factors.get("max_drawdown", {}).get("3y")
        if dd_val is not None:
            detail_parts.append(f"最大回撤{dd_val}%")
        cr_val = factors.get("calmar_ratio", {}).get("3y")
        if cr_val is not None:
            detail_parts.append(f"卡玛{cr_val}")
        if dd_pct.get("pct") is not None:
            detail_parts.append(f"同类{rank}")
        detail = "; ".join(detail_parts) if detail_parts else "无数据"
        return {"score": score, "detail": detail, "rank": rank}

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
        detail = "; ".join(detail_parts) if detail_parts else "数据不足"
        return {"score": score, "detail": detail, "rank": rank}

    elif dim == "style":
        conc = factors.get("concentration", {})
        ind = factors.get("industry", {})
        fe = factors.get("factor_exposure", {})
        detail_parts = []
        status_hit = False
        if conc.get("top10_pct") is not None:
            detail_parts.append(f"前10集中度{conc['top10_pct']}%")
        if ind.get("drift") is not None:
            flag = "⚠" if ind["drift"] > 15 else ""
            detail_parts.append(f"行业漂移{flag}{ind['drift']}%")
        if fe.get("status") in ("预警", "漂移"):
            status_hit = True
            detail_parts.append(f"因子暴露{fe['status']}")
        detail = "; ".join(detail_parts) if detail_parts else "定量数据不足"
        score = 0.3 if status_hit else (0.6 if detail_parts else None)
        return {"score": score, "detail": detail, "rank": "N/A" if detail_parts else "定量数据不足，仅定性参考"}

    elif dim == "fee":
        top10 = factors.get("concentration", {}).get("top10_pct")
        fee_rate = factors.get("fee_rate")
        detail_parts = []
        if top10 is not None:
            as_proxy = max(0, 100 - top10 * 0.8)
            detail_parts.append(f"前10集中度{top10}%（AS代理: {as_proxy:.0f}%）")
        if fee_rate is not None:
            detail_parts.append(f"费率{fee_rate}%")
        if not detail_parts:
            return {"score": None, "detail": "数据不足（持仓/费率均不可得）", "rank": "N/A"}
        score = 0.5
        if top10 is not None:
            if top10 > 60:
                score = 0.3
            elif top10 < 40:
                score = 0.7
        if fee_rate is not None:
            if fee_rate > 1.5:
                score = min(score, 0.4)
            elif fee_rate < 0.8:
                score = max(score, 0.6)
        detail = "; ".join(detail_parts)
        return {"score": round(score, 3), "detail": detail, "rank": "N/A"}

    return {"score": None, "detail": "未知维度", "rank": "N/A"}


def compute_behavior_consensus(factors: dict, case: str) -> dict:
    flow = factors.get("fund_flow", {})
    purchase = flow.get("purchase_status", "未知")
    restrictions = flow.get("restrictions", "正常")
    signals = []
    info_gaps = []
    boost = 0.0

    if "限" in purchase or "暂停" in purchase:
        signals.append(("限购/暂停申购", -0.05, "中"))
        boost += -0.05

    if restrictions != "正常" and "赎回" in str(restrictions):
        signals.append(("赎回受限", -0.05, "中"))
        boost += -0.05

    if flow.get("scale_trend") == "暴增":
        signals.append(("规模暴增（散户追涨）", BEHAVIOR_BOOST["retail_frenzy"], "中"))
        boost += BEHAVIOR_BOOST["retail_frenzy"]
    elif flow.get("scale_trend") is None:
        info_gaps.append("规模趋势数据不可得")

    if flow.get("institutional_trend") == "增持":
        signals.append(("机构增持", BEHAVIOR_BOOST["institutional_increase"], "高"))
        boost += BEHAVIOR_BOOST["institutional_increase"]

    if flow.get("institutional_pct") is None:
        info_gaps.append("机构持仓数据不可得")
    if factors.get("concentration", {}).get("top10_pct") is None:
        info_gaps.append("持仓明细数据不可得，无法追溯历史恢复力")

    modifier = BEHAVIOR_CASE_MODIFIER.get(case, 1.0)
    adjusted_boost = boost * modifier

    return {
        "boost": round(adjusted_boost, 3),
        "raw_boost": round(boost, 3),
        "case_modifier": modifier,
        "signals": signals,
        "info_gaps": info_gaps,
        "is_actionable": len(signals) > 0,
    }


def compute_overall_score(factors: dict, case: str,
                          behavior: dict = None) -> dict:
    weights = WEIGHTS.get(case, WEIGHTS["买入"])
    dim_scores = {}
    total = 0
    applied_weight = 0
    for dim, w in weights.items():
        ds = score_dimension(factors, dim)
        ds["confidence"] = _dim_confidence(factors, dim)
        ds["weight"] = w
        dim_scores[dim] = ds
        if ds["score"] is not None:
            total += ds["score"] * w
            applied_weight += w

    base_score = round(total / applied_weight, 3) if applied_weight > 0 else None

    if behavior and base_score is not None:
        final_score = round(max(0.0, min(1.0, base_score * (1 + behavior["boost"]))), 3)
    else:
        final_score = base_score

    result = {
        "overall_score": final_score,
        "base_score": base_score,
        "dim_scores": dim_scores,
        "weights_applied": weights,
    }
    if behavior:
        result["behavior"] = behavior
    return result


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
        fe = factors.get("factor_exposure", {})
        if fe.get("status") in ("稳定", "预警", "漂移"):
            return "中"
        return "低" if conc.get("top10_pct") is None else "中"
    elif dim == "fee":
        top10 = factors.get("concentration", {}).get("top10_pct")
        return "中" if top10 is not None else "低"
    return "低"
