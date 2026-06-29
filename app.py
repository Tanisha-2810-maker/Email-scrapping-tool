from pathlib import Path
import re
from urllib.parse import urlparse

import pandas as pd
import streamlit as st

from db_manager import (
    create_database,
    delete_lead,
    get_all_leads,
    get_email_logs,
    get_failed_count,
    get_success_count,
    get_total_leads,
    get_total_sent,
    save_email_log,
    save_lead,
)
from emailer.sender import send_email
from scraper.company_extractor import get_company_name
from scraper.contact_page_finder import get_contact_pages
from scraper.email_extractor import extract_emails
from scraper.website_scraper import get_pages
from templates import outreach_template
from verifier.hunter_verifier import verify_email

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

VALID_VERIFICATION_STATUSES = {"valid", "accept_all", "webmail", "unknown", "not_configured"}


def normalize_url(url: str) -> str:
    """Return a usable URL even when the user enters example.com."""
    url = (url or "").strip()
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url.rstrip("/")


def is_valid_email(email: str) -> bool:
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.match(pattern, email or "") is not None


def extract_and_verify(website: str):
    """Extract emails from multiple likely pages and return verified/unverified rows."""
    website = normalize_url(website)
    pages = list(dict.fromkeys(get_pages(website) + get_contact_pages(website)))

    all_emails = []
    for page in pages:
        all_emails.extend(extract_emails(page))

    all_emails = sorted(set(all_emails))

    # Optional JavaScript fallback. App still works if Playwright is not installed.
    if not all_emails:
        try:
            from scraper.dynamic_scraper import get_dynamic_html

            html = get_dynamic_html(website)
            all_emails = sorted(set(extract_emails(html, from_html=True)))
        except Exception:
            all_emails = []

    company = get_company_name(website)
    rows = []

    for email in all_emails:
        if not is_valid_email(email):
            continue

        verification = verify_email(email)
        status = verification.get("status", "unknown") if verification else "unknown"
        score = verification.get("score", "") if verification else ""

        if status in VALID_VERIFICATION_STATUSES:
            rows.append(
                {
                    "Website": website,
                    "Company": company,
                    "Email": email,
                    "Verification": "Not verified" if status == "not_configured" else status,
                    "Score": score,
                }
            )
            save_lead(company, email, "")

    return company, all_emails, rows


create_database()

st.set_page_config(page_title="Lead Extractor Pro", page_icon="🚀", layout="wide")

with st.sidebar:
    st.title("🚀 Lead Extractor")
    st.markdown("---")
    st.write("### Features")
    st.write("✅ Company detection")
    st.write("✅ Public email extraction")
    st.write("✅ Lead database")
    st.write("✅ Email campaigns")
    st.write("✅ Activity logs")
    st.write("✅ CSV export")
    st.markdown("---")
    st.info("Add EMAIL_ADDRESS and EMAIL_PASSWORD in .env before sending emails.")

st.title("🚀 Lead Extractor Pro")
st.caption("Extract public business emails, save leads, and send outreach campaigns from one dashboard.")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Dashboard",
    "🔍 Lead Discovery",
    "📂 Leads",
    "📧 Campaigns",
])

with tab1:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📂 Total Leads", get_total_leads())
    col2.metric("📧 Emails Sent", get_total_sent())
    col3.metric("✅ Success", get_success_count())
    col4.metric("❌ Failed", get_failed_count())

    logs = get_email_logs(limit=5)
    if logs:
        st.subheader("Recent Email Activity")
        st.dataframe(
            pd.DataFrame(logs, columns=["ID", "Recipient", "Subject", "Status", "Sent At"]),
            use_container_width=True,
            hide_index=True,
        )

