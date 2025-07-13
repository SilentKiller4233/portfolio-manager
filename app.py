from flask import Flask, render_template, redirect, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from helpers import (
    get_db_connection,
    get_crypto_price,
    get_stock_price,
    get_portfolio,
    login_required,
    add_or_update_asset
)

app = Flask(__name__)
app.secret_key = "this-is-a-fixed-dev-key-123"

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

# ---------------------- ADD ASSET ---------------------- #
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

        add_or_update_asset(user_id, symbol, quantity, buy_price, asset_type)
        flash("Asset added successfully.", "success")
        return redirect("/dashboard")

    return render_template("add_asset.html")

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

# ---------------------- REFRESH PRICES ---------------------- #
@app.route("/refresh", methods=["POST"])
@login_required
def refresh_prices():
    flash("Prices refreshed successfully.", "info")
    return redirect("/dashboard")



# ---------------------- FLASK SETTINGS ---------------------- #
app.config["TEMPLATES_AUTO_RELOAD"] = True

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
