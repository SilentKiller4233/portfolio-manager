import sqlite3
import requests
import yfinance as yf
from flask import session, redirect, flash
from functools import wraps

# ---------------------- DB CONNECTION ---------------------- #
def get_db_connection():
    conn = sqlite3.connect("portfolio.db")
    conn.row_factory = sqlite3.Row
    return conn

# ---------------------- PRICE HELPERS ---------------------- #
def get_crypto_price(symbol):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()
        return data[symbol.lower()]["usd"]
    except:
        return None

def get_stock_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        return stock.info["regularMarketPrice"]
    except:
        return None

# ---------------------- LOGIN REQUIRED DECORATOR ---------------------- #
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("You must be logged in to access this page.", "warning")
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# ---------------------- PORTFOLIO SUMMARY ---------------------- #
def get_portfolio(user_id):
    db = get_db_connection()
    assets = db.execute("SELECT * FROM assets WHERE user_id = ?", (user_id,)).fetchall()

    portfolio = []
    total_value = 0.0

    for asset in assets:
        symbol = asset["symbol"]
        quantity = asset["quantity"]
        avg_price = asset["avg_buy_price"]
        type_ = asset["asset_type"]

        price = get_crypto_price(symbol) if type_ == "crypto" else get_stock_price(symbol)
        current_value = quantity * price if price else 0
        unrealized = (price - avg_price) * quantity if price else 0

        portfolio.append({
            "symbol": symbol.upper(),
            "type": type_,
            "quantity": quantity,
            "avg_price": round(avg_price, 2),
            "current_price": round(price, 2) if price else "N/A",
            "current_value": round(current_value, 2),
            "unrealized_pnl": round(unrealized, 2),
        })

        total_value += current_value

    return portfolio, round(total_value, 2)

# ---------------------- ADD OR UPDATE ASSET ---------------------- #
def add_or_update_asset(user_id, symbol, quantity, buy_price, asset_type):
    db = get_db_connection()

    existing = db.execute("""
        SELECT quantity, avg_buy_price FROM assets
        WHERE user_id = ? AND symbol = ? AND asset_type = ?
    """, (user_id, symbol, asset_type)).fetchone()

    if existing:
        old_qty = existing["quantity"]
        old_avg = existing["avg_buy_price"]
        total_cost = old_qty * old_avg + quantity * buy_price
        total_quantity = old_qty + quantity
        new_avg = total_cost / total_quantity

        db.execute("""
            UPDATE assets
            SET quantity = ?, avg_buy_price = ?
            WHERE user_id = ? AND symbol = ? AND asset_type = ?
        """, (total_quantity, new_avg, user_id, symbol, asset_type))
    else:
        db.execute("""
            INSERT INTO assets (user_id, symbol, quantity, avg_buy_price, asset_type)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, symbol, quantity, buy_price, asset_type))

    db.commit()
