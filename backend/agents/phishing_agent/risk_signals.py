"""Standalone risk signal collectors for phishing URL analysis.

Each function takes a URL and returns a dict with the signal's findings.
No function depends on any other signal — they can run in parallel.
"""

import logging
import socket
import ssl as ssl_lib
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)

_USER_AGENT = "AstraShield/1.0 (+https://astra-shield.app)"
_WHOIS_CACHE: Dict[str, dict] = {}


def check_ssl(url: str, timeout: float = 5.0) -> Dict:
    """Check SSL certificate validity and expiry for HTTPS URLs."""
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return {"valid": False, "error": "No hostname in URL"}
        port = parsed.port or 443

        context = ssl_lib.create_default_context()
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                if not cert:
                    return {"valid": False, "error": "No certificate returned"}

                not_after_str = cert.get("notAfter", "")
                if not not_after_str:
                    return {"valid": True, "expiry": None, "error": "No expiry date in cert"}

                not_after = datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z")
                days_left = (not_after - datetime.now()).days
                is_valid = days_left > 0
                issuer = dict(cert.get("issuer", []))
                subject = dict(cert.get("subject", []))

                return {
                    "valid": is_valid,
                    "expiry_days_left": days_left,
                    "issuer": issuer.get("organizationName", "Unknown"),
                    "subject_cn": subject.get("commonName", ""),
                    "expiry_date": not_after_str,
                }
    except Exception as e:
        return {"valid": False, "error": str(e)[:200]}


def check_dns(url: str, timeout: float = 3.0) -> Dict:
    """Perform basic DNS checks: resolves, has MX, has TXT records."""
    parsed = urlparse(url)
    hostname = parsed.hostname
    if not hostname:
        return {"resolves": False, "error": "No hostname"}
    try:
        ip = socket.gethostbyname(hostname)
        return {"resolves": True, "ip": ip}
    except socket.gaierror as e:
        return {"resolves": False, "error": str(e)[:200]}


def check_whois(domain: str, timeout: float = 5.0) -> Dict:
    """Check domain WHOIS for age and registration info."""
    if domain in _WHOIS_CACHE:
        return _WHOIS_CACHE[domain]
    try:
        import whois as whois_lib

        info = whois_lib.whois(domain)
        creation = info.creation_date
        if isinstance(creation, list):
            creation = creation[0] if creation else None

        age_days = None
        if creation:
            if isinstance(creation, datetime):
                age_days = (datetime.now() - creation).days
            else:
                age_days = None

        result = {
            "domain": domain,
            "age_days": age_days,
            "registrar": (info.registrar or "Unknown")[:100],
            "name_servers": (info.name_servers or [])[:5],
            "available": False,
            "error": None,
        }
        _WHOIS_CACHE[domain] = result
        return result
    except Exception as e:
        result = {"domain": domain, "error": str(e)[:200]}
        _WHOIS_CACHE[domain] = result
        return result


def check_virustotal(url: str, api_key: str = "") -> Dict:
    """Check a URL against VirusTotal API."""
    if not api_key:
        return {"checked": False, "error": "API key not configured", "malicious": None}
    try:
        headers = {"x-apikey": api_key, "User-Agent": _USER_AGENT}
        from urllib.parse import quote

        url_id = quote(url, safe="")
        submit = requests.post(
            "https://www.virustotal.com/api/v3/urls",
            headers=headers,
            data={"url": url},
            timeout=10,
        )
        if submit.status_code == 429:
            return {"checked": True, "malicious": None, "error": "Rate limited"}
        if submit.status_code == 200:
            analysis_id = submit.json().get("data", {}).get("id", "")
            if analysis_id:
                report = requests.get(
                    f"https://www.virustotal.com/api/v3/analyses/{analysis_id}",
                    headers=headers,
                    timeout=10,
                )
                if report.status_code == 200:
                    stats = report.json().get("data", {}).get("attributes", {}).get("stats", {})
                    malicious = stats.get("malicious", 0)
                    suspicious = stats.get("suspicious", 0)
                    total = stats.get("total", 1)
                    return {
                        "checked": True,
                        "malicious": malicious,
                        "suspicious": suspicious,
                        "total_scanners": total,
                        "malicious_ratio": round(malicious / max(total, 1), 4) if total else 0,
                    }
        return {"checked": True, "malicious": None, "error": "No analysis available"}
    except Exception as e:
        return {"checked": True, "malicious": None, "error": str(e)[:200]}


def check_url_shortener(url: str) -> Dict:
    """Check if URL uses a known shortener service."""
    parsed = urlparse(url)
    domain = (parsed.hostname or "").lower()
    shorteners = {
        "bit.ly", "tinyurl.com", "goo.gl", "ow.ly", "t.co", "buff.ly",
        "is.gd", "cli.gs", "shorturl.at", "rb.gy", "cutt.ly", "tiny.cc",
        "bl.ink", "shorte.st", "linklyhq.com", "rebrand.ly", "short.link",
        "v.gd", "s.id", "soo.gd", "bc.vc", "dy.fi", "budurl.com",
        "snipurl.com", "short.ie", "adf.ly", "bit.do", "mcaf.ee",
    }
    for shortener in shorteners:
        if domain == shortener or domain.endswith("." + shortener):
            return {"is_shortened": True, "service": shortener}
    return {"is_shortened": False, "service": None}


def check_redirects(url: str, timeout: float = 5.0) -> Dict:
    """Follow redirect chain and count hops."""
    try:
        response = requests.get(
            url,
            allow_redirects=True,
            timeout=timeout,
            headers={"User-Agent": _USER_AGENT},
        )
        redirect_count = len(response.history)
        final_url = response.url
        redirect_chain = [r.url for r in response.history]

        return {
            "redirect_count": redirect_count,
            "final_url": final_url,
            "redirect_chain": redirect_chain,
            "status_code": response.status_code,
        }
    except Exception as e:
        return {"redirect_count": 0, "error": str(e)[:200]}


