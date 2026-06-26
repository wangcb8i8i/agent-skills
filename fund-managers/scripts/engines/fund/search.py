#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在基金列表中搜索（按代码/名称/拼音）。

用法:
  python engines/fund/search.py <关键词>
  python engines/fund/search.py 易方达 --type 混合 --max 10
"""
import sys, os, json, argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from engines._shared.eastmoney import fund_list_path
from engines._shared.output import save_output

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="*", help="名称/拼音/代码关键词")
    ap.add_argument("--type", default=None, help="按类型过滤（子串匹配）")
    ap.add_argument("--max", type=int, default=40)
    ap.add_argument("--output-dir", default=None, help="输出目录（传此参数则将结果写入文件而非 stdout）")
    args = ap.parse_args()

    list_path = fund_list_path()
    if not os.path.exists(list_path):
        print(json.dumps({"error": "缺少 fund_list.json，请先运行 build_fund_list.py"}, ensure_ascii=False))
        sys.exit(1)

    data = json.load(open(list_path, encoding="utf-8"))
    funds = data["funds"]

    def hit(f):
        if args.type and args.type not in f["type"]:
            return False
        if not args.query:
            return True
        for kw in args.query:
            up = kw.upper()
            if not any([kw in f["code"], kw in f["name"], up in f["abbr"], up in f["pinyin"]]):
                return False
        return True

    results = [f for f in funds if hit(f)]
    out = {
        "total": data["count"],
        "updated": data["updated"],
        "hits": len(results),
        "results": [{"code": f["code"], "name": f["name"], "type": f["type"]} for f in results[: args.max]],
        "truncated": len(results) > args.max,
    }
    save_output(out, f"search_{'_'.join(args.query) if args.query else 'all'}.json", args.output_dir)


if __name__ == "__main__":
    main()
