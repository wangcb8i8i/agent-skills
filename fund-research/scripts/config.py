WEIGHTS = {
    "买入": {"return": 0.35, "risk": 0.25, "style": 0.10, "quality": 0.20, "fee": 0.10},
    "持有": {"return": 0.15, "risk": 0.20, "style": 0.15, "quality": 0.45, "fee": 0.05},
    "监控": {"return": 0.10, "risk": 0.25, "style": 0.25, "quality": 0.25, "fee": 0.15},
    "对比": {"return": 0.25, "risk": 0.20, "style": 0.20, "quality": 0.25, "fee": 0.10},
}

WINDOWS = {"1y": 252, "3y": 756, "5y": 1260}

PEER_RANK_BINS = ["前25%", "中位偏上", "中位", "中位偏下", "后25%"]

THRESHOLDS = {
    "min_history_days": 252,
    "max_drawdown_warn": 0.30,
    "concentration_warn": 0.60,
    "turnover_warn": 2.0,
    "manager_tenure_warn": 1,
}

DEFAULT_END_DATE = None
DEFAULT_START_DATE_OFFSET = 5 * 365

# ── 排除层 — 不合格品不进入分析 ──
EXCLUSION_RULES = {
    "min_scale_active": 2.0,        # 主动管理 ≥ 2 亿元
    "min_scale_index": 1.0,         # 指数基金 ≥ 1 亿元
    "min_manager_years": 3,
    "max_institutional_pct": 90,    # 机构占比 > 90% → 否决
    "min_institutional_pct": 0,     # 0% 纯散户盘 → 否决（0 表示不启用）
    "max_turnover_rate": 500,       # 换手率 %/年
}

# ── 风格锚定 — 因子暴露漂移阈值 ──
STYLE_DRIFT_THRESHOLDS = {
    "factor_exposure_delta": 0.30,      # 因子暴露变化 > 0.3 → 漂移预警
    "sector_deviation_limit": 0.15,     # 行业偏离 > 15% → 预警
}

# ── 行为共识修正系数 ──
BEHAVIOR_BOOST = {
    "institutional_increase": 0.10,     # 机构/内部人增持
    "retail_frenzy": -0.10,             # 份额暴增（散户追涨）
    "lockup_high_retention": 0.05,      # 封闭期打开高留存
    "lockup_mass_redemption": -0.10,    # 大规模赎回
    "resilience_proven": 0.05,          # 历史恢复力已证明
}

# 案由对行为共识修正的缩放系数
BEHAVIOR_CASE_MODIFIER = {
    "买入": 1.0,
    "持有": 0.5,
    "监控": 0.0,    # 监控案由下行为共识本身就是核心输出，不做修正
    "对比": 0.7,
}
