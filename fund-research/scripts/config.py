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
# 键为策略类型推断关键词（命中规则取首个匹配），default 为兜底
EXCLUSION_RULES = {
    "default": {
        "min_scale": 2.0,
        "min_manager_years": 3,
        "max_institutional_pct": 90,
        "max_turnover_rate": 500,
    },
    "index": {
        "min_scale": 1.0,         # 被动产品规模门槛更低
        "min_manager_years": 1,   # 被动产品经理影响小
        "max_institutional_pct": 90,
        "max_turnover_rate": None,  # 不限制
    },
    "quant": {
        "min_scale": 2.0,
        "min_manager_years": 1,   # 量化新人可能出道即优秀
        "max_institutional_pct": 90,
        "max_turnover_rate": None,  # 高换手是量化策略特征，非风险
    },
    "bond": {
        "min_scale": 0.5,         # 债基规模门槛更低
        "min_manager_years": 3,
        "max_institutional_pct": 90,
        "max_turnover_rate": 500,
    },
}

# ── 风格锚定 — 因子暴露漂移阈值 ──
STYLE_DRIFT_THRESHOLDS = {
    "factor_exposure_delta": 0.30,      # 因子暴露变化 > 0.3 → 漂移预警
    "sector_deviation_limit": 0.15,     # 行业偏离 > 15% → 预警
}

# ── 行为共识修正（定性三段式，不涉及数值评分） ──
# 强度：强信号（可独立改变判断）/ 中信号（调整权重）/ 弱信号（仅记录）
# 方向：正面 / 负面
# 影响：直接改变结论 / 只影响可信度 / 不影响
