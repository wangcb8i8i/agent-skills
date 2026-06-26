# -*- coding: utf-8 -*-
"""天天基金 / 东方财富 API 公共模块：请求、解析。

所有 fund 引擎脚本通过此模块访问数据源，支持同一套重试/回退逻辑。

回退链路（每层失败自动尝试下一层）：
  主源 → 天天基金 HTTP (eastmoney)
           └→ 失败 → AKShare 基金 API
                        └→ 失败 → 返回 None（降级容忍）
"""
import os, re, json, time, datetime, sys
import requests
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings()

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
THIS_YEAR = datetime.date.today().year

_S = requests.Session()
_S.headers.update({"User-Agent": UA})
_S.verify = False

# AKShare 基金回退（延迟导入，仅在需要时加载）
_HAVE_AK = None


def _check_akshare():
    global _HAVE_AK
    if _HAVE_AK is None:
        try:
            import akshare as ak
            _HAVE_AK = True
        except ImportError:
            _HAVE_AK = False
    return _HAVE_AK


def get(url, referer=None, tries=3):
    """HTTP GET with retry. Returns response text or None."""
    h = {"Referer": referer} if referer else {}
    for i in range(tries):
        try:
            r = _S.get(url, headers=h, timeout=40)
            r.encoding = "utf-8"
            if r.status_code == 200:
                return r.text
        except Exception as e:
            print(f"    retry({i+1}) {url[:70]}: {e}", file=sys.stderr)
        time.sleep(1.5)
    return None


def safe(s):
    return re.sub(r'[\\/:*?"<>|\s]+', "_", (s or "").strip())[:80]


def fmt_ts(ms):
    try:
        return datetime.datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d")
    except Exception:
        return str(ms)


def _ak_parse_pingzhong(code):
    """AKShare 基金 API 回退：获取基金净值/规模/经理信息。

    AKShare 无单一接口对应 pingzhongdata.js 的所有字段，
    组合多个接口拼出近似的输出结构。
    """
    if not _check_akshare():
        return None
    try:
        import akshare as ak

        result = {"fS_name": None, "fS_code": code}

        # 1. 基金名称
        try:
            info = ak.fund_em_open_fund_info(fund=code, indicator="单位净值走势")
            if info is not None and not info.empty:
                result["fS_name"] = info.columns[-1] if len(info.columns) > 1 else code
        except Exception:
            pass

        # 2. 单位净值走势
        try:
            nav = ak.fund_em_open_fund_info(fund=code, indicator="单位净值走势")
            if nav is not None and not nav.empty:
                rows = []
                for _, r in nav.iterrows():
                    row = {}
                    for col in nav.columns:
                        row[col] = r[col]
                    rows.append(row)
                result["单位净值走势"] = rows
        except Exception:
            pass

        # 3. 累计净值走势
        try:
            acc = ak.fund_em_open_fund_info(fund=code, indicator="累计净值走势")
            if acc is not None and not acc.empty:
                rows = []
                for _, r in acc.iterrows():
                    row = {}
                    for col in acc.columns:
                        row[col] = r[col]
                    rows.append(row)
                result["累计净值走势"] = rows
        except Exception:
            pass

        # 4. 规模变动
        try:
            scale = ak.fund_em_open_fund_info(fund=code, indicator="规模变动")
            if scale is not None and not scale.empty:
                rows = []
                for _, r in scale.iterrows():
                    row = {}
                    for col in scale.columns:
                        row[col] = r[col]
                    rows.append(row)
                result["规模变动"] = rows
        except Exception:
            pass

        # 5. 基金经理 - AKShare 无直接接口，从 fund_em_manager 获取
        try:
            mgr = ak.fund_em_manager(fund=code)
            if mgr is not None and not mgr.empty:
                rows = []
                for _, r in mgr.iterrows():
                    row = {}
                    for col in mgr.columns:
                        row[col] = r[col]
                    rows.append(row)
                result["基金经理"] = rows
        except Exception:
            pass

        return result
    except Exception as e:
        print(f"    AKShare fund fallback ({code}) 失败: {e}", file=sys.stderr)
        return None


