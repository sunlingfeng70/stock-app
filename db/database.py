import sqlite3
from pathlib import Path
from config import DB_PATH


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    schema = Path(__file__).parent / "schema.sql"
    with get_conn() as conn:
        conn.executescript(schema.read_text())


def init_stocks(stocks_data):
    with get_conn() as conn:
        for s in stocks_data:
            conn.execute(
                "INSERT OR IGNORE INTO stocks (code, name) VALUES (?, ?)",
                (s["code"], s["name"]),
            )


def get_stocks():
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM stocks ORDER BY code").fetchall()]


def get_price_cache(code):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM price_cache WHERE stock_code = ? ORDER BY date", (code,)
        ).fetchall()
        return [dict(r) for r in rows]


def save_price_cache(code, rows):
    with get_conn() as conn:
        conn.execute("DELETE FROM price_cache WHERE stock_code = ?", (code,))
        for r in rows:
            conn.execute(
                """INSERT INTO price_cache (stock_code, date, open, high, low, close, volume)
                   VALUES (?,?,?,?,?,?,?)""",
                (code, r["date"], r["open"], r["high"], r["low"], r["close"], r["volume"]),
            )


def save_signal(code, date, signal_type, price, indicators, note):
    with get_conn() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO signals
               (stock_code, date, signal_type, price, ma20, ma60, rsi,
                boll_upper, boll_mid, boll_lower, volume_ratio, note)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                code, date, signal_type, price,
                indicators.get("ma20"), indicators.get("ma60"),
                indicators.get("rsi"), indicators.get("boll_upper"),
                indicators.get("boll_mid"), indicators.get("boll_lower"),
                indicators.get("volume_ratio"), note,
            ),
        )


def get_signals(code, limit=100):
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT * FROM signals WHERE stock_code = ?
               ORDER BY date DESC LIMIT ?""",
            (code, limit),
        ).fetchall()
        return [dict(r) for r in rows]