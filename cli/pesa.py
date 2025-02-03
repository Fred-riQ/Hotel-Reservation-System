import requests
from requests.auth import HTTPBasicAuth



# Replace with your credentials from Safaricom Developer Portal
CONSUMER_KEY = "WMCSmuK7QTDVJmcE5afjdcpuGrnOqgC0MgjA9QGwUBcjciKF"
CONSUMER_SECRET = "OQdsS2rbTIK1ExAEoLXVc4MosHaeRft6O6IfLp0DWqfGqpOhp6D9JY891hW78EWq"

def get_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET))
    access_token = response.json().get("access_token")
    return access_token

# Test the function
print(get_access_token())

import base64
from datetime import datetime

# Replace with your business details
BUSINESS_SHORTCODE = "174379"  # Use your PayBill/Till number
PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
CALLBACK_URL = "https://8c76-102-0-15-200.ngrok-free.app/daraja/callback"

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
    # Example usage
phone_number = "254703647000"  # Customer's phone number
amount = 1  # Amount to charge
response = stk_push(phone_number, amount)
print(response)