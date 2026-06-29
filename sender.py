import os
import smtplib
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")


def _get_secret(key):
    value = os.getenv(key)
    if value:
        return value

    # Allows the same code to work on Streamlit Cloud when secrets are configured.
    try:
        import streamlit as st

        return st.secrets.get(key)
    except Exception:
        return None


def send_email(receiver, subject, body):
    email_address = _get_secret("EMAIL_ADDRESS")
    email_password = _get_secret("EMAIL_PASSWORD")

    if not email_address or not email_password:
        raise ValueError("EMAIL_ADDRESS or EMAIL_PASSWORD is missing. Add them in .env or Streamlit secrets.")

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = email_address
    msg["To"] = receiver

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
        server.starttls()
        server.login(email_address, email_password)
        server.send_message(msg)
