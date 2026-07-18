"""XGBoost phishing URL classifier training pipeline.

Usage:
    python -m ml.training.train

Generates:
    - ml/models/phishing_xgboost.pkl       (trained model)
    - ml/models/feature_names.json          (ordered feature names)
    - ml/models/training_metadata.json      (best params, metrics, dates)
    - ml/evaluation/classification_report.txt
    - ml/evaluation/confusion_matrix.png
    - ml/evaluation/roc_curve.png
    - ml/evaluation/feature_importance.png
    - ml/evaluation/shap_summary.png
"""

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import (
    StratifiedShuffleSplit,
    RandomizedSearchCV,
    cross_val_score,
)
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
    roc_curve,
)
import xgboost as xgb
from xgboost import XGBClassifier
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Ensure we can import from the project root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.features.extractor import extract_features, FEATURE_NAMES

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "ml" / "datasets" / "PhiUSIIL_Phishing_URL_Dataset.csv"
MODEL_DIR = PROJECT_ROOT / "ml" / "models"
EVAL_DIR = PROJECT_ROOT / "ml" / "evaluation"
MODEL_PATH = MODEL_DIR / "phishing_xgboost.pkl"
FEATURE_NAMES_PATH = MODEL_DIR / "feature_names.json"
METADATA_PATH = MODEL_DIR / "training_metadata.json"

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(EVAL_DIR, exist_ok=True)


def build_training_dataset(csv_path: str, sample_size: int = None) -> pd.DataFrame:
    """Build a training dataset with URL-reproducible features only.

    Reads the PhiUSIIL CSV, extracts features from each URL using the same
    pipeline used during inference, and discards dataset-specific columns.

    Args:
        csv_path: Path to the PhiUSIIL CSV file.
        sample_size: If set, use only this many rows (for testing).

    Returns:
        DataFrame with extracted features + 'label' column.
    """
    logger.info("Loading dataset from %s", csv_path)
    df = pd.read_csv(csv_path, encoding="utf-8")

    if sample_size:
        df = df.sample(n=sample_size, random_state=42)

    total = len(df)
    logger.info("Dataset loaded: %d rows, %d columns", total, len(df.columns))
    label_counts = df["label"].value_counts()
    logger.info("Label distribution: %s", label_counts.to_dict())

    rows: List[Dict[str, float]] = []
    start = time.time()
    for idx, row in df.iterrows():
        url = str(row["URL"]).strip()
        label = int(row["label"])
        try:
            feats = extract_features(url)
            feats["label"] = float(label)
            rows.append(feats)
        except Exception as e:
            logger.warning("Failed to extract features for URL row %d: %s", idx, e)

        if (idx + 1) % 25000 == 0:
            elapsed = time.time() - start
            rate = (idx + 1) / elapsed
            logger.info("Processed %d/%d (%.1f%%) — %.0f rows/sec", idx + 1, total, 100 * (idx + 1) / total, rate)

    elapsed = time.time() - start
    logger.info("Feature extraction complete: %d rows in %.1fs (%.0f rows/sec)", len(rows), elapsed, len(rows) / elapsed)

    result_df = pd.DataFrame(rows)
    logger.info("Training dataset shape: %s", result_df.shape)
    return result_df


def train_xgboost(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    feature_names: List[str],
) -> Tuple[XGBClassifier, Dict]:
    """Train an XGBoost classifier with hyperparameter tuning.

    Args:
        X_train: Training features.
        y_train: Training labels.
        X_val: Validation features.
        y_val: Validation labels.
        feature_names: Ordered list of feature names.

    Returns:
        Tuple of (trained model, best parameters dict).
    """
    logger.info("Training XGBoost classifier...")
    logger.info("X_train shape: %s, X_val shape: %s", X_train.shape, X_val.shape)

    base_model = XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1,
        verbosity=0,
        use_label_encoder=False,
    )

    param_dist = {
        "n_estimators": [100, 200, 300, 500],
        "max_depth": [3, 4, 6, 8, 10],
        "learning_rate": [0.01, 0.05, 0.1, 0.2],
        "subsample": [0.6, 0.8, 1.0],
        "colsample_bytree": [0.6, 0.8, 1.0],
        "min_child_weight": [1, 3, 5, 7],
        "gamma": [0, 0.1, 0.2, 0.5],
        "reg_alpha": [0, 0.01, 0.1, 1.0],
        "reg_lambda": [0, 0.01, 0.1, 1.0],
    }

    logger.info("Running RandomizedSearchCV with 30 iterations...")

    search = RandomizedSearchCV(
        estimator=base_model,
        param_distributions=param_dist,
        n_iter=30,
        scoring="roc_auc",
        cv=5,
        verbose=1,
        random_state=42,
        n_jobs=-1,
    )

    search.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False,
    )

    best_model = search.best_estimator_
    best_params = search.best_params_
    logger.info("Best parameters: %s", best_params)
    logger.info("Best CV ROC AUC: %.4f", search.best_score_)

    # Cross-validation scores
    cv_scores = cross_val_score(
        best_model, X_train, y_train, cv=5, scoring="roc_auc", n_jobs=-1
    )
    logger.info("5-fold CV ROC AUC scores: %s", cv_scores)
    logger.info("5-fold CV ROC AUC mean: %.4f (std: %.4f)", cv_scores.mean(), cv_scores.std())

    return best_model, best_params, cv_scores


