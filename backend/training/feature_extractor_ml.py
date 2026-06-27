"""
feature_extractor_ml.py

Fast offline feature extractor used ONLY for ML training.
No network requests.
"""

import ipaddress
from urllib.parse import urlparse
import math


SUSPICIOUS_KEYWORDS = {
    "login",
    "signin",
    "verify",
    "secure",
    "update",
    "account",
    "bank",
    "paypal",
    "amazon",
    "microsoft",
    "google",
    "apple",
    "netflix",
    "crypto",
    "wallet",
}


SUSPICIOUS_TLDS = {
    "xyz",
    "top",
    "club",
    "click",
    "gq",
    "tk",
    "cf",
    "ml",
    "ga",
    "work",
    "zip",
    "review",
}


def is_ip_address(hostname: str) -> bool:
    try:
        ipaddress.ip_address(hostname)
        return True
    except ValueError:
        return False


def shannon_entropy(text: str) -> float:
    if not text:
        return 0.0
    entropy = 0.0
    for c in set(text):
        p = text.count(c) / len(text)
        entropy -= p * math.log2(p)
    return entropy


def max_consecutive_characters(text: str) -> int:
    if not text:
        return 0

    longest = 1
    current = 1

    for i in range(1, len(text)):
        if text[i] == text[i - 1]:
            current += 1
            longest = max(longest, current)
        else:
            current = 1

    return longest


def extract_features(url: str) -> dict:
    parsed = urlparse(url)

    hostname = parsed.hostname or ""

    path = parsed.path or ""
    query = parsed.query or ""

    parts = hostname.split(".")

    tld = parts[-1].lower() if parts else ""

    keywords = url.lower()

    return {
        "url_length": len(url),
        "domain_length": len(hostname),
        "path_length": len(path),
        "query_length": len(query),
        "subdomain_count": max(len(parts) - 2, 0),
        "dot_count": url.count("."),
        "slash_count": url.count("/"),
        "hyphen_count": url.count("-"),
        "underscore_count": url.count("_"),
        "digit_count": sum(c.isdigit() for c in url),
        "letter_count": sum(c.isalpha() for c in url),
        "special_char_count": sum(c in "@?=&_%" for c in url),
        "query_parameter_count": query.count("&") + (1 if query else 0),
        "hostname_entropy": shannon_entropy(hostname),
        "max_repeated_characters": max_consecutive_characters(hostname),
        "keyword_count": sum(word in keywords for word in SUSPICIOUS_KEYWORDS),
        "https": int(parsed.scheme == "https"),
        "has_at_symbol": int("@" in url),
        "ip_url": int(is_ip_address(hostname)),
        "punycode": int(hostname.startswith("xn--")),
        "suspicious_tld": int(tld in SUSPICIOUS_TLDS),
    }