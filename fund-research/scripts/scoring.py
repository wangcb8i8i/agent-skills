from config import WEIGHTS, EXCLUSION_RULES


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


def _infer_strategy_type(info: dict, turnover_rate: float = None) -> str:
    category = info.get("category", "")
    if "指数" in category or "ETF" in category:
        return "index"
    if "债" in category or "纯债" in category:
        return "bond"
    if turnover_rate is not None and turnover_rate > 500:
        return "quant"
    return "default"


def check_exclusion(code: str, info: dict, scale: dict, manager: dict,
                    inst_ratio: dict, turnover: dict) -> dict:
    reasons = []
    tr = turnover.get("turnover_rate")
    strategy = _infer_strategy_type(info, tr)
    rules = EXCLUSION_RULES.get(strategy, EXCLUSION_RULES["default"])

    scale_val = scale.get("scale")
    min_scale = rules["min_scale"]
    if scale_val is not None and scale_val < min_scale:
        reasons.append(f"规模不足: {scale_val}亿 < {min_scale}亿（{strategy}）")

    tenure = manager.get("tenure_years")
    min_years = rules["min_manager_years"]
    if tenure is not None and tenure < min_years:
        reasons.append(f"经理从业年限不足: {tenure}年 < {min_years}年（{strategy}）")

    inst = inst_ratio.get("institutional_pct")
    max_inst = rules["max_institutional_pct"]
    if inst is not None and inst > max_inst:
        reasons.append(f"机构占比过高: {inst}% > {max_inst}%")

    max_tr = rules["max_turnover_rate"]
    if max_tr is not None and tr is not None and tr > max_tr:
        reasons.append(f"换手率过高: {tr}%/年 > {max_tr}%/年")

    return {
        "blocked": len(reasons) > 0,
        "reasons": reasons,
        "strategy": strategy,
        "detail": {
            "scale": scale_val,
            "manager_tenure": tenure,
            "institutional_pct": inst,
            "turnover_rate": tr,
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
    has_negative = False
    has_positive = False

    if "限" in purchase or "暂停" in purchase:
        signals.append({"signal": "限购/暂停申购", "strength": "中", "direction": "负面"})
        has_negative = True

    if restrictions != "正常" and "赎回" in str(restrictions):
        signals.append({"signal": "赎回受限", "strength": "中", "direction": "负面"})
        has_negative = True

    if flow.get("scale_trend") == "暴增":
        signals.append({"signal": "规模暴增（散户追涨）", "strength": "中", "direction": "负面"})
        has_negative = True
    elif flow.get("scale_trend") is None:
        info_gaps.append("规模趋势数据不可得")

    if flow.get("institutional_trend") == "增持":
        signals.append({"signal": "机构增持", "strength": "强", "direction": "正面"})
        has_positive = True

    if flow.get("institutional_pct") is None:
        info_gaps.append("机构持仓数据不可得")
    if factors.get("concentration", {}).get("top10_pct") is None:
        info_gaps.append("持仓明细数据不可得，无法追溯历史恢复力")

    return {
        "signals": signals,
        "info_gaps": info_gaps,
        "has_negative": has_negative,
        "has_positive": has_positive,
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

    result = {
        "overall_score": base_score,
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
