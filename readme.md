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

## Database Schema

The application uses a SQLite database with tables:

- `users`: Stores user credentials
- `assets`: Stores active portfolio holdings per user
- `transactions`: Records all buy and sell actions, including realized PnL

Schema defined in `schema.sql`.

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

## Project Structure

- `app.py`: Main Flask application with route definitions
- `helpers.py`: Helper functions for DB access and price fetching
- `templates/`: HTML templates (Jinja2)
- `static/styles.css`: Custom CSS for consistent UI
- `schema.sql`: Database schema
- `portfolio.db`: SQLite database

## Usage

- Register and log in to your account.
- Add assets by entering their symbol, type, quantity, and average buy price.
- View and manage assets through the dashboard.
- Use the "Sell" button to reduce quantity and realize profit/loss.
- Check transaction history for a log of buy and sell actions.

