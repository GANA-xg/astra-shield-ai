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
    ".site",
    ".online",
    ".live",
    ".shop",
    ".cc",
    ".info",
    ".bid",
    ".trade",
    ".review",
    ".download",
    ".loan",
    ".men",
    ".rest",
    ".host",
    ".stream",
}


KNOWN_BRANDS = {
    # Indian
    "rbi", "sbi", "hdfc", "icici", "aadhaar", "uidai", "irctc",
    "npci", "paytm", "phonepe", "gpay",
    # Global
    "google", "gmail", "youtube", "paypal", "apple", "icloud",
    "amazon", "prime", "microsoft", "office365", "outlook",
    "netflix", "facebook", "fb", "instagram", "whatsapp",
    "twitter", "linkedin", "chase", "wellsfargo", "citibank",
    "capitalone", "americanexpress", "amex", "dropbox", "adobe",
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

    tld = next((t for t in SUSPICIOUS_TLDS if domain.endswith(t)), None)
    features["suspicious_tld"] = tld is not None
    features["tld"] = tld or ("." + parts[-1] if len(parts) > 1 else None)

    #################################################
    # Brand impersonation
    #################################################

    domain_lower = domain.lower()
    features["brand_impersonation"] = False
    features["brand_name"] = None

    for brand in KNOWN_BRANDS:
        for segment in domain_lower.split("."):
            if brand == segment or any(part == brand for part in segment.split("-")):
                # Skip if brand IS the actual second-level domain (legitimate site)
                sld = domain_lower.split(".")[-2] if len(domain_lower.split(".")) >= 2 else ""
                if sld and brand == sld:
                    continue
                features["brand_impersonation"] = True
                features["brand_name"] = brand.upper()
                break
        if features["brand_impersonation"]:
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

    # Split by non-alphanumeric characters for whole-word matching
    segments = __import__("re").split(r"[^a-z0-9]+", text)
    segments_set = {s for s in segments if s}

    features["keyword_count"] = sum(
        keyword in segments_set
        for keyword in SUSPICIOUS_KEYWORDS
    )

    return features