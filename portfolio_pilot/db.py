import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "portfolio.db"

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with connect() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS portfolios(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );
        CREATE TABLE IF NOT EXISTS transactions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER NOT NULL,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL CHECK(side IN ('BUY','SELL')),
            quantity REAL NOT NULL CHECK(quantity > 0),
            price REAL NOT NULL CHECK(price >= 0),
            traded_at TEXT NOT NULL,
            FOREIGN KEY(portfolio_id) REFERENCES portfolios(id)
        );
        CREATE TABLE IF NOT EXISTS dividends(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER NOT NULL,
            symbol TEXT NOT NULL,
            amount REAL NOT NULL CHECK(amount >= 0),
            paid_at TEXT NOT NULL,
            FOREIGN KEY(portfolio_id) REFERENCES portfolios(id)
        );
        CREATE TABLE IF NOT EXISTS alerts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER NOT NULL,
            symbol TEXT NOT NULL,
            kind TEXT NOT NULL,
            threshold REAL NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            FOREIGN KEY(portfolio_id) REFERENCES portfolios(id)
        );
        CREATE TABLE IF NOT EXISTS alert_history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            triggered_at TEXT NOT NULL,
            FOREIGN KEY(alert_id) REFERENCES alerts(id)
        );
        """)
        con.execute("INSERT OR IGNORE INTO portfolios(name) VALUES (?)", ("Growth Portfolio",))
        con.execute("INSERT OR IGNORE INTO portfolios(name) VALUES (?)", ("Income Portfolio",))
        count = con.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
        if count == 0:
            pid = con.execute("SELECT id FROM portfolios WHERE name='Growth Portfolio'").fetchone()[0]
            sample = [
                (pid,"AAPL","BUY",8,180,"2026-01-10"),
                (pid,"MSFT","BUY",5,420,"2026-02-14"),
                (pid,"NVDA","BUY",10,130,"2026-03-05"),
                (pid,"AAPL","BUY",4,195,"2026-04-20"),
                (pid,"MSFT","SELL",1,455,"2026-06-12"),
            ]
            con.executemany("""INSERT INTO transactions
                (portfolio_id,symbol,side,quantity,price,traded_at) VALUES (?,?,?,?,?,?)""", sample)
            con.executemany("""INSERT INTO dividends
                (portfolio_id,symbol,amount,paid_at) VALUES (?,?,?,?)""",
                [(pid,"AAPL",7.50,"2026-05-15"),(pid,"MSFT",6.00,"2026-06-10")])
