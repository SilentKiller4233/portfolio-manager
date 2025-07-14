import sqlite3
import requests
import yfinance as yf
from flask import session, redirect, flash
from functools import wraps

# ---------------------- DATABASE CONNECTION ---------------------- #
def get_db_connection():
    """Establish a connection to the SQLite database."""
    conn = sqlite3.connect("portfolio.db")
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------- PRICE FETCHING ---------------------- #
def get_crypto_price(symbol):
    """
    Fetch current USD price for a given cryptocurrency using CoinGecko.
    Returns None on failure.
    """
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()
        return data[symbol.lower()]["usd"]
    except:
        return None

def get_stock_price(symbol):
    """
    Fetch current price for a given stock symbol using yfinance.
    Returns None on failure.
    """
    try:
        stock = yf.Ticker(symbol)
        return stock.info["regularMarketPrice"]
    except:
        return None


# ---------------------- AUTHENTICATION DECORATOR ---------------------- #
def login_required(f):
    """
    Flask decorator to enforce login on protected routes.
    Redirects to login if user_id not in session.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("You must be logged in to access this page.", "warning")
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# ---------------------- PORTFOLIO SUMMARY ---------------------- #
def get_portfolio(user_id):
    """
    Returns a list of all user-held assets with updated prices and unrealized PnL.
    Also returns total current portfolio value.
    """
    db = get_db_connection()
    assets = db.execute(
        "SELECT * FROM assets WHERE user_id = ?", (user_id,)
    ).fetchall()

    portfolio = []
    total_value = 0.0

    for asset in assets:
        symbol = asset["symbol"]
        quantity = asset["quantity"]
        avg_price = asset["avg_buy_price"]
        asset_type = asset["asset_type"]

        current_price = get_crypto_price(symbol) if asset_type == "crypto" else get_stock_price(symbol)
        current_value = quantity * current_price if current_price else 0
        unrealized_pnl = (current_price - avg_price) * quantity if current_price else 0

        portfolio.append({
            "symbol": symbol.upper(),
            "type": asset_type,
            "quantity": quantity,
            "avg_price": round(avg_price, 2),
            "current_price": round(current_price, 2) if current_price else "N/A",
            "current_value": round(current_value, 2),
            "unrealized_pnl": round(unrealized_pnl, 2),
        })

        total_value += current_value

    return portfolio, round(total_value, 2)


# ---------------------- ADD OR UPDATE ASSET ---------------------- #
def add_or_update_asset(user_id, symbol, quantity, buy_price, asset_type):
    """
    Adds a new asset or updates existing one by recalculating average buy price.
    """
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


# ---------------------- TRANSACTION HISTORY ---------------------- #
def get_transaction_history(user_id):
    """
    Returns a user's historical sell transactions ordered by most recent.
    """
    db = get_db_connection()
    transactions = db.execute("""
        SELECT symbol, quantity, sell_price, realized_pnl, date AS timestamp
        FROM transactions
        WHERE user_id = ?
        ORDER BY date DESC
    """, (user_id,)).fetchall()

    return transactions
