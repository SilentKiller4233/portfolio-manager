from helpers import (
    get_db_connection,
    get_crypto_price,
    get_stock_price,
    get_portfolio,
    update_or_insert_asset
)

from flask import Flask, render_template, redirect, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3

app = Flask(__name__)
app.secret_key = "this-is-a-fixed-dev-key-123"


# ---------------------- LOGIN REQUIRED DECORATOR ---------------------- #
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
    return redirect("/dashboard") if "user_id" in session else redirect("/login")


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

        db = get_db_connection()
        user = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if user:
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

        db = get_db_connection()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        db.close()

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
    user_id = session["user_id"]
    portfolio, total_value = get_portfolio(user_id)
    return render_template("dashboard.html", portfolio=portfolio, total=total_value)

# ---------------------- EDIT ASSET ---------------------- #
@app.route("/edit/<symbol>", methods=["GET", "POST"])
@login_required
def edit_asset(symbol):
    asset_type = request.args.get("type")
    if not asset_type:
        flash("Asset type is required.", "danger")
        return redirect("/dashboard")

    db = get_db_connection()
    user_id = session["user_id"]
    asset = db.execute("""
        SELECT * FROM assets
        WHERE user_id = ? AND symbol = ? AND asset_type = ?
    """, (user_id, symbol.lower(), asset_type)).fetchone()

    if not asset:
        flash("Asset not found.", "danger")
        return redirect("/dashboard")

    if request.method == "POST":
        try:
            quantity = float(request.form["quantity"])
            avg_price = float(request.form["avg_buy_price"])
        except ValueError:
            flash("Invalid input.", "danger")
            return redirect(request.url)

        if quantity <= 0 or avg_price <= 0:
            flash("Values must be positive.", "danger")
            return redirect(request.url)

        db.execute("""
            UPDATE assets
            SET quantity = ?, avg_buy_price = ?
            WHERE user_id = ? AND symbol = ? AND asset_type = ?
        """, (quantity, avg_price, user_id, symbol.lower(), asset_type))
        db.commit()
        flash("Asset updated successfully.", "success")
        return redirect("/dashboard")

    return render_template("edit_asset.html", asset=asset)

# ---------------------- DELETE ASSET ---------------------- #
@app.route("/delete/<symbol>", methods=["POST"])
@login_required
def delete_asset(symbol):
    asset_type = request.args.get("type")
    if not asset_type:
        flash("Asset type is required.", "danger")
        return redirect("/dashboard")

    db = get_db_connection()
    user_id = session["user_id"]
    db.execute("""
        DELETE FROM assets
        WHERE user_id = ? AND symbol = ? AND asset_type = ?
    """, (user_id, symbol.lower(), asset_type))
    db.commit()
    flash("Asset deleted.", "info")
    return redirect("/dashboard")



# ---------------------- ADD ASSET (Updated with Manual Buy Price) ---------------------- #
@app.route("/add", methods=["GET", "POST"])
@login_required
def add_asset():
    if request.method == "POST":
        symbol = request.form["symbol"].strip().lower()
        asset_type = request.form["asset_type"]
        user_id = session["user_id"]

        try:
            quantity = float(request.form["quantity"])
            buy_price = float(request.form["buy_price"])
        except ValueError:
            flash("Invalid quantity or buy price.", "danger")
            return redirect("/add")

        if not symbol or quantity <= 0 or buy_price <= 0 or asset_type not in ["stock", "crypto"]:
            flash("All fields are required and must be valid.", "danger")
            return redirect("/add")

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
        flash("Asset added successfully.", "success")
        return redirect("/dashboard")

    return render_template("add_asset.html")




# ---------------------- FLASK SETTINGS ---------------------- #
app.config["TEMPLATES_AUTO_RELOAD"] = True
if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)

