-- Drop tables if they exist (for reset/testing)
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS assets;

-- Users table: stores registered user accounts
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL
);

-- Assets table: stores user portfolio entries
CREATE TABLE assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    asset_type TEXT CHECK(asset_type IN ('stock', 'crypto')) NOT NULL,
    quantity REAL NOT NULL,
    avg_buy_price REAL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
