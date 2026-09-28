from portfolio_pilot.db import init_db, connect
from portfolio_pilot.prices import get_price
from datetime import datetime

init_db()
with connect() as con:
    alerts = con.execute("SELECT * FROM alerts WHERE enabled=1").fetchall()
    for a in alerts:
        price, source = get_price(a["symbol"])
        hit = ((a["kind"]=="above" and price>=a["threshold"]) or
               (a["kind"]=="below" and price<=a["threshold"]))
        if hit:
            msg=f'{a["symbol"]} {a["kind"]} {a["threshold"]}: current ${price:.2f} ({source})'
            print("ALERT:", msg)
            con.execute("INSERT INTO alert_history(alert_id,message,triggered_at) VALUES(?,?,?)",
                        (a["id"],msg,datetime.utcnow().isoformat()))
