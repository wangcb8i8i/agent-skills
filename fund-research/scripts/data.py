import time
import pandas as pd

from providers._base import _record_status, get_data_status
from providers._akshare import (
    _ak_get_fund_code,
    _ak_get_fund_name,
    _ak_get_fund_category,
    _ak_get_fund_info,
    _ak_get_nav_history,
    _ak_get_portfolio_holdings,
    _ak_get_fund_latest_status,
    _ak_get_market_index_history,
    _ak_get_industry_allocation,
    _ak_get_fund_scale,
    _ak_get_manager_info,
    _ak_get_institutional_ratio,
    _ak_get_turnover_rate,
    _ak_get_fee_rate,
    _ak_get_scale_history,
    _ak_get_peer_nav_history,
)
try:
    from providers._efinance import (
        _ef_get_fund_code,
        _ef_get_fund_name,
        _ef_get_fund_category,
        _ef_get_fund_info,
        _ef_get_nav_history,
        _ef_get_portfolio_holdings,
        _ef_get_market_index_history,
        _ef_get_industry_allocation,
        _ef_get_manager_info,
        _ef_get_peer_nav_history,
    )
except ImportError:
    _ef_get_fund_code = _ef_get_fund_name = _ef_get_fund_category = _ef_get_fund_info = None
    _ef_get_nav_history = _ef_get_portfolio_holdings = _ef_get_market_index_history = None
    _ef_get_industry_allocation = _ef_get_manager_info = _ef_get_peer_nav_history = None
from providers._scraper import (
    _sc_get_fund_code,
    _sc_get_fund_name,
    _sc_get_fund_category,
    _sc_get_nav_history,
    _sc_get_portfolio_holdings,
    _sc_get_fund_latest_status,
    _sc_get_market_index_history,
    _sc_get_industry_allocation,
    _sc_get_fund_scale,
    _sc_get_manager_info,
    _sc_get_institutional_ratio,
    _sc_get_turnover_rate,
    _sc_get_fee_rate,
    _sc_get_scale_history,
    _sc_get_peer_nav_history,
)

_last_call = 0.0
_MIN_INTERVAL = 0.5


def _rate_limited_call(fn, *args, **kwargs):
    global _last_call
    elapsed = time.time() - _last_call
    if elapsed < _MIN_INTERVAL:
        time.sleep(_MIN_INTERVAL - elapsed)
    result = fn(*args, **kwargs)
    _last_call = time.time()
    return result


def _dispatch(sources, *args, status_key=None, critical=False, default=None):
    last_err = None
    for src_name, src_fn in sources:
        if src_fn is None:
            continue
        try:
            result = _rate_limited_call(src_fn, *args)
            return result
        except Exception as e:
            _record_status(status_key, False, f"{src_name}: {e}", source=src_name)
            last_err = e
            continue
    _record_status(status_key, False, f"全部源失败: {last_err}", source="全部源失败")
    if critical:
        raise RuntimeError(f"{status_key}: 全部源不可用 - {last_err}")
    return default


def get_fund_code(query: str) -> str:
    return _dispatch(
        [("AKShare", _ak_get_fund_code), ("efinance", _ef_get_fund_code), ("scraper", _sc_get_fund_code)],
        query, status_key="fund_basic_info", critical=True,
    )


def get_fund_name(code: str) -> str:
    return _dispatch(
        [("AKShare", _ak_get_fund_name), ("efinance", _ef_get_fund_name), ("scraper", _sc_get_fund_name)],
        code, status_key="fund_name", critical=False, default=code,
    )


def get_fund_category(code: str) -> str:
    return _dispatch(
        [("AKShare", _ak_get_fund_category), ("efinance", _ef_get_fund_category), ("scraper", _sc_get_fund_category)],
        code, status_key="fund_category", critical=False, default="未知",
    )


_FUND_INFO_CACHE = {}


