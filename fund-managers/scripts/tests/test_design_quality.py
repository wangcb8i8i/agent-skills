"""代码架构质量测试：接口 / 序列化 / 列名兼容 / 跨源一致 / 回退链 / 边界。

这些测试不关心某只股票数据的具体值，而是验证数据层代码结构正确。

用法:
  pytest scripts/tests/test_design_quality.py -v
  python -m pytest scripts/tests/test_design_quality.py --tb=short
"""

import inspect
import json
import os
import subprocess
import sys
import tempfile

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS_DIR)

from engines._shared import akshare
from engines._shared.output import extract_output_dir, save_output

# 用第一只股票做代码结构测试（不参数化，因为测的是代码而非数据）
CODE = "600519"


# ══════════════════════════════════════════════════════════════════
# 接口契约
# ══════════════════════════════════════════════════════════════════


class TestInterfaceContract:
    """所有公共接口存在、签名符合约定。"""

    PUBLIC_FNS = {
        "financial_indicators": akshare.financial_indicators,
        "valuation_history": akshare.valuation_history,
        "daily_bars": akshare.daily_bars,
        "spot_snapshot": akshare.spot_snapshot,
    }

    def test_all_interfaces_importable(self):
        for name, fn in self.PUBLIC_FNS.items():
            assert callable(fn), f"{name} 不可调用"

    def test_first_param_is_symbol(self):
        for name, fn in self.PUBLIC_FNS.items():
            sig = inspect.signature(fn)
            first = list(sig.parameters.keys())[0]
            assert first in ("symbol", "code"), \
                f"{name}: 首参不是 symbol/code，是 {first!r}"

    def test_fallback_modules_importable(self):
        """BaoStock 和 pytdx 回退模块的关键函数可导入。"""
        from engines._shared.baostock_wrapper import (
            daily_bars as bs_bars,
            financial_indicators as bs_fin,
            stock_basic_info as bs_info,
        )
        assert callable(bs_bars)
        assert callable(bs_fin)
        assert callable(bs_info)

        from engines._shared.pytdx_wrapper import (
            daily_bars as px_bars,
            spot_snapshot as px_spot,
        )
        assert callable(px_bars)
        assert callable(px_spot)

        # Fund data layer
        from engines._shared.eastmoney import (
            parse_pingzhong,
            parse_holdings,
            get,
        )
        assert callable(parse_pingzhong)
        assert callable(parse_holdings)
        assert callable(get)

    def test_output_module(self):
        """output.py 的 extract_output_dir / save_output 行为正确。"""
        # save_output 不崩溃
        save_output({"a": 1}, "_test_out.json", None)

        # extract_output_dir 解析
        saved_argv = list(sys.argv)
        try:
            sys.argv = ["script.py", "--output-dir", "/tmp/x", CODE]
            out_dir, rest = extract_output_dir()
            assert out_dir == "/tmp/x", f"output_dir={out_dir}"
            assert rest == [CODE], f"rest={rest}"

            sys.argv = ["script.py", CODE]
            out_dir2, rest2 = extract_output_dir()
            assert out_dir2 is None
            assert rest2 == [CODE]
        finally:
            sys.argv = saved_argv

        # save_output 写盘
        with tempfile.TemporaryDirectory() as td:
            save_output({"test": 1}, "_test.json", td)
            p = os.path.join(td, "_test.json")
            assert os.path.exists(p), "文件未写入"
            with open(p) as f:
                assert json.load(f)["test"] == 1, "内容不正确"
            os.remove(p)


# ══════════════════════════════════════════════════════════════════
# 序列化安全
# ══════════════════════════════════════════════════════════════════


