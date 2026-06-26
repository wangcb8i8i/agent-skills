#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""获取个股日线行情数据（含成交量、成交额、换手率）。

用法:
  python engines/stock/price.py <股票代码> [--start YYYYMMDD] [--end YYYYMMDD] [--adjust qfq|hfq|]
"""
import sys, os, json, argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from engines._shared.akshare import daily_bars, spot_snapshot
from engines._shared.output import save_output

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


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
    ap = argparse.ArgumentParser()
    ap.add_argument("code", help="股票代码（纯数字）")
    ap.add_argument("--start", default="20000101", help="起始日期 YYYYMMDD")
    ap.add_argument("--end", default="20500101", help="截止日期 YYYYMMDD")
    ap.add_argument("--adjust", default="qfq", choices=["", "qfq", "hfq"], help="复权方式")
    ap.add_argument("--output-dir", default=None, help="输出目录（传此参数则将结果写入文件而非 stdout）")
    args = ap.parse_args()

    # 获取股票名称
    snap = spot_snapshot(args.code)
    name = snap.get("名称", args.code) if snap else args.code

    df = daily_bars(args.code, start_date=args.start, end_date=args.end, adjust=args.adjust)
    if df is None or df.empty:
        print(json.dumps({"code": args.code, "name": name, "error": "未取到行情数据"}, ensure_ascii=False))
        sys.exit(1)

    bars = []
    for _, row in df.iterrows():
        bar = {}
        for col in df.columns:
            bar[col] = _safe_val(row[col])
        bars.append(bar)

    # 阶段统计
    closes = [b.get("收盘") for b in bars if b.get("收盘") is not None]
    stat = {}
    if len(closes) >= 2:
        stat["区间涨跌幅"] = round((closes[-1] / closes[0] - 1) * 100, 2)
    if closes:
        stat["最高收盘"] = max(closes)
        stat["最低收盘"] = min(closes)

    out = {
        "code": args.code,
        "name": name,
        "adjust": args.adjust,
        "days": len(bars),
        "period": {"start": args.start, "end": args.end},
        "stat": stat,
        "bars": bars,
    }
    save_output(out, f"{args.code}_price.json", args.output_dir)


if __name__ == "__main__":
    main()
