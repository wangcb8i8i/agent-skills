from config import EXCLUSION_RULES, THRESHOLDS


FUND_TYPE_LABELS = {
    "equity_active": "偏股主动",
    "index": "指数",
    "quant": "量化",
    "bond": "债基",
    "insufficient_data": "数据不足",
}


def _infer_strategy_type(info: dict, turnover_rate: float = None) -> str:
    """推断基金策略类型，用于排除层参数选择。"""
    category = info.get("category", "")
    if "指数" in category or "ETF" in category:
        return "index"
    if "债" in category or "纯债" in category:
        return "bond"
    if turnover_rate is not None and turnover_rate > 500:
        return "quant"
    return "equity_active"


def classify_fund_type(info: dict, turnover_rate: float = None,
                       nav_days: int = 0) -> str:
    """输出 Phase 2 路由用的基金类型标签。"""
    raw = _infer_strategy_type(info, turnover_rate)
    if nav_days < THRESHOLDS["min_history_days"]:
        return "insufficient_data"
    return raw


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