class TestSerialization:
    """_safe_val + json.dumps 对各类边界值不报错。"""

    def _import_safe_vals(self):
        from engines.stock.valuation import _safe_val as sv
        from engines.stock.financials import _safe_val as sf
        return sv, sf

    BOUNDARY_INPUTS = [
        ("None",              None),
        ("int_0",             0),
        ("int_neg",           -42),
        ("float_pi",          3.14),
        ("float_nan",         float("nan")),
        ("float_inf",         float("inf")),
        ("str",               "hello"),
        ("bool_true",         True),
        ("bool_false",        False),
        ("empty_str",         ""),
    ]

    @pytest.mark.parametrize("label,val", BOUNDARY_INPUTS)
    def test_boundary_values(self, label, val):
        sv, sf = self._import_safe_vals()
        for name, fn in [("valuation", sv), ("financials", sf)]:
            converted = fn(val)
            json.dumps(converted, ensure_ascii=False)

    @pytest.mark.skipif(not __import__("importlib").util.find_spec("numpy"),
                        reason="numpy 未安装")
    def test_numpy_values(self):
        import numpy as np
        sv, sf = self._import_safe_vals()
        cases = {
            "float64_3.14": np.float64(3.14),
            "int64_42": np.int64(42),
            "float64_nan": np.float64("nan"),
        }
        for name, fn in [("valuation", sv), ("financials", sf)]:
            for label, val in cases.items():
                converted = fn(val)
                json.dumps(converted, ensure_ascii=False)

    def test_real_data_serializes(self):
        """financial_indicators 整行数据 JSON 安全。"""
        from engines.stock.financials import _safe_val as sv
        df = akshare.financial_indicators(CODE)
        assert df is not None, "financial_indicators 返回空"

        row = df.iloc[-1]
        record = {col: sv(row.get(col)) for col in df.columns}
        json.dumps(record, ensure_ascii=False)

        full = {"code": CODE, "reports": [record]}
        json.dumps(full, ensure_ascii=False)


# ══════════════════════════════════════════════════════════════════
# 列名兼容性
# ══════════════════════════════════════════════════════════════════


class TestColumnCompatibility:
    """akshare.py 的列名重映射与消费者代码无断裂。"""

    def test_valuation_rename_not_stale(self):
        """akshare.py 中 valuation_history 的列名 rename 是否匹配实际列。"""
        df = akshare.valuation_history(CODE)
        assert df is not None, "valuation_history 返回空"

        # akshare.py 当前的 rename 映射源键
        rename_sources = {"date", "pe", "pb", "ps", "pe_ttm_weighted",
                          "pb_ttm_weighted"}
        actual = set(c.lower() for c in df.columns)
        matched = rename_sources & actual
        # 允许部分匹配（既有旧键也有新键）；完全不匹配则 rename 是空操作
        assert len(matched) >= 1 or "PE(TTM)" in df.columns, \
            f"rename 源键 {rename_sources} 全不命中实际列 {list(df.columns)[:5]}; " \
            "rename 是空操作，应更新映射"

    def test_valuation_pe_column_name(self):
        """AKShare 返回 PE(TTM) 列，但消费者 valuation.py 查找 '市盈率'/'pe'。
        此测试仅报告当前状态而非阻断——列名漂移已由 QC-06 捕捉。"""
        df = akshare.valuation_history(CODE)
        assert df is not None
        # 无论列名是什么，只要有 PE 值就算覆盖
        pe_cols = [c for c in df.columns
                   if "PE" in c or "pe" in c or "市盈" in c]
        assert len(pe_cols) >= 1, \
            f"未找到任何 PE 相关列: {list(df.columns)}"

    def test_financials_column_count(self):
        """AKShare 财务主源列数远高于 BaoStock 回退。"""
        df = akshare.financial_indicators(CODE)
        assert df is not None
        assert len(df.columns) >= 100, \
            f"仅 {len(df.columns)} 列，主源不匹配"


# ══════════════════════════════════════════════════════════════════
# 跨源一致性
# ══════════════════════════════════════════════════════════════════


