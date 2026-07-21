"""
Service layer for currency counterfeit detection.

Wires CNN prediction with visual feature extraction for enhanced analysis.
"""

from agents.currency_agent.feature_extractor import extract_features
from models.currency_cnn.predict import predict_currency


def analyze_currency(image_path: str, include_gradcam: bool = False):
    """
    Analyze a currency image using the trained CNN + visual feature extraction.

    Args:
        image_path: Path to the currency image.
        include_gradcam: Whether to include Grad-CAM visualization.

    Returns:
        dict with prediction, visual features, and optional Grad-CAM.
    """
    cnn_result = predict_currency(
        image_path,
        include_gradcam=include_gradcam,
        feature_extractor=None,
    )

    try:
        visual_features = extract_features(image_path)
        cnn_result["visual_features"] = visual_features
    except Exception:
        pass

    return cnn_result
