from functools import lru_cache
from datetime import datetime, timedelta

FALLBACK = {
    "AAPL": 225.00, "MSFT": 510.00, "NVDA": 185.00,
    "GOOGL": 245.00, "AMZN": 235.00, "META": 690.00,
    "TSLA": 430.00, "JPM": 305.00, "JNJ": 190.00
}

_cache = {}

def get_price(symbol):
    """Real-time yfinance price with a five-minute in-process cache and safe fallback."""
    symbol = symbol.upper().strip()
    now = datetime.utcnow()
    hit = _cache.get(symbol)
    if hit and now - hit[0] < timedelta(minutes=5):
        return hit[1], hit[2]
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        price = ticker.fast_info.get("last_price")
        if price is None:
            hist = ticker.history(period="1d")
            price = float(hist["Close"].iloc[-1])
        price = float(price)
        _cache[symbol] = (now, price, "live")
        return price, "live"
    except Exception:
        price = float(FALLBACK.get(symbol, 100.0))
        _cache[symbol] = (now, price, "fallback")
        return price, "fallback"
