from flask import Flask, request, jsonify
import sqlite3
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

# Safaricom Daraja API Credentials
CONSUMER_KEY = "WMCSmuK7QTDVJmcE5afjdcpuGrnOqgC0MgjA9QGwUBcjciKF"
CONSUMER_SECRET = "OQdsS2rbTIK1ExAEoLXVc4MosHaeRft6O6IfLp0DWqfGqpOhp6D9JY891hW78EWq"
BASE_URL = "https://sandbox.safaricom.co.ke"

# Initialize the database
def init_db():
    with sqlite3.connect("transactions.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            amount REAL,
                            phone TEXT,
                            transaction_id TEXT UNIQUE,
                            transaction_date TEXT
                        )''')
        conn.commit()

# Function to get access token
def get_access_token():
    url = f"{BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET))
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        return None

@app.route("/", methods=["GET"])
def home():
    return "Flask Server is Running! 🚀"

@app.route("/daraja/callback", methods=["POST"])
def mpesa_callback():
    data = request.json  # Get the JSON response from Safaricom
    print("Received M-Pesa Callback:", data)  # Log it for debugging

    try:
        # Extract transaction result
        result_code = data["Body"]["stkCallback"]["ResultCode"]

        if result_code == 0:
            print("✅ Payment Successful")
            metadata = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"]

            amount = next(item["Value"] for item in metadata if item["Name"] == "Amount")
            phone = next(item["Value"] for item in metadata if item["Name"] == "PhoneNumber")
            transaction_id = next(item["Value"] for item in metadata if item["Name"] == "MpesaReceiptNumber")
            transaction_date = next(item["Value"] for item in metadata if item["Name"] == "TransactionDate")

            # Save transaction to database
            with sqlite3.connect("transactions.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO transactions (amount, phone, transaction_id, transaction_date) VALUES (?, ?, ?, ?)", 
                               (amount, phone, transaction_id, transaction_date))
                conn.commit()

            print(f"💰 Amount: {amount}, 📞 Phone: {phone}")
            return jsonify({"message": "Payment Successful", "amount": amount, "phone": phone}), 200
        else:
            print("❌ Payment Failed")
            return jsonify({"message": "Payment Failed"}), 400
    except KeyError:
        print("⚠️ Error: Missing expected fields in callback data")
        return jsonify({"message": "Invalid callback data"}), 400
    except sqlite3.IntegrityError:
        print("⚠️ Duplicate Transaction ID detected")
        return jsonify({"message": "Duplicate transaction detected"}), 400

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)