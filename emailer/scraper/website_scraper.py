from urllib.parse import urljoin


def get_pages(base_url):
    paths = [
        "/",
        "/about",
        "/about-us",
        "/contact",
        "/contact-us",
        "/team",
        "/company",
        "/support",
        "/get-in-touch",
        "/community",
    ]
    return [urljoin(base_url.rstrip("/") + "/", path.lstrip("/")) for path in paths]
