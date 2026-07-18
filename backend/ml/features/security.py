"""Security-focused URL features — HTTPS, shorteners, redirects, protocol analysis.

All features reproducible from a raw URL string alone.
"""

import logging
import re
from typing import Dict
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

KNOWN_SHORTENERS = {
    "bit.ly", "tinyurl.com", "ow.ly", "t.co", "is.gd", "buff.ly",
    "shorturl.at", "shorturl.com", "cutt.ly", "rb.gy", "tiny.cc",
    "lc.chat", "u.to", "v.gd", "cli.gs", "soo.gd", "gg.gg",
    "tr.im", "zzb.bz", "x.co", "budurl.com", "snipurl.com",
    "snipr.com", "short.to", "2.gp", "qr.ae", "vzturl.com",
    "adf.ly", "goo.gl", "s.id", "tiny.one", "shorte.st",
    "bc.vc", "bit.do", "dlvr.it", "po.st", "q.gs",
    "shortlink", "shortlinkz", "clck.ru", "1url.com",
}


def extract_security_features(url: str) -> Dict[str, float]:
    try:
        parsed = urlparse(url)
    except Exception:
        return {}

    features: Dict[str, float] = {}

    features["is_https"] = 1.0 if parsed.scheme == "https" else 0.0
    features["is_http"] = 1.0 if parsed.scheme == "http" else 0.0

    hostname = parsed.hostname or ""
    domain_lower = hostname.lower()

    # Shortened URL detection
    is_shortened = 0.0
    for shortener in KNOWN_SHORTENERS:
        if shortener in domain_lower or shortener in url.lower():
            is_shortened = 1.0
            break
    features["is_shortened_url"] = is_shortened

    # Excessive dots in URL
    num_dots = url.count(".")
    features["excessive_dots"] = 1.0 if num_dots > 5 else 0.0
    features["num_dots_total"] = float(num_dots)
    features["dots_gt_5"] = 1.0 if num_dots > 5 else 0.0
    features["dots_gt_7"] = 1.0 if num_dots > 7 else 0.0

    # Multiple protocol indicators
    http_count = url.count("http://")
    https_count = url.count("https://")
    features["http_count"] = float(http_count)
    features["https_count"] = float(https_count)
    features["multiple_protocols"] = 1.0 if (http_count + https_count) > 1 else 0.0

    # Subdomain-protocol confusion (e.g., http://http://...)
    if "://" in url:
        after_proto = url.split("://", 1)[1]
        features["protocol_in_subdomain"] = 1.0 if "http" in after_proto.lower() else 0.0
    else:
        features["protocol_in_subdomain"] = 0.0
    if "://" in url:
        after_proto = url.split("://", 1)[1]
        features["http_after_proto"] = 1.0 if "http://" in after_proto.lower() or "https://" in after_proto.lower() else 0.0
    else:
        features["http_after_proto"] = 0.0

    # IP patterns in path
    ip_pattern = re.compile(r"(?:\d{1,3}\.){3}\d{1,3}")
    path = parsed.path or ""
    query = parsed.query or ""
    features["ip_in_path"] = 1.0 if ip_pattern.search(path) else 0.0
    features["ip_in_query"] = 1.0 if ip_pattern.search(query) else 0.0

    # Triple www
    features["triple_www"] = 1.0 if "www.www." in url.lower() else 0.0

    # Numeric TLD
    tld = ""
    parts = domain_lower.split(".")
    clean_parts = [p for p in parts if p]
    if len(clean_parts) >= 2:
        tld = clean_parts[-1]
    features["numeric_tld"] = 1.0 if tld.isdigit() else 0.0

    # Hyphen in domain
    features["hyphen_in_domain"] = 1.0 if "-" in hostname else 0.0

    # Check if there's a long string of non-alphanumeric chars in the URL
    non_alnum_sequence = re.findall(r"[^a-zA-Z0-9/:.?=&%\-_]{3,}", url)
    features["suspicious_char_sequences"] = float(len(non_alnum_sequence))

    # Double dash detection (phishers use -- to make domains look like valid names)
    features["double_hyphen_in_domain"] = 1.0 if "--" in hostname else 0.0

    # Legitimacy composite score (higher = more legitimate signal)
    legit_score = 0.0
    legit_score += 3.0 if features["is_https"] else 0.0
    legit_score += 2.0 if hostname.startswith("www.") else 0.0
    legit_score += 2.0 if tld in {"com", "org", "net", "edu", "gov"} else 0.0
    if tld in {"tk", "ml", "ga", "cf", "gq", "xyz"}:
        legit_score -= 3.0

    features["legitimacy_score"] = max(0.0, legit_score)

    # Number of directories in path
    path_parts = [p for p in path.split("/") if p]
    features["num_directories"] = float(len(path_parts))
    features["has_deep_path"] = 1.0 if len(path_parts) > 3 else 0.0

    # File extension in URL (suspicious when in strange places)
    suspicious_extensions = {".exe", ".scr", ".zip", ".rar", ".doc", ".docx",
                             ".xls", ".xlsx", ".pdf", ".js", ".vbs", ".bat",
                             ".apk", ".dmg", ".iso"}
    for ext in suspicious_extensions:
        if ext in url.lower():
            features["has_suspicious_extension"] = 1.0
            break
    else:
        features["has_suspicious_extension"] = 0.0

    return features
