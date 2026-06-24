import json
import re
import requests
import pandas as pd
import numpy as np
from datetime import datetime

from ._base import _record_status

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://fund.eastmoney.com/",
}
_FUND_CODE_URL = "https://fund.eastmoney.com/js/fundcode_search.js"
_PINGZHONG_URL = "https://fund.eastmoney.com/pingzhongdata/{}.js"
_JJJZ_URL = "https://fund.eastmoney.com/Data/Fund_JJJZ_Data.aspx"
_PORTFOLIO_INTERFACE = "https://fund.eastmoney.com/data/FundDataPortfolio_Interface.aspx"
_ARCHIVES_URL = "https://fundf10.eastmoney.com/FundArchivesDatas.aspx"
_INDEX_URL = "https://api-fund.eastmoney.com/f10/HYPZ/"
_INDUSTRY_API = "https://api.fund.eastmoney.com/f10/HYPZ/"
_MANAGER_PAGE = "https://fundf10.eastmoney.com/jjjl_{}.html"


def _parse_em_json(text: str, var_name: str = None) -> dict:
    if var_name:
        text = text.strip()
        if text.startswith(f"var {var_name}="):
            text = text[len(f"var {var_name}="):]
        if text.endswith(";"):
            text = text[:-1]
    text = re.sub(r'(\w+):', r'"\1":', text)
    return json.loads(text)


def _sc_get_fund_code(query: str) -> str:
    r = requests.get(_FUND_CODE_URL, headers=_HEADERS, timeout=15)
    text = r.text.strip().lstrip("var r = ").rstrip(";")
    data = json.loads(text)
    codes = {}
    for row in data:
        codes[row[0]] = (row[2], row[3])
    exact = codes.get(query)
    if exact:
        _record_status("fund_basic_info", True, f"精确匹配:{query}", source="scraper")
        return query
    for code, (name, _) in codes.items():
        if code.startswith(query):
            _record_status("fund_basic_info", True, f"前缀匹配:{code}", source="scraper")
            return code
    for code, (name, _) in codes.items():
        if query in name:
            _record_status("fund_basic_info", True, f"名称匹配:{code}", source="scraper")
            return code
    raise ValueError(f"未找到匹配基金: {query}")


def _sc_get_fund_name(code: str) -> str:
    r = requests.get(_FUND_CODE_URL, headers=_HEADERS, timeout=15)
    text = r.text.strip().lstrip("var r = ").rstrip(";")
    data = json.loads(text)
    for row in data:
        if row[0] == code:
            return row[2]
    return code


def _sc_get_fund_category(code: str) -> str:
    r = requests.get(_FUND_CODE_URL, headers=_HEADERS, timeout=15)
    text = r.text.strip().lstrip("var r = ").rstrip(";")
    data = json.loads(text)
    for row in data:
        if row[0] == code:
            return row[3]
    return "未知"


def _sc_get_nav_history(code: str) -> pd.DataFrame:
    r = requests.get(_PINGZHONG_URL.format(code), headers=_HEADERS, timeout=15)
    text = r.text
    match = re.search(r"var Data_ACWorthTrend = (\[.*?\]);", text, re.DOTALL)
    if not match:
        raise RuntimeError(f"无法解析净值数据: {code}")
    data = json.loads(match.group(1))
    rows = []
    for item in data:
        ts_ms, acc_nav = item
        d = datetime.fromtimestamp(ts_ms / 1000).strftime("%Y-%m-%d")
        rows.append({"date": d, "acc_nav": float(acc_nav)})
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df.sort_values("date", inplace=True)
    df["daily_return"] = df["acc_nav"].pct_change() * 100
    _record_status("nav_history", True, f"{len(df)}条记录", source="scraper")
    return df


