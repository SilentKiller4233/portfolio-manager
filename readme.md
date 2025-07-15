# Portfolio Manager

Portfolio Manager is a Flask-based web application designed to help users track and manage their investments across stocks and cryptocurrencies. It allows users to record purchases, monitor current market value, track unrealized and realized gains, and view transaction history. This project was developed as a final submission for Harvard's CS50x course.

## Features

- User registration and login with password hashing
- Add new assets (stock or crypto) with quantity and buy price
- Edit, sell, or delete existing assets
- Real-time market price fetching via CoinGecko (crypto) and yfinance (stocks)
- Dashboard view with asset breakdown:
  - Symbol, type, quantity
  - Average buy price
  - Live current price
  - Current value
  - Unrealized profit and loss (PnL)
- Realized PnL tracked and displayed per transaction
- Transactions page with complete buy/sell history
- Refresh prices button for up-to-date portfolio values
- Table sorting, filtering by type, and search by symbol
- Responsive user interface with consistent design

## Technologies Used

- Python, Flask, SQLite
- HTML, CSS, JavaScript (vanilla)
- Jinja2 templating
- CoinGecko API and yfinance library
- Bootstrap-inspired custom styling

## Setup Instructions

1. Clone the repository:

   ```bash
   git clone https://github.com/SilentKiller4233/portfolio-manager.git
   cd portfolio-manager
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   venv\Scripts\activate  # For Windows
   # or
   source venv/bin/activate  # For macOS/Linux
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:

   ```bash
   sqlite3 portfolio.db < schema.sql
   ```

5. Run the Flask app:

   ```bash
   set FLASK_APP=app.py
   set FLASK_ENV=development
   flask run
   ```

   Then navigate to `http://127.0.0.1:5000` in your browser.

## Usage

- Register and log in to your account.
- Add assets by entering their symbol, type, quantity, and average buy price.
- View and manage assets through the dashboard.
- Use the "Sell" button to reduce quantity and realize profit/loss.
- Check transaction history for a log of buy and sell actions.

## Project Structure

- `app.py`: Main Flask application with route definitions
- `helpers.py`: Helper functions for DB access and price fetching
- `templates/`: HTML templates (Jinja2)
- `static/styles.css`: Custom CSS for consistent UI
- `schema.sql`: Database schema
- `portfolio.db`: SQLite database

### File Descriptions

#### app.py

This is the core of the application. It defines all the Flask routes and handles request-response logic. It imports the necessary libraries, sets up session configuration and a secret key, and uses the `@login_required` decorator to restrict access to authenticated users for protected routes.

Key routes defined here include:

- `/register` – Handles user registration
- `/login` – Handles login and session setup
- `/logout` – Clears session and logs the user out
- `/dashboard` – Main landing page after login showing portfolio overview
- `/add` – Allows users to add new assets
- `/edit/<symbol>` – Allows users to update quantity and buy price of an asset
- `/sell/<symbol>` – Allows partial or full sale of an asset and logs it as a transaction
- `/delete/<symbol>` – Deletes an asset from the portfolio
- `/transactions` – Shows a table of historical transactions including realized PnL
- `/refresh` – Re-fetches current prices for all assets in a user’s portfolio

Each route is clearly defined, and the logic is modular and handles edge cases such as missing asset types, invalid inputs, or unknown symbols.

---

#### helpers.py

This file contains utility functions reused throughout the app.

Key functions:

- `get_db_connection()` – Provides a new SQLite connection, returning rows as dictionaries for easy templating
- `login_required(f)` – A custom decorator that redirects users to the login page if not authenticated
- `get_crypto_price(symbol)` – Fetches the real-time price of a cryptocurrency from the CoinGecko API
- `get_stock_price(symbol)` – Fetches real-time stock data from yfinance

---

#### schema.sql

Defines the structure of the SQLite database. Contains three tables:

- `users` – Stores user ID, username, and hashed password
- `assets` – Stores the currently held assets per user, including symbol, type (crypto or stock), quantity, and average buy price
- `transactions` – Records each buy/sell operation along with symbol, quantity, price, type (buy/sell), and timestamp

---

#### portfolio.db

This is the actual SQLite database file created based on schema.sql. It contains all the persisted user, asset, and transaction data.

---

#### templates/

This folder contains all HTML templates used by the app, structured using Flask’s Jinja2 syntax.

- `layout.html` – Defines the global layout (navbar, welcome text, and flash message area) and loads the CSS file. All other HTML pages extend from this base template.

- `dashboard.html` – Displays the logged-in user’s portfolio. Includes:

  - Filtering by type (crypto/stock)
  - Sorting by different metrics (symbol, value, PnL, etc.)
  - Search bar by asset symbol
  - Refresh button for price updates
  - Portfolio table with symbol, type, quantity, average buy price, current price, total value, and unrealized PnL
  - Inline edit/sell/delete links for each asset

- `add_asset.html` – Form for adding a new asset to the portfolio. Includes input fields for symbol, type (dropdown), quantity, and buy price.

- `edit_asset.html` – Form to update the quantity and buy price of an existing asset.

- `sell_asset.html` – Allows users to sell part or all of a held asset. Displays current holdings and accepts a quantity to sell.

- `transactions.html` – Displays all historical transactions by the user. Includes:

  - Symbol, type, quantity, price, action (buy/sell), timestamp
  - PnL shown for each sell transaction

- `login.html` and `register.html` – Simple authentication forms styled to match the rest of the app.

---

#### static/styles.css

The main stylesheet defines global variables, fonts, layout spacing, navbar, buttons, form elements, table design, and alert messages. It ensures consistent styling and responsive layout across all templates.

---

#### requirements.txt

Includes the Python dependencies used in the project:

- Flask
- yfinance
- requests

## Made for CS50 Final Project