def get_fund_info(code: str) -> dict:
    if code in _FUND_INFO_CACHE:
        return _FUND_INFO_CACHE[code]
    info = {"code": code, "name": code, "category": "未知"}
    try:
        info["name"] = get_fund_name(code)
    except Exception:
        pass
    try:
        info["category"] = get_fund_category(code)
    except Exception:
        pass
    _FUND_INFO_CACHE[code] = info
    return info


def get_nav_history(code: str) -> pd.DataFrame:
    return _dispatch(
        [("AKShare", _ak_get_nav_history), ("efinance", _ef_get_nav_history), ("scraper", _sc_get_nav_history)],
        code, status_key="nav_history", critical=True,
    )


def get_portfolio_holdings(code: str) -> list:
    return _dispatch(
        [("AKShare", _ak_get_portfolio_holdings), ("efinance", _ef_get_portfolio_holdings), ("scraper", _sc_get_portfolio_holdings)],
        code, status_key="portfolio_holdings", critical=False, default=[],
    )


def get_fund_latest_status(code: str) -> dict:
    return _dispatch(
        [("AKShare", _ak_get_fund_latest_status), ("scraper", _sc_get_fund_latest_status)],
        code, status_key="fund_status", critical=False, default={},
    )


def get_market_index_history(symbol: str = "000300", years: int = 10) -> pd.DataFrame:
    return _dispatch(
        [("AKShare", _ak_get_market_index_history), ("efinance", _ef_get_market_index_history), ("scraper", _sc_get_market_index_history)],
        symbol, years, status_key="market_index", critical=False, default=pd.DataFrame(),
    )


def get_industry_allocation(code: str) -> list:
    return _dispatch(
        [("AKShare", _ak_get_industry_allocation), ("efinance", _ef_get_industry_allocation), ("scraper", _sc_get_industry_allocation)],
        code, status_key="industry_allocation", critical=False, default=[],
    )


def get_fund_scale(code: str) -> dict:
    return _dispatch(
        [("AKShare", _ak_get_fund_scale), ("scraper", _sc_get_fund_scale)],
        code, status_key="fund_scale", critical=False,
        default={"scale": None, "unit": "亿元", "category": None},
    )


def get_manager_info(code: str) -> dict:
    return _dispatch(
        [("AKShare", _ak_get_manager_info), ("efinance", _ef_get_manager_info), ("scraper", _sc_get_manager_info)],
        code, status_key="manager_info", critical=False,
        default={"managers": [], "tenure_years": None, "count": 0},
    )


def get_institutional_ratio(code: str) -> dict:
    return _dispatch(
        [("AKShare", _ak_get_institutional_ratio), ("scraper", _sc_get_institutional_ratio)],
        code, status_key="inst_ratio", critical=False,
        default={"institutional_pct": None, "internal_pct": None},
    )


def get_turnover_rate(code: str) -> dict:
    return _dispatch(
        [("AKShare", _ak_get_turnover_rate), ("scraper", _sc_get_turnover_rate)],
        code, status_key="turnover", critical=False,
        default={"turnover_rate": None, "period": None},
    )


def get_fee_rate(code: str) -> dict:
    return _dispatch(
        [("AKShare", _ak_get_fee_rate), ("scraper", _sc_get_fee_rate)],
        code, status_key="fee_rate", critical=False,
        default={"management_fee": None, "custodian_fee": None, "total_fee": None},
    )


def get_scale_history(code: str) -> list:
    return _dispatch(
        [("AKShare", _ak_get_scale_history), ("scraper", _sc_get_scale_history)],
        code, status_key="scale_history", critical=False, default=[],
    )


def get_active_share(code: str) -> dict:
    _record_status("active_share", False, "AKShare 无 Active Share 数据源，无法精确计算")
    return {"active_share": None, "note": "AKShare 无法获取 Active Share。精确计算需基准指数持仓数据。"}


def get_peer_nav_history(category: str, max_peers: int = 15) -> dict:
    return _dispatch(
        [("AKShare", _ak_get_peer_nav_history), ("efinance", _ef_get_peer_nav_history), ("scraper", _sc_get_peer_nav_history)],
        category, max_peers, status_key="peer_nav_history", critical=False, default={},
    )
