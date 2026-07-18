"""Risk Fusion Engine — the central decision point.

Combines all risk signals into a weighted final score using configurable weights.
Returns a structured assessment with human-readable explanations.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from core.risk_config import (
    RISK_WEIGHTS,
    CLASSIFICATION_THRESHOLDS,
    SIGNAL_SCORES,
    SIGNAL_EXPLANATIONS,
    RECOMMENDATIONS,
)
from agents.phishing_agent.risk_signals import (
    check_ssl,
    check_dns,
    check_whois,
    check_virustotal,
    check_url_shortener,
    check_redirects,
    shap_to_explanations as shap_to_text,
)

logger = logging.getLogger(__name__)


class RiskFusionResult:
    """Structured risk fusion output."""

    def __init__(self):
        self.risk_score: int = 0
        self.risk_level: str = "LOW"
        self.ml_score: float = 0.0
        self.google_safe_browsing: str = "not_checked"
        self.virus_total: str = "not_checked"
        self.ssl_status: str = "not_checked"
        self.domain_age: str = "not_checked"
        self.brand_similarity: str = "not_checked"
        self.explanations: List[str] = []
        self.signals: List[str] = []
        self.classification: str = "unknown"
        self.confidence: float = 0.0
        self.recommendation: str = "Appears safe"
        self.signal_details: Dict = {}


def _score_to_level(score: int) -> str:
    if score >= 70:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 30:
        return "MEDIUM"
    return "LOW"


def _score_to_classification(score: int) -> str:
    if score >= CLASSIFICATION_THRESHOLDS.get("high", 70):
        return "phishing"
    if score >= CLASSIFICATION_THRESHOLDS.get("suspicious", 40):
        return "suspicious"
    return "safe"


def run_risk_fusion(
    url: str,
    ml_probability: float = 0.0,
    safe_browsing_result: Optional[Dict] = None,
    blacklist_results: Optional[Dict] = None,
    vt_api_key: str = "",
    shap_explanations: Optional[List[str]] = None,
) -> RiskFusionResult:
    """Run the complete risk fusion pipeline and return a structured result."""
    result = RiskFusionResult()
    weighted_score = 0.0
    all_signals: List[str] = []
    all_explanations: List[str] = []
    signal_details: Dict = {}

    if shap_explanations:
        all_explanations.extend(shap_explanations[:5])

    result.ml_score = round(ml_probability, 4)
    if ml_probability >= 0.7:
        weighted_score += RISK_WEIGHTS["ml_model"] * 100
        if ml_probability >= 0.95:
            all_explanations.append(
                "ML model analysis indicates a very high probability of phishing"
            )
        elif ml_probability >= 0.85:
            all_explanations.append(
                "ML model analysis indicates a high probability of phishing"
            )
        elif ml_probability >= 0.70:
            all_explanations.append(
                "ML model analysis indicates a moderately high probability of phishing"
            )
    else:
        safe_score = (1.0 - ml_probability) * 100 * RISK_WEIGHTS["ml_model"]
        weighted_score += safe_score * 0.3

    safe_browsing_malicious = False
    if safe_browsing_result:
        sb_mal = safe_browsing_result.get("malicious", False)
        if sb_mal:
            safe_browsing_malicious = True
            signal_details["safe_browsing"] = {
                "threat_type": safe_browsing_result.get("threat_type", "unknown")
            }
            weighted_score += RISK_WEIGHTS["safe_browsing"] * SIGNAL_SCORES["safe_browsing_malicious"]
            all_signals.append("safe_browsing_malicious")
            result.google_safe_browsing = "malicious"
        elif safe_browsing_result.get("error"):
            result.google_safe_browsing = "error"
        else:
            result.google_safe_browsing = "clean"

    if blacklist_results and any(v for k, v in blacklist_results.items() if v is True):
        detected = [k for k, v in blacklist_results.items() if v is True]
        all_signals.append(f"blacklisted:{','.join(detected)}")

    _add_signal_to_explanation("safe_browsing_malicious", all_signals, all_explanations)

    vt_result = check_virustotal(url, api_key=vt_api_key)
    if vt_result.get("checked") and vt_result.get("malicious") is not None:
        mal_count = vt_result["malicious"]
        if mal_count > 0:
            signal_details["virus_total"] = mal_count
            if mal_count >= 3:
                weighted_score += RISK_WEIGHTS["virus_total"] * SIGNAL_SCORES["virus_total_malicious"]
                all_signals.append("virus_total_malicious")
            result.virus_total = f"malicious({mal_count})"
            _add_signal_to_explanation("virus_total_malicious", all_signals, all_explanations)
        else:
            result.virus_total = "clean"
    elif vt_result.get("checked"):
        result.virus_total = "not_available"
    else:
        result.virus_total = "not_checked"

    from urllib.parse import urlparse as _urlparse
    _parsed = _urlparse(url)
    _is_https = _parsed.scheme == "https"

    ssl_result = check_ssl(url)
    signal_details["ssl"] = ssl_result
    if ssl_result.get("valid"):
        days_left = ssl_result.get("expiry_days_left", 0)
        if days_left is not None and days_left < 14:
            weighted_score += RISK_WEIGHTS["ssl"] * SIGNAL_SCORES["ssl_expires_soon"]
            all_signals.append("ssl_expires_soon")
            result.ssl_status = f"expires_soon({days_left}d)"
        else:
            result.ssl_status = f"valid({days_left}d)" if days_left else "valid"
    elif ssl_result.get("error"):
        error_msg = ssl_result["error"].lower()
        if "expired" in error_msg:
            weighted_score += RISK_WEIGHTS["ssl"] * SIGNAL_SCORES["ssl_expired"]
            all_signals.append("ssl_expired")
            result.ssl_status = "expired"
        elif "self" in error_msg:
            weighted_score += RISK_WEIGHTS["ssl"] * SIGNAL_SCORES["ssl_self_signed"]
            all_signals.append("ssl_self_signed")
            result.ssl_status = "self_signed"
        elif "certificate" in error_msg or "ssl" in error_msg:
            weighted_score += RISK_WEIGHTS["ssl"] * SIGNAL_SCORES["ssl_error"]
            all_signals.append("ssl_error")
            result.ssl_status = "error"
        elif _is_https:
            # HTTPS URL but SSL check failed (likely connection issue) — not penalized
            result.ssl_status = "check_failed"
        else:
            # HTTP (not HTTPS) — penalize missing encryption
            weighted_score += RISK_WEIGHTS["ssl"] * SIGNAL_SCORES["no_https"]
            all_signals.append("ssl_missing")
            result.ssl_status = "no_https"

    _add_signal_to_explanation("ssl_expired", all_signals, all_explanations)
    _add_signal_to_explanation("ssl_self_signed", all_signals, all_explanations)
    _add_signal_to_explanation("ssl_error", all_signals, all_explanations)
    _add_signal_to_explanation("ssl_expires_soon", all_signals, all_explanations)

    from urllib.parse import urlparse
    parsed = urlparse(url)
    hostname = parsed.hostname or ""

    whois_result = check_whois(hostname)
    signal_details["whois"] = whois_result
    age_days = whois_result.get("age_days")
    if age_days is not None:
        if age_days < 30:
            weighted_score += RISK_WEIGHTS["domain_age"] * SIGNAL_SCORES["new_domain_30_days"]
            all_signals.append("new_domain_30")
            all_explanations.append("The domain was registered less than 30 days ago")
            result.domain_age = f"{age_days} days"
        elif age_days < 90:
            weighted_score += RISK_WEIGHTS["domain_age"] * SIGNAL_SCORES["new_domain_90_days"]
            all_signals.append("new_domain_90")
            result.domain_age = f"{age_days} days"
        else:
            result.domain_age = f"{age_days} days"
    else:
        result.domain_age = "unknown"

    dns_result = check_dns(url)
    signal_details["dns"] = dns_result
    if not dns_result.get("resolves"):
        weighted_score += RISK_WEIGHTS["dns"] * SIGNAL_SCORES["dns_failure"]
        all_signals.append("dns_failure")
        all_explanations.append("The domain does not resolve to a valid IP address")

    from ml.features.extractor import extract_features
    ml_features = extract_features(url)

    if ml_features.get("suspicious_tld", 0) > 0:
        weighted_score += (RISK_WEIGHTS["brand_similarity"] * 0.5) * SIGNAL_SCORES["suspicious_tld"]
        all_signals.append("suspicious_tld")
        _add_signal_to_explanation("suspicious_tld", all_signals, all_explanations)

    if ml_features.get("very_suspicious_tld", 0) > 0:
        weighted_score += (RISK_WEIGHTS["brand_similarity"] * 0.5) * SIGNAL_SCORES["very_suspicious_tld"]
        all_signals.append("very_suspicious_tld")
        _add_signal_to_explanation("suspicious_tld", all_signals, all_explanations)

    if ml_features.get("has_homograph", 0) > 0:
        weighted_score += RISK_WEIGHTS["url_structure"] * SIGNAL_SCORES["homograph_char"]
        all_signals.append("homograph")
        _add_signal_to_explanation("homograph", all_signals, all_explanations)

    if ml_features.get("punycode", 0) > 0:
        weighted_score += RISK_WEIGHTS["url_structure"] * SIGNAL_SCORES["punycode_in_domain"]
        all_signals.append("punycode")
        _add_signal_to_explanation("punycode", all_signals, all_explanations)

    is_brand_actual = ml_features.get("brand_actual_domain", 0) > 0
    is_brand_close = ml_features.get("brand_close_match", 0) > 0
    max_sim = ml_features.get("brand_similarity_max", 0)
    brand_in_url = ml_features.get("has_brand_name", 0) > 0

    if is_brand_close and is_brand_actual:
        pass
    elif is_brand_close and not brand_in_url:
        weighted_score += RISK_WEIGHTS["brand_similarity"] * SIGNAL_SCORES["brand_impersonation"]
        all_signals.append("brand_impersonation")
        _add_signal_to_explanation("brand_impersonation", all_signals, all_explanations)
    elif max_sim > 0.8 and not is_brand_actual:
        weighted_score += RISK_WEIGHTS["brand_similarity"] * SIGNAL_SCORES["brand_impersonation_strong"]
        all_signals.append("brand_impersonation")
        _add_signal_to_explanation("brand_impersonation", all_signals, all_explanations)

    shortener_result = check_url_shortener(url)
    signal_details["shortener"] = shortener_result
    if shortener_result.get("is_shortened"):
        weighted_score += RISK_WEIGHTS["url_structure"] * SIGNAL_SCORES["url_shortener"]
        all_signals.append("url_shortener")
        _add_signal_to_explanation("url_shortener", all_signals, all_explanations)

    # redirect check
    redirect_result = check_redirects(url)
    signal_details["redirects"] = redirect_result
    redirect_count = redirect_result.get("redirect_count", 0)
    if redirect_count >= 5:
        weighted_score += RISK_WEIGHTS["url_structure"] * SIGNAL_SCORES["redirect_5_plus"]
        all_signals.append("redirect")
        _add_signal_to_explanation("redirect", all_signals, all_explanations)

    # ip_domain
    if ml_features.get("is_domain_ip", 0) > 0:
        weighted_score += RISK_WEIGHTS["url_structure"] * SIGNAL_SCORES["ip_domain"]
        all_signals.append("ip_domain")
        _add_signal_to_explanation("ip_domain", all_signals, all_explanations)

    # Phishing keywords
    kw_count = ml_features.get("num_phishing_keywords", 0)
    if kw_count >= 2:
        weighted_score += RISK_WEIGHTS["url_structure"] * SIGNAL_SCORES["keyword_density"]
        all_signals.append("keyword_phishing")
        _add_signal_to_explanation("keyword_phishing", all_signals, all_explanations)

    # Excessive path
    if ml_features.get("has_deep_path", 0) > 0:
        weighted_score += RISK_WEIGHTS["url_structure"] * SIGNAL_SCORES["excessive_path"]
        all_signals.append("excessive_path")
        _add_signal_to_explanation("excessive_path", all_signals, all_explanations)

    # No HTTPS
    if ml_features.get("is_http", 0) > 0 and "ssl_missing" not in all_signals:
        weighted_score += RISK_WEIGHTS["url_structure"] * SIGNAL_SCORES["no_https"]
        all_signals.append("ssl_missing")
        _add_signal_to_explanation("ssl_missing", all_signals, all_explanations)

    # Excessive subdomains
    if ml_features.get("subdomain_gt_3", 0) > 0:
        weighted_score += RISK_WEIGHTS["url_structure"] * SIGNAL_SCORES["excessive_subdomains"]
        all_signals.append("excessive_subdomains")
        _add_signal_to_explanation("excessive_subdomains", all_signals, all_explanations)

    result.risk_score = min(round(weighted_score), 100)
    result.risk_level = _score_to_level(result.risk_score)
    result.classification = _score_to_classification(result.risk_score)
    result.confidence = round(result.risk_score / 100.0, 4) if result.risk_score > 0 else 0.0
    result.recommendation = RECOMMENDATIONS.get(
        result.risk_level.lower(), "Appears safe"
    )
    result.signals = list(dict.fromkeys(all_signals))
    result.explanations = list(dict.fromkeys(all_explanations))
    result.signal_details = signal_details

    return result


def _add_signal_to_explanation(signal_key: str, signals: List[str], explanations: List[str]):
    if signal_key in signals:
        explanation = SIGNAL_EXPLANATIONS.get(signal_key)
        if explanation and explanation not in explanations:
            explanations.append(explanation)
