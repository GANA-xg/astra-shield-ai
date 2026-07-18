"""Lexical URL features - character-level, structural, and brand similarity analysis.

Extracts ~40 features from the raw URL string — no external calls.
"""

import math
import logging
from typing import Dict, List
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

PHISHING_KEYWORDS = [
    "login", "signin", "verify", "account", "update", "confirm",
    "password", "payment", "pay", "bank", "secure", "wallet",
    "authenticate", "credential", "recover", "reset", "token",
    "otp", "mpin", "tpin", "authorize", "validate", "session",
    "blocked", "suspended", "limited", "unusual", "unlock",
    "claim", "refund", "reward", "bonus", "free", "prize",
    "win", "offer", "promo", "urgent", "alert", "notice",
    "suspended", "service", "support", "security",
    "wells", "citi", "capitalone", "amex", "hsbc",
]

BRAND_NAMES = [
    "google", "youtube", "gmail", "facebook", "instagram",
    "whatsapp", "twitter", "x", "linkedin", "microsoft",
    "outlook", "office365", "sharepoint", "onedrive",
    "apple", "icloud", "amazon", "paypal", "netflix",
    "spotify", "dropbox", "adobe", "zoom", "teams",
    "slack", "github", "gitlab", "bitbucket",
    "sbi", "statebank", "hdfc", "icici", "axisbank",
    "kotak", "yesbank", "pnb", "bob", "canara",
    "phonepe", "paytm", "googlepay", "gpay", "amazonpay",
    "cryptocom", "coinbase", "binance", "blockchain",
]

FUZZY_BRANDS: List[str] = [
    "google", "facebook", "youtube", "gmail", "instagram",
    "whatsapp", "twitter", "linkedin", "microsoft", "outlook",
    "office365", "apple", "icloud", "amazon", "paypal",
    "netflix", "spotify", "dropbox", "adobe", "zoom",
    "github", "gitlab", "sbi", "statebank", "hdfc",
    "icici", "axisbank", "kotak", "yesbank", "phonepe",
    "paytm", "cryptocom", "coinbase", "binance", "blockchain",
    "wellsfargo", "chase", "capitalone", "americanexpress",
    "hsbc", "barclays", "natwest", "halifax", "lloyds",
]

# Homograph look-alike characters (Unicode confusables)
HOMOGRAPH_MAP: Dict[str, str] = {
    "а": "a",  # Cyrillic small letter a
    "е": "e",  # Cyrillic small letter ie
    "о": "o",  # Cyrillic small letter o
    "р": "p",  # Cyrillic small letter er
    "с": "c",  # Cyrillic small letter es
    "у": "y",  # Cyrillic small letter u
    "х": "x",  # Cyrillic small letter ha
    "і": "i",  # Cyrillic small letter Byelorussian-Ukrainian i
    "ј": "j",  # Cyrillic small letter je
    "ӏ": "i",  # Cyrillic small letter palochka
    "ɑ": "a",  # Latin small letter alpha
    "ɜ": "e",  # Latin small letter reversed open e
    "ɩ": "l",  # Latin small letter iota
    "ʝ": "j",  # Latin small letter j with crossed tail
    "ʟ": "l",  # Latin small letter L with belt
    "ᴋ": "k",  # Latin letter small capital k
    "ᴛ": "t",  # Latin letter small capital t
    "ᴀ": "a",  # Latin letter small capital a
    "ᴇ": "e",  # Latin letter small capital e
    "ʜ": "h",  # Latin letter small capital h
    "ɪ": "i",  # Latin letter small capital i
    "ʟ": "l",  # Latin letter small capital l
    "ɴ": "n",  # Latin letter small capital n
    "ʀ": "r",  # Latin letter small capital r
    "ѕ": "s",  # Cyrillic small letter dze
    "ο": "o",  # Greek small letter omicron
    "е": "e",  # Cyrillic small letter ie (duplicate for coverage)
}


def entropy(s: str) -> float:
    if not s:
        return 0.0
    s_lower = s.lower()
    length = len(s_lower)
    freq = {}
    for c in s_lower:
        freq[c] = freq.get(c, 0) + 1
    ent = 0.0
    for c in freq:
        p = freq[c] / length
        if p > 0:
            ent -= p * math.log2(p)
    return ent


