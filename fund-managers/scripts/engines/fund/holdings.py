#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""获取基金季度前十大持仓。

用法:
  python engines/fund/holdings.py <基金代码>
"""
import sys, os, json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from engines._shared.eastmoney import parse_holdings, THIS_YEAR, fund_list_path
from engines._shared.output import extract_output_dir, save_output

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main():
    output_dir, remaining = extract_output_dir()
    if len(remaining) < 1:
        print(json.dumps({"error": "用法: python engines/fund/holdings.py <基金代码> [--output-dir <目录>]"}, ensure_ascii=False))
        sys.exit(1)

    code = remaining[0]
    quarters = []
    for y in range(2003, THIS_YEAR + 1):
        qs = parse_holdings(code, y)
        quarters += qs

    # dedup
    uniq = {}
    for q in quarters:
        uniq[(q["year"], q["quarter"])] = q
    quarters = list(uniq.values())
    quarters.sort(key=lambda x: (x["year"], x["quarter"]), reverse=True)

    # name
    name = code
    try:
        fl = json.load(open(fund_list_path(), encoding="utf-8"))
        for f in fl.get("funds", []):
            if f["code"] == code:
                name = f["name"]
                break
    except Exception:
        pass

    save_output({"code": code, "name": name, "quarters": quarters}, f"{code}_holdings.json", output_dir)


if __name__ == "__main__":
    main()
