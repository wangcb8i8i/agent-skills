WEIGHTS = {
    "买入": {"return": 0.30, "risk": 0.25, "style": 0.10, "quality": 0.15, "flow": 0.10, "fee": 0.10},
    "持有": {"return": 0.15, "risk": 0.20, "style": 0.15, "quality": 0.30, "flow": 0.15, "fee": 0.05},
    "监控": {"return": 0.10, "risk": 0.15, "style": 0.20, "quality": 0.15, "flow": 0.35, "fee": 0.05},
    "对比": {"return": 0.25, "risk": 0.20, "style": 0.15, "quality": 0.20, "flow": 0.10, "fee": 0.10},
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
