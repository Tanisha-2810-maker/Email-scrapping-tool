from urllib.parse import urljoin


def get_contact_pages(base_url):
    paths = [
        "/contact",
        "/contact-us",
        "/about",
        "/team",
        "/careers",
        "/support",
    ]

    return [
        urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
        for path in paths
    ]
