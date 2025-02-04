import re
from datetime import datetime
from database.db_connection import fetch_query, execute_query, get_db_connection
from colorama import Fore, Style, init
import requests
from requests.auth import HTTPBasicAuth
import base64
import os
import sqlite3 

# Initialize colorama for Windows compatibility
init()

# Replace with your credentials from Safaricom Developer Portal
CONSUMER_KEY = "WMCSmuK7QTDVJmcE5afjdcpuGrnOqgC0MgjA9QGwUBcjciKF"
CONSUMER_SECRET = "OQdsS2rbTIK1ExAEoLXVc4MosHaeRft6O6IfLp0DWqfGqpOhp6D9JY891hW78EWq"
BUSINESS_SHORTCODE = "174379"  # Use your PayBill/Till number
PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
CALLBACK_URL = "https://dd5f-102-0-15-200.ngrok-free.app/daraja/callback"

def get_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET))
    access_token = response.json().get("access_token")
    return access_token

def generate_password():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(f"{BUSINESS_SHORTCODE}{PASSKEY}{timestamp}".encode()).decode()
    return password, timestamp

def stk_push(phone_number, amount):
    access_token = get_access_token()
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    password, timestamp = generate_password()

    payload = {
        "BusinessShortCode": BUSINESS_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": BUSINESS_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": "Order123",
        "TransactionDesc": "Payment for Order123"
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def is_valid_date(date_str):
    """Check if the input is a valid future date format (YYYY-MM-DD)."""
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        if date.date() >= datetime.today().date():
            return True
        else:
            print(Fore.RED + "❌ Date cannot be in the past. Please enter a future date." + Style.RESET_ALL)
            return False
    except ValueError:
        print(Fore.RED + "❌ Invalid date format. Please enter in YYYY-MM-DD format." + Style.RESET_ALL)
        return False  

def check_room_availability(conn):
    """Check available rooms for a given date range."""
    while True:
        print(Fore.CYAN + "\n🔍 Check Room Availability" + Style.RESET_ALL)
        check_in_date = input(Fore.YELLOW + "Enter check-in date (YYYY-MM-DD): " + Style.RESET_ALL).strip()
        if check_in_date == '6':  
            exit()  # Exit application
        if check_in_date == '0':  
            return  # Return to the main menu
        if not is_valid_date(check_in_date):
            continue  

        check_out_date = input(Fore.YELLOW + "Enter check-out date (YYYY-MM-DD): " + Style.RESET_ALL).strip()
        if check_out_date == '6':  
            exit()  
        if check_out_date == '0':  
            return  
        if not is_valid_date(check_out_date):
            continue  

        query = """
            SELECT room_id, room_number, room_type, price
            FROM rooms
            WHERE is_available = 1 AND room_id NOT IN (
                SELECT room_id FROM reservations
                WHERE NOT (check_out_date <= ? OR check_in_date >= ?)
            );
        """
        rooms = fetch_query(conn, query, (check_in_date, check_out_date))

        if rooms:
            print(Fore.GREEN + "\n✅ Available Rooms:" + Style.RESET_ALL)
            for idx, room in enumerate(rooms):
                print(Fore.BLUE + f"{idx + 1}. Room Number: {room[1]}, Type: {room[2]}, Price: ${room[3]}" + Style.RESET_ALL)
            return rooms  # Return the list of available rooms
        else:
            print(Fore.RED + "❌ No rooms available for the selected dates." + Style.RESET_ALL)
            return None  

def login(conn):
    """Login system (Required for booking or viewing reservations)."""
    print(Fore.CYAN + "\n🔑 User Login" + Style.RESET_ALL)
    username = input(Fore.YELLOW + "Enter username: " + Style.RESET_ALL)
    password = input(Fore.YELLOW + "Enter password: " + Style.RESET_ALL)

    query = "SELECT * FROM users WHERE username = ?;"
    user = fetch_query(conn, query, (username,))

    if user:
        try:
            stored_password = user[0]['password']
            if password == stored_password:
                print(Fore.GREEN + "✅ Login successful!" + Style.RESET_ALL)
                return user[0]['user_id']
            else:
                print(Fore.RED + "❌ Invalid username or password." + Style.RESET_ALL)
                return None
        except KeyError as e:
            print(Fore.RED + f"❌ Error: Missing expected data {e}. User data might be incomplete." + Style.RESET_ALL)
            return None
    else:
        print(Fore.RED + "❌ User not found." + Style.RESET_ALL)
        return None

def book_room(conn, user_id):
    """Handle booking a room after successful login."""
    print(Fore.CYAN + "\n🛏️ Book a Room" + Style.RESET_ALL)
    
    # Check room availability and display available rooms
    rooms = check_room_availability(conn)
    if not rooms:
        return  # No rooms available to book

    try:
        choice = int(input(Fore.YELLOW + "Enter the number of the room you want to book: " + Style.RESET_ALL))
        if 1 <= choice <= len(rooms):
            room_id = rooms[choice - 1][0]  # Get room_id from the selected room
            check_in_date = input(Fore.YELLOW + "Enter check-in date (YYYY-MM-DD): " + Style.RESET_ALL).strip()
            if not is_valid_date(check_in_date):
                return  

            check_out_date = input(Fore.YELLOW + "Enter check-out date (YYYY-MM-DD): " + Style.RESET_ALL).strip()
            if not is_valid_date(check_out_date):
                return  

            # Insert reservation into the database
            query = """
                INSERT INTO reservations (user_id, room_id, check_in_date, check_out_date)
                VALUES (?, ?, ?, ?);
            """
            execute_query(conn, query, (user_id, room_id, check_in_date, check_out_date))

            # Mark room as unavailable after booking
            query = "UPDATE rooms SET is_available = 0 WHERE room_id = ?;"
            execute_query(conn, query, (room_id,))

            print(Fore.GREEN + "✅ Room booked successfully!" + Style.RESET_ALL)

            # Prompt for phone number and initiate payment
            phone_number = input(Fore.YELLOW + "Enter your phone number (e.g., 254703647000): " + Style.RESET_ALL).strip()
            amount = rooms[choice - 1][3]  # Get the room price from the selected room

            # Initiate STK Push payment
            response = stk_push(phone_number, amount)
            if response.get('ResponseCode') == '0':
                print(Fore.GREEN + "✅ Payment initiated successfully. Please complete the payment on your phone." + Style.RESET_ALL)
            else:
                print(Fore.RED + "❌ Failed to initiate payment. Please try again." + Style.RESET_ALL)
        else:
            print(Fore.RED + "❌ Invalid choice. Please try again." + Style.RESET_ALL)
    except ValueError:
        print(Fore.RED + "⚠️ Invalid input. Please enter a number." + Style.RESET_ALL)

def view_reservations(conn, user_id):
    """View reservations for a logged-in user."""
    query = """
        SELECT r.room_number, res.check_in_date, res.check_out_date
        FROM reservations res
        JOIN rooms r ON res.room_id = r.room_id
        WHERE res.user_id = ?;
    """
    reservations = fetch_query(conn, query, (user_id,))
    if reservations:
        print(Fore.GREEN + "\n✅ Your Reservations:" + Style.RESET_ALL)
        for reservation in reservations:
            print(Fore.BLUE + f"Room Number: {reservation[0]}, Check-in: {reservation[1]}, Check-out: {reservation[2]}" + Style.RESET_ALL)
    else:
        print(Fore.RED + "❌ No reservations found." + Style.RESET_ALL)

def registered_user_menu(conn):
    """Registered user menu."""
    user_id = None  # Track if user is logged in
    
    while True:
        print(Fore.MAGENTA + "\n🌟 Welcome Back to the Hotel Booking System 🌟" + Style.RESET_ALL)
        print("1. Check Room Availability")
        
        if user_id:
            print("2. Book a Room")  # Only show 'Book a Room' if the user is logged in
            print("3. View My Reservations")  # Only show 'View My Reservations' if the user is logged in
        else:
            print("2. Login to Book a Room")
            print("3. View My Reservations")
        
        print("4. Logout")
        print("5. Exit")

        choice = input(Fore.YELLOW + "Enter your choice: " + Style.RESET_ALL).strip()

        if choice == "1":
            check_room_availability(conn)

        elif choice == "2":
            if user_id:
                # Proceed to book a room directly if the user is logged in
                book_room(conn, user_id)  # Pass the logged-in user_id to book a room
            else:
                # Login before booking a room
                user_id = login(conn)
        
        elif choice == "3":
            if user_id:
                # Proceed to view reservations directly if the user is logged in
                view_reservations(conn, user_id)  # Pass the logged-in user_id to view reservations
            else:
                # Login before viewing reservations
                user_id = login(conn)
        
        elif choice == "4":
            print(Fore.CYAN + "Logging out...\n" + Style.RESET_ALL)
            user_id = None  # Set user_id to None to log out

        elif choice == "5":
            print(Fore.RED + "Exiting... Goodbye!" + Style.RESET_ALL)
            exit()

        else:
            print(Fore.RED + "❌ Invalid choice. Please enter a number between 1 and 5." + Style.RESET_ALL)

if __name__ == "__main__":
    conn = get_db_connection()  # Get connection to hotel_management.db
    registered_user_menu(conn)
