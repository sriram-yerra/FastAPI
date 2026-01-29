from app.auth import hash_password, verified_password, create_acess_token
import random
import smtplib
from email.message import EmailMessage

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(to_email, otp):
    msg = EmailMessage()
    msg["Subject"] = "Your Registration OTP"
    msg["From"] = "noreply@itspe.co.in"
    msg["To"] = to_email
    msg.set_content(f"Your OTP is {otp}. Valid for 2 minutes.")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login("your_email@gmail.com", "app_password")
        server.send_message(msg)