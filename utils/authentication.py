
from database.db_connection import get_db_connection, fetch_query, execute_query
from colorama import Fore, Style, init

# Initialize colorama for Windows compatibility
init(autoreset=True)

def login(conn):
    """Login system."""
    username = input(Fore.CYAN + "🔹 Enter username: ")
    password = input(Fore.CYAN + "🔹 Enter password: ")

    query = "SELECT * FROM users WHERE username = ? AND password = ?;"
    user = fetch_query(conn, query, (username, password))

    if user:
        print(Fore.GREEN + "✅ Login successful!")
        print(Fore.YELLOW + f"🎉 Welcome, {user[0][1]}! You are now logged in.")
    else:
        print(Fore.RED + "❌ Invalid username or password.")

def register_user(conn):
    """Register a new user."""
    username = input(Fore.CYAN + "🔹 Enter username: ")
    password = input(Fore.CYAN + "🔹 Enter password: ")
    email = input(Fore.CYAN + "🔹 Enter email: ")

    query = "INSERT INTO users (username, password, email) VALUES (?, ?, ?);"
    execute_query(conn, query, (username, password, email))

    print(Fore.GREEN + "✅ Registration successful!")
    print(Fore.YELLOW + "📩 Check your email for a confirmation message.")

def main():
    """Main function to handle authentication system."""
    print(Fore.MAGENTA + "🌟 Welcome to the Authentication System! 🌟")

    # Establish database connection
    conn = get_db_connection()

    if conn is None:
        print(Fore.RED + "❌ Failed to connect to the database.")
        return

    while True:
        print(Fore.BLUE + "\n📌 Menu:")
        print(Fore.CYAN + "1️⃣  Login")
        print(Fore.CYAN + "2️⃣  Register")
        print(Fore.YELLOW + "🚪 Press Enter  to Exit")
        
        choice = input(Fore.WHITE + "➡️  Enter your choice: ")

        if choice == "1":
            print(Fore.MAGENTA + "\n🔑 --- Login ---")
            login(conn)
        elif choice == "2":
            print(Fore.MAGENTA + "\n📝 --- Register User ---")
            register_user(conn)
        elif choice == "0" or choice == "1" or choice == "":
            print(Fore.RED + "👋 Exiting the system. Goodbye!")
            conn.close()  # Ensure database connection is closed
            break  # Exit the loop and the program
        else:
            print(Fore.RED + "❌ Invalid choice. Please enter 1, 2, or 0.")

if __name__ == "__main__":
    main()