def _sc_get_portfolio_holdings(code: str) -> list:
    years = [datetime.now().year, datetime.now().year - 1]
    headers = {**_HEADERS, "Referer": f"https://fundf10.eastmoney.com/ccmx_{code}.html"}
    for y in years:
        try:
            params = {"type": "jjcc", "code": code, "topline": "10000", "year": str(y), "month": ""}
            r = requests.get(_ARCHIVES_URL, params=params, headers=headers, timeout=15)
            text = r.text
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if not match:
                continue
            data = _parse_em_json(match.group(), "apidata")
            content = data.get("content", "")
            if not content:
                continue
            tables = pd.read_html(content)
            result = []
            for tbl in tables:
                if "占净值比例" in tbl.columns or "占净值" in tbl.columns:
                    pct_col = "占净值比例" if "占净值比例" in tbl.columns else "占净值"
                    for _, row in tbl.iterrows():
                        try:
                            pct = float(str(row.get(pct_col, "0")).replace("%", ""))
                            result.append({
                                "股票代码": str(row.get("股票代码", "")),
                                "股票名称": str(row.get("股票名称", row.get("股票简称", ""))),
                                "占净值比例": pct,
                            })
                        except (ValueError, TypeError):
                            continue
            if result:
                _record_status("portfolio_holdings", True, f"{len(result)}只持仓（{y}年）", source="scraper")
                return sorted(result, key=lambda x: x["占净值比例"], reverse=True)
        except Exception:
            continue
    _record_status("portfolio_holdings", False, "scraper 未获取到持仓数据", source="scraper")
    return []


def _sc_get_fund_latest_status(code: str) -> dict:
    params = {"t": "1", "lx": "1", "page": "1,50000"}
    r = requests.get(_JJJZ_URL, params=params, headers=_HEADERS, timeout=30)
    text = r.text
    data = _parse_em_json(text, "db")
    for row in data.get("datas", []):
        if row[0] == code:
            result = {
                "基金代码": row[0],
                "基金简称": row[1],
                "申购状态": row[9],
                "赎回状态": row[10],
            }
            try:
                result["日增长率"] = float(row[8])
            except (ValueError, IndexError):
                pass
            _record_status("fund_status", True, "已获取申购/赎回状态", source="scraper")
            return result
    _record_status("fund_status", False, "代码未在日行情列表中找到", source="scraper")
    return {}


def _sc_get_market_index_history(symbol: str = "000300", years: int = 10) -> pd.DataFrame:
    end = datetime.now()
    start = end - pd.DateOffset(years=years)
    url = "https://api-fund.eastmoney.com/f10/HYPZ/"
    params = {
        "fundCode": symbol,
        "year": str(end.year),
    }
    headers = {**_HEADERS, "Referer": "https://fundf10.eastmoney.com/"}
    try:
        url_idx = "https://push2.eastmoney.com/api/qt/stock/kline/get"
        secid = f"1.{symbol}" if symbol.startswith("000") else f"0.{symbol}"
        params = {
            "secid": secid,
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
            "klt": "101",
            "fqt": "1",
            "beg": start.strftime("%Y%m%d"),
            "end": end.strftime("%Y%m%d"),
        }
        r = requests.get(url_idx, params=params, headers=_HEADERS, timeout=15)
        data = r.json()
        klines = data.get("data", {}).get("klines", [])
        rows = []
        for line in klines:
            parts = line.split(",")
            rows.append({"date": parts[0], "close": float(parts[2])})
        if not rows:
            raise ValueError("Empty kline data")
        df = pd.DataFrame(rows)
        df["date"] = pd.to_datetime(df["date"])
        df.sort_values("date", inplace=True)
        _record_status("market_index", True, f"沪深300: {len(df)}条", source="scraper")
        return df
    except Exception:
        _record_status("market_index", False, "scraper 未获取到指数数据", source="scraper")
        return pd.DataFrame()