def evaluate_model(
    model: XGBClassifier,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    feature_names: List[str],
):
    """Evaluate the model and save all evaluation artifacts.

    Args:
        model: Trained XGBoost model.
        X_test: Test features.
        y_test: Test labels.
        feature_names: Ordered list of feature names.
    """
    logger.info("Evaluating model on test set...")

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_proba)
    cm = confusion_matrix(y_test, y_pred)

    logger.info("Test Results:")
    logger.info("  Accuracy:  %.4f", accuracy)
    logger.info("  Precision: %.4f", precision)
    logger.info("  Recall:    %.4f", recall)
    logger.info("  F1 Score:  %.4f", f1)
    logger.info("  ROC AUC:   %.4f", roc_auc)
    logger.info("  Confusion Matrix:\n%s", cm)

    # Classification report
    report = classification_report(y_test, y_pred, target_names=["Safe", "Phishing"])
    report_path = EVAL_DIR / "classification_report.txt"
    with open(report_path, "w") as f:
        f.write("XGBoost Phishing URL Classifier Evaluation\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Accuracy:  {accuracy:.4f}\n")
        f.write(f"Precision: {precision:.4f}\n")
        f.write(f"Recall:    {recall:.4f}\n")
        f.write(f"F1 Score:  {f1:.4f}\n")
        f.write(f"ROC AUC:   {roc_auc:.4f}\n\n")
        f.write("Classification Report:\n")
        f.write(report)
        f.write("\n\n")
        f.write("Confusion Matrix:\n")
        f.write(f"              Predicted Safe  Predicted Phishing\n")
        f.write(f"Actual Safe        {cm[0][0]:>8d}        {cm[0][1]:>8d}\n")
        f.write(f"Actual Phishing    {cm[1][0]:>8d}        {cm[1][1]:>8d}\n")
    logger.info("Classification report saved to %s", report_path)

    # Confusion Matrix Plot
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    ax.set_title("Confusion Matrix")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    tick_marks = [0, 1]
    ax.set_xticks(tick_marks)
    ax.set_yticks(tick_marks)
    ax.set_xticklabels(["Safe", "Phishing"])
    ax.set_yticklabels(["Safe", "Phishing"])
    thresh = cm.max() / 2
    for i in range(2):
        for j in range(2):
            ax.text(j, i, format(cm[i, j], "d"),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black")
    plt.colorbar(im)
    plt.tight_layout()
    plt.savefig(EVAL_DIR / "confusion_matrix.png", dpi=150)
    plt.close()
    logger.info("Confusion matrix saved to %s", EVAL_DIR / "confusion_matrix.png")

    # ROC Curve
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(fpr, tpr, color="darkorange", lw=2, label=f"ROC curve (AUC = {roc_auc:.4f})")
    ax.plot([0, 1], [0, 1], color="navy", lw=2, linestyle="--")
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("Receiver Operating Characteristic")
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(EVAL_DIR / "roc_curve.png", dpi=150)
    plt.close()
    logger.info("ROC curve saved to %s", EVAL_DIR / "roc_curve.png")

    # Feature Importance
    importance_dict = model.get_booster().get_score(importance_type="gain")
    importance_df = pd.DataFrame([
        {"feature": f, "importance": importance_dict.get(f, 0)}
        for f in feature_names
    ]).sort_values("importance", ascending=False)

    top_n = min(30, len(importance_df))
    fig, ax = plt.subplots(figsize=(10, max(8, top_n * 0.3)))
    top_features = importance_df.head(top_n)
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(top_features)))
    ax.barh(range(len(top_features)), top_features["importance"].values, color=colors)
    ax.set_yticks(range(len(top_features)))
    ax.set_yticklabels(top_features["feature"].values)
    ax.set_xlabel("Importance (gain)")
    ax.set_title("Top Feature Importances")
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(EVAL_DIR / "feature_importance.png", dpi=150)
    plt.close()
    logger.info("Feature importance saved to %s", EVAL_DIR / "feature_importance.png")

    # SHAP Summary Plot
    try:
        import shap
        logger.info("Generating SHAP explanations...")
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_test)

        fig, ax = plt.subplots(figsize=(12, 10))
        shap.summary_plot(shap_values, X_test, feature_names=feature_names, show=False)
        plt.tight_layout()
        plt.savefig(EVAL_DIR / "shap_summary.png", dpi=150, bbox_inches="tight")
        plt.close()
        logger.info("SHAP summary saved to %s", EVAL_DIR / "shap_summary.png")
    except ImportError:
        logger.warning("SHAP not installed — skipping SHAP summary plot.")
    except Exception as e:
        logger.warning("SHAP summary plot failed: %s", e)

    return {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "roc_auc": float(roc_auc),
    }


