"""Domain-level URL features — subdomain count, TLD analysis, entropy, IP detection.

All features reproducible from the raw URL alone.
"""

import math
import logging
from typing import Dict, Set
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

SUSPICIOUS_TLDS: Set[str] = {
    "xyz", "top", "tk", "ml", "ga", "cf", "gq",
    "site", "icu", "cc", "info", "bid", "loan", "men",
    "kim", "red", "cricket", "press", "win", "zip",
    "mom", "global", "chat", "review", "work",
    "club", "date", "faith", "hair", "tel", "buzz",
    "trade", "webcam", "science", "party", "gdn",
    "click", "download", "stream", "live", "link",
    "help", "rest", "golf", "surf", "fun",
}

VERY_SUSPICIOUS_TLDS: Set[str] = {
    "tk", "ml", "ga", "cf", "gq", "xyz",
}

PUNYCODE_PREFIX = "xn--"

# TLDs commonly used by legitimate sites
LEGITIMATE_TLDS: Set[str] = {
    "com", "org", "net", "edu", "gov", "mil",
    "co", "uk", "de", "ca", "au", "in", "jp", "fr",
    "io", "ai", "app", "dev", "me", "info",
}


def count_subdomains(hostname: str) -> int:
    if not hostname:
        return 0
    parts = hostname.split(".")
    if len(parts) <= 2:
        return 0
    return len(parts) - 2


def extract_domain_features(url: str) -> Dict[str, float]:
    try:
        parsed = urlparse(url)
    except Exception:
        return {}

    hostname = parsed.hostname or ""
    features: Dict[str, float] = {}

    features["domain_len"] = float(len(hostname))

    sub_count = count_subdomains(hostname)
    features["subdomain_count"] = float(sub_count)
    features["subdomain_gt_1"] = float(sub_count > 1)
    features["subdomain_gt_2"] = float(sub_count > 2)
    features["subdomain_gt_3"] = float(sub_count > 3)

    # IP address detection
    is_ip = 0.0
    if hostname:
        parts = hostname.split(".")
        if len(parts) == 4 and all(p.isdigit() for p in parts):
            try:
                if all(0 <= int(p) <= 255 for p in parts):
                    is_ip = 1.0
            except ValueError:
                pass
    if hostname and (hostname.startswith("[") and hostname.endswith("]")):
        is_ip = 1.0
    features["is_domain_ip"] = is_ip

    # Punycode detection
    punycode = 1.0 if PUNYCODE_PREFIX in hostname else 0.0
    no_punycode = 0.0
    for part in hostname.split("."):
        if PUNYCODE_PREFIX in part:
            no_punycode = 1.0
            break
    features["punycode"] = punycode
    features["punycode_in_sld"] = no_punycode

    # TLD extraction and analysis
    tld = ""
    sld = ""
    parts = hostname.split(".")
    clean_parts = [p for p in parts if p]
    if len(clean_parts) >= 2:
        tld = clean_parts[-1].lower()
        sld = clean_parts[-2].lower()

    features["tld_length"] = float(len(tld))
    features["suspicious_tld"] = 1.0 if tld in SUSPICIOUS_TLDS else 0.0
    features["very_suspicious_tld"] = 1.0 if tld in VERY_SUSPICIOUS_TLDS else 0.0
    features["legitimate_tld"] = 1.0 if tld in LEGITIMATE_TLDS else 0.0
    features["tld_gt_3"] = 1.0 if len(tld) > 3 else 0.0

    # Port analysis
    non_standard_port = 0.0
    try:
        port = parsed.port
        if port is not None:
            if parsed.scheme == "https" and port != 443:
                non_standard_port = 1.0
            elif parsed.scheme == "http" and port != 80:
                non_standard_port = 1.0
            else:
                non_standard_port = 1.0
    except Exception:
        pass
    features["non_standard_port"] = non_standard_port
    features["has_port"] = 1.0 if parsed.port else 0.0

    # At symbol in URL (significant for phishing)
    features["has_at_symbol"] = 1.0 if "@" in url else 0.0

    # Hyphen in domain
    features["domain_has_hyphen"] = 1.0 if "-" in hostname else 0.0

    # SLD analysis
    features["sld_length"] = float(len(sld))
    features["sld_digit_count"] = float(sum(c.isdigit() for c in sld))
    features["sld_has_digit"] = 1.0 if any(c.isdigit() for c in sld) else 0.0
    features["sld_digit_ratio"] = float(sum(c.isdigit() for c in sld)) / max(len(sld), 1)

    # SLD vowel-consonant ratio (random SLDs have abnormal ratios)
    if sld:
        vowels = set("aeiou")
        vowel_count = sum(1 for c in sld.lower() if c in vowels)
        cons_count = sum(1 for c in sld.lower() if c.isalpha() and c not in vowels)
        features["sld_vowel_ratio"] = float(vowel_count) / max(vowel_count + cons_count, 1)
        features["sld_consonant_density"] = float(cons_count) / max(len(sld), 1)
    else:
        features["sld_vowel_ratio"] = 0.0
        features["sld_consonant_density"] = 0.0

    # Domain dots beyond usual (www.example.com = 2 dots max for standard)
    num_dots = float(hostname.count("."))
    features["domain_num_dots"] = num_dots
    features["domain_dots_gt_2"] = 1.0 if num_dots > 2 else 0.0
    features["domain_dots_gt_3"] = 1.0 if num_dots > 3 else 0.0

    # Short IP look-alike: pure numeric first segment
    if sld and sld.replace(".", "").isdigit():
        features["numeric_sld"] = 1.0
    else:
        features["numeric_sld"] = 0.0

    # Hostname entropy
    host_entropy = 0.0
    if hostname:
        hl = hostname.lower()
        length = len(hl)
        freq = {}
        for c in hl:
            freq[c] = freq.get(c, 0) + 1
        entropy = 0.0
        for c in freq:
            p = freq[c] / length
            entropy -= p * math.log2(p)
        host_entropy = entropy
    features["hostname_entropy"] = host_entropy

    # WWW usage
    features["www_used"] = 1.0 if hostname.startswith("www.") else 0.0

    # SLD length product with subdomain count (catches lengthy abnormal domains)
    features["sld_times_subdomain"] = float(len(sld) * max(sub_count, 1))

    return features
