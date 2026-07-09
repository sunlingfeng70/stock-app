from datetime import datetime, timedelta
import pandas as pd
from curl_cffi import requests
from config import FETCH_DAYS


def fetch_daily(code, name):
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=FETCH_DAYS)).strftime("%Y%m%d")

    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f116",
        "ut": "7eea3edcaed734bea9cbfc24409ed989",
        "klt": "101",
        "fqt": "1",
        "secid": f"0.{code}",
        "beg": start_date,
        "end": end_date,
    }
    resp = requests.get(url, params=params, timeout=30, impersonate="chrome124")
    data = resp.json()
    klines = data.get("data", {}).get("klines", [])
    if not klines:
        return []

    rows = []
    for line in klines:
        parts = line.split(",")
        rows.append({
            "date": parts[0],
            "open": float(parts[1]),
            "close": float(parts[2]),
            "high": float(parts[3]),
            "low": float(parts[4]),
            "volume": int(float(parts[5])),
            "amount": float(parts[6]),
            "amplitude": float(parts[7]),
            "pct_chg": float(parts[8]),
            "change": float(parts[9]),
            "turnover": float(parts[10]),
        })
    return rows