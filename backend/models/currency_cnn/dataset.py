"""
Load the training, validation, and test datasets for currency detection.

Supports two dataset formats:
1. Binary: train/genuine/, train/fake/
2. Multi-class with denominations: train/genuine_10/, train/fake_50/, etc.
"""

from pathlib import Path

import tensorflow as tf


PROJECT_ROOT = Path(__file__).resolve().parents[4]
DATASET_ROOT = PROJECT_ROOT / "currency-research" / "datasets"

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 16


def load_datasets(data_dir=None):
    """
    Load training, validation, and test datasets.

    Args:
        data_dir: Override dataset root directory.

    Returns:
        (train_dataset, validation_dataset, test_dataset)
    """
    root = Path(data_dir) if data_dir else DATASET_ROOT

    train_dir = root / "train"
    val_dir = root / "validation"
    test_dir = root / "test"

    preprocess = tf.keras.applications.efficientnet.preprocess_input

    def load_split(split_dir, shuffle=False):
        ds = tf.keras.utils.image_dataset_from_directory(
            split_dir,
            image_size=IMAGE_SIZE,
            batch_size=BATCH_SIZE,
            label_mode="binary",
            shuffle=shuffle,
        )
        return ds.map(lambda x, y: (preprocess(x), y))

    train_ds = load_split(train_dir, shuffle=True)
    val_ds = load_split(val_dir, shuffle=False)
    test_ds = load_split(test_dir, shuffle=False)

    return train_ds, val_ds, test_ds
