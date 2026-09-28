from flask import Flask, render_template, request, redirect, url_for, jsonify
from portfolio_pilot.db import init_db, connect
from portfolio_pilot.analytics import positions, summary
from portfolio_pilot.prices import get_price
from datetime import datetime

app = Flask(__name__)
init_db()

def portfolio_data(pid):
    with connect() as con:
        tx = con.execute("SELECT * FROM transactions WHERE portfolio_id=? ORDER BY traded_at,id",(pid,)).fetchall()
        div = con.execute("SELECT * FROM dividends WHERE portfolio_id=? ORDER BY paid_at",(pid,)).fetchall()
        p = positions(tx)
        return p, summary(p, div), div

@app.route("/")
def home():
    with connect() as con:
        portfolios = con.execute("SELECT * FROM portfolios ORDER BY id").fetchall()
    pid = int(request.args.get("portfolio", portfolios[0]["id"]))
    pos, stats, dividends = portfolio_data(pid)
    sector = {}
    for x in pos: sector[x["sector"]] = sector.get(x["sector"],0)+x["value"]
    return render_template("index.html", portfolios=portfolios, selected=pid, positions=pos,
                           stats=stats, sector=sector, dividends=dividends)

@app.post("/portfolio")
def add_portfolio():
    name=request.form["name"].strip()
    if name:
        with connect() as con: con.execute("INSERT OR IGNORE INTO portfolios(name) VALUES (?)",(name,))
    return redirect(url_for("home"))

@app.post("/transaction")
def add_transaction():
    with connect() as con:
        con.execute("""INSERT INTO transactions(portfolio_id,symbol,side,quantity,price,traded_at)
        VALUES(?,?,?,?,?,?)""",(int(request.form["portfolio_id"]),request.form["symbol"].upper().strip(),
        request.form["side"],float(request.form["quantity"]),float(request.form["price"]),request.form["traded_at"]))
    return redirect(url_for("home",portfolio=request.form["portfolio_id"]))

@app.post("/dividend")
def add_dividend():
    with connect() as con:
        con.execute("""INSERT INTO dividends(portfolio_id,symbol,amount,paid_at) VALUES(?,?,?,?)""",
        (int(request.form["portfolio_id"]),request.form["symbol"].upper().strip(),
         float(request.form["amount"]),request.form["paid_at"]))
    return redirect(url_for("home",portfolio=request.form["portfolio_id"]))

@app.post("/alert")
def add_alert():
    with connect() as con:
        con.execute("""INSERT INTO alerts(portfolio_id,symbol,kind,threshold,created_at)
        VALUES(?,?,?,?,?)""",(int(request.form["portfolio_id"]),request.form["symbol"].upper().strip(),
        request.form["kind"],float(request.form["threshold"]),datetime.utcnow().isoformat()))
    return redirect(url_for("home",portfolio=request.form["portfolio_id"]))

@app.route("/api/portfolio/<int:pid>")
def api_portfolio(pid):
    pos, stats, _ = portfolio_data(pid)
    return jsonify({"summary":stats,"positions":pos})

@app.route("/health")
def health():
    return jsonify({"status":"healthy","project":"PortfolioPilot","price_cache":"5 minutes"})

if __name__ == "__main__":
    app.run(debug=True)
