# PortfolioPilot — Personal Stock Portfolio Tracker

PortfolioPilot is a Python/Flask portfolio intelligence application created for **ProStackHub's Python Programming Internship — Task 3**.

## Highlights
- Multiple portfolios with normalized SQLite persistence
- BUY/SELL transaction ledger and weighted-average cost basis
- Realized and unrealized P&L
- Real-time prices through `yfinance`
- Five-minute in-process price cache with graceful fallback values
- Portfolio value and sector allocation
- Dividend/payment logging, income total and TTM yield
- Price alerts with persistent alert-history support
- Responsive analytics dashboard
- JSON portfolio API and `/health` endpoint
- Vercel-ready Flask entry point (`api/index.py`)

## Quick start
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open `http://127.0.0.1:5000`.

## API
`GET /api/portfolio/1` returns summary metrics and positions.
`GET /health` returns service health.

## Alert check
```bash
python check_alerts.py
```

## Deployment
Push the repository to GitHub, import it into Vercel, select the Flask preset, keep the root directory as `./`, and deploy. The `api/index.py` entry point is included.

## Architecture
`portfolio_pilot/db.py` owns persistence; `analytics.py` computes cost basis/P&L; `prices.py` handles market data/cache/fallback; `app.py` exposes the dashboard and API.

## Notes
Market data can be delayed or unavailable. Fallback values exist only so the application remains demonstrable during API failure; the UI labels whether each displayed price came from the live feed or fallback.

**Developer:** Shibaji Biswas  
**Project:** ProStackHub Python Programming Internship — Task 3
