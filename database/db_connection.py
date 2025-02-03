import sqlite3
import os

# Set correct database path dynamically
DATABASE_NAME = os.path.join(os.path.dirname(__file__), "hotel_connection.db")

def get_db_connection():
    """Establish and return a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        conn.row_factory = sqlite3.Row  # Access columns by name
        return conn
    except sqlite3.Error as e:
        print(f"❌ Database connection error: {e}")
        return None
def execute_query(conn, query, params=()):
    """Execute a query that modifies the database (INSERT, UPDATE, DELETE)."""
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid  # Return the last inserted row ID (useful for user/booking IDs)
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}\nQuery: {query}\nParams: {params}")
    finally:
        if cursor:
            cursor.close()

def fetch_query(conn, query, params=()):
    """Execute a SELECT query and return results."""
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        return results
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}\nQuery: {query}\nParams: {params}")
        return []
    finally:
        if cursor:
            cursor.close()

def create_tables():
    """Create necessary tables if they do not exist."""
    conn = get_db_connection()
    if not conn:
        return  # Exit if connection fails

    queries = [
        """CREATE TABLE IF NOT EXISTS rooms (
            room_id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT NOT NULL UNIQUE,
            room_type TEXT NOT NULL,
            price REAL NOT NULL,
            is_available INTEGER DEFAULT 1
        );""",
        """CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            is_admin INTEGER DEFAULT 0
        );""",
        """CREATE TABLE IF NOT EXISTS reservations (
            reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            room_id INTEGER NOT NULL,
            check_in_date TEXT NOT NULL,
            check_out_date TEXT NOT NULL,
            status TEXT DEFAULT 'confirmed',
            UNIQUE(room_id, check_in_date),  -- Prevents double booking of same room on same date
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (room_id) REFERENCES rooms (room_id)
        );"""
    ]
    
    try:
        for query in queries:
            execute_query(conn, query)
        print("✅ Database tables ensured.")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
    finally:
        conn.close()

# Run table creation when this script is executed
if __name__ == "__main__":
    create_tables()
