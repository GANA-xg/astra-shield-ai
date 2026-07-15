"""
Load the training, validation, and test datasets.

Returns:
    train_dataset,
    validation_dataset,
    test_dataset
"""

from pathlib import Path

import tensorflow as tf


# Dataset location
PROJECT_ROOT = Path(__file__).resolve().parents[4]

DATASET_ROOT = (
    PROJECT_ROOT
    / "currency-research"
    / "datasets"
)

TRAIN_DIR = DATASET_ROOT / "train"

VALIDATION_DIR = DATASET_ROOT / "validation"

TEST_DIR = DATASET_ROOT / "test"

IMAGE_SIZE = (224, 224)

BATCH_SIZE = 16


def load_datasets():
    """
    Load training and validation datasets.

    Returns:
        train_dataset,
        validation_dataset
    """

    train_dataset = (
        tf.keras.utils.image_dataset_from_directory(
            TRAIN_DIR,
            image_size=IMAGE_SIZE,
            batch_size=BATCH_SIZE,
            label_mode="binary",
            shuffle=True,
        )
    )

    validation_dataset = (
        tf.keras.utils.image_dataset_from_directory(
            VALIDATION_DIR,
            image_size=IMAGE_SIZE,
            batch_size=BATCH_SIZE,
            label_mode="binary",
            shuffle=False,
        )
    )

    preprocess = tf.keras.applications.efficientnet.preprocess_input

    train_dataset = train_dataset.map(
        lambda x, y: (
            preprocess(x),
            y,
        )
    )

    validation_dataset = validation_dataset.map(
        lambda x, y: (
            preprocess(x),
            y,
        )
    )
    

    test_dataset = (
        tf.keras.utils.image_dataset_from_directory(
            TEST_DIR,
            image_size=IMAGE_SIZE,
            batch_size=BATCH_SIZE,
            label_mode="binary",
            shuffle=False,
        )
    )

    test_dataset = test_dataset.map(
        lambda x, y: (
            preprocess(x),
            y,
        )
    )


    return (
        train_dataset,
        validation_dataset,
        test_dataset,
    )