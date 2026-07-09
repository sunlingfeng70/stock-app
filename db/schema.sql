CREATE TABLE IF NOT EXISTS stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    added_at TEXT NOT NULL DEFAULT (date('now'))
);

CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_code TEXT NOT NULL REFERENCES stocks(code),
    date TEXT NOT NULL,
    signal_type TEXT NOT NULL CHECK(signal_type IN ('buy','add','sell','hold')),
    price REAL,
    ma20 REAL,
    ma60 REAL,
    rsi REAL,
    boll_upper REAL,
    boll_mid REAL,
    boll_lower REAL,
    volume_ratio REAL,
    note TEXT,
    UNIQUE(stock_code, date)
);

CREATE TABLE IF NOT EXISTS price_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_code TEXT NOT NULL,
    date TEXT NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER,
    UNIQUE(stock_code, date)
);

CREATE INDEX IF NOT EXISTS idx_signals_code ON signals(stock_code);
CREATE INDEX IF NOT EXISTS idx_price_cache_code ON price_cache(stock_code);