def save_model(
    model: XGBClassifier,
    feature_names: List[str],
    best_params: Dict,
    metrics: Dict,
    cv_scores: np.ndarray,
):
    """Save the trained model and metadata.

    Args:
        model: Trained XGBoost classifier.
        feature_names: Ordered list of feature names.
        best_params: Best hyperparameters from search.
        metrics: Evaluation metrics dict.
        cv_scores: Cross-validation scores.
    """
    joblib.dump(model, MODEL_PATH)
    logger.info("Model saved to %s", MODEL_PATH)

    with open(FEATURE_NAMES_PATH, "w") as f:
        json.dump(feature_names, f, indent=2)
    logger.info("Feature names saved to %s", FEATURE_NAMES_PATH)

    metadata = {
        "model": "XGBoost",
        "objective": "binary:logistic",
        "feature_count": len(feature_names),
        "feature_names": feature_names,
        "best_params": {k: str(v) if isinstance(v, (float,)) else v for k, v in best_params.items()},
        "test_metrics": metrics,
        "cv_mean_roc_auc": float(cv_scores.mean()),
        "cv_std_roc_auc": float(cv_scores.std()),
        "cv_scores": [float(s) for s in cv_scores],
        "dataset": "PhiUSIIL_Phishing_URL_Dataset.csv",
        "training_date": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info("Training metadata saved to %s", METADATA_PATH)


def main():
    logger.info("=" * 60)
    logger.info("Phishing URL XGBoost Training Pipeline")
    logger.info("=" * 60)

    # Step 1: Build training dataset (extract features from URLs)
    if not DATASET_PATH.exists():
        logger.error("Dataset not found at %s", DATASET_PATH)
        sys.exit(1)

    df = build_training_dataset(str(DATASET_PATH))

    if len(df) == 0:
        logger.error("No training data generated.")
        sys.exit(1)

    # Step 2: Prepare features and labels
    feature_cols = [c for c in df.columns if c != "label"]
    X = df[feature_cols].values
    y = df["label"].values

    logger.info("Total samples: %d", len(X))
    logger.info("Positive (phishing) samples: %d", int(y.sum()))
    logger.info("Negative (safe) samples: %d", int((1 - y).sum()))
    logger.info("Number of features: %d", X.shape[1])

    # Step 3: Stratified train/val/test split (60/20/20)
    sss = StratifiedShuffleSplit(n_splits=1, test_size=0.4, random_state=42)
    train_idx, temp_idx = next(sss.split(X, y))

    X_train, X_temp = X[train_idx], X[temp_idx]
    y_train, y_temp = y[train_idx], y[temp_idx]

    sss2 = StratifiedShuffleSplit(n_splits=1, test_size=0.5, random_state=42)
    val_idx, test_idx = next(sss2.split(X_temp, y_temp))

    X_val, X_test = X_temp[val_idx], X_temp[test_idx]
    y_val, y_test = y_temp[val_idx], y_temp[test_idx]

    logger.info("Split sizes — Train: %d, Val: %d, Test: %d", len(X_train), len(X_val), len(X_test))

    # Step 4: Convert to DataFrames with column names
    X_train_df = pd.DataFrame(X_train, columns=feature_cols)
    X_val_df = pd.DataFrame(X_val, columns=feature_cols)
    X_test_df = pd.DataFrame(X_test, columns=feature_cols)
    y_train_s = pd.Series(y_train)
    y_val_s = pd.Series(y_val)
    y_test_s = pd.Series(y_test)

    # Step 5: Train model
    model, best_params, cv_scores = train_xgboost(
        X_train_df, y_train_s, X_val_df, y_val_s, feature_cols
    )

    # Step 6: Evaluate
    metrics = evaluate_model(model, X_test_df, y_test_s, feature_cols)

    # Step 7: Save
    save_model(model, feature_cols, best_params, metrics, cv_scores)

    logger.info("=" * 60)
    logger.info("Training complete!")
    logger.info("Test Accuracy:  %.4f", metrics["accuracy"])
    logger.info("Test Precision: %.4f", metrics["precision"])
    logger.info("Test Recall:    %.4f", metrics["recall"])
    logger.info("Test F1 Score:  %.4f", metrics["f1"])
    logger.info("Test ROC AUC:   %.4f", metrics["roc_auc"])
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
