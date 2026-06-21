#!/usr/bin/env python3
"""
基金因子分析入口脚本。
用法：python run_analysis.py <基金代码> [--case 买入|持有|监控|对比] [--no-exclude]
输出：因子分析报告（Markdown + JSON）

流程：排除层 → 数据获取 → 6维度因子计算 → 验证校验 → 第一层评分 → 行为共识修正 → 报告
"""
import argparse
import json
import sys
from datetime import datetime

from data import (get_fund_code, get_fund_info, get_nav_history,
                  get_peer_nav_history, get_portfolio_holdings,
                  get_fund_latest_status, get_industry_allocation,
                  get_market_index_history, get_data_status,
                  get_fund_scale, get_manager_info,
                  get_institutional_ratio, get_turnover_rate,
                  get_active_share, get_fee_rate, get_scale_history)
from factors import compute_all_factors
from validation import run_all_checks
from scoring import (compute_overall_score, compute_behavior_consensus,
                     check_exclusion)
from report_generator import generate_factor_report


def main():
    parser = argparse.ArgumentParser(description="基金因子分析")
    parser.add_argument("fund_code", help="基金代码或名称")
    parser.add_argument("--case", default="买入", choices=["买入", "持有", "监控", "对比"],
                        help="案由（决定权重）")
    parser.add_argument("--output", default=None, help="输出JSON路径（可选）")
    parser.add_argument("--no-exclude", action="store_true",
                        help="跳过排除层（调试用）")
    args = parser.parse_args()

    code = get_fund_code(args.fund_code)
    info = get_fund_info(code)
    category = info.get("category", "未知")

    print(f"基金: {info.get('name', code)} ({code})", file=sys.stderr)
    print(f"类型: {category}", file=sys.stderr)
    print(f"案由: {args.case}", file=sys.stderr)

    # ── 0. 排除层 ──
    if not args.no_exclude:
        print("\n排除层检查...", file=sys.stderr)
        scale = get_fund_scale(code)
        manager = get_manager_info(code)
        inst_ratio = get_institutional_ratio(code)
        turnover = get_turnover_rate(code)
        exclusion = check_exclusion(code, info, scale, manager, inst_ratio, turnover)
        if exclusion["blocked"]:
            print("\n✗ 排除层未通过，终止分析。", file=sys.stderr)
            for r in exclusion["reasons"]:
                print(f"  - {r}", file=sys.stderr)
            output = {
                "fund": info,
                "case": args.case,
                "generated_at": datetime.now().isoformat(),
                "exclusion": exclusion,
                "status": "blocked_by_exclusion",
            }
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    json.dump(output, f, ensure_ascii=False, indent=2, default=str)
            print(json.dumps(output, ensure_ascii=False, indent=2))
            sys.exit(2)
        print("排除层通过 ✓", file=sys.stderr)
    else:
        scale = get_fund_scale(code)
        manager = get_manager_info(code)
        inst_ratio = get_institutional_ratio(code)
        turnover = get_turnover_rate(code)
        exclusion = check_exclusion(code, info, scale, manager, inst_ratio, turnover)

    # ── 1. 数据获取 ──
    print("\n正在获取净值数据...", file=sys.stderr)
    nav = get_nav_history(code)
    if nav.empty:
        print("错误：无净值数据", file=sys.stderr)
        sys.exit(1)
    print(f"获取到 {len(nav)} 条净值记录", file=sys.stderr)

    print("正在获取持仓数据...", file=sys.stderr)
    holdings = get_portfolio_holdings(code)
    print(f"获取到 {len(holdings)} 条持仓记录", file=sys.stderr)

    print("正在获取同类数据...", file=sys.stderr)
    peer_navs = get_peer_nav_history(category)

    print("正在获取行业配置...", file=sys.stderr)
    industry = get_industry_allocation(code)
    print(f"获取到 {len(industry)} 条行业配置记录", file=sys.stderr)

    print("正在获取市场指数数据...", file=sys.stderr)
    market_index = get_market_index_history()
    print(f"获取到 {len(market_index)} 条指数记录", file=sys.stderr)

    print("正在获取最新状态...", file=sys.stderr)
    status = get_fund_latest_status(code)

    print("正在计算 Active Share...", file=sys.stderr)
    active_share = get_active_share(code)

    print("正在获取费率数据...", file=sys.stderr)
    fee_rate = get_fee_rate(code)

    print("正在获取规模历史...", file=sys.stderr)
    scale_history = get_scale_history(code)

    # ── 2. 因子计算 ──
    print("正在计算因子...", file=sys.stderr)
    factors = compute_all_factors(nav, peer_navs, holdings, status, industry,
                                  scale_history, inst_ratio)
    factors["active_share"] = active_share
    factors["fee_rate"] = fee_rate.get("total_fee")

    # ── 3. 验证校验 ──
    print("正在运行验证...", file=sys.stderr)
    validation = run_all_checks(nav, market_index)

    # ── 4. 第一层评分（不含行为共识） ──
    print("正在计算第一层评分...", file=sys.stderr)
    behavior = compute_behavior_consensus(factors, args.case)
    scores = compute_overall_score(factors, args.case, behavior)

    data_status = get_data_status()

    print("正在生成报告...", file=sys.stderr)
    report = generate_factor_report(factors, validation, scores, info, data_status)

    output = {
        "fund": info,
        "case": args.case,
        "generated_at": datetime.now().isoformat(),
        "status": "completed",
        "data_status": data_status,
        "exclusion": exclusion,
        "factors": {k: v for k, v in factors.items() if v is not None},
        "validation": {
            "stability": validation.get("stability", {}),
            "sensitivity": validation.get("sensitivity", {}),
            "scenario": validation.get("scenario", {}),
        },
        "scores": scores,
        "report_markdown": report,
    }

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2, default=str)
        print(f"JSON输出: {args.output}", file=sys.stderr)

    print("\n" + report)


if __name__ == "__main__":
    main()
