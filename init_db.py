
import sqlite3

DB_NAME = "weather.db"

conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS weather (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    avg_temp REAL,
    min_temp REAL,
    max_temp REAL
)
""")

conn.commit()
conn.close()

print("✅ Database initialized")

import sqlite3

DB_NAME = "weather.db"

conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS weather (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    avg_temp REAL,
    min_temp REAL,
    max_temp REAL
)
""")

conn.commit()
conn.close()

print("✅ Database initialized")

