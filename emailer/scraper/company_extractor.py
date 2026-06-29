from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


def get_company_name(url):
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; LeadExtractorPro/1.0)"},
            timeout=12,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.title and soup.title.text.strip():
            return " ".join(soup.title.text.split())
    except Exception:
        pass

    domain = urlparse(url).netloc.replace("www.", "")
    return domain or "Unknown Company"
