"""
CNN model for Indian Currency Counterfeit Detection.

Supports multi-class output: genuine/fake classification + denomination detection.
Includes Grad-CAM visualization for explainability.
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models


DENOMINATIONS = ["10", "20", "50", "100", "200", "500", "2000"]
NUM_DENOMINATIONS = len(DENOMINATIONS)


def build_currency_model(
    input_shape=(224, 224, 3),
    num_classes=2,
    include_denomination=True,
):
    """
    Build the CNN model using EfficientNetB3.

    Args:
        input_shape: Shape of the input image.
        num_classes: Number of output classes (2 for binary, or more).
        include_denomination: Whether to include denomination head.

    Returns:
        Dictionary with 'classifier' and optional 'denomination' models.
    """
    base_model = tf.keras.applications.EfficientNetB3(
        include_top=False,
        weights="imagenet",
        input_shape=input_shape,
    )
    base_model.trainable = False

    inputs = layers.Input(shape=input_shape)
    x = base_model(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.BatchNormalization()(x)
    shared = layers.Dense(256, activation="relu")(x)
    shared = layers.Dropout(0.4)(shared)

    classifier_output = layers.Dense(
        num_classes, activation="softmax" if num_classes > 2 else "sigmoid", name="classifier"
    )(shared)

    outputs = {"classifier": classifier_output}

    if include_denomination:
        denom_dense = layers.Dense(128, activation="relu")(shared)
        denom_output = layers.Dense(
            NUM_DENOMINATIONS, activation="softmax", name="denomination"
        )(denom_dense)
        outputs["denomination"] = denom_output

    model = models.Model(inputs=inputs, outputs=outputs)
    return model


def build_gradcam_model(model, last_conv_layer_name="top_conv"):
    """
    Build a model that exposes the last conv layer output for Grad-CAM.

    Args:
        model: Trained Keras model.
        last_conv_layer_name: Name of the last convolutional layer.

    Returns:
        Keras model that outputs (classifier_pred, conv_features).
    """
    base_model = None
    for layer in model.layers:
        if hasattr(layer, "layers"):
            base_model = layer
            break

    if base_model is None:
        return None

    grad_model = models.Model(
        inputs=model.input,
        outputs=[
            base_model.get_layer(last_conv_layer_name).output,
            model.output["classifier"],
        ],
    )
    return grad_model


def compute_gradcam(model, image, class_index=0, last_conv_layer_name="top_conv"):
    """
    Compute Grad-CAM heatmap for a given image.

    Args:
        model: Trained Keras model.
        image: Preprocessed image array (1, 224, 224, 3).
        class_index: Target class index for visualization.
        last_conv_layer_name: Name of last conv layer.

    Returns:
        numpy array heatmap (224, 224).
    """
    grad_model = models.Model(
        inputs=model.input,
        outputs=[
            model.get_layer("efficientnetb3").get_layer(last_conv_layer_name).output,
            model.output["classifier"],
        ],
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(image)
        if isinstance(predictions, dict):
            predictions = predictions["classifier"]
        loss = predictions[:, class_index]

    grads = tape.gradient(loss, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    conv_outputs = conv_outputs[0]
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
    return heatmap.numpy()


def apply_gradcam_overlay(original_image, heatmap, alpha=0.4):
    """
    Apply Grad-CAM heatmap overlay on original image.

    Args:
        original_image: Original RGB image (H, W, 3), values 0-255.
        heatmap: Grad-CAM heatmap (H, W), values 0-1.
        alpha: Transparency of heatmap overlay.

    Returns:
        numpy array (H, W, 3) with heatmap overlay.
    """
    import cv2

    heatmap_resized = cv2.resize(heatmap, (original_image.shape[1], original_image.shape[0]))
    heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET)
    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)

    overlay = original_image.astype(np.float32) * (1 - alpha) + heatmap_colored.astype(np.float32) * alpha
    overlay = np.clip(overlay, 0, 255).astype(np.uint8)
    return overlay
