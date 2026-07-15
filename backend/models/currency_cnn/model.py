"""
CNN model for Indian Currency Counterfeit Detection.

This module defines the EfficientNetB3-based classifier.
"""

import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras import models


def build_currency_model(
    input_shape=(224, 224, 3)
):
    """
    Build the CNN model using EfficientNetB3.

    Args:
        input_shape:
            Shape of the input image.

    Returns:
        Compiled TensorFlow model.
    """

    base_model = tf.keras.applications.EfficientNetB3(
        include_top=False,
        weights="imagenet",
        input_shape=input_shape,
    )

    # Freeze pretrained layers
    base_model.trainable = False

    model = models.Sequential(
        [
            base_model,

            layers.GlobalAveragePooling2D(),

            layers.BatchNormalization(),

            layers.Dense(
                256,
                activation="relu",
            ),

            layers.Dropout(
                0.4,
            ),

            layers.Dense(
                1,
                activation="sigmoid",
            ),
        ]
    )


    return model