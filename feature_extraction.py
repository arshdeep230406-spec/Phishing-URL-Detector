import re
from urllib.parse import urlparse


def extract_features(url):
    features = {}

    # URL length
    features["url_length"] = len(url)

    # Number of dots
    features["dot_count"] = url.count(".")

    # Number of hyphens
    features["hyphen_count"] = url.count("-")

    # Number of special characters
    features["special_char_count"] = len(
        re.findall(r"[@?&=%_]", url)
    )

    # @ symbol
    features["has_at_symbol"] = int("@" in url)

    # HTTPS
    features["uses_https"] = int(
        url.lower().startswith("https://")
    )

    # IP address
    features["has_ip"] = int(
        bool(
            re.search(
                r"https?://\d{1,3}(?:\.\d{1,3}){3}",
                url
            )
        )
    )

    # Domain
    try:
        domain = urlparse(url).netloc
    except Exception:
        domain = ""

    # Subdomain count
    features["subdomain_count"] = max(
        domain.count(".") - 1,
        0
    )

    # Suspicious keywords
    suspicious_words = [
        "login",
        "verify",
        "verification",
        "account",
        "secure",
        "update",
        "bank",
        "password",
        "signin",
        "confirm"
    ]

    features["suspicious_word_count"] = sum(
        word in url.lower()
        for word in suspicious_words
    )

    return features