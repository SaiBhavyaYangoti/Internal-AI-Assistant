import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")


def send_email(recipient: str, subject: str, body: str):
    """
    Sends a real email using Gmail SMTP.
    """

    if not SENDER_EMAIL or not APP_PASSWORD:
        raise ValueError("Email credentials not found in .env file")

    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)

    # Gmail SMTP Server
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SENDER_EMAIL, APP_PASSWORD)
        smtp.send_message(msg)
