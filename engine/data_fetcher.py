import pandas as pd
import akshare as ak
from datetime import datetime, timedelta
from config import FETCH_DAYS


def fetch_daily(code, name):
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=FETCH_DAYS)).strftime("%Y%m%d")
    try:
        df = ak.stock_zh_a_hist(
            symbol=code,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq",
        )
    except Exception:
        df = ak.stock_zh_a_hist(
            symbol=code,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq",
        )
    if df is None or df.empty:
        return []
    df.columns = [c.strip() for c in df.columns]
    rename_map = {
        "日期": "date",
        "开盘": "open",
        "最高": "high",
        "最低": "low",
        "收盘": "close",
        "成交量": "volume",
        "涨跌幅": "pct_chg",
    }
    df = df.rename(columns=rename_map)
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    return df.to_dict("records")