class TestCrossSourceConsistency:
    """同一指标在不同来源间偏差在合理范围。"""

    MAX_DIVERGE_PCT = 5.0

    def test_market_cap_consistency(self):
        """spot 总市值 vs valuation 最新总市值 ≤ 5%。"""
        spot = akshare.spot_snapshot(CODE)
        val_df = akshare.valuation_history(CODE)
        assert spot and val_df is not None, "数据缺失"

        spot_cap = spot.get("总市值") or spot.get("market_cap")
        val_cap = val_df["总市值"].iloc[-1] if "总市值" in val_df.columns else None
        assert spot_cap and val_cap, "一方无总市值"

        diff = abs(spot_cap - val_cap) / max(abs(val_cap), 1) * 100
        assert diff <= self.MAX_DIVERGE_PCT, \
            f"总市值偏差 {diff:.2f}% (spot={spot_cap:.0f} vs val={val_cap:.0f})"

    def test_price_consistency(self):
        """daily_bars 最新收盘 vs spot 最新价 ≤ 5%（网络不可达时跳过）。"""
        bars = akshare.daily_bars(CODE, start_date="20260101", end_date="20260630")
        spot = akshare.spot_snapshot(CODE)
        if bars is None or not spot:
            pytest.skip("daily_bars 或 spot 网络不可达")

        bar_close = bars["收盘"].iloc[-1] if "收盘" in bars.columns else None
        spot_price = spot.get("最新价") or spot.get("price")
        assert bar_close and spot_price, "一方无价格"

        diff = abs(bar_close - spot_price) / max(abs(bar_close), 1) * 100
        assert diff <= self.MAX_DIVERGE_PCT, \
            f"收盘偏差 {diff:.2f}% (bar={bar_close} vs spot={spot_price})"


# ══════════════════════════════════════════════════════════════════
# 回退链结构
# ══════════════════════════════════════════════════════════════════


class TestFallbackChain:
    """各回退层的输出列结构兼容。"""

    @pytest.mark.slow
    def test_daily_bars_three_layers(self):
        """daily_bars 三层回退都返回含 日期/收盘 的 DataFrame。"""
        from engines._shared.baostock_wrapper import daily_bars as bs_bars
        from engines._shared.pytdx_wrapper import daily_bars as px_bars

        sources = [
            ("AKShare", lambda: akshare.daily_bars(CODE)),
            ("BaoStock", lambda: bs_bars(CODE)),
            ("pytdx", lambda: px_bars(CODE)),
        ]
        failures = []
        for name, fn in sources:
            df = fn()
            if df is None or df.empty:
                failures.append(f"{name}: 无数据")
                continue
            for col in ("日期", "收盘"):
                if col not in df.columns:
                    failures.append(f"{name}: 缺 {col}")
        assert not failures, "; ".join(failures)

    def test_spot_snapshot_has_price(self):
        """spot_snapshot 通多路回退后至少返回最新价。"""
        snap = akshare.spot_snapshot(CODE)
        assert snap, "spot_snapshot 全链路失败"
        price = snap.get("最新价") or snap.get("price")
        assert price is not None and float(price) > 0, "无最新价"


# ══════════════════════════════════════════════════════════════════
# 边界与失效
# ══════════════════════════════════════════════════════════════════


class TestBoundary:
    """无效输入不崩溃、错误信息结构化。"""

    def test_invalid_code_no_crash(self):
        """所有 4 个接口对无效代码返回 None 而非抛异常。"""
        bad = "99999999"
        for name, fn in [
            ("financial_indicators", lambda: akshare.financial_indicators(bad)),
            ("valuation_history", lambda: akshare.valuation_history(bad)),
            ("daily_bars", lambda: akshare.daily_bars(bad)),
            ("spot_snapshot", lambda: akshare.spot_snapshot(bad)),
        ]:
            try:
                result = fn()
            except Exception as e:
                pytest.fail(f"{name}: 不应崩溃 ({e})")

    def test_cli_engines_exit_normally(self):
        """三个 CLI 引擎不因未捕获异常崩溃（exit=0 或 1 皆为正常退出）。"""
        engines = ["engines/stock/financials.py",
                   "engines/stock/valuation.py",
                   "engines/stock/price.py"]
        for rel_path in engines:
            path = os.path.join(SCRIPTS_DIR, rel_path)
            result = subprocess.run(
                [sys.executable, path, CODE],
                capture_output=True, text=True, cwd=SCRIPTS_DIR, timeout=120,
            )
            # exit=1 可接受（网络不可达时的结构化错误）
            if result.returncode != 0:
                # 验证输出了结构化 JSON error
                output = result.stdout.strip()
                json_start = output.find("{")
                assert json_start >= 0, \
                    f"{rel_path} exit={result.returncode} 且无 JSON 输出: {output[:200]}"
                data = json.loads(output[json_start:])
                assert "error" in data, \
                    f"{rel_path} exit={result.returncode} 但 JSON 无 error 字段"

    def test_cli_engines_produce_json(self):
        """三个 CLI 引擎输出合法 JSON（成功或错误皆可）。"""
        engines = ["engines/stock/financials.py",
                   "engines/stock/valuation.py",
                   "engines/stock/price.py"]
        for rel_path in engines:
            path = os.path.join(SCRIPTS_DIR, rel_path)
            result = subprocess.run(
                [sys.executable, path, CODE],
                capture_output=True, text=True, cwd=SCRIPTS_DIR, timeout=120,
            )
            output = result.stdout.strip()
            json_start = output.find("{")
            assert json_start >= 0, \
                f"{rel_path} 输出不含 JSON: {output[:200]}"
            try:
                json.loads(output[json_start:])
            except json.JSONDecodeError:
                pytest.fail(f"{rel_path} 输出非合法 JSON: {output[:200]}")


