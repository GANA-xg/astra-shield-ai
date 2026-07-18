"""Risk fusion configuration.

All weights and settings for the comprehensive risk calculation.
Easily adjustable; no hardcoded numbers in the engine.
"""

from typing import Dict

RISK_WEIGHTS: Dict[str, float] = {
    "ml_model": 0.35,
    "safe_browsing": 0.20,
    "virus_total": 0.15,
    "ssl": 0.07,
    "domain_age": 0.06,
    "dns": 0.04,
    "brand_similarity": 0.05,
    "url_structure": 0.08,
}

CLASSIFICATION_THRESHOLDS = {
    "safe": 25,
    "suspicious": 50,
    "high": 75,
}

CRITICAL_SCORE = 100

SIGNAL_SCORES: Dict[str, int] = {
    "safe_browsing_malicious": 90,
    "virus_total_malicious": 85,
    "new_domain_30_days": 40,
    "new_domain_90_days": 25,
    "punycode_in_domain": 35,
    "punycode_entire_sld": 50,
    "homograph_char": 35,
    "multiple_homographs": 50,
    "url_shortener": 30,
    "redirect_5_plus": 35,
    "redirect_10_plus": 50,
    "ssl_missing": 25,
    "ssl_expired": 70,
    "ssl_expires_soon": 30,
    "ssl_self_signed": 30,
    "ssl_error": 15,
    "dns_failure": 10,
    "brand_impersonation": 40,
    "brand_impersonation_strong": 55,
    "suspicious_tld": 30,
    "very_suspicious_tld": 45,
    "keyword_density": 15,
    "excessive_path": 15,
    "ip_domain": 35,
    "excessive_subdomains": 20,
    "no_https": 15,
}

SIGNAL_EXPLANATIONS = {
    "safe_browsing_malicious": "Google Safe Browsing flagged this URL as malicious.",
    "virus_total_malicious": "VirusTotal detected this URL as malicious.",
    "ssl_missing": "The site does not use SSL/TLS encryption. Data you send is visible to attackers.",
    "ssl_expired": "The SSL certificate has expired which suggests poor domain maintenance.",
    "ssl_self_signed": "The SSL certificate is self-signed and not verified by a Certificate Authority.",
    "ssl_error": "There is a problem with the SSL certificate. Do not submit any information.",
    "ssl_expires_soon": "The SSL certificate expires soon, common for disposable phishing domains.",
    "new_domain_30": "The domain is less than 30 days old, within the typical phishing window.",
    "new_domain_90": "The domain is less than 90 days old, which is relatively new for a legitimate site.",
    "punycode": "The domain uses Punycode encoding to disguise its true characters.",
    "homograph": "The URL uses characters that look like Latin letters but come from a different script.",
    "url_shortener": "The URL uses a link shortener, hiding the true destination.",
    "redirect": "The URL redirects through multiple pages, a typical evasion technique.",
    "brand_impersonation": "The URL is designed to impersonate a well-known brand or company.",
    "keyword_phishing": "The URL contains words commonly used in phishing attacks like login or verify.",
    "excessive_path": "The URL path is unusually long, typical of phishing URLs designed to bypass filters.",
    "ip_domain": "The URL uses an IP address instead of a domain name which is atypical for legitimate services.",
    "dns_failure": "The domain could not be resolved which may indicate it is temporary or unmaintained.",
    "suspicious_tld": "The domain uses a Top-Level Domain often associated with spam and phishing.",
    "excessive_subdomains": "The URL uses many subdomains to appear more complex or legitimate.",
    "no_https": "The site does not use HTTPS encryption for data in transit.",
    "domain_age": "The domain was registered recently which is common for phishing operations.",
}

RECOMMENDATIONS = {
    "safe": "Appears safe",
    "suspicious": "Proceed with caution",
    "high": "Do not interact",
    "critical": "Block immediately",
}
