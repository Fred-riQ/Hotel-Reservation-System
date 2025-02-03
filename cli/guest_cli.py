import re
from datetime import datetime
from database.db_connection import fetch_query, execute_query, get_db_connection
from colorama import Fore, Style, init
import requests
from requests.auth import HTTPBasicAuth
import base64
import os
import sqlite3
from utils.email_notifications import send_welcome_email, send_booking_email

# Initialize colorama for Windows compatibility
init()

# Replace with your credentials from Safaricom Developer Portal
CONSUMER_KEY = "WMCSmuK7QTDVJmcE5afjdcpuGrnOqgC0MgjA9QGwUBcjciKF"
CONSUMER_SECRET = "OQdsS2rbTIK1ExAEoLXVc4MosHaeRft6O6IfLp0DWqfGqpOhp6D9JY891hW78EWq"
BUSINESS_SHORTCODE = "174379"  # Use your PayBill/Till number
PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
CALLBACK_URL = "https://8c76-102-0-15-200.ngrok-free.app/daraja/callback"

def get_access_token():
    """Fetch the access token from Safaricom API."""
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET))
    access_token = response.json().get("access_token")
    return access_token

def generate_password():
    """Generate the password for STK push."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(f"{BUSINESS_SHORTCODE}{PASSKEY}{timestamp}".encode()).decode()
    return password, timestamp

def stk_push(phone_number, amount):
    """Initiate STK push payment."""
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

def register_user(conn):
    """Register a new user and send a confirmation email."""
    print("\n\033[1;34m🔹 Register a New Account\033[0m")
    username = input("Enter your username: ").strip()
    email = input("Enter your email: ").strip()
    password = input("Enter a password: ").strip()  # Store as plain text

    # Check if email already exists
    existing_user = fetch_query(conn, "SELECT user_id FROM users WHERE email = ?;", (email,))
    if existing_user:
        print("\033[1;31m❌ This email is already registered. Try logging in.\033[0m")
        return

    # Insert user into the database WITHOUT hashing the password
    query = "INSERT INTO users (username, email, password) VALUES (?, ?, ?);"
    execute_query(conn, query, (username, email, password))  # Store plain text password

    # Fetch the newly registered user ID
    user = fetch_query(conn, "SELECT user_id FROM users WHERE email = ?;", (email,))
    
    if user:
        user_id = user[0]["user_id"]
        print(f"\033[1;32m🎉 Welcome, {username}! Registration successful. You are now logged in.\033[0m")

        # ✅ Send welcome email
        send_welcome_email(email, username)

        registered_user_menu(conn, user_id)  # Redirect to user menu
    else:
        print("\033[1;31m❌ Registration failed. Please try again.\033[0m")

def login_user(conn):
    """Allow users to log in."""
    print("\n\033[1;34m🔐 Login to Your Account\033[0m")
    email = input("Enter your email: ").strip()
    password = input("Enter your password: ").strip()  # Compare plain text password

    # Verify user credentials WITHOUT hashing
    query = "SELECT user_id, username FROM users WHERE email = ? AND password = ?;"
    user = fetch_query(conn, query, (email, password))  # Compare plain text password

    if user:
        user_id, username = user[0]["user_id"], user[0]["username"]
        print(f"\033[1;32m✅ Welcome back, {username}!\033[0m")
        registered_user_menu(conn, user_id)  # Redirect to user menu
    else:
        print("\033[1;31m❌ Invalid email or password.\033[0m")

def view_my_reservations(conn, user_id):
    """View reservations for a logged-in user."""
    query = """
        SELECT r.reservation_id, rm.room_number, rm.room_type, r.check_in_date, r.check_out_date, r.status
        FROM reservations r
        JOIN rooms rm ON r.room_id = rm.room_id
        WHERE r.user_id = ?;
    """
    reservations = fetch_query(conn, query, (user_id,))

    if reservations:
        print("\n\033[1;36m📋 Your Reservations:\033[0m")
        for res in reservations:
            print(f"Reservation ID: {res['reservation_id']}, Room: {res['room_number']} ({res['room_type']}), Check-in: {res['check_in_date']}, Check-out: {res['check_out_date']}, Status: {res['status']}")
    else:
        print("\033[1;31m❌ You have no reservations.\033[0m")

def book_room(conn, user_id):
    """Allow registered users to book a room and send a confirmation email."""
    try:
        while True:
            check_in_date = input("Enter check-in date (YYYY-MM-DD): ").strip()
            if not is_valid_date(check_in_date):
                continue  # Retry if the date is not valid

            check_out_date = input("Enter check-out date (YYYY-MM-DD): ").strip()
            if not is_valid_date(check_out_date):
                continue  # Retry if the date is not valid

            # Check if the dates make sense (check-out cannot be before check-in)
            check_in_date = datetime.strptime(check_in_date, '%Y-%m-%d')
            check_out_date = datetime.strptime(check_out_date, '%Y-%m-%d')

            if check_out_date <= check_in_date:
                print(Fore.RED + "❌ Check-out date must be later than check-in date." + Style.RESET_ALL)
                continue

            break  # If dates are valid, break out of the loop

        query = """
            SELECT room_id, room_number, room_type, price
            FROM rooms
            WHERE is_available = 1;
        """
        available_rooms = fetch_query(conn, query)

        if available_rooms:
            print("\n\033[1;36m🏨 Available Rooms:\033[0m")
            for room in available_rooms:
                print(f"Room ID: {room['room_id']}, Number: {room['room_number']}, Type: {room['room_type']}, Price: ${room['price']}")

            try:
                room_id = int(input("Enter Room ID to book: ").strip())

                room_check = fetch_query(conn, "SELECT room_number, room_type, price FROM rooms WHERE room_id = ? AND is_available = 1;", (room_id,))
                if not room_check:
                    print("\033[1;31m❌ Invalid Room ID or Room is not available.\033[0m")
                    return

                room_info = f"Room {room_check[0]['room_number']} ({room_check[0]['room_type']})"

                # Prompt for phone number
                phone_number = input(Fore.YELLOW + "Enter your phone number (e.g., 254703647000): " + Style.RESET_ALL).strip()

                # Insert reservation into the database
                query = """
                    INSERT INTO reservations (user_id, room_id, check_in_date, check_out_date, status)
                    VALUES (?, ?, ?, ?, 'confirmed');
                """
                reservation_id = execute_query(conn, query, (user_id, room_id, check_in_date.strftime('%Y-%m-%d'), check_out_date.strftime('%Y-%m-%d')))

                if reservation_id:
                    execute_query(conn, "UPDATE rooms SET is_available = 0 WHERE room_id = ?;", (room_id,))

                    user = fetch_query(conn, "SELECT email, username FROM users WHERE user_id = ?;", (user_id,))
                    
                    if user:
                        user_email, username = user[0]["email"], user[0]["username"]
                        send_booking_email(user_email, username, room_info, check_in_date.strftime('%Y-%m-%d'), check_out_date.strftime('%Y-%m-%d'))
                        print("\033[1;32m✅ Booking successful! Check your email for confirmation.\033[0m")

                        # Initiate STK Push payment
                        amount = room_check[0]["price"]  # Get the room price
                        response = stk_push(phone_number, amount)
                        if response.get('ResponseCode') == '0':
                            print(Fore.GREEN + "✅ Payment initiated successfully. Please complete the payment on your phone." + Style.RESET_ALL)
                        else:
                            print(Fore.RED + "❌ Failed to initiate payment. Please try again." + Style.RESET_ALL)
                    else:
                        print("\033[1;31m❌ User not found. Unable to send email confirmation.\033[0m")
                else:
                    print("\033[1;31m❌ Booking failed. Please try again.\033[0m")

            except ValueError:
                print("\033[1;31m❌ Invalid input. Please enter a numerical Room ID.\033[0m")
        else:
            print("\033[1;31m❌ No available rooms at the moment.\033[0m")

    except Exception as e:
        print(f"\033[1;31m❌ Error: {e}\033[0m")

def registered_user_menu(conn, user_id):
    """Menu for registered users."""
    while True:
        print("\n\033[1;36m👤 You can proceed to:\033[0m")
        print("1. Book a Room ")
        print("2. View My Reservations")
        print("3. Logout")
        print("4. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            book_room(conn, user_id)
        elif choice == "2":
            view_my_reservations(conn, user_id)
        elif choice == "3":
            print("\033[1;33mLogging out...\n\033[0m")
            return  # Exit to main menu
        elif choice == "4":
            print("\033[1;33mExiting... Goodbye!\033[0m")
            exit()
        else:
            print("\033[1;31mInvalid choice. Please try again.\033[0m")

def main():
    conn = get_db_connection()

    while True:
        print("\n\033[1;34m🔑 Welcome to the Hotel Booking System\033[0m")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            register_user(conn)
        elif choice == "2":
            login_user(conn)
        elif choice == "3":
            print("\033[1;33mGoodbye! 👋\033[0m")
            break
        else:
            print("\033[1;31mInvalid choice. Please try again.\033[0m")

if __name__ == "__main__":
    main()