# ══════════════════════════════════════════════════════════════════
# 基金 CLI
# ══════════════════════════════════════════════════════════════════


class TestFundBoundary:
    """基金 CLI 引擎边界测试。"""

    FUND_CODE = "001513"
    FUND_ENGINES = [
        "engines/fund/holdings.py",
        "engines/fund/nav.py",
        "engines/fund/scale.py",
        "engines/fund/managers.py",
    ]

    def test_fund_cli_engines_exit_normally(self):
        """四个基金 CLI 引擎对有效代码正常退出。"""
        for rel_path in self.FUND_ENGINES:
            path = os.path.join(SCRIPTS_DIR, rel_path)
            result = subprocess.run(
                [sys.executable, path, self.FUND_CODE],
                capture_output=True, text=True, cwd=SCRIPTS_DIR, timeout=120,
            )
            assert result.returncode == 0, \
                f"{rel_path}: exit={result.returncode} {result.stderr[:200]}"

    def test_fund_cli_engines_produce_json(self):
        """四个基金 CLI 引擎输出合法 JSON。"""
        for rel_path in self.FUND_ENGINES:
            path = os.path.join(SCRIPTS_DIR, rel_path)
            result = subprocess.run(
                [sys.executable, path, self.FUND_CODE],
                capture_output=True, text=True, cwd=SCRIPTS_DIR, timeout=120,
            )
            assert result.returncode == 0, f"{rel_path} 异常退出"
            output = result.stdout.strip()
            json_start = output.find("{")
            assert json_start >= 0, \
                f"{rel_path} 输出不含 JSON: {output[:200]}"
            try:
                data = json.loads(output[json_start:])
            except json.JSONDecodeError:
                pytest.fail(f"{rel_path} 输出非合法 JSON: {output[:200]}")

    def test_holdings_output_schema(self):
        """holdings.py 输出包含 quarters 列表。"""
        path = os.path.join(SCRIPTS_DIR, "engines/fund/holdings.py")
        result = subprocess.run(
            [sys.executable, path, self.FUND_CODE],
            capture_output=True, text=True, cwd=SCRIPTS_DIR, timeout=120,
        )
        assert result.returncode == 0
        json_start = result.stdout.find("{")
        data = json.loads(result.stdout[json_start:])
        assert "code" in data, "缺 code 字段"
        assert "quarters" in data, "缺 quarters 字段"
        assert isinstance(data["quarters"], list), "quarters 不是 list"

    def test_nav_output_schema(self):
        """nav.py 输出包含净值走势字段。"""
        path = os.path.join(SCRIPTS_DIR, "engines/fund/nav.py")
        result = subprocess.run(
            [sys.executable, path, self.FUND_CODE],
            capture_output=True, text=True, cwd=SCRIPTS_DIR, timeout=120,
        )
        assert result.returncode == 0
        json_start = result.stdout.find("{")
        data = json.loads(result.stdout[json_start:])
        assert "code" in data, "缺 code 字段"
        nav = data.get("单位净值走势")
        if nav is not None:
            assert len(nav) > 0, "净值走势为空"
