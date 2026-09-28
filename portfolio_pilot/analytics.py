from collections import defaultdict
from .prices import get_price

SECTORS = {
    "AAPL":"Technology","MSFT":"Technology","NVDA":"Technology","GOOGL":"Communication",
    "AMZN":"Consumer","META":"Communication","TSLA":"Consumer","JPM":"Financials","JNJ":"Healthcare"
}

def positions(rows):
    state = defaultdict(lambda: {"qty":0.0, "cost":0.0, "realized":0.0})
    for r in rows:
        s = state[r["symbol"]]
        q, p = float(r["quantity"]), float(r["price"])
        if r["side"] == "BUY":
            s["cost"] += q*p
            s["qty"] += q
        else:
            sold = min(q, s["qty"])
            avg = s["cost"]/s["qty"] if s["qty"] else 0
            s["realized"] += sold*(p-avg)
            s["qty"] -= sold
            s["cost"] -= sold*avg
    result = []
    for symbol, s in state.items():
        if s["qty"] <= 0: continue
        price, source = get_price(symbol)
        avg = s["cost"]/s["qty"]
        value = s["qty"]*price
        unrealized = (price-avg)*s["qty"]
        result.append({
            "symbol":symbol,"quantity":round(s["qty"],4),"avg_cost":round(avg,2),
            "price":round(price,2),"value":round(value,2),"unrealized":round(unrealized,2),
            "realized":round(s["realized"],2),"sector":SECTORS.get(symbol,"Other"),"price_source":source
        })
    return result

def summary(pos, dividends):
    value = sum(x["value"] for x in pos)
    unreal = sum(x["unrealized"] for x in pos)
    realized = sum(x["realized"] for x in pos)
    income = sum(float(x["amount"]) for x in dividends)
    cost = sum(x["avg_cost"]*x["quantity"] for x in pos)
    ttm_yield = (income/value*100) if value else 0
    return {"value":round(value,2),"unrealized":round(unreal,2),"realized":round(realized,2),
            "income":round(income,2),"cost":round(cost,2),"ttm_yield":round(ttm_yield,2)}
