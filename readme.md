# 📊 Portfolio Manager

A Flask-based web app that allows users to manage their investments across stocks and cryptocurrencies. Built for CS50x final project, this app supports user authentication, portfolio tracking with financial calculations, and transactional history.

---

## 🚀 Features

### 🧭 Core
- **User Registration & Login** with hashed passwords
- **Add Assets**: Specify symbol, type (stock/crypto), quantity, and buy price
- **Edit / Sell / Delete Assets**
- **Portfolio Dashboard**: Displays holdings, avg buy price, current price, quantity, current value, realized & unrealized PnL
- **Transactions Log**: Tracks buy/sell operations with timestamp and realized gain/loss
- **Live Price Fetching** via yfinance (stocks) & CoinGecko (crypto)
- **Refresh Prices** button to get updated market values
- **Client-side sorting & filtering** in dashboard
- **Responsive UI** with clean layout and mobile improvements

### 🔧 Under the Hood
- **SQLite database** (`portfolio.db`), defined in `schema.sql`
- **Modular code structure**:
  - `app.py` – Flask routes
  - `helpers.py` – Database logic, price fetchers, portfolio/transaction utilities
- **Custom CSS** for polished UI across layouts

---

## 📦 Installation & Setup

```bash
git clone https://github.com/SilentKiller4233/portfolio-manager.git
cd portfolio-manager
python -m venv venv
venv\Scripts\activate  # Windows
# or on macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
sqlite3 portfolio.db < schema.sql
set FLASK_APP=app.py
set FLASK_ENV=development
flask run
