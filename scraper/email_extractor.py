import re

import requests

EMAIL_PATTERN = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
BAD_WORDS = [
    "example",
    "test",
    "noreply",
    "no-reply",
    "localhost",
    "sample",
    "sentry",
    "wixpress",
]


def _clean_emails(emails):
    clean = []
    for email in set(emails):
        email = email.strip().strip(".,;:()[]{}<>'\"")
        if not any(word in email.lower() for word in BAD_WORDS):
            clean.append(email)
    return sorted(set(clean))


def extract_emails(url_or_html, from_html=False):
    try:
        html = url_or_html
        if not from_html:
            response = requests.get(
                url_or_html,
                headers={"User-Agent": "Mozilla/5.0 (compatible; LeadExtractorPro/1.0)"},
                timeout=12,
            )
            response.raise_for_status()
            html = response.text

        emails = re.findall(EMAIL_PATTERN, html or "")
        return _clean_emails(emails)
    except Exception:
        return []
