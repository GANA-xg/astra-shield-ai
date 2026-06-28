import os
import joblib
import pandas as pd

from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report


# -----------------------------
# Paths
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATASET_PATH = os.path.join(
    BASE_DIR,
    "datasets",
    "phishing",
    "extracted_features.csv",
)

MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "phishing_xgb.pkl")


# -----------------------------
# Load Dataset
# -----------------------------
print("Loading dataset...")

df = pd.read_csv(DATASET_PATH)


# -----------------------------
# Target Column
# -----------------------------
TARGET_COLUMN = "label"      # Change if needed

X = df.drop(columns=[TARGET_COLUMN])
y = df[TARGET_COLUMN]


# -----------------------------
# Train/Test Split
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)


# -----------------------------
# Model
# -----------------------------
model = XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="logloss",
    random_state=42,
)

print("Training model...")

model.fit(X_train, y_train)


# -----------------------------
# Evaluation
# -----------------------------
predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("\nAccuracy:", accuracy)

print("\nClassification Report:\n")
print(classification_report(y_test, predictions))


# -----------------------------
# Save Model
# -----------------------------
os.makedirs(MODEL_DIR, exist_ok=True)

joblib.dump(model, MODEL_PATH)

print(f"\nModel saved to:\n{MODEL_PATH}")