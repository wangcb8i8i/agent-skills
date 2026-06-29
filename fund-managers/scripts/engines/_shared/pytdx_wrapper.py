# -*- coding: utf-8 -*-
"""pytdx 公共封装层：A 股实时行情、日线、板块成份数据。

回退链路定位（由 _shared/akshare.py 编排）：
  BaoStock → pytdx → 东财 HTTP

pytdx 通过通达信协议直连行情服务器，不依赖爬虫，适合作为 stock
层的稳定回退源。

覆盖：
  - 日线行情（约 800 条历史 bar）   → daily_bars()
  - 实时行情快照                     → spot_snapshot()

不覆盖：财务指标、估值序列、板块成份（BaoStock / AKShare 负责）。
"""

import sys
import time
from datetime import datetime

import pandas as pd

try:
    from pytdx.hq import TdxHq_API
    _HAVE_TDX = True
except ImportError:
    _HAVE_TDX = False

# 已知可用的通达信行情服务器 IP（避免 select_best_ip 的慢速测速）
_TDX_SERVERS = [
    {"ip": "115.238.90.165", "port": 7709},
    {"ip": "115.238.56.198", "port": 7709},
    {"ip": "60.191.117.167", "port": 7709},
    {"ip": "218.75.126.9", "port": 7709},
    {"ip": "180.153.18.170", "port": 7709},
    {"ip": "60.12.136.250", "port": 7709},
]


def _check_tdx():
    if not _HAVE_TDX:
        print("需要安装 pytdx：pip install pytdx", file=sys.stderr)
        return False
    return True


def _connect(api):
    """快速连接可用的通达信服务器，返回 True 表示成功。"""
    for s in _TDX_SERVERS:
        s_to = time.time()
        try:
            if api.connect(s["ip"], s["port"]):
                if time.time() - s_to < 8:  # 过滤超时连接
                    return True
        except Exception:
            continue
    return False


def _market_code(symbol):
    """将纯数字股票代码转为 pytdx market 枚举。

    pytdx 市场编码：1=上海, 0=深圳, 2=北京。
    """
    prefix = symbol[:3]
    if prefix in ("600", "601", "603", "605", "688", "689"):
        return 1  # 上海
    elif prefix in ("000", "001", "002", "003", "300", "301", "920"):
        return 0  # 深圳
    elif prefix in ("430", "830", "831", "832", "833", "834", "835", "836",
                    "837", "838", "839", "870", "871", "872", "873", "874"):
        return 2  # 北京
    if symbol and symbol[0] in ("6", "9"):
        return 1
    return 0


# ─── 日线行情 ────────────────────────────────────────────────


def daily_bars(symbol, start_date="20000101", end_date="20500101", adjust=""):
    """获取个股日线行情（pytdx 版本）。

    接口签名与 akshare.daily_bars() / baostock_wrapper.daily_bars() 对齐。

    pytdx 不直接支持复权，如需要复权数据，优先使用前两层的返回。
    adjust 参数接受但不处理，仅返回不复权数据。

    返回 DataFrame（列：日期, 开盘, 收盘, 最高, 最低, 成交量, 成交额,
    换手率, 涨跌幅），失败返回 None。
    """
    if not _check_tdx():
        return None

    api = TdxHq_API(heartbeat=True)
    if not _connect(api):
        return None
    try:
        market = _market_code(symbol)
        bars = api.get_security_bars(9, market, symbol, 0, 800)
        if not bars:
            return None

        rows = []
        for b in bars:
            try:
                dt = datetime(b["year"], b["month"], b["day"])
                date_str = dt.strftime("%Y-%m-%d")
                if date_str < start_date[:4] + "-" + start_date[4:6] + "-" + start_date[6:]:
                    continue
                if date_str > end_date[:4] + "-" + end_date[4:6] + "-" + end_date[6:]:
                    continue
                row = {
                    "日期": date_str,
                    "开盘": float(b.get("open", 0)),
                    "收盘": float(b.get("close", 0)),
                    "最高": float(b.get("high", 0)),
                    "最低": float(b.get("low", 0)),
                    "成交量": float(b.get("vol", 0)) * 100,  # pytdx 单位是手
                    "成交额": float(b.get("amount", 0)),
                }
                rows.append(row)
            except Exception:
                continue

        if not rows:
            return None
        df = pd.DataFrame(rows)
        df.sort_values("日期", inplace=True)
        return df
    except Exception as e:
        print(f"    pytdx daily_bars({symbol}) 失败: {e}", file=sys.stderr)
        return None
    finally:
        try:
            api.disconnect()
        except Exception:
            pass


# ─── 实时快照 ────────────────────────────────────────────────


def spot_snapshot(symbol):
    """获取个股实时行情快照（pytdx 版本）。

    与 akshare.spot_snapshot() 接口对齐。

    返回 dict（代码, 名称, 最新价, 涨跌幅, 涨跌额, 成交量, 成交额,
    开盘, 最高, 最低, 市盈率, 市净率, 总市值），失败返回 None。
    """
    if not _check_tdx():
        return None

    api = TdxHq_API(heartbeat=True)
    if not _connect(api):
        return None
    try:
        market = _market_code(symbol)
        quotes = api.get_security_quotes([(market, symbol)])
        if not quotes or len(quotes) == 0:
            return None
        q = quotes[0]

        price = float(q.get("price", 0))
        last_close = float(q.get("last_close", 0))
        chg_pct = (price - last_close) / last_close if last_close else 0

        result = {
            "代码": symbol,
            "最新价": price,
            "涨跌幅": chg_pct,
            "涨跌额": price - last_close,
            "开盘": float(q.get("open", 0)),
            "最高": float(q.get("high", 0)),
            "最低": float(q.get("low", 0)),
            "成交量": float(q.get("vol", 0)) * 100,  # 手→股
            "成交额": float(q.get("amount", 0)),
        }
        return result
    except Exception as e:
        print(f"    pytdx spot_snapshot({symbol}) 失败: {e}", file=sys.stderr)
        return None
    finally:
        try:
            api.disconnect()
        except Exception:
            pass



