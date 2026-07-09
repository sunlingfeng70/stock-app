import numpy as np
from config import STRATEGY


def evaluate_signal(row_idx, indicators):
    p = STRATEGY

    close = indicators["close"][row_idx]
    ma20 = indicators["ma20"][row_idx]
    ma60 = indicators["ma60"][row_idx]
    rsi_val = indicators["rsi"][row_idx]
    boll_lower = indicators["boll_lower"][row_idx]
    boll_upper = indicators["boll_upper"][row_idx]
    boll_mid = indicators["boll_mid"][row_idx]
    vol_ratio = indicators["volume_ratio"][row_idx]

    if np.isnan(ma20) or np.isnan(ma60) or np.isnan(rsi_val):
        return "hold", ""

    near_boll_lower = close <= boll_lower * 1.01
    near_boll_upper = close >= boll_upper * 0.99
    rsi_oversold = rsi_val <= p["rsi_oversold"]
    rsi_overbought = rsi_val >= p["rsi_overbought"]
    above_ma20 = close > ma20
    above_ma60 = close > ma60
    volume_surge = vol_ratio >= p["volume_surge_ratio"]
    ma20_rising = ma20 > indicators["ma20"][max(0, row_idx - 5)]
    ma20_falling = ma20 < indicators["ma20"][max(0, row_idx - 5)]

    buy_score = 0
    buy_reasons = []
    if near_boll_lower:
        buy_score += 1
        buy_reasons.append("触及布林下轨")
    if rsi_oversold:
        buy_score += 1
        buy_reasons.append(f"RSI超卖({rsi_val:.0f})")
    if volume_surge:
        buy_score += 1
        buy_reasons.append("放量")

    add_score = 0
    add_reasons = []
    if above_ma20:
        add_score += 1
        add_reasons.append("站上MA20")
    if ma20_rising:
        add_score += 1
        add_reasons.append("MA20向上")
    if rsi_val < 65:
        add_score += 1
        add_reasons.append("RSI适中")
    if above_ma60:
        add_score += 1
        add_reasons.append("站上MA60")

    sell_score = 0
    sell_reasons = []
    if near_boll_upper:
        sell_score += 1
        sell_reasons.append("触及布林上轨")
    if rsi_overbought:
        sell_score += 1
        sell_reasons.append(f"RSI超买({rsi_val:.0f})")
    if (not above_ma20) and ma20_falling:
        sell_score += 1
        sell_reasons.append("跌破MA20且向下")

    if sell_score >= 2:
        return "sell", "、".join(sell_reasons)
    if buy_score >= 2:
        return "buy", "、".join(buy_reasons)
    if add_score >= 3 and row_idx > 0:
        prev = evaluate_signal(row_idx - 1, indicators)
        if prev[0] in ("buy", "hold"):
            return "add", "、".join(add_reasons)
    return "hold", ""


def evaluate_current(df, indicators):
    row_idx = len(df) - 1
    return evaluate_signal(row_idx, indicators)