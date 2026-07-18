"""Feature extraction orchestrator.

Single entry point for extracting features from a URL.
Used during BOTH training and inference — never duplicate this logic.
All ~80+ features are reproducible from the raw URL string alone.
"""

import logging
from typing import Dict, List

from ml.features.lexical import extract_lexical_features
from ml.features.domain import extract_domain_features
from ml.features.security import extract_security_features

logger = logging.getLogger(__name__)


FEATURE_NAMES: List[str] = []


def extract_features(url: str) -> Dict[str, float]:
    """Extract all features from a URL.

    This is the SINGLE source of truth for feature engineering.
    Every feature returned here is reproducible from the raw URL string alone.

    Args:
        url: The URL to extract features from.

    Returns:
        A flat dictionary of feature_name -> float value.
    """
    features: Dict[str, float] = {}

    features.update(extract_lexical_features(url))
    features.update(extract_domain_features(url))
    features.update(extract_security_features(url))

    # Fix key conflicts (security.py's hyphen_in_domain vs domain.py's domain_has_hyphen)
    if "hyphen_in_domain" in features and "domain_has_hyphen" in features:
        del features["hyphen_in_domain"]

    # Verify no NaN or inf values
    for k, v in list(features.items()):
        if v != v or v == float("inf") or v == float("-inf"):
            features[k] = 0.0

    return features


def get_feature_vector(url: str) -> List[float]:
    """Extract features as a fixed-order list (for model input)."""
    features = extract_features(url)
    global FEATURE_NAMES
    if not FEATURE_NAMES:
        FEATURE_NAMES = sorted(features.keys())
    return [features[name] for name in FEATURE_NAMES]


# Populate FEATURE_NAMES with a sample URL
_reference = extract_features("https://example.com/test")
FEATURE_NAMES = sorted(_reference.keys())
