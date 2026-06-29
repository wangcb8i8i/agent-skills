"""数据层面测试：字段覆盖 + 合理性。

测试范围：
  - 估值序列：PE(TTM)/PE(静)/PB/PS/PCF/PEG 是否存在、非空、区间合理
  - 财务指标：盈利能力/规模/现金流/资产负债/营运各字段非空率和值域
  - 实时快照：最新价/PE/PB/市值是否存在
  - 自由现金流 FCF：FCFF_FORWARD/FCFF_BACK 列可用性
  - 基金数据：净值走势/规模变动/基金经理信息
  - 基金持仓：季度前十大持仓字段可用

用法:
  pytest scripts/tests/test_data_quality.py -v
  python -m pytest scripts/tests/test_data_quality.py --tb=short -k "fund"
"""

from datetime import datetime

import pytest

from engines._shared.akshare import (
    financial_indicators,
    valuation_history,
    spot_snapshot,
)
from engines._shared.eastmoney import parse_pingzhong, parse_holdings

# ─── 阈值 ──────────────────────────────────────────────────────
PE_MIN, PE_MAX = 0, 500
PB_MIN, PB_MAX = 0, 100
ROE_MIN, ROE_MAX = -200, 200
NONNULL_THRESHOLD = 60  # %

FUND_CODES = ["001513", "110011"]


# ─── 辅助 ──────────────────────────────────────────────────────


def _latest(df, col):
    vals = df[col].dropna()
    return float(vals.iloc[-1]) if len(vals) > 0 else None


# ══════════════════════════════════════════════════════════════════
# 估值序列
# ══════════════════════════════════════════════════════════════════


class TestValuation:
    """估值历史序列字段覆盖与合理性。"""

    @pytest.fixture(autouse=True)
    def _setup(self, stock_code):
        self.code = stock_code
        self.df = valuation_history(stock_code)
        assert self.df is not None and not self.df.empty, \
            f"{stock_code}: valuation_history() 返回空"

    def test_valuation_has_pe_ttm(self):
        assert "PE(TTM)" in self.df.columns, "PE(TTM) 列缺失"
        v = _latest(self.df, "PE(TTM)")
        assert v is not None and PE_MIN <= v <= PE_MAX, \
            f"PE(TTM)={v} 超出 [{PE_MIN},{PE_MAX}]"

    def test_valuation_has_pe_static(self):
        assert "PE(静)" in self.df.columns
        v = _latest(self.df, "PE(静)")
        assert v is not None and PE_MIN <= v <= PE_MAX, \
            f"PE(静)={v} 超出 [{PE_MIN},{PE_MAX}]"

    def test_valuation_has_pb(self):
        assert "市净率" in self.df.columns, "市净率列缺失"
        v = _latest(self.df, "市净率")
        assert v is not None and PB_MIN <= v <= PB_MAX, \
            f"PB={v} 超出 [{PB_MIN},{PB_MAX}]"

    def test_valuation_has_ps(self):
        assert "市销率" in self.df.columns
        v = _latest(self.df, "市销率")
        assert v is not None and PB_MIN <= v <= PB_MAX * 10, \
            f"PS={v} 超出范围"

    def test_valuation_has_pcf(self):
        assert "市现率" in self.df.columns

    def test_valuation_has_peg(self):
        assert "PEG值" in self.df.columns

    def test_valuation_sequence_length(self):
        rows = len(self.df)
        assert rows >= 200, f"历史序列仅 {rows} 日，预期 >= 200"

    def test_valuation_nonnull_rate(self):
        threshold = len(self.df) * 0.95
        for col in ("PE(TTM)", "市净率", "市销率"):
            nn = int(self.df[col].notna().sum())
            assert nn >= threshold, \
                f"{col}: {nn}/{len(self.df)} 非空，低于 95%"


# ══════════════════════════════════════════════════════════════════
# 财务指标
# ══════════════════════════════════════════════════════════════════


