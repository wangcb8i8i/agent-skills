#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""获取基金净值数据（单位净值、累计净值、阶段收益）。

用法:
  python engines/fund/nav.py <基金代码>
"""
import sys, os, json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from engines._shared.eastmoney import parse_pingzhong, fund_list_path
from engines._shared.output import extract_output_dir, save_output

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main():
    output_dir, remaining = extract_output_dir()
    if len(remaining) < 1:
        print(json.dumps({"error": "用法: python engines/fund/nav.py <基金代码> [--output-dir <目录>]"}, ensure_ascii=False))
        sys.exit(1)

    code = remaining[0]
    pz = parse_pingzhong(code)
    if not pz:
        print(json.dumps({"code": code, "error": "未取到净值数据"}, ensure_ascii=False))
        sys.exit(1)

    name = pz.get("fS_name") or code
    nav = {
        "code": code,
        "name": name,
        "unit_nav_trend": pz.get("单位净值走势"),
        "accum_nav_trend": pz.get("累计净值走势"),
        "grand_total": pz.get("累计收益率走势"),
        "ranking": pz.get("同类排名走势"),
        "asset_allocation": pz.get("资产配置"),
        "performance_eval": pz.get("业绩评价"),
    }
    save_output(nav, f"{code}_nav.json", output_dir)


if __name__ == "__main__":
    main()
