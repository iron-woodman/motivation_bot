import sqlite3
import logging

DATABASE_NAME = "quotes.db"

def create_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    return conn

def create_tables():
    conn = create_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            scheduled_time TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quotes (
            quote_id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def get_quotes():
    conn = create_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT text FROM quotes")
    quotes = [row[0] for row in cursor.fetchall()]
    conn.close()
    return quotes

def add_quote(quote):
    conn = create_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO quotes (text) VALUES (?)", (quote,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        logging.error(f"Error adding quote: {e}")
        return False
    finally:
        conn.close()

def add_quote_from_file(file_path):
    conn = create_db_connection()
    cursor = conn.cursor()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            quotes = [line.strip() for line in f if line.strip()]
            cursor.executemany("INSERT INTO quotes (text) VALUES (?)", [(quote,) for quote in quotes])
            conn.commit()
        return True
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return False
    except sqlite3.Error as e:
        logging.error(f"Error adding quotes from file: {e}")
        return False
    finally:
        conn.close()

def get_scheduled_time(user_id):
  conn = create_db_connection()
  cursor = conn.cursor()
  cursor.execute("SELECT scheduled_time FROM users WHERE user_id = ?", (user_id,))
  result = cursor.fetchone()
  conn.close()
  if result:
    return result[0]
  else:
    return None

def set_scheduled_time(user_id, time_str):
    conn = create_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR REPLACE INTO users (user_id, scheduled_time) VALUES (?, ?)", (user_id, time_str))
        conn.commit()
        return True
    except sqlite3.Error as e:
        logging.error(f"Error setting schedule time: {e}")
        return False
    finally:
        conn.close()
