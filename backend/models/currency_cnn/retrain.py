"""
Retrain currency CNN model.

Usage:
    python -m models.currency_cnn.retrain --data-dir /path/to/dataset
    python -m models.currency_cnn.retrain --data-dir /path/to/dataset --epochs 20

Expected dataset structure:
    data-dir/
        train/
            genuine/
                img1.jpg, img2.jpg, ...
            fake/
                img1.jpg, img2.jpg, ...
        validation/
            genuine/
                img1.jpg, img2.jpg, ...
            fake/
                img1.jpg, img2.jpg, ...
        test/
            genuine/
                img1.jpg, img2.jpg, ...
            fake/
                img1.jpg, img2.jpg, ...
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import tensorflow as tf


def load_dataset(data_dir, subset, image_size=(224, 224), batch_size=16):
    """Load a dataset subset."""
    subset_dir = Path(data_dir) / subset
    if not subset_dir.exists():
        raise FileNotFoundError(f"Dataset subset not found: {subset_dir}")

    dataset = tf.keras.utils.image_dataset_from_directory(
        subset_dir,
        image_size=image_size,
        batch_size=batch_size,
        label_mode="binary",
        shuffle=(subset == "train"),
    )

    preprocess = tf.keras.applications.efficientnet.preprocess_input
    dataset = dataset.map(lambda x, y: (preprocess(x), y))
    return dataset


def train(data_dir, epochs=15, learning_rate=1e-3, output_dir=None):
    """Train the currency CNN model."""
    from .model import build_currency_model

    if output_dir is None:
        output_dir = Path(__file__).parent
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Loading datasets...")
    train_ds = load_dataset(data_dir, "train")
    val_ds = load_dataset(data_dir, "validation")
    test_ds = load_dataset(data_dir, "test")

    print("Building model...")
    model = build_currency_model(include_denomination=False)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )

    model.summary()

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=5, restore_best_weights=True
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=3, min_lr=1e-7
        ),
        tf.keras.callbacks.ModelCheckpoint(
            str(output_dir / "best_model.keras"),
            monitor="val_accuracy",
            save_best_only=True,
        ),
    ]

    print(f"Training for {epochs} epochs...")
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        callbacks=callbacks,
    )

    print("Evaluating on test set...")
    test_loss, test_acc = model.evaluate(test_ds)
    print(f"Test accuracy: {test_acc:.4f}")

    report = {
        "test_loss": float(test_loss),
        "test_accuracy": float(test_acc),
        "epochs_trained": len(history.history["loss"]),
        "best_val_accuracy": float(max(history.history["val_accuracy"])),
        "training_samples": sum(1 for _ in train_ds.unbatch()),
        "validation_samples": sum(1 for _ in val_ds.unbatch()),
        "test_samples": sum(1 for _ in test_ds.unbatch()),
    }

    report_path = output_dir / "evaluation_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Report saved to {report_path}")

    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrain currency CNN")
    parser.add_argument("--data-dir", required=True, help="Path to dataset root")
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    train(args.data_dir, args.epochs, args.lr, args.output_dir)
