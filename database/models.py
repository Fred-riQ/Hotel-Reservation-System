import sqlite3

def create_tables():
    """Create necessary tables in the database."""
    conn = sqlite3.connect('hotel_management.db')
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT 0  -- Use BOOLEAN for admin flag
        );
    """)

    # Create rooms table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            room_id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT NOT NULL UNIQUE,
            room_type TEXT NOT NULL,
            price REAL NOT NULL,
            is_available BOOLEAN DEFAULT 1  -- Use BOOLEAN for availability
        );
    """)

    # Create reservations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            room_id INTEGER NOT NULL,
            check_in_date DATE NOT NULL,
            check_out_date DATE NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (room_id) REFERENCES rooms (room_id)
        );
    """)

    conn.commit()
    conn.close()

# Call the function to create tables
create_tables()