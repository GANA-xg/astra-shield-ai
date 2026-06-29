from pathlib import Path

import tensorflow as tf

from models.currency_cnn.dataset import load_datasets
from models.currency_cnn.model import build_currency_model


# -----------------------------
# Load datasets
# -----------------------------

train_dataset, validation_dataset, test_dataset = load_datasets()



# -----------------------------
# Build model
# -----------------------------

model = build_currency_model()


model = build_currency_model()

# -----------------------------
# Compile model
# -----------------------------

model.compile(
    optimizer=tf.keras.optimizers.Adam(
        learning_rate=1e-4
    ),
    loss="binary_crossentropy",
    metrics=[
        "accuracy",
        tf.keras.metrics.AUC(name="auc"),
    ],
)



# -----------------------------
# Callbacks
# -----------------------------

MODEL_DIR = Path(__file__).parent

callbacks = [

    tf.keras.callbacks.ModelCheckpoint(
        filepath=MODEL_DIR / "best_model.keras",
        monitor="val_accuracy",
        save_best_only=True,
        verbose=1,
    ),

    tf.keras.callbacks.EarlyStopping(
        monitor="val_loss",
        patience=5,
        restore_best_weights=True,
    ),

    tf.keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.2,
        patience=3,
        verbose=1,
    ),
]


# -----------------------------
# Train model
# -----------------------------

history = model.fit(
    train_dataset,
    validation_data=validation_dataset,
    epochs=20,
    callbacks=callbacks,
)


# -----------------------------
# Evaluate model
# -----------------------------

print("\nEvaluating on test dataset...")

results = model.evaluate(
    test_dataset,
    verbose=1,
)

print(f"\nTest Loss     : {results[0]:.4f}")
print(f"Test Accuracy : {results[1]:.4f}")
print(f"Test AUC      : {results[2]:.4f}")