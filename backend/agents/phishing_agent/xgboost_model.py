"""
XGBoost model loader and predictor.
"""

import os
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "phishing_xgb.pkl")

FEATURE_COLUMNS = [
    "url_length",
    "domain_length",
    "path_length",
    "query_length",
    "subdomain_count",
    "dot_count",
    "slash_count",
    "hyphen_count",
    "underscore_count",
    "digit_count",
    "letter_count",
    "special_char_count",
    "query_parameter_count",
    "hostname_entropy",
    "max_repeated_characters",
    "keyword_count",
    "https",
    "has_at_symbol",
    "ip_url",
    "punycode",
    "suspicious_tld",
]

_model = None

try:
    _model = joblib.load(MODEL_PATH)
    print(f"Loaded XGBoost model from {MODEL_PATH}")
except Exception as e:
    print(f"Warning: Could not load XGBoost model: {e}")


def predict_probability(features: dict) -> float:
    """Return phishing probability between 0.0 and 1.0."""
    if _model is None:
        raise RuntimeError(f"Model not loaded. Expected at: {MODEL_PATH}")

    row = {col: features.get(col, 0) for col in FEATURE_COLUMNS}
    df = pd.DataFrame([row])
    probability = _model.predict_proba(df)[0][1]
    return float(probability)


def predict_label(features: dict) -> bool:
    """Return True if predicted as phishing."""
    return predict_probability(features) >= 0.5
