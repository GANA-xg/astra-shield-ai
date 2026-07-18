"""Tests for the ML-based phishing detection pipeline."""

import json
import os
import sys
from pathlib import Path

# Ensure the backend directory is on sys.path
BACKEND_DIR = Path(__file__).parent
sys.path.insert(0, str(BACKEND_DIR))

import joblib
import numpy as np
import pytest

from ml.features.extractor import extract_features
from ml.features.lexical import extract_lexical_features
from ml.features.domain import extract_domain_features
from ml.features.security import extract_security_features
from ml.predict import load_model, predict


# ── Fixtures ──────────────────────────────────────────────────────────────


def _model_loaded():
    result = load_model()
    if not result:
        pytest.skip("Model file not found — run training first")
    return result


# ── Feature Extraction Tests ──────────────────────────────────────────────


class TestFeatureExtraction:
    """Every feature must be reproducible from the URL string alone."""

    def test_lexical_features_return_all_keys(self):
        feats = extract_lexical_features("https://example.com/test?q=1")
        assert len(feats) > 20
        assert "url_len" in feats
        assert "num_digits" in feats
        assert "num_slashes" in feats
        assert "num_at" in feats
        assert "has_phishing_keyword" in feats
        assert isinstance(feats["url_len"], float)

    def test_domain_features_return_all_keys(self):
        feats = extract_domain_features("https://www.amazon.com/path")
        assert "domain_len" in feats
        assert "subdomain_count" in feats
        assert "tld_length" in feats
        assert isinstance(feats["domain_len"], float)

    def test_security_features_return_all_keys(self):
        feats = extract_security_features("https://bit.ly/3xK9mN2")
        assert "is_https" in feats
        assert "is_shortened_url" in feats
        assert isinstance(feats["is_https"], float)

    def test_extract_features_integration(self):
        feats = extract_features("https://www.paypal.com/signin")
        assert len(feats) > 80
        assert feats["url_len"] > 0
        assert feats["domain_len"] > 0

    def test_no_nan_or_inf(self):
        feats = extract_features("http://example.com")
        for k, v in feats.items():
            assert v == v, f"{k} is NaN"
            assert v != float("inf"), f"{k} is inf"
            assert v != float("-inf"), f"{k} is -inf"

    def test_same_url_produces_same_features(self):
        url = "https://www.google.com/search"
        f1 = extract_features(url)
        f2 = extract_features(url)
        for k in f1:
            assert f1[k] == f2[k], f"{k} differs: {f1[k]} != {f2[k]}"

    def test_phishing_keyword_detection(self):
        feats = extract_features("http://verify-login-secure-bank.ml/")
        assert feats["has_phishing_keyword"] == 1.0
        assert feats["num_phishing_keywords"] >= 1

    def test_brand_name_detection_with_rapidfuzz(self):
        feats = extract_features("https://www.amazon.com/dp/B08N5WRWNW")
        assert feats["has_brand_name"] == 1.0
        assert feats["brand_similarity_max"] >= 0.8

    def test_ip_url_detection(self):
        feats = extract_features("http://192.168.1.1/admin/")
        assert feats["is_domain_ip"] == 1.0

    def test_shortened_url_detection(self):
        feats = extract_features("http://bit.ly/3xK9mN2")
        assert feats["is_shortened_url"] == 1.0

    def test_homograph_detection(self):
        feats = extract_features("https://xn--mgba3a4e16a.com/")
        assert feats["punycode"] == 1.0


# ── Model Loading Tests ───────────────────────────────────────────────────


class TestModelLoading:
    def test_load_model(self):
        _model_loaded()

    def test_feature_names_json_exists(self):
        path = BACKEND_DIR / "ml" / "models" / "feature_names.json"
        assert path.exists()
        with open(path) as f:
            names = json.load(f)
        assert len(names) >= 70

    def test_optimal_threshold_json_exists(self):
        path = BACKEND_DIR / "ml" / "models" / "optimal_threshold.json"
        assert path.exists()
        with open(path) as f:
            data = json.load(f)
        assert 0 < data["optimal_threshold"] < 1

    def test_model_file_exists(self):
        path = BACKEND_DIR / "ml" / "models" / "phishing_xgboost.pkl"
        assert path.exists()
        assert path.stat().st_size > 1_000_000  # at least 1 MB


# ── Prediction Tests ──────────────────────────────────────────────────────


class TestPrediction:
    def _predict(self, url):
        _model_loaded()
        return predict(url)

    def test_safe_url_returns_low_probability(self):
        result = self._predict("https://github.com/user/repo")
        assert result["phishing_probability"] < 0.5

    def test_output_contains_all_keys(self):
        result = self._predict("https://example.com")
        assert "url" in result
        assert "phishing_probability" in result
        assert "safe_probability" in result
        assert "classification" in result
        assert "confidence" in result
        assert "risk_score" in result
        assert "top_contributors" in result

    def test_classification_is_valid(self):
        result = self._predict("https://github.com")
        assert result["classification"] in ("safe", "suspicious", "phishing")

    def test_safe_url_has_top_contributors(self):
        result = self._predict("https://github.com")
        assert len(result["top_contributors"]) == 10
        for c in result["top_contributors"]:
            assert "feature" in c
            assert "contribution" in c

    def test_probabilities_sum_to_one(self):
        result = self._predict("https://github.com")
        total = result["phishing_probability"] + result["safe_probability"]
        assert abs(total - 1.0) < 0.001

    def test_suspicious_url(self):
        result = self._predict("https://www.amazon.com/login")
        if result["phishing_probability"] >= 0.45:
            assert result["classification"] in ("suspicious", "phishing")

    def test_malformed_url_fallback(self):
        result = self._predict("not-a-valid-url!")
        assert result["classification"] == "safe"

    def test_deterministic_output(self):
        r1 = self._predict("https://www.python.org/downloads/")
        r2 = self._predict("https://www.python.org/downloads/")
        assert r1["phishing_probability"] == r2["phishing_probability"]

    def test_safe_thresholds(self):
        safe_urls = [
            "https://github.com",
            "https://stackoverflow.com/questions/1",
            "https://twitter.com/home",
            "http://bit.ly/3xK9mN2",
        ]
        for url in safe_urls:
            result = self._predict(url)
            if result.get("fallback"):
                continue
            assert result["phishing_probability"] < 0.5, f"{url} should be safe"


# ── URL Analyzer Integration Tests ────────────────────────────────────────


class TestAnalyzerIntegration:
    def test_analyzer_uses_new_model(self):
        from agents.phishing_agent.url_analyzer import analyze_url
        result = analyze_url("https://github.com")
        assert "ml_probability" in result
        assert "ml_classification" in result
        assert isinstance(result["ml_probability"], float)
        assert result["ml_classification"] in ("safe", "suspicious", "phishing")

    def test_analyzer_returns_risk_score(self):
        from agents.phishing_agent.url_analyzer import analyze_url
        result = analyze_url("http://amaz0n-verify-login.ml/account/update")
        assert "risk_score" in result
        assert "risk_level" in result
        assert "signals" in result
        assert isinstance(result["risk_score"], int)

    def test_analyzer_handles_normal_urls(self):
        from agents.phishing_agent.url_analyzer import analyze_url
        result = analyze_url("https://www.google.com/search?q=python")
        assert "domain" in result
        assert "url" in result
        assert "features" in result
