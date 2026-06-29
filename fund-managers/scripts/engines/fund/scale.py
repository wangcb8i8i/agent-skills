#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""获取基金规模变动和持有人结构数据。

用法:
  python engines/fund/scale.py <基金代码>
"""
import sys, os, json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from engines._shared.eastmoney import parse_pingzhong
from engines._shared.output import extract_output_dir, save_output

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main():
    output_dir, remaining = extract_output_dir()
    if len(remaining) < 1:
        print(json.dumps({"error": "用法: python engines/fund/scale.py <基金代码> [--output-dir <目录>]"}, ensure_ascii=False))
        sys.exit(1)

    code = remaining[0]
    pz = parse_pingzhong(code)
    if not pz:
        print(json.dumps({"code": code, "error": "未取到规模数据"}, ensure_ascii=False))
        sys.exit(1)

    name = pz.get("fS_name") or code
    data = {
        "code": code,
        "name": name,
        "scale": pz.get("规模变动"),
        "holder_structure": pz.get("持有人结构"),
        "asset_allocation": pz.get("资产配置"),
    }
    save_output(data, f"{code}_scale.json", output_dir)


if __name__ == "__main__":
    main()
