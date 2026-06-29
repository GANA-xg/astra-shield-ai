import ipaddress
import whois
import math

from urllib.parse import urlparse
from datetime import datetime


SUSPICIOUS_TLDS = {
    ".xyz",
    ".top",
    ".click",
    ".tk",
    ".ml",
    ".ga",
    ".cf",
    ".gq",
    ".work",
    ".support",
}


INDIAN_BRANDS = {
    "rbi",
    "sbi",
    "hdfc",
    "icici",
    "aadhaar",
    "uidai",
    "irctc",
    "npci",
    "paytm",
    "phonepe",
    "gpay",
}


SUSPICIOUS_KEYWORDS = {
    "login",
    "verify",
    "update",
    "secure",
    "account",
    "bank",
    "otp",
    "wallet",
    "payment",
    "signin",
}


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
    """
    Extract phishing-related features from a URL.

    This function DOES NOT calculate risk.
    It only returns extracted features.
    """

    # Normalize URL
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    parsed = urlparse(url)

    domain = parsed.hostname or ""

    path = parsed.path.lower()
    query = parsed.query or ""
    parts = domain.split(".") if domain else []

    features = {
        "url": url,
        "domain": domain,
    }

    #################################################
    # WHOIS
    #################################################

    features["whois_failed"] = False
    features["domain_age_days"] = None

    try:
        info = whois.whois(domain)

        creation = info.creation_date

        if isinstance(creation, list):
            creation = creation[0]

        if creation:
            features["domain_age_days"] = (
                datetime.now() - creation
            ).days

    except Exception:
        features["whois_failed"] = True

    #################################################
    # Suspicious TLD
    #################################################

    features["suspicious_tld"] = any(
        domain.endswith(tld)
        for tld in SUSPICIOUS_TLDS
    )

    #################################################
    # Brand impersonation
    #################################################

    label = domain.split(".")[0].lower()

    features["brand_impersonation"] = False
    features["brand_name"] = None

    for brand in INDIAN_BRANDS:

        if (
            label.startswith(brand + "-")
            or label.endswith("-" + brand)
            or f"-{brand}-" in label
        ):

            features["brand_impersonation"] = True
            features["brand_name"] = brand.upper()
            break

    #################################################
    # IP URL
    #################################################

    try:
        ipaddress.ip_address(domain)
        features["ip_url"] = True
    except ValueError:
        features["ip_url"] = False

    #################################################
    # URL length
    #################################################

    features["url_length"] = len(url)
    features["domain_length"] = len(domain)
    features["path_length"] = len(path)
    features["query_length"] = len(query)
    features["slash_count"] = url.count("/")
    features["hyphen_count"] = url.count("-")
    features["underscore_count"] = url.count("_")
    features["digit_count"] = sum(c.isdigit() for c in url)
    features["letter_count"] = sum(c.isalpha() for c in url)
    features["special_char_count"] = sum(c in "@?=&_%" for c in url)
    features["query_parameter_count"] = query.count("&") + (1 if query else 0)
    features["hostname_entropy"] = shannon_entropy(domain)
    features["max_repeated_characters"] = max_consecutive_characters(domain)

    #################################################
    # Number of dots
    #################################################

    features["dot_count"] = domain.count(".")

    #################################################
    # Number of subdomains
    #################################################

    features["subdomain_count"] = max(len(parts) - 2, 0)

    #################################################
    # HTTPS
    #################################################

    features["https"] = parsed.scheme == "https"

    #################################################
    # @ symbol
    #################################################

    features["has_at_symbol"] = "@" in url

    #################################################
    # Punycode
    #################################################

    features["punycode"] = "xn--" in domain

    #################################################
    # Suspicious keywords
    #################################################

    text = (domain + path).lower()

    features["keyword_count"] = sum(
        keyword in text
        for keyword in SUSPICIOUS_KEYWORDS
    )

    return features