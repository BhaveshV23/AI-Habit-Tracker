import sqlite3
import os

# Create directory to prevent OperationalError
os.makedirs("data", exist_ok=True)

conn = sqlite3.connect("data/habits.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS habits (
    date TEXT PRIMARY KEY,
    coding INTEGER,
    exercise INTEGER,
    reading INTEGER,
    study_hours REAL,
    sleep_hours REAL
)
""")

conn.commit()


def insert_data(date, coding, exercise, reading, study_hours, sleep_hours):
    cursor.execute("""
    INSERT OR REPLACE INTO habits VALUES (?, ?, ?, ?, ?, ?)
    """, (date, coding, exercise, reading, study_hours, sleep_hours))

    conn.commit()