class TestFinancialIndicators:
    """财务指标字段覆盖与非空率。"""

    AKSHARE_EXPECTED = {
        "盈利能力": ["ROEJQ", "ROEKCJQ", "ROIC", "XSMLL", "XSJLL", "ZZCJLL"],
        "规模利润": ["TOTALOPERATEREVE", "PARENTNETPROFIT", "KCFJCXSYJLR",
                     "EPSJB", "PER_TOI"],
        "现金流":   ["MGJYXJJE", "FCFF_FORWARD", "FCFF_BACK"],
        "资产负债": ["BPS", "ZCFZL", "LD", "SD", "CASH_RATIO"],
        "营运周转": ["TOAZZL", "CHZZL", "YSZKZZL", "FIXED_ASSET_TR"],
    }

    AKSHARE_RANGE_CHECKS = {
        "ROEJQ": (ROE_MIN, ROE_MAX, "ROE-加权"),
        "XSMLL": (-10, 100, "销售毛利率"),
        "XSJLL": (-50, 100, "销售净利率"),
        "ZCFZL": (0, 100, "资产负债率"),
        "LD":    (0, 50,  "流动比率"),
    }

    @pytest.fixture(autouse=True)
    def _setup(self, stock_code):
        self.code = stock_code
        self.df = financial_indicators(stock_code)
        assert self.df is not None and not self.df.empty, \
            f"{stock_code}: financial_indicators() 返回空"

    def test_has_expected_columns(self):
        cols = set(self.df.columns)
        missing = []
        for group, columns in self.AKSHARE_EXPECTED.items():
            for col in columns:
                if col not in cols:
                    missing.append(f"{group}/{col}")
        assert not missing, \
            f"缺 {len(missing)} 列: {missing}"

    def test_column_count(self):
        assert len(self.df.columns) >= 100, \
            f"仅 {len(self.df.columns)} 列，AKShare 预期 >= 100"

    def test_report_periods(self):
        assert len(self.df) >= 4, \
            f"仅 {len(self.df)} 个报告期"

    def test_nonnull_rate(self):
        cols = ["ROEJQ", "XSMLL", "XSJLL", "TOTALOPERATEREVE",
                "PARENTNETPROFIT", "EPSJB", "ZCFZL", "BPS"]
        total = len(self.df)
        low = []
        for col in cols:
            nn = int(self.df[col].notna().sum())
            rate = nn / total * 100
            if rate < NONNULL_THRESHOLD:
                low.append(f"{col}={rate:.0f}%({nn}/{total})")
        assert not low, \
            f"{len(low)} 列非空率低于 {NONNULL_THRESHOLD}%: {low}"

    def test_value_ranges(self):
        latest = self.df.iloc[0]
        issues = []
        for col, (lo, hi, label) in self.AKSHARE_RANGE_CHECKS.items():
            if col not in self.df.columns:
                continue
            v = latest.get(col)
            if v is None or (isinstance(v, float) and v != v):
                continue
            if v < lo or v > hi:
                issues.append(f"{label}({col})={v} 超出 [{lo},{hi}]")
        assert not issues, "; ".join(issues)

    def test_roe_reasonable(self):
        if "ROEJQ" not in self.df.columns:
            pytest.skip("ROEJQ 列缺失")
        vals = self.df["ROEJQ"].dropna()
        assert len(vals) > 0, "ROEJQ 全为空"
        outliers = [(i, float(v)) for i, v in vals.items()
                    if v < ROE_MIN or v > ROE_MAX]
        assert not outliers, \
            f"{len(outliers)} 期 ROE 超出 [{ROE_MIN},{ROE_MAX}]: {[f'{v:.1f}' for _, v in outliers[:5]]}"


# ══════════════════════════════════════════════════════════════════
# 自由现金流 FCF
# ══════════════════════════════════════════════════════════════════


class TestFCF:
    """自由现金流列可用性。"""

    @pytest.fixture(autouse=True)
    def _setup(self, stock_code):
        self.df = financial_indicators(stock_code)

    def test_fcff_forward_column(self):
        assert self.df is not None, "financial_indicators 无数据"
        assert "FCFF_FORWARD" in self.df.columns, "FCFF_FORWARD 列缺失"

    def test_fcff_back_column(self):
        assert self.df is not None
        assert "FCFF_BACK" in self.df.columns, "FCFF_BACK 列缺失"

    def test_fcff_has_values(self):
        assert self.df is not None
        nn = int(self.df["FCFF_FORWARD"].notna().sum())
        assert nn >= 1, "FCFF_FORWARD 全为空"

    def test_operating_cf_per_share(self):
        assert self.df is not None
        assert "MGJYXJJE" in self.df.columns, "每股经营现金流列缺失"


# ══════════════════════════════════════════════════════════════════
# 实时快照
# ══════════════════════════════════════════════════════════════════