def max_consecutive_repeats(s: str) -> int:
    if not s:
        return 0
    max_repeat = 1
    current = 1
    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            current += 1
            max_repeat = max(max_repeat, current)
        else:
            current = 1
    return max_repeat


def count_phishing_keywords(text: str) -> int:
    text_lower = text.lower()
    count = 0
    for kw in PHISHING_KEYWORDS:
        if kw in text_lower:
            count += 1
    return count


def count_brand_names(text: str) -> int:
    text_lower = text.lower()
    count = 0
    for brand in BRAND_NAMES:
        if brand in text_lower:
            count += 1
    return count


def detect_homograph(hostname: str) -> float:
    """Detect homograph attacks using Unicode confusable characters."""
    if not hostname:
        return 0.0
    for ch in hostname:
        if ch in HOMOGRAPH_MAP or (ord(ch) > 127 and ch.isalpha()):
            return 1.0
    return 0.0


def count_homograph_chars(hostname: str) -> int:
    if not hostname:
        return 0
    count = 0
    for ch in hostname:
        if ord(ch) > 127 and ch.isalpha():
            count += 1
    return count


def compute_brand_similarity(hostname: str) -> Dict[str, float]:
    """Compute fuzzy brand similarity using RapidFuzz."""
    result = {
        "brand_similarity_max": 0.0,
        "brand_similarity_top3_avg": 0.0,
        "brand_close_match": 0.0,
    }
    if not hostname:
        return result

    sld = ""
    parts = hostname.lower().split(".")
    parts = [p for p in parts if p]
    if len(parts) >= 2:
        sld = parts[-2]
    if not sld or len(sld) < 3:
        return result

    try:
        from rapidfuzz import fuzz

        scores = []
        for brand in FUZZY_BRANDS:
            score = fuzz.ratio(sld, brand) / 100.0
            if score > 0.5:
                scores.append((brand, score))

        if scores:
            scores.sort(key=lambda x: -x[1])
            top = scores[:3]
            result["brand_similarity_max"] = top[0][1]
            result["brand_similarity_top3_avg"] = sum(s for _, s in top) / len(top)
            result["brand_close_match"] = 1.0 if top[0][1] >= 0.85 else 0.0
    except ImportError:
        pass

    return result


def is_brand_actual_domain(hostname: str) -> float:
    """Check if the SLD matches a known brand (not impersonation)."""
    if not hostname:
        return 0.0
    parts = hostname.lower().split(".")
    parts = [p for p in parts if p]
    if len(parts) < 2:
        return 0.0
    sld = parts[-2]
    known_brands = {b.lower() for b in FUZZY_BRANDS}
    return 1.0 if sld in known_brands else 0.0


def get_random_looking_score(s: str) -> float:
    if not s:
        return 0.0
    path_part = ""
    try:
        parsed = urlparse(s)
        path_part = parsed.path
    except Exception:
        path_part = s

    if not path_part:
        return 0.0

    cleaned = "".join(c for c in path_part if c.isalpha())

    if len(cleaned) < 4:
        return 0.0

    vowels = set("aeiou")
    consonants = sum(1 for c in cleaned if c.lower() not in vowels)

    ratio = consonants / max(len(cleaned), 1)

    if ratio > 0.75:
        return 1.0
    if ratio > 0.65:
        return 0.5
    return 0.0


