import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "leads.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_database():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT,
                email TEXT UNIQUE,
                phone TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS email_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient TEXT,
                subject TEXT,
                status TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def save_lead(company, email, phone=""):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO leads (company, email, phone) VALUES (?, ?, ?)",
            (company, email, phone),
        )
        conn.commit()


def get_all_leads():
    create_database()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, company, email, phone FROM leads ORDER BY id DESC")
        return cursor.fetchall()


def get_all_emails():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM leads ORDER BY email")
        return [row[0] for row in cursor.fetchall()]


def delete_lead(lead_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM leads WHERE id=?", (lead_id,))
        conn.commit()


def save_email_log(recipient, subject, status):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO email_logs (recipient, subject, status)
            VALUES (?, ?, ?)
            """,
            (recipient, subject, status),
        )
        conn.commit()


def get_email_logs(limit=None):
    create_database()
    query = "SELECT id, recipient, subject, status, sent_at FROM email_logs ORDER BY id DESC"
    if limit:
        query += " LIMIT ?"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (limit,) if limit else ())
        return cursor.fetchall()


def get_total_leads():
    create_database()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM leads")
        return cursor.fetchone()[0]


def get_total_sent():
    create_database()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM email_logs")
        return cursor.fetchone()[0]


def get_success_count():
    create_database()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM email_logs WHERE status='Sent'")
        return cursor.fetchone()[0]


def get_failed_count():
    create_database()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM email_logs WHERE status='Failed'")
        return cursor.fetchone()[0]
