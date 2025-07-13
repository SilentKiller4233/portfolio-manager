from helpers import get_db_connection
from flask import Flask, render_template, redirect, request, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

import sqlite3
import requests
import yfinance as yf
import os

app = Flask(__name__)
app.secret_key = "this-is-a-fixed-dev-key-123"
DATABASE = "portfolio.db"

# ---------------------- DB CONNECTION ---------------------- #
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------------- LOGIN REQUIRED ---------------------- #
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# ---------------------- INDEX REDIRECT ---------------------- #
@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/dashboard")
    return redirect("/login")

# ---------------------- REGISTER ---------------------- #
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        confirm = request.form["confirmation"]

        if not username or not password or not confirm:
            flash("All fields required.", "danger")
            return redirect("/register")

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect("/register")

        db = get_db()
        cursor = db.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            flash("Username already taken.", "danger")
            return redirect("/register")

        hash_pw = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash_pw))
        db.commit()
        flash("Registered successfully! Please log in.", "success")
        return redirect("/login")

    return render_template("register.html")

# ---------------------- LOGIN ---------------------- #
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Please fill in both fields", "danger")
            return redirect("/login")

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Logged in successfully!", "success")
            return redirect("/dashboard")
        else:
            flash("Invalid username or password", "danger")
            return redirect("/login")

    return render_template("login.html")


# ---------------------- LOGOUT ---------------------- #
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect("/login")

# ---------------------- DASHBOARD ---------------------- #
@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    user_id = session["user_id"]
    assets = db.execute("SELECT * FROM assets WHERE user_id = ?", (user_id,)).fetchall()

    portfolio = []
    total_value = 0.0

    for asset in assets:
        symbol = asset["symbol"]
        quantity = asset["quantity"]
        avg_price = asset["avg_buy_price"]
        type_ = asset["asset_type"]

        if type_ == "crypto":
            price = get_crypto_price(symbol)
        else:
            price = get_stock_price(symbol)

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

    return render_template("dashboard.html", portfolio=portfolio, total=round(total_value, 2))

# ---------------------- ADD ASSET ---------------------- #
@app.route("/add", methods=["GET", "POST"])
@login_required
def add_asset():
    if request.method == "POST":
        symbol = request.form["symbol"].strip().lower()
        try:
            quantity = float(request.form["quantity"])
        except ValueError:
            flash("Invalid quantity.", "danger")
            return redirect("/add")

        asset_type = request.form["asset_type"]

        if not symbol or quantity <= 0 or asset_type not in ["stock", "crypto"]:
            flash("All fields are required and must be valid.", "danger")
            return redirect("/add")

        db = get_db()
        user_id = session["user_id"]

        # Check if this asset already exists for the user
        existing = db.execute("""
            SELECT quantity, avg_buy_price FROM assets
            WHERE user_id = ? AND symbol = ? AND asset_type = ?
        """, (user_id, symbol, asset_type)).fetchone()

        if existing:
            old_qty = existing["quantity"]
            old_avg = existing["avg_buy_price"]

            # Prompt user to enter buy price in future version
            current_price = get_crypto_price(symbol) if asset_type == "crypto" else get_stock_price(symbol)
            if not current_price:
                flash("Could not fetch current price.", "danger")
                return redirect("/add")

            total_cost = old_qty * old_avg + quantity * current_price
            total_quantity = old_qty + quantity
            new_avg = total_cost / total_quantity

            db.execute("""
                UPDATE assets
                SET quantity = ?, avg_buy_price = ?
                WHERE user_id = ? AND symbol = ? AND asset_type = ?
            """, (total_quantity, new_avg, user_id, symbol, asset_type))
        else:
            # Insert new asset with current price as buy price
            current_price = get_crypto_price(symbol) if asset_type == "crypto" else get_stock_price(symbol)
            if not current_price:
                flash("Could not fetch current price.", "danger")
                return redirect("/add")

            db.execute("""
                INSERT INTO assets (user_id, symbol, quantity, avg_buy_price, asset_type)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, symbol, quantity, current_price, asset_type))

        db.commit()
        flash("Asset added successfully.", "success")
        return redirect("/dashboard")

    return render_template("add_asset.html")


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


# ---------------------- APP RUN ---------------------- #
app.config["TEMPLATES_AUTO_RELOAD"] = True
if __name__ == "__main__":
    app.run(debug=True)