def extract_lexical_features(url: str) -> Dict[str, float]:
    try:
        parsed = urlparse(url)
    except Exception:
        parsed = None

    features: Dict[str, float] = {}

    url_lower = url.lower()

    features["url_len"] = float(len(url))

    path = parsed.path if parsed else ""
    query = parsed.query if parsed else ""
    fragment = parsed.fragment if parsed else ""
    hostname = parsed.hostname if parsed else ""
    params = parsed.params if parsed else ""

    features["path_len"] = float(len(path))
    features["query_len"] = float(len(query))
    features["fragment_len"] = float(len(fragment))
    features["params_len"] = float(len(params))
    features["hostname_len"] = float(len(hostname))

    features["num_digits"] = float(sum(c.isdigit() for c in url))
    features["num_letters"] = float(sum(c.isalpha() for c in url))
    features["num_uppercase"] = float(sum(c.isupper() for c in url))
    features["num_lowercase"] = float(sum(c.islower() for c in url))

    features["digit_ratio"] = features["num_digits"] / max(len(url), 1)
    features["letter_ratio"] = features["num_letters"] / max(len(url), 1)
    features["uppercase_ratio"] = features["num_uppercase"] / max(features["num_letters"], 1)

    features["num_slashes"] = float(url.count("/"))
    features["num_hyphens"] = float(url.count("-"))
    features["num_underscores"] = float(url.count("_"))
    features["num_dots"] = float(url.count("."))
    features["num_colons"] = float(url.count(":"))
    features["num_semicolons"] = float(url.count(";"))
    features["num_at"] = float(url.count("@"))
    features["num_percent"] = float(url.count("%"))
    features["num_ampersand"] = float(url.count("&"))
    features["num_question"] = float(url.count("?"))
    features["num_equals"] = float(url.count("="))
    features["num_plus"] = float(url.count("+"))
    features["num_hash"] = float(url.count("#"))
    features["num_tilde"] = float(url.count("~"))
    features["num_pipe"] = float(url.count("|"))
    features["num_parens"] = float(url.count("(") + url.count(")"))

    special_chars = (
        features["num_at"] + features["num_percent"] + features["num_ampersand"]
        + features["num_question"] + features["num_equals"] + features["num_hyphens"]
        + features["num_underscores"] + features["num_plus"] + features["num_hash"]
    )
    features["special_char_ratio"] = special_chars / max(len(url), 1)

    features["url_entropy"] = entropy(url)

    features["max_consecutive_repeats"] = float(max_consecutive_repeats(url))
    features["repeated_chars_gt_3"] = float(max_consecutive_repeats(url) > 3)

    features["num_phishing_keywords"] = float(count_phishing_keywords(url))
    features["has_phishing_keyword"] = float(features["num_phishing_keywords"] > 0)
    features["phishing_keyword_density"] = features["num_phishing_keywords"] / max(len(url), 1) * 1000

    features["num_brand_names"] = float(count_brand_names(url))
    features["has_brand_name"] = float(features["num_brand_names"] > 0)

    features["random_looking_score"] = get_random_looking_score(url)

    # Path segment analysis
    path_segments = [s for s in path.split("/") if s]
    features["num_path_segments"] = float(len(path_segments))
    features["avg_segment_len"] = (
        float(sum(len(s) for s in path_segments)) / max(len(path_segments), 1)
    )
    features["longest_segment_len"] = float(max((len(s) for s in path_segments), default=0))
    features["has_long_segment"] = float(features["longest_segment_len"] > 50)

    features["has_double_slash"] = 1.0 if "//" in url[len("https://"):] else 0.0

    hex_segments = 0
    for seg in path_segments:
        cleaned = seg.replace(".", "").replace("-", "").replace("_", "")
        if cleaned and all(c in "0123456789abcdefABCDEF" for c in cleaned) and len(cleaned) >= 8:
            hex_segments += 1
    features["num_hex_segments"] = float(hex_segments)

    # Query parameter analysis
    if query:
        params_list = query.split("&")
        features["num_query_params"] = float(len(params_list))
        features["avg_query_param_len"] = float(sum(len(p) for p in params_list)) / max(len(params_list), 1)
    else:
        features["num_query_params"] = 0.0
        features["avg_query_param_len"] = 0.0

    # Homograph detection on hostname
    features["has_homograph"] = detect_homograph(hostname)
    features["homograph_char_count"] = float(count_homograph_chars(hostname))

    # Brand similarity
    brand_sim = compute_brand_similarity(hostname)
    features["brand_similarity_max"] = brand_sim["brand_similarity_max"]
    features["brand_similarity_top3_avg"] = brand_sim["brand_similarity_top3_avg"]
    features["brand_close_match"] = brand_sim["brand_close_match"]
    features["brand_actual_domain"] = is_brand_actual_domain(hostname)

    return features
