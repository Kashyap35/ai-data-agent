import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "ai_agent.db")
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

# Create tables with bad names/unnamed columns
cur.execute('''
CREATE TABLE t1 (col1 TEXT, c2 INTEGER, "" TEXT);
''')

cur.execute('''
CREATE TABLE sales_data (id INTEGER PRIMARY KEY, prod TEXT, qty INTEGER, price REAL, sold_on TEXT);
''')

# Insert dirty / inconsistent data
cur.executemany('INSERT INTO t1 (col1,c2,"") VALUES (?,?,?)', [
    ("Alice", 10, "x"),
    ("Bob", None, ""),
    ("Charlie", 5, "z"),
])

cur.executemany('INSERT INTO sales_data (prod,qty,price,sold_on) VALUES (?,?,?,?)', [
    ("LED Bulb", 10, 120.0, "2024-01-03"),
    ("LED Strip", 5, 450.5, "2024-02-10"),
    ("Smart Lamp", 2, 1999.99, "2024-02-15"),
    ("LED Bulb", 7, 115.0, "2024-03-01"),
])

conn.commit()
conn.close()
print("Seeded DB at:", DB_FILE)
