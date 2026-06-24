# -*- coding: utf-8 -*-
"""Utility functions for fetching and computing fund data from public sources.

Data source: 天天基金 (eastmoney.com) public disclosure.
Research and study use only. Not investment advice.
"""
import os, sys, re, json, math, datetime, time
import requests
from bs4 import BeautifulSoup


HERE = os.path.dirname(os.path.abspath(__file__))
THIS_YEAR = datetime.datetime.now().year
S = requests.Session()
S.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
})

def get(url, referer="https://fund.eastmoney.com/"):
    S.headers["Referer"] = referer
    try:
        r = S.get(url, timeout=20)
        r.encoding = "utf-8"
        return r.text
    except Exception as e:
        print(f"[fetch_fund_data] GET error: {e}", file=sys.stderr)
        return None

def fmt_ts(ms):
    try:
        return datetime.datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d")
    except Exception:
        return str(ms)

def window_return(ac, days):
    if not ac or len(ac) < 2:
        return None
    last_ts, last_v = ac[-1]
    target = last_ts - days * 86400 * 1000
    base = None
    for ts, v in ac:
        if ts >= target:
            base = v
            break
    if not base:
        base = ac[0][1]
    if not base:
        return None
    return round((last_v / base - 1) * 100, 2)

def max_drawdown(ac):
    if not ac:
        return None
    peak = -1e9
    mdd = 0
    for _, v in ac:
        peak = max(peak, v)
        if peak > 0:
            mdd = min(mdd, v / peak - 1)
    return round(mdd * 100, 2)

def year_return(ac):
    if not ac:
        return None
    last_ts, last_v = ac[-1]
    jan1 = datetime.datetime(THIS_YEAR, 1, 1).timestamp() * 1000
    base = None
    for ts, v in ac:
        if ts >= jan1:
            base = v
            break
    if not base or not base:
        return None
    return round((last_v / base - 1) * 100, 2)

def parse_holdings(code, year):
    url = (f"https://fundf10.eastmoney.com/FundArchivesDatas.aspx?"
           f"type=jjcc&code={code}&topline=10&year={year}&month=")
    txt = get(url, referer="https://fundf10.eastmoney.com/")
    if not txt:
        return []
    try:
        m = re.search(r'apidata\.content\s*=\s*"(.+?)";', txt)
        if not m:
            return []
        html = m.group(1).replace("\\r", "").replace("\\n", "").replace("\\t", "")
        html = html.replace('\\"', '"').replace("\\'", "'").replace("\\\\", "\\")
        html = re.sub(r'\\(.)', r'\1', html)
        soup = BeautifulSoup(html, "lxml")
        rows = soup.select("table tbody tr")
        holdings = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 4:
                continue
            name_tag = cols[1].find("a")
            name = name_tag.get_text(strip=True) if name_tag else cols[1].get_text(strip=True)
            code_tag = cols[2].find("a")
            code = code_tag.get_text(strip=True) if code_tag else cols[2].get_text(strip=True)
            pct = cols[3].get_text(strip=True)
            holdings.append({"股票名称": name, "股票代码": code, "占净值比": pct})
        return holdings
    except Exception as e:
        print(f"[parse_holdings] error {code}/{year}: {e}", file=sys.stderr)
        return []

def parse_pingzhong(code):
    url = f"https://api.fund.eastmoney.com/f10/lsjz?callback=jQuery&fundCode={code}&pageIndex=1&pageSize=2000"
    txt = get(url, referer="https://fundf10.eastmoney.com/")
    if not txt:
        return None
    m = re.search(r'\[.*?\]', txt)
    if not m:
        return None
    try:
        data = json.loads(m.group())
        nav = []
        for d in data:
            ts = d.get("FSRQ", "")
            if not ts:
                continue
            dt = datetime.datetime.strptime(ts, "%Y-%m-%d")
            ms = int(dt.timestamp() * 1000)
            val = d.get("DWJZ")
            if val and val != "":
                nav.append([ms, float(val)])
        nav.sort(key=lambda x: x[0])
        return nav
    except Exception as e:
        print(f"[parse_pingzhong] error {code}: {e}", file=sys.stderr)
        return None

def render_quarterly(quarters):
    lines = []
    for q in sorted(quarters, key=lambda q: (q["year"], q["quarter"])):
        lines.append(f"\n### {q['year']}年 第{q['quarter']}季度")
        for i, h in enumerate(q["holdings"], 1):
            lines.append(f"{i}. {h['股票名称']}（{h['股票代码']}） {h['占净值比']}")
        lines.append("")
    return "\n".join(lines)

def safe(s):
    return re.sub(r'[\\/:*?"<>|\s]+', "_", (s or "").strip())[:80]

