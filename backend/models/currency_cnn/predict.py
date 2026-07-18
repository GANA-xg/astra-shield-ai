"""
Predict whether a currency note is genuine or counterfeit using a trained CNN.
"""
from pathlib import Path
import sys

MODEL_PATH = (
    Path(__file__).parent
    / "best_model.keras"
)


def predict_currency(image_path):
    """
    Predict whether the currency note is genuine or fake.

    Args:
        image_path: Path to the currency image.

    Returns:
        dict with 'prediction' and 'confidence' keys.
    """
    import numpy as np

    try:
        import tensorflow as tf
        from tensorflow.keras.preprocessing import image
    except ImportError:
        return {
            "prediction": "error",
            "confidence": 0.0,
            "detail": "TensorFlow not installed — cannot run currency detection",
        }

    model = tf.keras.models.load_model(MODEL_PATH)

    img = image.load_img(image_path, target_size=(224, 224))
    img = image.img_to_array(img)
    img = tf.keras.applications.efficientnet.preprocess_input(img)
    img = np.expand_dims(img, axis=0)

    prediction = model.predict(img, verbose=0)[0][0]

    if prediction >= 0.5:
        label = "Genuine"
        confidence = prediction * 100
    else:
        label = "Fake"
        confidence = (1 - prediction) * 100

    return {
        "prediction": label.lower(),
        "confidence": round(float(confidence), 2),
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m models.currency_cnn.predict <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    result = predict_currency(image_path)
    print(f"\nPrediction : {result['prediction']}")
    print(f"Confidence : {result['confidence']:.2f}%")