def _sc_get_industry_allocation(code: str) -> list:
    years = [datetime.now().year, datetime.now().year - 1]
    headers = {**_HEADERS, "Referer": "https://fundf10.eastmoney.com/"}
    all_dfs = []
    for y in years:
        try:
            params = {"fundCode": code, "year": str(y)}
            r = requests.get(_INDUSTRY_API, params=params, headers=headers, timeout=15)
            data = r.json()
            quarters = data.get("Data", {}).get("QuarterInfos", [])
            for q in quarters:
                info_list = q.get("HYPZInfo", [])
                if not info_list:
                    continue
                temp_df = pd.DataFrame(info_list)
                temp_df.rename(columns={
                    "HYMC": "行业类别",
                    "ZJZBL": "占净值比例",
                    "SZDesc": "市值",
                    "FSRQ": "截止时间",
                }, inplace=True)
                temp_df["占净值比例"] = pd.to_numeric(temp_df.get("占净值比例", 0), errors="coerce")
                temp_df["截止时间"] = pd.to_datetime(temp_df.get("截止时间", "2025-01-01"), errors="coerce")
                all_dfs.append(temp_df)
        except Exception:
            continue
    if not all_dfs:
        _record_status("industry_allocation", False, "scraper 未获取到行业配置数据", source="scraper")
        return []
    combined = pd.concat(all_dfs, ignore_index=True)
    _record_status("industry_allocation", True, f"{len(all_dfs)}季度行业配置", source="scraper")
    return combined.to_dict("records")


def _sc_get_fund_scale(code: str) -> dict:
    try:
        url = _MANAGER_PAGE.format(code)
        r = requests.get(url, headers=_HEADERS, timeout=15)
        soup = __import__("bs4").BeautifulSoup(r.text, "html.parser")
        scale_el = soup.select_one(".bs_gl label:last-child span")
        if scale_el:
            scale_text = scale_el.text.strip()
            import re
            nums = re.findall(r"[\d.]+", scale_text)
            if nums:
                scale = float(nums[0])
                _record_status("fund_scale", True, f"规模: {scale}亿元", source="scraper")
                return {"scale": scale, "unit": "亿元", "category": None}
        _record_status("fund_scale", False, "scraper 未解析到规模数据", source="scraper")
        return {"scale": None, "unit": "亿元", "category": None}
    except Exception:
        _record_status("fund_scale", False, "scraper 请求失败", source="scraper")
        return {"scale": None, "unit": "亿元", "category": None}


def _sc_get_manager_info(code: str) -> dict:
    try:
        url = _MANAGER_PAGE.format(code)
        r = requests.get(url, headers=_HEADERS, timeout=15)
        soup = __import__("bs4").BeautifulSoup(r.text, "html.parser")
        labels = soup.select_one(".bs_gl")
        if not labels:
            raise ValueError("未找到经理信息区域")
        contents = labels.find_all("label")
        if len(contents) < 2:
            raise ValueError("经理信息不完整")
        start_date = contents[0].span.text.strip() if contents[0].span else "未知"
        manager_names = []
        if len(contents) >= 2:
            for a in contents[1].find_all("a"):
                manager_names.append(a.text.strip())
        manager_str = "; ".join(manager_names) if manager_names else "未知"
        tenure_years = None
        try:
            start = pd.to_datetime(start_date)
            tenure_years = round((datetime.now() - start).days / 365, 1)
        except Exception:
            pass
        result = [{
            "name": manager_str,
            "tenure_years": tenure_years,
            "tenure_raw": start_date,
        }]
        _record_status("manager_info", True, f"{len(result)}位经理, 最长{tenure_years}年", source="scraper")
        return {"managers": result, "tenure_years": tenure_years, "count": len(result)}
    except Exception as e:
        _record_status("manager_info", False, str(e), source="scraper")
        return {"managers": [], "tenure_years": None, "count": 0}


def _sc_get_institutional_ratio(code: str) -> dict:
    try:
        r = requests.get(_PINGZHONG_URL.format(code), headers=_HEADERS, timeout=15)
        text = r.text
        match = re.search(r'var Data_holderStructure\s*=\s*(\{.*?\});', text, re.DOTALL)
        if not match:
            raise ValueError("未找到持有人结构数据")
        data = json.loads(match.group(1))
        series = {s["name"]: s["data"] for s in data.get("series", [])}
        inst_data = series.get("机构持有比例", [])
        internal_data = series.get("内部持有比例", [])
        inst_pct = float(inst_data[-1]) if inst_data else None
        internal_pct = float(internal_data[-1]) if internal_data else None
        _record_status("inst_ratio", inst_pct is not None, f"机构: {inst_pct}%", source="scraper")
        return {"institutional_pct": inst_pct, "internal_pct": internal_pct}
    except Exception as e:
        _record_status("inst_ratio", False, str(e), source="scraper")
        return {"institutional_pct": None, "internal_pct": None}


