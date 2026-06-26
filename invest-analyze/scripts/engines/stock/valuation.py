#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""获取个股估值数据（PE/PB 历史序列 + 当前快照 + 历史百分位）。

用法:
  python engines/stock/valuation.py <股票代码>
"""
import sys, os, json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from engines._shared.akshare import valuation_history, spot_snapshot
from engines._shared.output import extract_output_dir, save_output

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _percentile(series, value):
    """计算 value 在 series 中的历史百分位（0-100）。"""
    if not series or len(series) < 2:
        return None
    below = sum(1 for v in series if v <= value)
    return round(below / len(series) * 100, 1)


def _safe_val(val):
    if val is None or (isinstance(val, float) and (val != val)):
        return None
    try:
        if isinstance(val, (int, float, str, bool)):
            return val
        return float(val)
    except Exception:
        return str(val)


def main():
    output_dir, remaining = extract_output_dir()
    if len(remaining) < 1:
        print(json.dumps({"error": "用法: python engines/stock/valuation.py <股票代码> [--output-dir <目录>]"}, ensure_ascii=False))
        sys.exit(1)

    code = remaining[0]

    # 1. 估值历史序列
    df = valuation_history(code)
    name = code

    history = []
    latest = {}
    percentiles = {}

    if df is not None and not df.empty:
        for _, row in df.iterrows():
            entry = {"date": str(row.get("日期", row.get("date", "")))}
            for col in df.columns:
                if col == "日期" or col == "date":
                    continue
                entry[col] = _safe_val(row[col])
            history.append(entry)

        if history:
            latest = history[-1]
            name = latest.pop("股票名称", code)

        # 计算历史百分位（PE, PB, PS）
        for key in ("市盈率", "pe", "市净率", "pb", "市销率", "ps"):
            series = [h.get(key) for h in history if h.get(key) is not None]
            if series:
                current = series[-1]
                pct = _percentile(series[:-1], current)  # 不含自身
                if pct is not None:
                    label = "pe" if key in ("市盈率", "pe") else \
                            "pb" if key in ("市净率", "pb") else "ps"
                    percentiles[f"{label}_5y_pct"] = pct

    # 2. 当前快照
    snap = spot_snapshot(code)
    if snap:
        name = snap.get("名称", name)
        current = {
            "price": _safe_val(snap.get("最新价")),
            "change_pct": _safe_val(snap.get("涨跌幅")),
            "volume": _safe_val(snap.get("成交量")),
            "amount": _safe_val(snap.get("成交额")),
            "turnover": _safe_val(snap.get("换手率")),
            "pe_dynamic": _safe_val(snap.get("市盈率-动态")),
            "pb": _safe_val(snap.get("市净率")),
            "market_cap": _safe_val(snap.get("总市值")),
            "circulating_cap": _safe_val(snap.get("流通市值")),
        }
    else:
        current = {}

    out = {
        "code": code,
        "name": name,
        "current": current,
        "history": history,
        "percentile": percentiles,
    }
    save_output(out, f"{code}_valuation.json", output_dir)


if __name__ == "__main__":
    main()
