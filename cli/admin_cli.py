import logging
import getpass  # For secure password input
import sqlite3
import os
from database.db_connection import execute_query, fetch_query
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("admin_cli.log")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def get_db_connection():
    """Get database connection and confirm connection."""
    db_path = 'hotel_management.db'
    print(Fore.CYAN + "Database Path:" + Fore.YELLOW, os.path.abspath(db_path))  # Show the absolute path
    conn = sqlite3.connect(db_path)  # Adjust path if needed
    print(Fore.GREEN + "Connected to database:" + Fore.YELLOW, db_path)  # Confirm connection
    return conn

def admin_login(conn):
    """Admin login system."""
    print(Fore.BLUE + "\n🔒 Admin Login")
    username = input(Fore.CYAN + "Enter username: ")
    password = getpass.getpass(Fore.CYAN + "Enter password: ")  # Hides password input

    query = "SELECT * FROM admins WHERE username = ? AND password = ?;"
    admin = fetch_query(conn, query, (username, password))

    if admin:
        print(Fore.GREEN + f"✅ Welcome, {username}!")
        logger.info(f"Admin {username} logged in successfully.")
        return True
    else:
        print(Fore.RED + "❌ Invalid credentials! Please try again.")
        logger.warning(f"Failed login attempt for username: {username}.")
        return False

def add_room(conn):
    """Allow admin to add a new room."""
    room_number = input(Fore.CYAN + "Enter room number: ")
    room_type = input(Fore.CYAN + "Enter room type (e.g., Deluxe, Standard, Suite): ")
    
    try:
        price = float(input(Fore.CYAN + "Enter room price: "))
        query = "INSERT INTO rooms (room_number, room_type, price, is_available) VALUES (?, ?, ?, 1);"
        execute_query(conn, query, (room_number, room_type, price))
        print(Fore.GREEN + f"✅ Room {room_number} added successfully!")
        logger.info(f"Room added: {room_number}, Type: {room_type}, Price: {price}")
    except ValueError:
        print(Fore.RED + "⚠️ Invalid price format. Please enter a number.")
        logger.warning("Invalid price entered.")
    except Exception as e:
        print(Fore.RED + f"⚠️ Error: {e}")
        logger.error(f"Failed to add room: {e}")

def view_rooms(conn):
    """Display all available rooms."""
    rooms = fetch_query(conn, "SELECT * FROM rooms;")
    if rooms:
        print(Fore.BLUE + "\n🏨 Available Rooms:")
        for room in rooms:
            print(Fore.YELLOW + f"Room ID: {room[0]}, Number: {room[1]}, Type: {room[2]}, Price: ${room[3]}, Available: {'Yes' if room[4] else 'No'}")
        logger.info("Rooms displayed successfully.")
    else:
        print(Fore.RED + "⚠️ No rooms found.")
        logger.warning("No rooms found in database.")

def delete_room(conn):
    """Allow admin to delete a room."""
    room_number = input(Fore.CYAN + "Enter room number to delete: ")
    
    # Check if the room exists before attempting deletion
    check_query = "SELECT * FROM rooms WHERE room_number = ?;"
    room = fetch_query(conn, check_query, (room_number,))
    
    if room:
        try:
            query = "DELETE FROM rooms WHERE room_number = ?;"
            execute_query(conn, query, (room_number,))
            print(Fore.GREEN + f"✅ Room {room_number} deleted successfully!")
            logger.info(f"Room {room_number} deleted successfully from database.")
        except Exception as e:
            print(Fore.RED + f"⚠️ Error deleting room: {e}")
            logger.error(f"Failed to delete room {room_number}: {e}")
    else:
        print(Fore.RED + f"⚠️ Room {room_number} not found!")
        logger.warning(f"Attempted to delete non-existing room: {room_number}")

def admin_cli():
    """Admin panel CLI with login."""
    conn = get_db_connection()

    # Require login before showing menu
    if not admin_login(conn):
        print(Fore.RED + "🚫 Access Denied. Exiting...")
        logger.warning("Admin access denied due to failed login.")
        conn.close()
        return

    while True:
        print(Fore.GREEN + "\n1️⃣ Add Room")
        print(Fore.GREEN + "2️⃣ View Rooms")
        print(Fore.GREEN + "3️⃣ Delete Room")
        print(Fore.RED + "4️⃣ Exit")

        choice = input(Fore.CYAN + "Enter your choice: ")

        if choice == "1":
            add_room(conn)
        elif choice == "2":
            view_rooms(conn)
        elif choice == "3":
            delete_room(conn)
        elif choice == "4":
            print(Fore.MAGENTA + "👋 Exiting Admin CLI.")
            logger.info("Admin exited the CLI panel.")
            break
        else:
            print(Fore.RED + "❌ Invalid choice. Please try again.")
            logger.warning("Invalid menu choice entered.")

    conn.close()

if __name__ == "__main__":
    admin_cli()