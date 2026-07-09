from engine.strategy import evaluate_signal


def run_backtest(df, indicators):
    trades = []
    position = 0
    buy_price = 0.0

    for i in range(len(df)):
        signal, reason = evaluate_signal(i, indicators)
        close = float(df.iloc[i]["close"])
        date = str(df.iloc[i]["date"])

        if signal == "buy" and position == 0:
            position = 1
            buy_price = close
            trades.append({"date": date, "type": "buy", "price": close, "reason": reason})
        elif signal == "add" and position == 1:
            position = 2
            trades.append({"date": date, "type": "add", "price": close, "reason": reason})
        elif signal == "sell" and position > 0:
            profit_pct = (close - buy_price) / buy_price * 100
            trades.append({
                "date": date,
                "type": "sell",
                "price": close,
                "profit_pct": round(profit_pct, 2),
                "reason": reason,
            })
            position = 0
            buy_price = 0.0

    win_count = sum(1 for t in trades if t.get("profit_pct", 0) > 0)
    total_trades = sum(1 for t in trades if t["type"] == "sell")
    win_rate = round(win_count / total_trades * 100, 1) if total_trades > 0 else 0.0
    total_profit = sum(t.get("profit_pct", 0) for t in trades if t["type"] == "sell")

    return {
        "trades": trades,
        "win_rate": win_rate,
        "total_trades": total_trades,
        "total_profit": round(total_profit, 2),
    }