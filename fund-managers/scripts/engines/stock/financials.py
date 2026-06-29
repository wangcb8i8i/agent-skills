#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""获取个股财务指标（ROE、营收、毛利率、资产负债率等，按报告期）。

用法:
  python engines/stock/financials.py <股票代码>
"""
import sys, os, json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from engines._shared.akshare import financial_indicators, spot_snapshot
from engines._shared.output import extract_output_dir, save_output

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _safe_val(val):
    """将 numpy 类型转为 Python 原生类型以便 JSON 序列化。"""
    if val is None or (isinstance(val, float) and (val != val)):  # NaN
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
        print(json.dumps({"error": "用法: python engines/stock/financials.py <股票代码> [--output-dir <目录>]"}, ensure_ascii=False))
        sys.exit(1)

    code = remaining[0]

    # 获取财务指标（按报告期）
    df = financial_indicators(code)
    if df is None or df.empty:
        # 回退：至少返回股票名称
        snap = spot_snapshot(code)
        name = snap.get("名称", code) if snap else code
        print(json.dumps({"code": code, "name": name, "error": "未取到财务指标数据"}, ensure_ascii=False))
        sys.exit(1)

    # 取股票名称（第一列通常是股票代码+名称信息）
    name = code
    # 解析 DataFrame
    reports = []
    for _, row in df.iterrows():
        report = {}
        for col in df.columns:
            report[col] = _safe_val(row[col])
        reports.append(report)

    # 从第一行取股票名（AKShare 字段名 vs 统一字段名）
    if reports:
        name = reports[0].get("股票名称") or reports[0].get("SECURITY_NAME_ABBR") or name

    out = {
        "code": code,
        "name": name,
        "reports": reports,
    }
    save_output(out, f"{code}_financials.json", output_dir)


if __name__ == "__main__":
    main()
