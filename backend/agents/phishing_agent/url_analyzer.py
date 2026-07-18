"""URL analysis orchestrator for the phishing agent.

Uses the Risk Fusion Engine to combine ML predictions with external signals
(Safe Browsing, VirusTotal, SSL, WHOIS, DNS, URL structure analysis).
"""

import logging
from typing import Dict, List, Optional

from .feature_extractor import extract_features as old_extract_features
from .safe_browsing import check_google_safe_browsing
from .blacklist_checker import check_blacklists
from .risk_fusion import run_risk_fusion
from .risk_signals import build_explanations
from ml.predict import load_model, predict as ml_predict

logger = logging.getLogger(__name__)

_model_loaded = False


def _ensure_model():
    global _model_loaded
    if not _model_loaded:
        _model_loaded = load_model()
        if not _model_loaded:
            logger.warning("New ML model failed to load, falling back to default")


def analyze_url(url: str) -> dict:
    """
    Analyze a URL using the complete phishing detection pipeline.

    Returns a dictionary containing:
    - normalized URL
    - domain
    - extracted features
    - safe_browsing
    - blacklists
    - ml_probability
    - Risk Fusion results (risk_score, risk_level, signals, recommendation,
      classification, confidence, ml_score, google_safe_browsing, virus_total,
      ssl_status, domain_age, brand_similarity, explanations)
    """

    _ensure_model()

    # Step 1: Extract features (old extractor for backward compat)
    features = old_extract_features(url)
    normalized_url = features.get("url", url)
    domain = features.get("domain", "")

    # Step 2: Google Safe Browsing
    safe_browsing_result = check_google_safe_browsing(normalized_url)

    # Step 3: Blacklist aggregation
    blacklist_results = check_blacklists(
        normalized_url,
        safe_browsing_result=safe_browsing_result,
    )

    # Step 4: XGBoost prediction
    ml_result = ml_predict(url)
    ml_probability = ml_result["phishing_probability"]
    shap_text = build_explanations(ml_result)

    # Step 5: Risk Fusion — combines all signals
    from core.config import settings

    fusion = run_risk_fusion(
        url=url,
        ml_probability=ml_probability,
        safe_browsing_result=safe_browsing_result,
        blacklist_results=blacklist_results,
        vt_api_key=settings.VIRUSTOTAL_API_KEY,
        shap_explanations=shap_text,
    )

    return {
        "url": normalized_url,
        "domain": domain,
        "features": features,
        "safe_browsing": safe_browsing_result,
        "blacklists": blacklist_results,
        "ml_probability": ml_probability,
        "ml_classification": ml_result.get("classification", "unknown"),
        "ml_top_contributors": ml_result.get("top_contributors", []),
        "classification": fusion.classification,
        "risk_score": fusion.risk_score,
        "risk_level": fusion.risk_level,
        "confidence": fusion.confidence,
        "ml_score": fusion.ml_score,
        "google_safe_browsing": fusion.google_safe_browsing,
        "virus_total": fusion.virus_total,
        "ssl_status": fusion.ssl_status,
        "domain_age": fusion.domain_age,
        "brand_similarity": fusion.brand_similarity,
        "signals": fusion.signals,
        "recommendation": fusion.recommendation,
        "explanations": fusion.explanations,
    }