with tab2:
    st.markdown("### Extract Public Email Addresses From Any Website")
    website = st.text_input("🌐 Website URL", placeholder="example.com or https://example.com")

    if st.button("🔍 Extract Emails", type="primary"):
        if not website.strip():
            st.warning("Please enter a website URL.")
        else:
            website = normalize_url(website)
            with st.spinner("Searching pages and extracting emails..."):
                company, raw_emails, rows = extract_and_verify(website)

            if not rows:
                st.warning(
                    "No usable email addresses were found. The site may hide emails, block scraping, "
                    "or only expose contact forms/social links."
                )
            else:
                df = pd.DataFrame(rows)
                csv_path = DATA_DIR / "leads.csv"
                df.to_csv(csv_path, index=False)

                col1, col2, col3 = st.columns(3)
                col1.metric("Emails Found", len(raw_emails))
                col2.metric("Saved Leads", len(rows))
                col3.metric("Company", company[:30] if company else urlparse(website).netloc)

                st.success(f"{len(rows)} email(s) found and saved for {company}.")
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.download_button(
                    "📥 Download Results as CSV",
                    df.to_csv(index=False).encode("utf-8"),
                    "emails.csv",
                    "text/csv",
                )

with tab3:
    st.subheader("📂 Saved Leads Database")
    search = st.text_input("🔍 Search Leads", placeholder="Search by company or email...")
    leads = get_all_leads()

    if search:
        leads = [lead for lead in leads if search.lower() in str(lead).lower()]

    if not leads:
        st.warning("No leads found.")
    else:
        df = pd.DataFrame(leads, columns=["ID", "Company", "Email", "Phone"])
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.subheader("🗑️ Delete Lead")
        selected_id = st.selectbox("Select Lead ID", df["ID"].tolist())
        if st.button("Delete Selected Lead"):
            delete_lead(selected_id)
            st.success("Lead deleted successfully!")
            st.rerun()

with tab4:
    st.subheader("📧 Send Email Campaign")
    saved_emails = sorted(set(lead[2] for lead in get_all_leads() if is_valid_email(lead[2])))

    if not saved_emails:
        st.info("No saved leads yet. Extract emails first from the Lead Discovery tab.")
    else:
        receivers = st.multiselect("Select Recipients", saved_emails)
        default_subject, default_body = outreach_template()
        subject = st.text_input("Subject", value=default_subject)
        body = st.text_area("Message", value=default_body, height=220)
        schedule_followup = st.checkbox("Schedule a follow-up after sending", value=False)
        followup_hours = st.number_input("Follow-up after how many hours?", min_value=1, value=24) if schedule_followup else None

        if st.button("Send Campaign", type="primary"):
            if not receivers:
                st.warning("Please select at least one recipient.")
            elif not subject.strip() or not body.strip():
                st.warning("Subject and message cannot be empty.")
            else:
                success_count = 0
                failed_count = 0
                progress_bar = st.progress(0)
                status_text = st.empty()

                for index, receiver in enumerate(receivers, start=1):
                    status_text.text(f"Sending email {index} of {len(receivers)}: {receiver}")
                    try:
                        send_email(receiver, subject, body)
                        save_email_log(receiver, subject, "Sent")
                        success_count += 1

                        if schedule_followup:
                            from scheduler.followup_scheduler import schedule_followups

                            schedule_followups(receiver, delay_hours=int(followup_hours))
                    except Exception as exc:
                        failed_count += 1
                        save_email_log(receiver, subject, "Failed")
                        st.error(f"Failed for {receiver}: {exc}")

                    progress_bar.progress(index / len(receivers))

                status_text.empty()
                progress_bar.empty()
                st.success(f"Campaign completed. Sent: {success_count}, Failed: {failed_count}")

    st.divider()
    st.subheader("📊 Email Logs")
    logs = get_email_logs()
    if not logs:
        st.warning("No email logs found.")
    else:
        df_logs = pd.DataFrame(logs, columns=["ID", "Recipient", "Subject", "Status", "Sent At"])
        st.dataframe(df_logs, use_container_width=True, hide_index=True)

st.caption("Made with ❤️ by Tanisha")