class TestSpotSnapshot:
    """实时行情快照基本字段。"""

    @pytest.fixture(autouse=True)
    def _setup(self, stock_code):
        self.snap = spot_snapshot(stock_code)

    def test_spot_has_price(self):
        assert self.snap, "spot_snapshot 返回 None"
        price = self.snap.get("最新价") or self.snap.get("price")
        assert price is not None and float(price) > 0, "无最新价"

    def test_spot_has_market_cap(self):
        assert self.snap
        cap = self.snap.get("总市值") or self.snap.get("market_cap")
        assert cap is not None and float(cap) > 1e8, \
            f"总市值异常: {cap}"


# ══════════════════════════════════════════════════════════════════
# 基金—净值/规模/经理
# ══════════════════════════════════════════════════════════════════


class TestFundPingzhong:
    """基金综合数据（净值走势/规模变动/经理信息）字段覆盖。"""

    @pytest.fixture(params=FUND_CODES)
    def fund_code(self, request):
        return request.param

    @pytest.fixture(autouse=True)
    def _setup(self, fund_code):
        self.code = fund_code
        self.data = parse_pingzhong(fund_code)

    def test_pingzhong_returns_dict(self):
        assert self.data is not None, f"{self.code}: parse_pingzhong() 返回 None"
        assert isinstance(self.data, dict), "返回值不是 dict"

    def test_pingzhong_has_name_and_code(self):
        assert self.data
        assert self.data.get("fS_name") is not None, "基金名称缺失"
        code = self.data.get("fS_code")
        assert code is not None and str(code).strip(), "基金代码缺失"

    def test_pingzhong_nav_history(self):
        """单位净值走势存在且有值。"""
        assert self.data
        nav = self.data.get("单位净值走势")
        assert nav is not None, "单位净值走势缺失"
        assert len(nav) > 0, "单位净值走势为空"
        first = nav[0] if isinstance(nav, list) else list(nav.values())[0]
        assert first is not None, "净值首条数据为空"

    def test_pingzhong_scale_history(self):
        """规模变动存在且有值。"""
        assert self.data
        scale = self.data.get("规模变动")
        assert scale is not None, "规模变动缺失"
        assert len(scale) > 0, "规模变动为空"

    def test_pingzhong_manager(self):
        """基金经理信息存在。"""
        assert self.data
        mgr = self.data.get("基金经理")
        assert mgr is not None, "基金经理信息缺失"
        assert len(mgr) > 0, "基金经理信息为空"


# ══════════════════════════════════════════════════════════════════
# 基金—前十大持仓
# ══════════════════════════════════════════════════════════════════


class TestFundHoldings:
    """季度前十大持仓字段覆盖。"""

    @pytest.fixture(params=FUND_CODES)
    def fund_code(self, request):
        return request.param

    @pytest.fixture(autouse=True)
    def _setup(self, fund_code):
        self.code = fund_code
        from engines._shared.eastmoney import THIS_YEAR
        self.quarters = parse_holdings(fund_code, THIS_YEAR)

    def test_holdings_returns_list(self):
        assert isinstance(self.quarters, list), f"返回值不是 list: {type(self.quarters)}"

    def test_holdings_has_latest_quarter(self):
        if not self.quarters:
            pytest.skip(f"{self.code}: 今年暂无持仓数据")
        q = self.quarters[0]
        assert "year" in q, "季度缺少 year"
        assert "quarter" in q, "季度缺少 quarter"
        assert "holdings" in q, "季度缺少 holdings"

    def test_holdings_stock_fields(self):
        if not self.quarters:
            pytest.skip("无持仓数据")
        q = self.quarters[0]
        stocks = q.get("holdings", [])
        if not stocks:
            pytest.skip("该季度无持仓明细")
        s = stocks[0]
        assert "股票代码" in s, f"持仓缺股票代码: {list(s.keys())}"
        assert "股票名称" in s, "持仓缺股票名称"
        assert "占净值比" in s, "持仓缺占净值比"

    def test_holdings_recent_years_structure(self):
        """最近 3 年持仓结构完整（非空字段按季度呈现）。"""
        if not self.quarters:
            pytest.skip("无持仓数据")
        count = len(self.quarters)
        assert count >= 1, f"最近 3 年 {self.code} 仅 {count} 个季度持仓"
        for i, q in enumerate(self.quarters[:4]):
            assert q.get("holdings"), \
                f"第 {i+1} 季度 {q.get('title','')} 持仓列表为空"
            assert len(q["holdings"]) > 0, \
                f"第 {i+1} 季度持仓明细为空"