def render_fund_md(meta, pz):
    nm = pz.get("fS_name") if pz else meta["name"]
    L = [f"# {nm}（{meta['code']}） · 净值/业绩/规模", ""]
    L.append(f"- 类型：{meta.get('type','')}")
    if not pz:
        L.append("\n> 未取到天天基金数据。")
        return "\n".join(L)
    ac = [p for p in (pz.get("累计净值走势") or []) if p and len(p) >= 2 and p[1] is not None]
    nwt = [p for p in (pz.get("单位净值走势") or []) if isinstance(p, dict) and p.get("y") is not None]
    if nwt:
        last = nwt[-1]
        L.append(f"- 最新单位净值：{last.get('y')}（{fmt_ts(last.get('x'))}）")
    if ac:
        L.append(f"- 最新累计净值：{ac[-1][1]}（{fmt_ts(ac[-1][0])}）")
    L.append("")
    L.append("## 区间收益与回撤（按累计净值估算）")
    L.append(f"- 今年以来：{year_return(ac)}%")
    L.append(f"- 近1年：{window_return(ac,365)}%")
    L.append(f"- 近3年：{window_return(ac,365*3)}%")
    L.append(f"- 成立以来累计：{round((ac[-1][1]/ac[0][1]-1)*100,2) if ac else None}%")
    L.append(f"- 最大回撤（成立以来）：{max_drawdown(ac)}%")
    gt = pz.get("累计收益率走势") or []
    if gt and (gt[0].get("data")):
        rng = gt[0]["data"]
        L.append("")
        L.append(f"## 区间收益率对比（{fmt_ts(rng[0][0])} ~ {fmt_ts(rng[-1][0])}）")
        for s in gt:
            data = s.get("data") or []
            if data:
                L.append(f"- {s.get('name')}：{data[-1][1]}%")
    fs = pz.get("规模变动") or {}
    cats = fs.get("categories") or [] if isinstance(fs, dict) else []
    series = fs.get("series") or [] if isinstance(fs, dict) else []
    if cats and series:
        last = series[-1]
        y = last.get("y") if isinstance(last, dict) else last
        L.append("")
        L.append(f"## 规模\n- 最新披露规模：{y} 亿元（{cats[-1]}，环比 {last.get('mom') if isinstance(last,dict) else ''}）")
    aa = pz.get("资产配置") or {}
    if isinstance(aa, dict) and aa.get("categories"):
        acats = aa["categories"]
        parts = []
        for s in aa.get("series", []):
            data = s.get("data") or []
            if data and "占" in (s.get("name") or ""):
                parts.append(f"{s['name']} {data[-1]}%")
        if parts:
            L.append(f"\n## 资产配置（{acats[-1]}）\n- " + "；".join(parts))
    fm = pz.get("基金经理") or []
    if isinstance(fm, list) and fm:
        L.append("")
        L.append("## 现任基金经理（天天基金口径）")
        for m in fm:
            line = f"- {m.get('name')}：任职 {m.get('workTime')}，在管 {m.get('fundSize')}"
            prof = m.get("profit") or {}
            ser = (prof.get("series") or [{}])[0].get("data") if prof.get("series") else None
            if prof.get("categories") and ser:
                rets = "；".join(f"{c} {d.get('y')}%" for c, d in zip(prof["categories"], ser))
                line += f"\n    - 任职回报：{rets}（截至 {prof.get('jzrq','')}）"
            L.append(line)
    pe = pz.get("业绩评价") or {}
    if isinstance(pe, dict) and pe.get("categories") and isinstance(pe.get("data"), list):
        L.append("")
        L.append("## 业绩评价（天天基金五维，满分100）")
        for c, v in zip(pe["categories"], pe["data"]):
            L.append(f"- {c}：{v}")
    return "\n".join(L)

def render_holdings_md(meta, quarters):
    nm = meta["name"]
    L = [f"# {nm}（{meta['code']}） · 季度前十大重仓股", ""]
    L.append(f"- 类型：{meta.get('type','')}")
    L.append(f"- 共 {len(quarters)} 个季度披露\n")
    for q in sorted(quarters, key=lambda x: (x["year"], x["quarter"]), reverse=True):
        L.append(f"## {q['year']}年第{q['quarter']}季度")
        for i, h in enumerate(q["holdings"], 1):
            L.append(f"{i}. {h['股票名称']}（{h['股票代码']}） 占净值 {h['占净值比']}")
        L.append("")
    return "\n".join(L)

def render_nav(nav):
    if not nav or len(nav) < 2:
        return "数据不足"
    return (f"最新 {fmt_ts(nav[-1][0])}：{nav[-1][1]} | "
            f"今年以来 {year_return(nav)}% | "
            f"近1年 {window_return(nav, 365)}% | "
            f"近3年 {window_return(nav, 365*3)}% | "
            f"成立以来 {round((nav[-1][1]/nav[0][1]-1)*100,2)}% | "
            f"最大回撤 {max_drawdown(nav)}%")
