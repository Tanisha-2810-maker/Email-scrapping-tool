import os
from pathlib import Path

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")


def _get_secret(key):
    value = os.getenv(key)
    if value:
        return value

    try:
        import streamlit as st

        return st.secrets.get(key)
    except Exception:
        return None


def verify_email(email):
    """Verify email with Hunter if HUNTER_API_KEY exists. Otherwise skip verification safely."""
    api_key = _get_secret("HUNTER_API_KEY")
    if not api_key:
        return {"status": "not_configured", "score": ""}

    try:
        response = requests.get(
            "https://api.hunter.io/v2/email-verifier",
            params={"email": email, "api_key": api_key},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json().get("data") or {}
        return {
            "status": data.get("status", "unknown"),
            "score": data.get("score", ""),
        }
    except Exception:
        return {"status": "unknown", "score": ""}
