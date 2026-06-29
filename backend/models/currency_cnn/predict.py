from pathlib import Path
import sys

import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image

MODEL_PATH = (
    Path(__file__).parent
    / "best_model.keras"
)

model = tf.keras.models.load_model(MODEL_PATH)

def load_image(image_path):
    """
    Load and preprocess a currency image.
    """

    img = image.load_img(
        image_path,
        target_size=(224, 224),
    )

    img = image.img_to_array(img)

    img = tf.keras.applications.efficientnet.preprocess_input(
        img
    )

    img = np.expand_dims(
        img,
        axis=0,
    )

    return img


def predict_currency(image_path):
    """
    Predict whether the currency note is genuine or fake.
    """

    img = load_image(image_path)

    prediction = model.predict(
        img,
        verbose=0,
    )[0][0]

    if prediction >= 0.5:
        label = "Genuine"
        confidence = prediction * 100
    else:
        label = "Fake"
        confidence = (1 - prediction) * 100

    return {
        "prediction": label.lower(),
        "confidence": round(confidence, 2),
    }



if __name__ == "__main__":

    if len(sys.argv) != 2:
        print(
            "Usage: python -m models.currency_cnn.predict <image_path>"
        )
        sys.exit(1)

    image_path = sys.argv[1]

    result = predict_currency(image_path)

    print(f"\nPrediction : {result['prediction']}")
    print(f"Confidence : {result['confidence']:.2f}%")