import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 🔹 Configure your email credentials
EMAIL_SENDER = "belascohotel@gmail.com"  # Replace with your real email
EMAIL_PASSWORD = "pciu hmmg jtkm rasu"   # Replace with your app password (Not your real email password)
ADMIN_EMAIL = "berylberry788@gmail.com"  # Replace with the hotel admin's email

def send_email(subject, recipient_email, body, recipient_type="User"):
    """
    Generic function to send an email, with logging for clarity.
    """
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Establish connection with Gmail SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)  # Login using App Password
        server.sendmail(EMAIL_SENDER, recipient_email, msg.as_string())
        server.quit()

    except Exception as e:
        print(f"❌ Error sending email to {recipient_email} ({recipient_type}): {e}")
        return False
    return True

# ✅ Send reservation confirmation email
def send_reservation_confirmation(user_email, username, reservation_details):
    subject = "Hotel Reservation Confirmation"
    body = f"""
    Hello {username},

    Your reservation has been successfully confirmed! 🎉

    📌 Reservation Details:
    {reservation_details}

    Thank you for choosing our hotel! 🏨
    """

    # Send to user
    user_sent = send_email(subject, user_email, body, "User")
    
    # Send to admin
    admin_sent = send_email(subject, ADMIN_EMAIL, f"Admin Notification:\n{username} made a new reservation.\n{reservation_details}", "Admin")
    
    # Only log success for user email
    if user_sent:
        print("✅ Reservation confirmation sent successfully to user.")
    if admin_sent:
        print("✅ Admin notified of new reservation.")

# ✅ Send cancellation notification email
def send_cancellation_notification(user_email, username, reservation_details):
    subject = "Hotel Reservation Cancellation"
    body = f"""
    Hello {username},

    Your reservation has been cancelled. ❌

    📌 Cancelled Reservation Details:
    {reservation_details}

    If this was a mistake, you can book again anytime. 😊
    """

    # Send to user
    user_sent = send_email(subject, user_email, body, "User")
    
    # Send to admin
    admin_sent = send_email(subject, ADMIN_EMAIL, f"Admin Notification:\n{username} cancelled their reservation.\n{reservation_details}", "Admin")
    
    # Only log success for user email
    if user_sent:
        print("✅ Reservation cancellation notification sent successfully to user.")
    if admin_sent:
        print("✅ Admin notified of cancellation.")

# ✅ Send booking confirmation email (can be used as an example for booking related notifications)
def send_booking_email(user_email, username, room_type, check_in_date, check_out_date):
    subject = "Hotel Booking Confirmation"
    body = f"""
    Hello {username},

    Your booking has been successfully confirmed! 🎉

    📌 Booking Details:
    Room: {room_type}
    Check-in: {check_in_date}
    Check-out: {check_out_date}

    Thank you for choosing our hotel! 🏨
    """

    # Send to user
    user_sent = send_email(subject, user_email, body, "User")
    
    # Send to admin
    admin_sent = send_email(subject, ADMIN_EMAIL, f"Admin Notification:\n{username} made a new booking.\n{room_type} from {check_in_date} to {check_out_date}", "Admin")
    
    # Only log success for user email
    
    if admin_sent:
        print("✅ The management has been notified of new booking.")

# ✅ Send welcome email (for new users)
def send_welcome_email(user_email, username):
    subject = "Welcome to Our Hotel!"
    body = f"""
    Hello {username},

    Welcome to our hotel! 🎉

    We're excited to have you with us. If you have any questions or need assistance, feel free to reach out.

    Looking forward to serving you soon! 🏨
    """

    # Send only to user (not admin)
    user_sent = send_email(subject, user_email, body, "User")
    
    # Only log success for user email
    if user_sent:
        print("✅ check your email for confirmation.")

if __name__ == "__main__":
    print("Running test emails...")
    
    # Running all test cases
    send_reservation_confirmation("testuser@example.com", "Test User", "Deluxe Room - Ocean View, Check-in: 2025-02-01, Check-out: 2025-02-07")
    send_cancellation_notification("testuser@example.com", "Test User", "Deluxe Room - Ocean View, Check-in: 2025-02-01, Check-out: 2025-02-07")
    send_booking_email("testuser@example.com", "Test User", "Deluxe Room - Ocean View", "2025-02-01", "2025-02-07")
    send_welcome_email("testuser@example.com", "Test User")

    print("Test emails completed.")
