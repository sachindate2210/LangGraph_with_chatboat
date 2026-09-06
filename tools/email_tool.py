import os
import smtplib

from dotenv import load_dotenv
from email.message import EmailMessage

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("EMAIL_PASSWORD")


def send_email(receiver_email: str, body: str):

    msg = EmailMessage()

    msg["Subject"] = "AI Agent Result"

    msg["From"] = EMAIL

    msg["To"] = receiver_email

    msg.set_content(body)

    server = smtplib.SMTP(
        "smtp.gmail.com",
        587
    )

    server.starttls()

    server.login(EMAIL, PASSWORD)

    server.send_message(msg)

    server.quit()

    return "Email Sent Successfully"