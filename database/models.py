import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "hotel.db")

def get_db_connection():
    """Establish a connection to the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Create database tables if they do not exist and insert default rooms."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
            is_admin INTEGER DEFAULT 0
        );
    """)

    # Create rooms table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            room_id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT NOT NULL UNIQUE,
            room_type TEXT NOT NULL,
            price REAL NOT NULL,
            is_available INTEGER DEFAULT 1
        );
    """)

    # Create reservations table with UNIQUE constraint
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            room_id INTEGER NOT NULL,
            check_in_date TEXT NOT NULL,
            check_out_date TEXT NOT NULL,
            status TEXT NOT NULL,
            UNIQUE(room_id, check_in_date),  -- Prevents double booking of same room on same date
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (room_id) REFERENCES rooms(room_id)
        );
    """)

    # Insert default rooms only if table is empty
    cursor.execute("SELECT COUNT(*) FROM rooms")
    if cursor.fetchone()[0] == 0:
        rooms_data = [
            ('101', 'Deluxe', 1000, 1),
            ('102', 'Deluxe', 1000, 1),
            ('103', 'Deluxe', 1000, 1),
            ('201', 'Standard', 3000, 1),
            ('202', 'Standard', 3000, 1),
            ('203', 'Standard', 3000, 1),
            ('301', 'Suite', 5000, 1),
            ('302', 'Suite', 5000, 1),
            ('303', 'Suite', 5000, 1),
            ('223', 'Suite', 5000, 2),
        ]
        cursor.executemany("INSERT INTO rooms (room_number, room_type, price, is_available) VALUES (?, ?, ?, ?);", rooms_data)
        print("✅ Default rooms inserted.")

    conn.commit()
    conn.close()
    print("✅ Database setup complete.")

# Run table creation when this script is executed
if __name__ == "__main__":
    create_tables()
