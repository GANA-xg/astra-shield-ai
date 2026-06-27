"""URL analysis orchestrator for the phishing agent."""

from .feature_extractor import extract_features
from .safe_browsing import check_google_safe_browsing
from .blacklist_checker import check_blacklists
from .risk_engine import calculate_risk
from .xgboost_model import predict_probability


def analyze_url(url: str) -> dict:
    """
    Analyze a URL using the complete phishing detection pipeline.

    Returns a dictionary containing:
    - normalized URL
    - domain
    - extracted features
    - Safe Browsing result
    - blacklist results
    - final risk assessment
    """

    # Step 1: Extract features
    features = extract_features(url)

    normalized_url = features.get("url", url)
    domain = features.get("domain", "")

    # Step 2: Google Safe Browsing
    safe_browsing_result = check_google_safe_browsing(normalized_url)

    # Step 3: Blacklist aggregation (reuse Safe Browsing result)
    blacklist_results = check_blacklists(
        normalized_url,
        safe_browsing_result=safe_browsing_result,
    )

    # Step 4: XGBoost prediction
    ml_probability = predict_probability(features)

    # Step 5: LLM placeholder
    llm_result = None

    # Step 6: Final risk calculation
    risk_result = calculate_risk(
        features=features,
        ml_probability=ml_probability,
        blacklist_results=blacklist_results,
        safe_browsing_result=safe_browsing_result,
        llm_result=llm_result,
    )

    return {
        "url": normalized_url,
        "domain": domain,
        "features": features,
        "safe_browsing": safe_browsing_result,
        "blacklists": blacklist_results,
        "ml_probability": ml_probability,
        **risk_result,
    }