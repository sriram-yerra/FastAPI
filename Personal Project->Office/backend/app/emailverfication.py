from app.auth import hash_password, verified_password, create_acess_token
import random, smtplib
from sqlmodel import SQLModel, create_engine, Session, select, delete
from dotenv import load_dotenv
from email.message import EmailMessage
import smtplib
from email.mime.text import MIMEText
import random, os
from datetime import datetime, timedelta

load_dotenv()  # Reads .env file

SENDER_EMAIL = os.getenv("EMAIL_SENDER")
APP_PASSWORD = os.getenv("EMAIL_PASSWORD")

def generate_otp():
    return str(random.randint(1000, 9999))

def send_otp_email(receiver_email: str, otp: str):

    if not SENDER_EMAIL or not APP_PASSWORD:
        raise ValueError("Email credentials not configured")

    try:
        subject = "Your OTP Code"
        body = f"Your OTP is: {otp}. It expires in 2 minutes."

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = receiver_email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())

        print(f"OTP sent to {receiver_email}")

    except Exception as e:
        print("Email send failed:", e)
        raise

def save_otp(session, email, otp):
    session.exec(delete(EmailOTP).where(EmailOTP.email == email))
    expire = datetime.utcnow() + timedelta(minutes=2)
    otp_entry = EmailOTP(email=email, otp=otp, expires_at=expire, used=False)
    session.add(otp_entry)
    session.commit()
