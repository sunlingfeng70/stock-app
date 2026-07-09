import pandas as pd
import numpy as np
from config import STRATEGY


def compute_all(df):
    df = df.sort_values("date").reset_index(drop=True)
    close = df["close"].values.astype(float)
    high = df["high"].values.astype(float)
    low = df["low"].values.astype(float)
    volume = df["volume"].values.astype(float)

    p = STRATEGY
    ma_short = p["ma_short"]
    ma_long = p["ma_long"]
    boll_p = p["boll_period"]
    boll_std = p["boll_std"]
    rsi_p = p["rsi_period"]
    vol_p = p["volume_ma_period"]

    result = {}

    result["ma20"] = _ma(close, ma_short)
    result["ma60"] = _ma(close, ma_long)

    boll_mid, boll_upper, boll_lower = _bollinger(close, boll_p, boll_std)
    result["boll_mid"] = boll_mid
    result["boll_upper"] = boll_upper
    result["boll_lower"] = boll_lower

    result["rsi"] = _rsi(close, rsi_p)

    result["volume_ratio"] = _volume_ratio(volume, vol_p)

    return result


def _ma(data, period):
    s = pd.Series(data)
    return s.rolling(period).mean().values


def _bollinger(data, period, std_mult):
    s = pd.Series(data)
    mid = s.rolling(period).mean()
    std = s.rolling(period).std()
    upper = mid + std_mult * std
    lower = mid - std_mult * std
    return mid.values, upper.values, lower.values


def _rsi(data, period):
    deltas = np.diff(data)
    seed = deltas[:period + 1]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    if down == 0:
        rs = 100.0
    else:
        rs = up / down
    rsi = np.zeros(len(data))
    rsi[:period] = 100.0 - 100.0 / (1.0 + rs)
    for i in range(period, len(data)):
        delta = deltas[i - 1]
        if delta > 0:
            upval = delta
            downval = 0.0
        else:
            upval = 0.0
            downval = -delta
        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period
        if down == 0:
            rs = 100.0
        else:
            rs = up / down
        rsi[i] = 100.0 - 100.0 / (1.0 + rs)
    return rsi


def _volume_ratio(volume, period):
    s = pd.Series(volume)
    ma_vol = s.rolling(period).mean()
    return (s / ma_vol).values