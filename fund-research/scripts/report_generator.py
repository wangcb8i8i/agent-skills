from datetime import datetime
from config import WINDOWS


def _fmt(v, unit=""):
    if v is None:
        return "N/A"
    return f"{v}{unit}"


def _conf_label(c):
    return {"高": "高", "中": "中", "低": "低"}.get(c, c)


def _status_icon(success):
    return "✓" if success else "✗"


def generate_factor_report(factors: dict, validation: dict, scores: dict,
                           fund_info: dict, data_status: dict = None) -> str:
    lines = []
    lines.append(f"# 因子分析报告 — {fund_info.get('name', fund_info.get('code', ''))}")
    lines.append(f"代码：{fund_info.get('code', '')}  |  类型：{fund_info.get('category', '未知')}")
    lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")

    # ── 数据获取状态 ──
    if data_status:
        lines.append("## 数据获取状态")
        lines.append("")
        lines.append("| 数据项 | 状态 | 说明 | 来源 |")
        lines.append("|:-------|:----|:-----|:-----|")
        key_order = [
            ("fund_basic_info", "基金基本信息"),
            ("fund_scale", "基金规模"),
            ("manager_info", "经理信息"),
            ("inst_ratio", "机构占比"),
            ("turnover", "换手率"),
            ("nav_history", "净值历史"),
            ("portfolio_holdings", "持仓明细"),
            ("industry_allocation", "行业配置"),
            ("fund_status", "申购/赎回状态"),
            ("market_index", "市场指数"),
            ("peer_nav_history", "同类净值"),
            ("active_share", "Active Share"),
        ]
        for key, label in key_order:
            ds = data_status.get(key, {})
            if not ds:
                lines.append(f"| {label} | — | 未获取 | — |")
                continue
            icon = _status_icon(ds.get("success"))
            detail = ds.get("detail", "")
            source = ds.get("source", "AKShare")
            lines.append(f"| {label} | {icon} | {detail} | {source} |")
        lines.append("")

    # ── 同类池信息 ──
    peer_pool = factors.get("_peer_pool", {})
    percentiles = factors.get("_percentiles", {})
    if peer_pool:
        lines.append("## 同类池信息")
        lines.append("")
        lines.append(f"同类基金数：{peer_pool.get('size', 0)} 只")
        lines.append(f"代表性评估：{peer_pool.get('representativeness', '未知')}")
        if peer_pool.get("size", 0) < 5:
            lines.append("> ⚠ 同类池规模不足，排名分位仅供参考，不可作为交易依据")
        lines.append("")

    window_labels = list(WINDOWS.keys())

    # ── 收益类因子 ──
    lines.append("## 收益类因子")
    lines.append("")
    lines.append("格式：基金收益率 / 同类均值")
    lines.append("")

    er_pct = percentiles.get("excess_return", {})
    ir_pct = percentiles.get("information_ratio", {})

    header_cols = window_labels[:]
    if er_pct.get("pct") is not None:
        header_cols.append("同类分位(3年)")
    lines.append(f"| 指标 | {' | '.join(header_cols)} |")
    lines.append(f"|{':--|' * (len(header_cols) + 1)}")

    er = factors.get("excess_return", {})
    fund_cells = []
    peer_cells = []
    exc_cells = []
    for k in window_labels:
        v = er.get(k, {})
        if isinstance(v, dict):
            fund_cells.append(_fmt(v.get("fund_return"), "%"))
            peer_cells.append(_fmt(v.get("peer_return"), "%"))
            exc_cells.append(_fmt(v.get("excess"), "%"))
        else:
            fund_cells.append("N/A")
            peer_cells.append("N/A")
            exc_cells.append("N/A")
    if er_pct.get("pct") is not None:
        fund_cells.append(f"{er_pct['rank']}(p{er_pct['pct']:.0f})")
        peer_cells.append("")
        exc_cells.append("")

    lines.append(f"| 基金收益 | {' | '.join(fund_cells)} |")
    lines.append(f"| 同类均值 | {' | '.join(peer_cells)} |")
    lines.append(f"| 超额收益 | {' | '.join(exc_cells)} |")

    ir = factors.get("information_ratio", {})
    ir_cells = [_fmt(ir.get(k)) for k in window_labels]
    if ir_pct.get("pct") is not None:
        ir_cells.append(f"{ir_pct['rank']}(p{ir_pct['pct']:.0f})")
    lines.append(f"| 信息比率 | {' | '.join(ir_cells)} |")
    lines.append("")

    # ── 风险类因子 ──
    lines.append("## 风险类因子")
    lines.append("")

    dd_pct = percentiles.get("max_drawdown", {})
    vol_pct = percentiles.get("volatility", {})
    dv_pct = percentiles.get("downside_deviation", {})
    var_pct = percentiles.get("var_95", {})
    rt_pct = percentiles.get("recovery_time", {})
    cr_pct = percentiles.get("calmar_ratio", {})

    risk_cols = window_labels[:]
    if dd_pct.get("pct") is not None:
        risk_cols.append("同类分位(3年)")
    lines.append(f"| 指标 | {' | '.join(risk_cols)} |")
    lines.append(f"|{':--|' * (len(risk_cols) + 1)}")

    dd = factors.get("max_drawdown", {})
    dd_cells = [_fmt(dd.get(k)) for k in window_labels]
    if dd_pct.get("pct") is not None:
        dd_cells.append(f"{dd_pct['rank']}(回撤大=差, p{dd_pct['pct']:.0f})")
    lines.append(f"| 最大回撤(%) | {' | '.join(dd_cells)} |")

    vol = factors.get("volatility", {})
    vol_cells = [_fmt(vol.get(k)) for k in window_labels]
    if vol_pct.get("pct") is not None:
        vol_cells.append(f"{vol_pct['rank']}")
    lines.append(f"| 年化波动(%) | {' | '.join(vol_cells)} |")

    dd_dev = factors.get("downside_deviation", {})
    dv_cells = [_fmt(dd_dev.get(k)) for k in window_labels]
    if dv_pct.get("pct") is not None:
        dv_cells.append(f"{dv_pct['rank']}")
    lines.append(f"| 下行偏差(%) | {' | '.join(dv_cells)} |")

    var95 = factors.get("var_95", {})
    var_cells = [_fmt(var95.get(k)) for k in window_labels]
    if var_pct.get("pct") is not None:
        var_cells.append(f"{var_pct['rank']}")
    lines.append(f"| VaR(95%) | {' | '.join(var_cells)} |")

    cr = factors.get("calmar_ratio", {})
    cr_cells = [_fmt(cr.get(k)) for k in window_labels]
    if cr_pct.get("pct") is not None:
        cr_cells.append(f"{cr_pct['rank']}(p{cr_pct['pct']:.0f})")
    lines.append(f"| 卡玛比率 | {' | '.join(cr_cells)} |")

    rt3 = factors.get("recovery_time", {}).get("3y")
    rt_cell = _fmt(rt3, "天")
    if rt_pct.get("pct") is not None:
        rt_cell += f" / {rt_pct['rank']}"
    lines.append(f"| 回撤恢复(3年) | {rt_cell} |")
    lines.append("")

    # ── 持仓与行业 + 因子暴露 ──
    conc = factors.get("concentration", {})
    ind = factors.get("industry", {})
    fe = factors.get("factor_exposure", {})
    as_val = factors.get("active_share", {})
    top10 = conc.get("top10_pct")
    if top10 is not None or ind.get("top3_pct") is not None or fe.get("status") in ("稳定", "预警", "漂移"):
        lines.append("## 持仓与风格锚定")
        lines.append("")
        lines.append("> 注：持仓/行业数据来自季报，滞后 1-3 个月。")
        lines.append("")
        if top10 is not None:
            lines.append(f"前 10 持仓占比：{top10}%")
        if ind.get("top3_pct") is not None:
            lines.append(f"前 3 行业占比：{ind['top3_pct']}%  ({_fmt(ind.get('latest_quarter'))})")
        if ind.get("drift") is not None:
            drift = ind["drift"]
            flag = "⚠" if drift > 15 else ""
            lines.append(f"行业漂移(季环比)：{flag} {drift}%")
        if fe.get("status") in ("稳定", "预警", "漂移"):
            lines.append(f"因子暴露稳定性：{fe['status']} {('⚠ ' + '; '.join(fe.get('issues', []))) if fe.get('issues') else ''}")
        if as_val.get("active_share") is not None:
            lines.append(f"Active Share：{as_val['active_share']}%")
            if as_val.get("note"):
                lines.append(f"  > {as_val['note']}")
        else:
            lines.append(f"Active Share：数据不可得（需基准指数持仓数据）")
        lines.append("")

    # ── 资金行为 ──
    lines.append("## 资金行为")
    lines.append("")
    flow = factors.get("fund_flow", {})
    lines.append(f"申购状态：{flow.get('purchase_status', 'N/A')}  |  赎回状态：{flow.get('redeem_status', 'N/A')}")
    restrictions = flow.get("restrictions", "")
    if restrictions and restrictions != "正常":
        lines.append(f"限制：{restrictions}")
    lines.append("")

    # ── 验证校验 ──
    lines.append("## 验证校验")
    lines.append("")
    stab = validation.get("stability", {})
    lines.append(f"**稳定性**：{stab.get('status', 'N/A')}")
    if stab.get("issues"):
        for i in stab["issues"]:
            lines.append(f"- ⚠ {i}")
    if stab.get("detail"):
        lines.append(f"  {stab['detail']}")
    sens = validation.get("sensitivity", {})
    if sens.get("flips"):
        lines.append(f"**敏感性**：⚠ {len(sens['flips'])} 项结论可能翻转")
        for f in sens["flips"]:
            lines.append(f"- {f}")
    else:
        lines.append("**敏感性**：✓ 参数变化不改变结论方向")
    scenario = validation.get("scenario", {})
    scenario_note = scenario.get("_note", "")

    if isinstance(scenario, dict) and "牛市" in scenario:
        lines.append("**多情景回测（年化）**：")
        for phase in ["牛市", "熊市", "震荡"]:
            sp = scenario.get(phase)
            if sp:
                lines.append(f"- {phase}：年化 {_fmt(sp.get('return_ann'), '%')}"
                             f"  累计 {_fmt(sp.get('total_return'), '%')}"
                             f"  波动 {_fmt(sp.get('volatility'), '%')}"
                             f"  区间 {sp.get('period', '')}")
            else:
                lines.append(f"- {phase}：无足够样本")
    else:
        lines.append(f"**多情景回测**：{scenario.get('status', 'N/A')}")

    if scenario_note:
        lines.append(f"> ⚠ {scenario_note}")
    lines.append("")

    # ── 第一层评分（不含行为共识） ──
    lines.append("## 第一层评分（基础因子评分）")
    lines.append("")
    base_score = scores.get("base_score", scores.get("overall_score"))
    if base_score is not None:
        lines.append(f"基础分：{base_score}  （范围 0-1，基于同类排名分位加权计算。不含行为共识修正）")
    else:
        lines.append("基础分：数据不足，无法评分")
    lines.append("")
    lines.append("| 维度 | 得分 | 权重 | 置信度 | 同类分位 | 说明 |")
    lines.append("|:-----|:-----|:-----|:------|:---------|:-----|")
    dim_labels = {"return": "收益", "risk": "风险", "style": "风格锚定",
                  "quality": "质量", "fee": "费率效率"}
    for dim, ds in scores.get("dim_scores", {}).items():
        label = dim_labels.get(dim, dim)
        score = ds.get("score", "N/A")
        if score is None:
            score = "—"
        w = ds.get("weight", 0)
        conf = ds.get("confidence", "低")
        rank = ds.get("rank", "N/A")
        detail = ds.get("detail", "")
        lines.append(f"| {label} | {score} | {int(w*100)}% | {conf} | {rank} | {detail} |")
    lines.append("")

    # ── 行为共识修正 ──
    behavior = scores.get("behavior")
    if behavior:
        lines.append("## 行为共识修正")
        lines.append("")
        lines.append(f"修正系数：{behavior.get('boost', 0):+.3f}  (案由缩放: {behavior.get('case_modifier', 1.0)})")
        if behavior.get("signals"):
            lines.append("信号：")
            for sig in behavior["signals"]:
                lbl, val, conf = sig[0], sig[1], sig[2] if len(sig) >= 3 else ""
                arrow = "↑" if val >= 0 else "↓"
                lines.append(f"  {arrow} {lbl} ({abs(val):.0%}) [{conf}]")
        if behavior.get("info_gaps"):
            lines.append("信息缺口：")
            for gap in behavior["info_gaps"]:
                lines.append(f"  ⚠ {gap}（数据不可得）")
        final_score = scores.get("overall_score", "N/A")
        if final_score is not None:
            lines.append("")
            lines.append(f"最终得分（修正后）：**{final_score}**")
        else:
            lines.append("")
            lines.append("最终得分：数据不足以评分")
        lines.append("")

    # ── 定量层局限性 ──
    lines.append("## 定量层局限性")
    lines.append("")
    lines.append("- 数据源：AKShare（爬取天天基金/东方财富公开页面），数据延迟 T+1 以上，持仓数据滞后 1-3 个月")
    lines.append("- 同类池：按基金类型字符串匹配，存在分类粒度粗糙的风险；同类池规模不足 10 只时排名分位不可靠")
    lines.append("- 费率效率维度使用前10持仓集中度作为 Active Share 的粗糙代理，非精确计算")
    lines.append("- 因子暴露稳定性为基于净值收益分布的前后两段对比，非真实的恒生五因子回归暴露")
    limitations = []
    if peer_pool.get("size", 0) < 5:
        limitations.append("同类池规模不足，整体评分可信度下降")
    if scenario.get("status") == "无市场指数数据":
        limitations.append("无市场指数数据，无法做情景回测")
    if stab.get("status") == "预警":
        limitations.append("稳定性检验预警，因子特征可能已变化")
    for lim in limitations:
        lines.append(f"- ⚠ {lim}")
    lines.append("")

    lines.append("---")
    lines.append("*第一层输出：因子分析到此为止，不涉及买卖判断。第二层综合判断由 AI 基于因子报告+定性查证给出。*")
    lines.append("")
    lines.append("*定性查证关键词/来源将在第二层报告中补充。*")
    return "\n".join(lines)
