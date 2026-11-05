"""SQLite connection boundary for the evaluation fixture."""
import sqlite3


def connect(path):
    connection = sqlite3.connect(path)
    connection.execute("CREATE TABLE IF NOT EXISTS orders (order_id TEXT PRIMARY KEY, status TEXT NOT NULL)")
    connection.commit()
    return connection
