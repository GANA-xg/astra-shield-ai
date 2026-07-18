"""Phishing URL prediction module.

Loaded once at application startup. Never reloads per request.
Provides three-tier classification and SHAP-powered explanations.
"""

import json
import logging
import os
from typing import Dict, List, Optional, Tuple

import joblib
import numpy as np

from ml.features.extractor import extract_features

logger = logging.getLogger(__name__)

_MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
_MODEL_PATH = os.path.join(_MODEL_DIR, "phishing_xgboost.pkl")
_FEATURES_PATH = os.path.join(_MODEL_DIR, "feature_names.json")
_THRESHOLD_PATH = os.path.join(_MODEL_DIR, "optimal_threshold.json")

_model = None
_explainer = None
_feature_names: List[str] = []
_threshold: float = 0.5

SAFE_THRESHOLD = 0.45
PHISHING_THRESHOLD = 0.668


def load_model() -> bool:
    global _model, _explainer, _feature_names, _threshold

    try:
        import shap
        _model = joblib.load(_MODEL_PATH)
        with open(_FEATURES_PATH) as f:
            _feature_names = json.load(f)
        with open(_THRESHOLD_PATH) as f:
            _threshold = json.load(f)["optimal_threshold"]
        _explainer = shap.TreeExplainer(_model)
        logger.info(
            "Phishing model loaded: %d features, threshold=%.4f",
            len(_feature_names), _threshold,
        )
        return True
    except Exception as e:
        logger.error("Failed to load phishing model: %s", e)
        _model = None
        return False


def predict(
    url: str,
) -> Dict:
    if _model is None:
        return _fallback_prediction(url, "model_not_loaded")

    try:
        features = extract_features(url)
        vec = np.array([[features.get(f, 0.0) for f in _feature_names]])
        ph_prob = float(_model.predict_proba(vec)[0][1])
        safe_prob = 1.0 - ph_prob

        if ph_prob >= PHISHING_THRESHOLD:
            classification = "phishing"
            confidence = ph_prob
        elif ph_prob >= SAFE_THRESHOLD:
            classification = "suspicious"
            confidence = ph_prob
        else:
            classification = "safe"
            confidence = safe_prob

        shap_values = _explainer.shap_values(vec)

        vals = (
            shap_values[0]
            if isinstance(shap_values, list)
            else shap_values
        )
        vals = np.array(vals).flatten()
        feature_contributions = sorted(
            [
                {"feature": _feature_names[i], "contribution": round(float(vals[i]), 6)}
                for i in range(len(_feature_names))
            ],
            key=lambda x: abs(x["contribution"]),
            reverse=True,
        )

        return {
            "url": url,
            "phishing_probability": round(ph_prob, 6),
            "safe_probability": round(safe_prob, 6),
            "classification": classification,
            "confidence": round(float(confidence), 6),
            "risk_score": round(ph_prob * 100, 2),
            "top_contributors": feature_contributions[:10],
        }

    except Exception as e:
        logger.warning("Prediction failed for %s: %s", url, e)
        return _fallback_prediction(url, "prediction_error")


def _fallback_prediction(url: str, reason: str) -> Dict:
    return {
        "url": url,
        "phishing_probability": 0.0,
        "safe_probability": 1.0,
        "classification": "safe",
        "confidence": 1.0,
        "risk_score": 0.0,
        "fallback": True,
        "fallback_reason": reason,
        "top_contributors": [],
    }
