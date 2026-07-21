"""
Predict whether a currency note is genuine or counterfeit using a trained CNN.

Supports multi-class classification (genuine/fake + denomination)
and Grad-CAM visualization for explainability.
"""
from pathlib import Path
import sys

import numpy as np
import cv2

MODEL_PATH = Path(__file__).parent / "best_model.keras"
DENOMINATIONS = ["10", "20", "50", "100", "200", "500", "2000"]


def preprocess_image_for_model(image_path):
    """Load and preprocess image for EfficientNet input."""
    try:
        import tensorflow as tf
        from tensorflow.keras.preprocessing import image
    except ImportError:
        return None, "TensorFlow not installed"

    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_preprocessed = tf.keras.applications.efficientnet.preprocess_input(img_array)
    return np.expand_dims(img_preprocessed, axis=0), img_array


def predict_currency(image_path, include_gradcam=False, feature_extractor=None):
    """
    Predict whether the currency note is genuine or fake.

    Args:
        image_path: Path to the currency image.
        include_gradcam: Whether to generate Grad-CAM heatmap.
        feature_extractor: Optional feature extractor function.

    Returns:
        dict with prediction results.
    """
    try:
        import tensorflow as tf
    except ImportError:
        return {
            "prediction": "error",
            "confidence": 0.0,
            "detail": "TensorFlow not installed — cannot run currency detection",
        }

    if not Path(image_path).exists():
        return {
            "prediction": "error",
            "confidence": 0.0,
            "detail": f"Image file not found: {image_path}",
        }

    if not MODEL_PATH.exists():
        return {
            "prediction": "error",
            "confidence": 0.0,
            "detail": f"Model file not found: {MODEL_PATH}",
        }

    model = tf.keras.models.load_model(MODEL_PATH)
    img_preprocessed, img_raw = preprocess_image_for_model(image_path)
    if img_preprocessed is None:
        return {"prediction": "error", "confidence": 0.0, "detail": img_raw}

    predictions = model.predict(img_preprocessed, verbose=0)

    if isinstance(predictions, dict):
        classifier_pred = predictions["classifier"][0]
        denomination_pred = predictions.get("denomination", None)
        if denomination_pred is not None:
            denomination_pred = denomination_pred[0]
    else:
        classifier_pred = predictions[0]
        denomination_pred = None

    if len(classifier_pred) == 1:
        genuine_prob = float(classifier_pred[0])
        fake_prob = 1.0 - genuine_prob
    else:
        fake_prob = float(classifier_pred[0])
        genuine_prob = float(classifier_pred[1]) if len(classifier_pred) > 1 else 1.0 - fake_prob

    is_genuine = genuine_prob >= fake_prob
    confidence = max(genuine_prob, fake_prob) * 100

    result = {
        "prediction": "genuine" if is_genuine else "fake",
        "confidence": round(float(confidence), 2),
        "genuine_probability": round(float(genuine_prob * 100), 2),
        "fake_probability": round(float(fake_prob * 100), 2),
    }

    if denomination_pred is not None:
        denom_idx = int(np.argmax(denomination_pred))
        denom_conf = float(denomination_pred[denom_idx]) * 100
        result["denomination"] = DENOMINATIONS[denom_idx]
        result["denomination_confidence"] = round(denom_conf, 2)

    if feature_extractor is not None:
        try:
            features = feature_extractor(image_path)
            result["visual_features"] = features
        except Exception:
            pass

    if include_gradcam:
        try:
            from .model import compute_gradcam, apply_gradcam_overlay
            heatmap = compute_gradcam(model, img_preprocessed, class_index=0)
            original_rgb = cv2.cvtColor(
                cv2.imread(image_path), cv2.COLOR_BGR2RGB
            )
            overlay = apply_gradcam_overlay(original_rgb, heatmap)

            import base64
            _, buffer = cv2.imencode(".png", cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
            gradcam_b64 = base64.b64encode(buffer).decode("utf-8")
            result["gradcam_overlay"] = gradcam_b64
        except Exception as e:
            result["gradcam_error"] = str(e)

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m models.currency_cnn.predict <image_path> [--gradcam]")
        sys.exit(1)

    image_path = sys.argv[1]
    include_gradcam = "--gradcam" in sys.argv
    result = predict_currency(image_path, include_gradcam=include_gradcam)
    print(f"\nPrediction    : {result['prediction']}")
    print(f"Confidence    : {result['confidence']:.2f}%")
    if "denomination" in result:
        print(f"Denomination  : ₹{result['denomination']} ({result['denomination_confidence']:.2f}%)")
    if "gradcam_overlay" in result:
        print("Grad-CAM heatmap generated")