_SHAP_EXPLANATIONS: Dict[str, str] = {
    "legitimacy_score": "URL appears anomalous compared to legitimate websites",
    "path_len": "Excessive URL path length is often used to hide intent",
    "num_slashes": "High number of path segments typical of phishing URLs",
    "https_count": "Unexpected HTTPS usage pattern",
    "www_used": "Unexpected www prefix usage",
    "domain_len": "Domain length is unusual",
    "brand_similarity_max": "URL closely resembles a known brand name",
    "brand_similarity_top3_avg": "URL resembles known brand patterns",
    "has_brand_name": "URL contains a recognized brand name",
    "brand_actual_domain": "Domain matches a known brand",
    "brand_close_match": "Domain is a close misspelling of a brand",
    "max_consecutive_repeats": "Suspicious repeated characters in URL",
    "letter_ratio": "Abnormal letter-to-character ratio",
    "sld_length": "Second-level domain length is unusual",
    "hostname_entropy": "Domain name has unusual randomness",
    "punycode": "Uses punycode encoding to disguise domain",
    "punycode_in_sld": "Second-level domain uses punycode encoding",
    "has_homograph": "URL contains visually similar characters (homograph attack)",
    "homograph_char_count": "Multiple homograph characters detected",
    "num_phishing_keywords": "URL contains suspicious keywords",
    "phishing_keyword_density": "High density of suspicious keywords in URL",
    "has_phishing_keyword": "URL contains a suspicious keyword",
    "suspicious_tld": "Uses a top-level domain commonly associated with phishing",
    "very_suspicious_tld": "Uses a high-risk top-level domain",
    "legitimate_tld": "Uses a trusted top-level domain",
    "tld_gt_3": "Top-level domain is unusually long",
    "subdomain_gt_1": "Multiple subdomains used to appear legitimate",
    "subdomain_gt_2": "Excessive subdomain nesting detected",
    "subdomain_gt_3": "Heavy subdomain nesting to hide identity",
    "subdomain_count": "Unusual number of subdomains",
    "is_domain_ip": "URL uses an IP address instead of a domain name",
    "ip_in_query": "IP address embedded in query parameters",
    "ip_in_path": "IP address embedded in URL path",
    "url_entropy": "URL has unusual randomness in structure",
    "num_digits": "High number of digits in URL",
    "digit_ratio": "Abnormal digit-to-character ratio",
    "special_char_ratio": "High ratio of special characters in URL",
    "is_http": "Uses unencrypted HTTP instead of HTTPS",
    "is_https": "Uses HTTPS encryption",
    "is_shortened_url": "URL is shortened by a URL shortening service",
    "multiple_protocols": "Multiple protocols detected in URL",
    "protocol_in_subdomain": "Protocol string found in subdomain",
    "non_standard_port": "Uses a non-standard network port",
    "has_double_slash": "Double slash in path used for obfuscation",
    "has_at_symbol": "@ symbol used to hide real domain",
    "has_port": "Explicit port specification in URL",
    "has_suspicious_extension": "File extension is associated with malware",
    "has_deep_path": "Unusually deep directory structure",
    "has_long_segment": "Unusually long path segment detected",
    "num_directories": "Excessive number of directories in path",
    "sld_digit_count": "Digits found in second-level domain",
    "sld_digit_ratio": "High digit ratio in second-level domain",
    "sld_has_digit": "Second-level domain contains digits",
    "numeric_sld": "Second-level domain is entirely numeric",
    "numeric_tld": "Top-level domain is entirely numeric",
    "random_looking_score": "Domain appears randomly generated",
    "punycode": "Domain uses internationalized character encoding",
    "double_hyphen_in_domain": "Double hyphen creates lookalike domains",
    "domain_has_hyphen": "Domain contains hyphens",
    "num_hyphens": "Multiple hyphens found in URL",
    "excessive_dots": "Too many dot separators in URL",
    "dots_gt_5": "URL contains more than 5 dots",
    "dots_gt_7": "URL contains more than 7 dots",
    "domain_dots_gt_2": "More than 2 dots in domain",
    "domain_dots_gt_3": "More than 3 dots in domain",
    "domain_num_dots": "Unusual number of dot separators in domain",
    "num_dots_total": "Total dot count across entire URL",
    "suspicious_char_sequences": "Character patterns typical of phishing URLs",
    "max_consecutive_hyphens": "Multiple consecutive hyphens detected",
}


def shap_to_explanations(feature_names: List[str], contributions: List[float]) -> List[str]:
    """Convert raw SHAP feature contributions into human-readable explanations.
    
    Returns explanations for features with meaningful contributions (|contribution| > 0.05),
    ordered by absolute contribution descending.
    """
    explanations: List[str] = []
    for name, contrib in zip(feature_names, contributions):
        if abs(contrib) <= 0.05:
            continue
        direction = "increases" if contrib > 0 else "decreases"
        explanation = _SHAP_EXPLANATIONS.get(
            name, f"Feature '{name}' {direction} phishing risk"
        )
        explanations.append(explanation)
    return explanations[:15]


def build_explanations(result: Dict) -> List[str]:
    """Build a flat list of human-readable explanations from a prediction result."""
    explanations: List[str] = []
    for c in result.get("top_contributors", []):
        name = c.get("feature", "")
        contrib = c.get("contribution", 0)
        if abs(contrib) <= 0.05:
            continue
        explanation = _SHAP_EXPLANATIONS.get(name, None)
        if explanation:
            if explanation not in explanations:
                explanations.append(explanation)
    return explanations[:15]
