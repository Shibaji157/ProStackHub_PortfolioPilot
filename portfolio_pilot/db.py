import os
import shutil
import sqlite3
from pathlib import Path


# ============================================================
# DATABASE PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
LOCAL_DB_PATH = BASE_DIR / "data" / "portfolio.db"


# Vercel's deployed project directory is read-only.
# Therefore, on Vercel we copy the SQLite database to /tmp,
# which is writable by the serverless function.
if os.environ.get("VERCEL"):
    DB_PATH = Path("/tmp/portfolio_pilot.db")

    if not DB_PATH.exists():
        if LOCAL_DB_PATH.exists():
            shutil.copy2(LOCAL_DB_PATH, DB_PATH)
        else:
            DB_PATH.touch()

else:
    # Normal local development database
    DB_PATH = LOCAL_DB_PATH
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def connect():
    """
    Create and return a SQLite database connection.
    """

    con = sqlite3.connect(
        str(DB_PATH),
        timeout=10
    )

    con.row_factory = sqlite3.Row

    return con


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_db():
    """
    Create all required PortfolioPilot database tables
    and insert demonstration data when the database is empty.
    """

    con = connect()

    try:

        # ----------------------------------------------------
        # CREATE TABLES
        # ----------------------------------------------------

        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS portfolios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );


            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                portfolio_id INTEGER NOT NULL,

                symbol TEXT NOT NULL,

                transaction_type TEXT NOT NULL,

                quantity REAL NOT NULL,

                price REAL NOT NULL,

                transaction_date TEXT NOT NULL,

                FOREIGN KEY (portfolio_id)
                    REFERENCES portfolios(id)
            );


            CREATE TABLE IF NOT EXISTS dividends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                portfolio_id INTEGER NOT NULL,

                symbol TEXT NOT NULL,

                amount REAL NOT NULL,

                payment_date TEXT NOT NULL,

                FOREIGN KEY (portfolio_id)
                    REFERENCES portfolios(id)
            );


            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                portfolio_id INTEGER NOT NULL,

                symbol TEXT NOT NULL,

                alert_type TEXT NOT NULL,

                target REAL NOT NULL,

                enabled INTEGER DEFAULT 1,

                FOREIGN KEY (portfolio_id)
                    REFERENCES portfolios(id)
            );


            CREATE TABLE IF NOT EXISTS alert_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                alert_id INTEGER,

                symbol TEXT NOT NULL,

                message TEXT NOT NULL,

                triggered_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (alert_id)
                    REFERENCES alerts(id)
            );
            """
        )


        # ----------------------------------------------------
        # CREATE DEFAULT PORTFOLIOS
        # ----------------------------------------------------

        con.execute(
            """
            INSERT OR IGNORE INTO portfolios(name)
            VALUES (?)
            """,
            ("Growth Portfolio",)
        )


        con.execute(
            """
            INSERT OR IGNORE INTO portfolios(name)
            VALUES (?)
            """,
            ("Income Portfolio",)
        )


        con.commit()


        # ----------------------------------------------------
        # CHECK WHETHER DEMO DATA ALREADY EXISTS
        # ----------------------------------------------------

        result = con.execute(
            """
            SELECT COUNT(*) AS count
            FROM transactions
            """
        ).fetchone()


        transaction_count = result["count"]


        # ----------------------------------------------------
        # INSERT DEMONSTRATION DATA
        # ----------------------------------------------------

        if transaction_count == 0:

            growth_portfolio = con.execute(
                """
                SELECT id
                FROM portfolios
                WHERE name = ?
                """,
                ("Growth Portfolio",)
            ).fetchone()


            if growth_portfolio:

                portfolio_id = growth_portfolio["id"]


                # --------------------------------------------
                # DEMO STOCK TRANSACTIONS
                # --------------------------------------------

                demo_transactions = [

                    (
                        portfolio_id,
                        "AAPL",
                        "BUY",
                        8,
                        180,
                        "2026-01-10"
                    ),

                    (
                        portfolio_id,
                        "MSFT",
                        "BUY",
                        5,
                        420,
                        "2026-02-14"
                    ),

                    (
                        portfolio_id,
                        "NVDA",
                        "BUY",
                        10,
                        130,
                        "2026-03-05"
                    ),

                    (
                        portfolio_id,
                        "AAPL",
                        "BUY",
                        4,
                        195,
                        "2026-04-20"
                    ),

                    (
                        portfolio_id,
                        "MSFT",
                        "SELL",
                        1,
                        455,
                        "2026-06-12"
                    )

                ]


                con.executemany(
                    """
                    INSERT INTO transactions
                    (
                        portfolio_id,
                        symbol,
                        transaction_type,
                        quantity,
                        price,
                        transaction_date
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    demo_transactions
                )


                # --------------------------------------------
                # DEMO DIVIDEND PAYMENTS
                # --------------------------------------------

                demo_dividends = [

                    (
                        portfolio_id,
                        "AAPL",
                        7.50,
                        "2026-05-15"
                    ),

                    (
                        portfolio_id,
                        "MSFT",
                        6.00,
                        "2026-06-20"
                    )

                ]


                con.executemany(
                    """
                    INSERT INTO dividends
                    (
                        portfolio_id,
                        symbol,
                        amount,
                        payment_date
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    demo_dividends
                )


                con.commit()


    finally:

        con.close()


# ============================================================
# HELPER FUNCTION
# ============================================================

def get_db_path():
    """
    Return the active SQLite database path.
    Useful for debugging and health checks.
    """

    return str(DB_PATH)