def _sc_get_turnover_rate(code: str) -> dict:
    _record_status("turnover", False, "scraper 无换手率数据源", source="scraper")
    return {"turnover_rate": None, "period": None}


def _sc_get_fee_rate(code: str) -> dict:
    try:
        r = requests.get(_FUND_CODE_URL, headers=_HEADERS, timeout=15)
        text = r.text.strip().lstrip("var r = ").rstrip(";")
        json.loads(text)
        _record_status("fee_rate", False, "fundcode_search 无法获取费率，需基金详情页", source="scraper")
        return {"management_fee": None, "custodian_fee": None, "total_fee": None}
    except Exception:
        _record_status("fee_rate", False, "scraper 请求失败", source="scraper")
        return {"management_fee": None, "custodian_fee": None, "total_fee": None}


def _sc_get_scale_history(code: str) -> list:
    try:
        params = {"dt": "9", "pi": "1", "pn": "50", "mc": "hypzDetail", "st": "desc", "sc": "reportdate"}
        r = requests.get(_PORTFOLIO_INTERFACE, params=params, headers=_HEADERS, timeout=30)
        data = _parse_em_json(r.text, "hypzDetail")
        total_pages = int(data.get("pages", 1))
        all_rows = list(data.get("data", []))
        for page in range(2, total_pages + 1):
            params["pi"] = str(page)
            r = requests.get(_PORTFOLIO_INTERFACE, params=params, headers=_HEADERS, timeout=30)
            data = _parse_em_json(r.text, "hypzDetail")
            all_rows.extend(data.get("data", []))

        col_headers = requests.get(_PORTFOLIO_INTERFACE, params=params, headers=_HEADERS, timeout=15).text
        result = []
        for row in all_rows:
            row_code = row[1]
            if row_code == code:
                try:
                    scale = float(str(row[5]).replace(",", ""))
                    date = str(row[0])
                    result.append({"date": date, "scale": scale})
                except (ValueError, IndexError, TypeError):
                    continue
        _record_status("scale_history", True, f"{len(result)}期规模数据", source="scraper")
        return result
    except Exception as e:
        _record_status("scale_history", False, str(e), source="scraper")
        return []


def _sc_get_peer_nav_history(category: str, max_peers: int = 15) -> dict:
    r = requests.get(_FUND_CODE_URL, headers=_HEADERS, timeout=15)
    text = r.text.strip().lstrip("var r = ").rstrip(";")
    data = json.loads(text)
    candidates = [row for row in data if row[3] == category]
    match_method = "精确匹配"
    if len(candidates) < 5:
        prefix = category.split("-")[0] if "-" in category else category
        candidates = [row for row in data if prefix in row[3]]
        match_method = f"前缀匹配({prefix}), 精确匹配池不足"
    if not candidates:
        _record_status("peer_nav_history", False, f"分类'{category}'未找到同类基金", source="scraper")
        return {}
    if len(candidates) > max_peers:
        import random
        random.seed(42)
        candidates = random.sample(candidates, max_peers)
        match_method += ", 随机抽样"
    codes = [row[0] for row in candidates]
    _record_status("peer_nav_history", True, f"{match_method}: 备选{len(codes)}只, 分类'{category}'", source="scraper")
    result = {}
    fetch_success = 0
    for c in codes:
        try:
            result[c] = _sc_get_nav_history(c)
            fetch_success += 1
        except Exception:
            continue
        if len(result) >= max_peers:
            break
    _record_status("peer_nav_history", fetch_success > 0, f"实际拉取{fetch_success}/{len(codes)}只同类净值, 分类'{category}'", source="scraper")
    return result
