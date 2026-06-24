#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键抓取基金数据 → 计算机械指标 → 输出结构化 JSON。

输出直接喂给 Claude，Claude 按 references/scorecard.md 的六维评分卡逐项打分。
Python 只算机械指标，所有判断性评分由 Claude 做。

用法:
  python scripts/fetch_fund.py 005827
  python scripts/fetch_fund.py 易方达蓝筹精选
  python scripts/fetch_fund.py 005827 --no-cache

输出: stdout 打印 JSON（可重定向到文件或 pipe）。
数据源: 天天基金公开数据。研究学习辅助，非投资建议。
"""
import os, sys, json, re, math, time, datetime
from typing import Optional

import requests
from bs4 import BeautifulSoup

# ── 配置 ──────────────────────────────────────
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.abspath(os.path.join(HERE, "..", "references", "fund_data_cache"))
CACHE_TTL_DAYS = 7
THIS_YEAR = datetime.datetime.now().year
HTTP_TIMEOUT = 20
REQ_SLEEP = 0.5  # 请求间隔（秒）

COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def _get(url: str, referer: str = "https://fund.eastmoney.com/") -> Optional[str]:
    """GET 请求，每次创建新 Session 以避免限流累积。"""
    S = requests.Session()
    S.headers.update(COMMON_HEADERS)
    S.headers["Referer"] = referer
    try:
        r = S.get(url, timeout=HTTP_TIMEOUT)
        r.encoding = "utf-8"
        return r.text
    except Exception as e:
        print(f"[fetch] GET error: {e}", file=sys.stderr)
        return None
    finally:
        S.close()


# ── 1. 基金解析（名称→代码）──────────────────

def resolve(code_or_name: str) -> dict:
    """把代码或名称解析为基金基本信息。不依赖预生成索引。"""
    q = code_or_name.strip()
    url = (f"https://fundsuggest.eastmoney.com/FundSearch/api/"
           f"FundSearchAPI.ashx?m=1&key={q}")
    txt = _get(url)
    if not txt:
        return {"code": q, "name": q, "type": "", "manager": ""}
    try:
        data = json.loads(txt)
        items = data.get("Datas") or []
        if not items:
            return {"code": q, "name": q, "type": "", "manager": ""}
        first = items[0]
        base = first.get("FundBaseInfo") or {}
        return {
            "code": base.get("FCODE", q),
            "name": base.get("SHORTNAME", q),
            "type": base.get("FTYPE", ""),
            "manager": base.get("JJJL", ""),
        }
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"[resolve] 搜索失败: {e}", file=sys.stderr)
        return {"code": q, "name": q, "type": "", "manager": ""}


# ── 2. 抓持仓 ────────────────────────────────

def _parse_holdings_page(txt: str) -> list[dict]:
    """解析单年持仓页面（可能含 1~4 个季度）。

    天天基金有两种响应格式:
      旧: var apidata.content = "...";
      新: var apidata={ content:"...", arryear:[...], curyear:... };
    """
    html = None
    # 旧格式: apidata.content = "..."
    m = re.search(r'apidata\.content\s*=\s*"(.+?)";', txt)
    if m:
        html = m.group(1)
    # 新格式: apidata={ content:"...", ... }
    if not html:
        m = re.search(r'apidata\s*=\s*\{\s*content\s*:\s*"(.+?)"\s*,', txt, re.DOTALL)
        if m:
            html = m.group(1)
    if not html:
        return []
    # 解 HTML 转义
    html = html.replace("\\r", "").replace("\\n", "").replace("\\t", "")
    html = html.replace('\\"', '"').replace("\\'", "'").replace("\\\\", "\\")
    html = re.sub(r'\\(.)', r'\1', html)
    soup = BeautifulSoup(html, "lxml")
    boxes = soup.select("div.box")
    results = []
    for box in boxes:
        h4 = box.select_one("h4")
        if not h4:
            continue
        h4_text = h4.get_text()
        m_q = re.search(r"(\d{4})年(\d)季度", h4_text)
        if not m_q:
            continue
        y, q = int(m_q.group(1)), int(m_q.group(2))
        rows = box.select("table tbody tr")
        holdings = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 4:
                continue
            # 列结构因年份而异（近期增加涨跌幅列），按特征定位：
            #   序号(1列) + 股票代码 + 股票名称 + [可选: 涨跌幅等] + 占净值比(含%) + 持股数 + 持仓市值
            code_a = cols[1].find("a")
            code = code_a.get_text(strip=True) if code_a else cols[1].get_text(strip=True)
            name_a = cols[2].find("a")
            name = name_a.get_text(strip=True) if name_a else cols[2].get_text(strip=True)
            # 找含 % 的列（占净值比）
            weight = ""
            for c in cols:
                txt_c = c.get_text(strip=True)
                if txt_c.endswith("%"):
                    weight = txt_c
                    break
            holdings.append({"name": name, "code": code, "weight": weight})
        results.append({"year": y, "quarter": q, "holdings": holdings})
    return results


def fetch_top10_history(code: str) -> list[dict]:
    """抓最近 5 年的季度前十大持仓，按 (year, quarter) 去重。

    5 年（~20 个季度）对评分卡足够——换手代理只需 5 季，集中度看最新一季就够了。
    """
    all_q: dict[tuple[int, int], dict] = {}
    start = max(THIS_YEAR - 5, 2004)
    for y in range(start, THIS_YEAR + 1):
        url = (f"https://fundf10.eastmoney.com/FundArchivesDatas.aspx?"
               f"type=jjcc&code={code}&topline=10&year={y}&month=")
        txt = _get(url, referer="https://fundf10.eastmoney.com/")
        if txt and "apidata" in txt.lower():
            qs = _parse_holdings_page(txt)
            for qd in qs:
                all_q[(qd["year"], qd["quarter"])] = qd
        time.sleep(REQ_SLEEP)
    return list(all_q.values())


# ── 3. 抓净值 ────────────────────────────────

def fetch_nav_history(code: str) -> list[dict]:
    """抓取基金净值历史，返回 [{FSRQ, DWJZ, LJJZ}, ...]。

    数据源：
      首选  lsjz API（api.fund.eastmoney.com）——有累计净值，适合计算收益。
      备选  pingzhongdata（fund.eastmoney.com）——仅单位净值 + 日回报率，反推累计净值。
    """
    records = _fetch_nav_from_api(code)
    if records and len(records) >= 2:
        return records
    records = _fetch_nav_from_pingzhong(code)
    return records


def _fetch_nav_from_api(code: str) -> list[dict]:
    """通过 lsjz API 抓取累计净值。"""
    all_records = []
    page = 1
    while True:
        url = (f"https://api.fund.eastmoney.com/f10/lsjz?"
               f"callback=cb&fundCode={code}&pageIndex={page}&pageSize=2000")
        txt = _get(url, referer="https://fundf10.eastmoney.com/")
        if not txt or len(txt) < 200:
            break
        try:
            inner = re.sub(r'^cb\(', '', txt).rstrip(';)\n\r ')
            data = json.loads(inner)
            d = data.get("Data")
            if d is None:
                break
            lst = d.get("LSJZList", [])
            if not lst:
                break
            all_records.extend(lst)
            total = int(data.get("TotalCount", 0))
            if len(all_records) >= total:
                break
            page += 1
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            break
    return all_records


def _fetch_nav_from_pingzhong(code: str) -> list[dict]:
    """从 pingzhongdata.js 读取单位净值 + 日回报率，反推累计净值序列。"""
    url = f"https://fund.eastmoney.com/pingzhongdata/{code}.js"
    txt = _get(url, referer="https://fund.eastmoney.com/")
    if not txt:
        return []

    m = re.search(r'var Data_netWorthTrend\s*=\s*(\[.*?\]);', txt, re.DOTALL)
    if not m:
        return []
    try:
        raw = json.loads(m.group(1))
    except json.JSONDecodeError:
        return []

    # 按日期排序，计算累计净值：cumulative = 1 * Π(1 + equityReturn/100)
    pts = [(p["x"], p["y"], float(p.get("equityReturn") or 0)) for p in raw if p.get("x") and p.get("y")]
    pts.sort(key=lambda x: x[0])

    results = []
    cum = 1.0
    for ts, unit_nav, daily_r in pts:
        cum *= (1 + daily_r / 100)
        dt = datetime.datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
        results.append({
            "FSRQ": dt,
            "DWJZ": str(round(unit_nav, 4)),
            "LJJZ": str(round(cum, 4)),
        })
    return results


# ── 4. 计算指标 ──────────────────────────────

def calc_concentration(top10: list[dict]) -> Optional[float]:
    """前十大合计占净值比。"""
    total = 0.0
    for h in top10:
        try:
            total += float(h["weight"].rstrip("%"))
        except (ValueError, AttributeError):
            pass
    return round(total, 1) if total else None


def calc_turnover_proxy(quarters: list[dict]) -> Optional[float]:
    """相邻季度前十大变化率。值越高 = 调仓越频繁 = 越像周期拼接。"""
    qs = sorted(quarters, key=lambda q: (q["year"], q["quarter"]))[-5:]
    diffs = []
    for a, b in zip(qs, qs[1:]):
        codes_a = {h["code"] for h in a["holdings"]}
        codes_b = {h["code"] for h in b["holdings"]}
        if codes_a and codes_b:
            overlap = len(codes_a & codes_b) / max(len(codes_b), 1)
            diffs.append(1 - overlap)
    return round(sum(diffs) / len(diffs) * 100, 1) if diffs else None


def _nav_points(records: list[dict]) -> list[dict]:
    """筛选有效累计净值，按日期升序排列。"""
    pts = []
    for r in records:
        fsrq = r.get("FSRQ", "")
        lj = r.get("LJJZ", "")
        if not fsrq or not lj:
            continue
        try:
            dt = datetime.datetime.strptime(fsrq, "%Y-%m-%d")
            pts.append({"ts": int(dt.timestamp() * 1000), "nav": float(lj)})
        except (ValueError, TypeError):
            pass
    pts.sort(key=lambda x: x["ts"])
    return pts


def _window_return(pts: list[dict], days: int) -> Optional[float]:
    """计算指定天数的窗口收益（基于累计净值）。"""
    if len(pts) < 2:
        return None
    last_nav = pts[-1]["nav"]
    target = pts[-1]["ts"] - days * 86400 * 1000
    base = next((p["nav"] for p in pts if p["ts"] >= target), None)
    if base is None:
        base = pts[0]["nav"]
    if not base:
        return None
    return round((last_nav / base - 1) * 100, 2)


def _max_drawdown(pts: list[dict]) -> Optional[float]:
    max_nav = -1e18
    mdd = 0.0
    for p in pts:
        max_nav = max(max_nav, p["nav"])
        if max_nav > 0:
            mdd = min(mdd, p["nav"] / max_nav - 1)
    return round(mdd * 100, 2)


def calc_returns(nav_records: list[dict]) -> dict:
    """计算全部收益/回撤指标，附带净值范围信息。"""
    pts = _nav_points(nav_records)
    result = {
        "ytd_pct": None,
        "one_year_pct": None,
        "three_year_pct": None,
        "since_inception_pct": None,
        "max_drawdown_pct": None,
        "nav_start_date": None,
        "nav_end_date": None,
    }
    if len(pts) < 2:
        return result

    result["since_inception_pct"] = round(
        (pts[-1]["nav"] / pts[0]["nav"] - 1) * 100, 2)
    result["max_drawdown_pct"] = _max_drawdown(pts)
    result["nav_start_date"] = datetime.datetime.fromtimestamp(
        pts[0]["ts"] / 1000).strftime("%Y-%m-%d")
    result["nav_end_date"] = datetime.datetime.fromtimestamp(
        pts[-1]["ts"] / 1000).strftime("%Y-%m-%d")
    result["nav_start_value"] = pts[0]["nav"]
    result["nav_end_value"] = pts[-1]["nav"]

    # 今年以来（取1月1日后的第一个净值）
    jan1 = datetime.datetime(THIS_YEAR, 1, 1).timestamp() * 1000
    ytd_base = next((p["nav"] for p in pts if p["ts"] >= jan1), None)
    if ytd_base:
        result["ytd_pct"] = round(
            (pts[-1]["nav"] / ytd_base - 1) * 100, 2)

    result["one_year_pct"] = _window_return(pts, 365)
    result["three_year_pct"] = _window_return(pts, 365 * 3)
    return result


# ── 5. 缓存 ──────────────────────────────────

def _cache_path(code: str) -> str:
    os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join(CACHE_DIR, f"{code}.evidence.json")


def _cache_valid(path: str) -> bool:
    if not os.path.exists(path):
        return False
    age = time.time() - os.path.getmtime(path)
    return age < CACHE_TTL_DAYS * 86400


# ── 6. 主流程 ────────────────────────────────

def build_evidence(
    fund: dict,
    quarters: list[dict],
    nav_records: list[dict],
) -> dict:
    """聚合所有机械指标，输出结构化证据包。"""
    # 最新季度
    sorted_q = sorted(quarters, key=lambda q: (q["year"], q["quarter"]))
    latest_q = sorted_q[-1] if sorted_q else None
    top10 = latest_q["holdings"] if latest_q else []
    concentration = calc_concentration(top10)
    turnover = calc_turnover_proxy(quarters)

    returns = calc_returns(nav_records)

    def _conc_label(v: Optional[float]) -> str:
        if v is None:
            return "未知"
        if v > 70:
            return "高度集中"
        if v > 50:
            return "较集中"
        return "分散"

    def _turn_label(v: Optional[float]) -> str:
        if v is None:
            return "未知"
        if v > 40:
            return "高换手（积极调仓）"
        if v > 20:
            return "中等换手"
        return "低换手"

    return {
        "version": 1,
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data_source": "天天基金 (eastmoney.com)",
        "fund": fund,
        "portfolio": {
            "latest_quarter": {
                "year": latest_q["year"],
                "quarter": latest_q["quarter"],
            } if latest_q else None,
            "top10": top10,
            "concentration_pct": concentration,
            "concentration_label": _conc_label(concentration),
        },
        "turnover": {
            "proxy_pct": turnover,
            "label": _turn_label(turnover),
            "quarters_used": min(len(quarters), 5),
            "quarters_total": len(quarters),
        },
        "returns": returns,
        "nav_records": len(nav_records),
    }


def main():
    if len(sys.argv) < 2:
        print("用法: python scripts/fetch_fund.py <基金代码或名称> [--no-cache]",
              file=sys.stderr)
        sys.exit(1)

    query = sys.argv[1]
    no_cache = "--no-cache" in sys.argv

    # 解析基金
    fund = resolve(query)
    if not fund.get("code") or not fund.get("name"):
        print(json.dumps({"error": f"未找到基金：{query}"}, ensure_ascii=False))
        sys.exit(1)

    code = fund["code"]

    # 缓存检查
    cache_file = _cache_path(code)
    if not no_cache and _cache_valid(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                sys.stdout.write(f.read())
            return
        except Exception:
            pass  # 缓存损坏则重新抓

    # 抓取（净值在前：1 次请求；持仓在后：约 24 次请求）
    print(f"[进度] 净值 {code}...", file=sys.stderr)
    nav = fetch_nav_history(code)
    print(f"[进度] 持仓 {code}...", file=sys.stderr)
    quarters = fetch_top10_history(code)
    print(f"[进度] 完成 ({len(quarters)} 季, {len(nav)} 条净值)", file=sys.stderr)

    evidence = build_evidence(fund, quarters, nav)

    # 写缓存
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(evidence, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[cache] 写入失败: {e}", file=sys.stderr)

    # 输出
    json.dump(evidence, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