def _ak_parse_holdings(code, year):
    """AKShare 基金 API 回退：获取指定年度的季度前十大持仓。

    AKShare 通过 fund_em_portfolio_hold 一次返回所有披露季度持仓。
    """
    if not _check_akshare():
        return []
    try:
        import akshare as ak
        # AKShare 一次拉全部季度持仓
        df = ak.fund_em_portfolio_hold(code=code)
        if df is None or df.empty:
            return []

        results = []
        for _, row in df.iterrows():
            try:
                # 尝试从 "YYYY-MM-DD" 推算出年份季度
                date_str = str(row.get("截止日期", ""))
                if not date_str or len(date_str) < 7:
                    continue
                y = int(date_str[:4])
                if y != year:
                    continue
                m = int(date_str[5:7])
                q = (m + 2) // 3  # 月份→季度
                stock_code = str(row.get("股票代码", ""))
                stock_name = str(row.get("股票名称", ""))
                pct = row.get("占净值比例", row.get("持仓占比", ""))
                if isinstance(pct, (int, float)):
                    pct = f"{pct:.2f}%"
                results.append({
                    "股票代码": stock_code,
                    "股票名称": stock_name,
                    "占净值比": str(pct),
                })
            except Exception:
                continue

        if results:
            return [{
                "year": year,
                "quarter": max(((int(str(row.get("截止日期", ""))[5:7]) + 2) // 3) if row.get("截止日期") else 4, 1),
                "title": f"{year}年第{max(((int(str(row.get('截止日期', ''))[5:7]) + 2) // 3), 1)}季度",
                "holdings": results,
            }]
        return []
    except Exception as e:
        print(f"    AKShare fund holdings fallback ({code}) 失败: {e}", file=sys.stderr)
        return []


def parse_pingzhong(code):
    """解析天天基金 pingzhongdata/{code}.js → dict (净值/业绩/规模/经理等)。

    回退链路：eastmoney HTTP → AKShare 基金 API → None
    """
    # 第 1 层：eastmoney HTTP
    txt = get(f"https://fund.eastmoney.com/pingzhongdata/{code}.js")
    if txt:
        def var(name, default=None):
            m = re.search(
                r"var\s+" + re.escape(name) + r"\s*=\s*(.*?);\s*(?:/\*|var\s|function|$)",
                txt, re.S,
            )
            if not m:
                return default
            raw = m.group(1).strip()
            try:
                return json.loads(raw)
            except Exception:
                return raw.strip('"')

        return {
            "fS_name": var("fS_name"),
            "fS_code": var("fS_code"),
            "单位净值走势": var("Data_netWorthTrend"),
            "累计净值走势": var("Data_ACWorthTrend"),
            "累计收益率走势": var("Data_grandTotal"),
            "同类排名走势": var("Data_rateInSimilarType"),
            "规模变动": var("Data_fluctuationScale"),
            "持有人结构": var("Data_holderStructure"),
            "资产配置": var("Data_assetAllocation"),
            "业绩评价": var("Data_performanceEvaluation"),
            "基金经理": var("Data_currentFundManager"),
        }

    # 第 2 层：AKShare 基金 API 回退
    return _ak_parse_pingzhong(code)


def parse_holdings(code, year):
    """解析天天基金某年度的季度前十大持仓 → list[dict]

    回退链路：eastmoney HTTP → AKShare 基金 API → []
    """
    # 第 1 层：eastmoney HTTP
    url = (
        f"https://fundf10.eastmoney.com/FundArchivesDatas.aspx?"
        f"type=jjcc&code={code}&topline=10&year={year}&month="
    )
    txt = get(url, referer="https://fundf10.eastmoney.com/")
    if txt:
        m = re.search(r'content:"(.*)",arryear:', txt, re.S)
        if m:
            html = m.group(1)
            if "\\u" in html:
                html = html.encode().decode("unicode_escape", errors="ignore")
            soup = BeautifulSoup(html, "lxml")
            quarters = []
            for box in soup.select(".boxitem"):
                h = box.select_one("h4 .left")
                title = h.get_text(" ", strip=True) if h else ""
                qm = re.search(r"(\d{4})年(\d)季度", title)
                if not qm:
                    continue
                rows = []
                for tr in box.select("table tbody tr"):
                    tds = [td.get_text(strip=True) for td in tr.select("td")]
                    if len(tds) < 4:
                        continue
                    code_ = tds[1]
                    name_ = tds[2]
                    pct = next((t for t in tds if t.endswith("%")), "")
                    rows.append({"股票代码": code_, "股票名称": name_, "占净值比": pct})
                if rows:
                    quarters.append(
                        {
                            "year": int(qm.group(1)),
                            "quarter": int(qm.group(2)),
                            "title": title,
                            "holdings": rows,
                        }
                    )
            return quarters

    # 第 2 层：AKShare 基金 API 回退
    return _ak_parse_holdings(code, year)


def fund_list_path():
    """返回 fund_list.json 的绝对路径。"""
    return _rel_root("references", "shared", "all_funds", "fund_list.json")


def _rel_root(*parts):
    """从脚本位置向上追溯到项目根目录。"""
    p = os.path.abspath(__file__)
    for _ in range(4):
        p = os.path.dirname(p)
    return os.path.join(p, *parts)


