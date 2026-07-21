"""Retrain XGBoost with rebuilt legitimacy_score and produce honest evaluation metrics.

This replaces the old train_optimized.py run after the legitimacy_score rebuild.
Uses a faster pipeline (fewer CV iterations) while still producing rigorous metrics.

Usage:
    cd backend && .venv/bin/python -m ml.training.retrain
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
from sklearn.model_selection import StratifiedShuffleSplit, StratifiedKFold, RandomizedSearchCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    roc_curve, precision_recall_curve, matthews_corrcoef,
    balanced_accuracy_score,
)
from sklearn.feature_selection import mutual_info_classif
import xgboost as xgb
from xgboost import XGBClassifier
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.features.extractor import extract_features, FEATURE_NAMES
from ml.training.validate_features import build_full_feature_matrix, analyze_features

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
BEST_PARAMS_PATH = MODEL_DIR / "best_params.json"
SELECTED_FEATURES_PATH = MODEL_DIR / "selected_features.json"
THRESHOLD_PATH = MODEL_DIR / "optimal_threshold.json"

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(EVAL_DIR, exist_ok=True)


def _pr_auc(y_true, y_proba):
    from sklearn.metrics import auc
    prec, rec, _ = precision_recall_curve(y_true, y_proba)
    return auc(rec, prec)


def find_optimal_threshold(y_true, y_proba):
    thresholds = np.linspace(0.01, 0.99, 199)
    best_thresh = 0.5
    best_f1 = 0.0
    for t in thresholds:
        y_pred = (y_proba >= t).astype(int)
        f1 = f1_score(y_true, y_pred)
        if f1 > best_f1:
            best_f1 = f1
            best_thresh = t
    return best_thresh, best_f1


def main():
    logger.info("=" * 60)
    logger.info("Retraining XGBoost with rebuilt legitimacy_score")
    logger.info("=" * 60)

    # Step 1: Build feature matrix
    logger.info("\n[Step 1] Building feature matrix from URLs...")
    t0 = time.time()
    feature_df = build_full_feature_matrix(str(DATASET_PATH))
    logger.info("Feature matrix built in %.1fs", time.time() - t0)

    # Step 2: Validate & select features
    logger.info("\n[Step 2] Running feature validation & selection...")
    report = analyze_features(feature_df)
    selected_features = report["selected_features"]
    feature_cols = selected_features
    logger.info("Selected %d features for training", len(feature_cols))

    # Verify legitimacy_score is in the selected features
    assert "legitimacy_score" in feature_cols, "legitimacy_score missing from selected features!"

    X = feature_df[feature_cols].fillna(0).values
    y = feature_df["label"].values

    logger.info("\nDataset: %d samples, %d features", len(X), len(feature_cols))
    logger.info("Phishing: %d (%.1f%%), Safe: %d (%.1f%%)",
                int(y.sum()), 100 * y.mean(), int((1 - y).sum()), 100 * (1 - y.mean()))

    # Step 3: Stratified split (60/20/20)
    sss = StratifiedShuffleSplit(n_splits=1, test_size=0.4, random_state=42)
    train_idx, temp_idx = next(sss.split(X, y))
    X_train, X_temp = X[train_idx], X[temp_idx]
    y_train, y_temp = y[train_idx], y[temp_idx]

    sss2 = StratifiedShuffleSplit(n_splits=1, test_size=0.5, random_state=42)
    val_idx, test_idx = next(sss2.split(X_temp, y_temp))
    X_val, X_test = X_temp[val_idx], X_temp[test_idx]
    y_val, y_test = y_temp[val_idx], y_temp[test_idx]

    X_train_df = pd.DataFrame(X_train, columns=feature_cols)
    X_val_df = pd.DataFrame(X_val, columns=feature_cols)
    X_test_df = pd.DataFrame(X_test, columns=feature_cols)
    y_train_s = pd.Series(y_train)
    y_val_s = pd.Series(y_val)
    y_test_s = pd.Series(y_test)

    logger.info("Split: Train=%d, Val=%d, Test=%d", len(X_train), len(X_val), len(X_test))

    # Step 4: Train with hyperparameter tuning (faster: 15 iterations, 3-fold)
    logger.info("\n[Step 4] Training with hyperparameter optimization...")
    param_dist = {
        "n_estimators": [100, 200, 300, 500],
        "max_depth": [4, 6, 8, 10],
        "learning_rate": [0.01, 0.05, 0.1, 0.2],
        "min_child_weight": [1, 3, 5],
        "gamma": [0, 0.1, 0.3],
        "subsample": [0.6, 0.8, 1.0],
        "colsample_bytree": [0.6, 0.8, 1.0],
        "reg_alpha": [0, 0.1, 1.0],
        "reg_lambda": [0, 0.1, 1.0],
    }

    base = XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1,
        verbosity=0,
    )

    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    search = RandomizedSearchCV(
        estimator=base,
        param_distributions=param_dist,
        n_iter=15,
        scoring="roc_auc",
        cv=cv,
        verbose=1,
        random_state=42,
        n_jobs=-1,
    )

    t0 = time.time()
    search.fit(
        X_train_df, y_train_s,
        eval_set=[(X_val_df, y_val_s)],
        verbose=False,
    )
    logger.info("Training completed in %.1fs", time.time() - t0)

    model = search.best_estimator_
    logger.info("Best params: %s", search.best_params_)
    logger.info("Best CV ROC AUC: %.4f", search.best_score_)

    # Step 5: Threshold optimization
    logger.info("\n[Step 5] Optimizing decision threshold...")
    val_proba = model.predict_proba(X_val_df)[:, 1]
    best_threshold, best_val_f1 = find_optimal_threshold(y_val, val_proba)
    logger.info("Optimal threshold: %.4f (F1: %.4f)", best_threshold, best_val_f1)

    # Step 6: Test evaluation
    logger.info("\n[Step 6] Evaluating on test set...")
    y_proba = model.predict_proba(X_test_df)[:, 1]
    y_pred = (y_proba >= best_threshold).astype(int)

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred)),
        "recall": float(recall_score(y_test, y_pred)),
        "f1": float(f1_score(y_test, y_pred)),
        "roc_auc": float(roc_auc_score(y_test, y_proba)),
        "pr_auc": float(_pr_auc(y_test, y_proba)),
        "mcc": float(matthews_corrcoef(y_test, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_test, y_pred)),
        "optimal_threshold": float(best_threshold),
    }

    logger.info("\n=== Test Metrics (threshold=%.3f) ===", best_threshold)
    for k, v in metrics.items():
        logger.info("  %s: %.4f", k, v)

    # Classification report
    report_text = classification_report(y_test, y_pred, target_names=["Safe", "Phishing"])
    report_path = EVAL_DIR / "classification_report.txt"
    with open(report_path, "w") as f:
        f.write(f"XGBoost Phishing Classifier — Test Set Evaluation (retrained with rebuilt legitimacy_score)\n")
        f.write(f"Optimal threshold: {best_threshold:.4f}\n")
        f.write(f"Retrained: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Dataset: PhiUSIIL ({len(feature_df)} samples, {len(feature_cols)} features)\n")
        f.write("=" * 60 + "\n\n")
        for k, v in metrics.items():
            f.write(f"{k}: {v}\n")
        f.write("\n\n")
        f.write(report_text)
    logger.info("Report saved to %s", report_path)

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    ax.set_title("Confusion Matrix (retrained)")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(["Safe", "Phishing"])
    ax.set_yticklabels(["Safe", "Phishing"])
    for i in range(2):
        for j in range(2):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                    color="white" if cm[i, j] > cm.max() / 2 else "black")
    plt.colorbar(im)
    plt.tight_layout()
    plt.savefig(EVAL_DIR / "confusion_matrix.png", dpi=150)
    plt.close()

    # ROC Curve
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(fpr, tpr, color="darkorange", lw=2, label=f"ROC (AUC = {metrics['roc_auc']:.4f})")
    ax.plot([0, 1], [0, 1], color="navy", lw=2, linestyle="--")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curve (retrained)")
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(EVAL_DIR / "roc_curve.png", dpi=150)
    plt.close()

    # Precision-Recall Curve
    prec, rec, _ = precision_recall_curve(y_test, y_proba)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(rec, prec, color="darkgreen", lw=2, label=f"PR (AUC = {metrics['pr_auc']:.4f})")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title("Precision-Recall Curve (retrained)")
    ax.legend(loc="lower left")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(EVAL_DIR / "precision_recall_curve.png", dpi=150)
    plt.close()

    # Feature Importance
    importance_dict = model.get_booster().get_score(importance_type="gain")
    imp_df = pd.DataFrame([
        {"feature": f, "importance": importance_dict.get(f, 0)}
        for f in feature_cols
    ]).sort_values("importance", ascending=False)

    top_n = min(30, len(imp_df))
    fig, ax = plt.subplots(figsize=(10, max(8, top_n * 0.3)))
    top = imp_df.head(top_n)
    colors = plt.cm.plasma(np.linspace(0.2, 0.9, len(top)))
    ax.barh(range(len(top)), top["importance"].values, color=colors)
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(top["feature"].values)
    ax.set_xlabel("Importance (gain)")
    ax.set_title("Top Feature Importances (retrained)")
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(EVAL_DIR / "feature_importance.png", dpi=150)
    plt.close()

    # Mutual Information
    logger.info("Computing Mutual Information scores...")
    mi = mutual_info_classif(X_test_df.fillna(0), y_test, random_state=42, n_neighbors=3)
    mi_df = pd.DataFrame({"feature": feature_cols, "mi_score": mi})
    mi_df = mi_df.sort_values("mi_score", ascending=False)

    fig, ax = plt.subplots(figsize=(10, max(6, 20 * 0.25)))
    top_mi = mi_df.head(20)
    colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(top_mi)))
    ax.barh(range(len(top_mi)), top_mi["mi_score"].values, color=colors)
    ax.set_yticks(range(len(top_mi)))
    ax.set_yticklabels(top_mi["feature"].values)
    ax.set_xlabel("Mutual Information")
    ax.set_title("Top 20 Features by Mutual Information (retrained)")
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(EVAL_DIR / "mutual_information.png", dpi=150)
    plt.close()

    # Save model and artifacts
    logger.info("\n[Step 7] Saving model and artifacts...")
    joblib.dump(model, MODEL_PATH)
    with open(FEATURE_NAMES_PATH, "w") as f:
        json.dump(feature_cols, f, indent=2)
    with open(BEST_PARAMS_PATH, "w") as f:
        params_ser = {}
        for k, v in search.best_params_.items():
            try:
                json.dumps(v)
                params_ser[k] = v
            except (TypeError, OverflowError):
                params_ser[k] = str(v)
        json.dump(params_ser, f, indent=2)
    with open(SELECTED_FEATURES_PATH, "w") as f:
        json.dump(feature_cols, f, indent=2)
    with open(THRESHOLD_PATH, "w") as f:
        json.dump({"optimal_threshold": float(best_threshold), "val_f1": float(best_val_f1)}, f, indent=2)

    metadata = {
        "model": "XGBoost",
        "feature_count": len(feature_cols),
        "dataset": "PhiUSIIL_Phishing_URL_Dataset.csv",
        "dataset_size": len(feature_df),
        "positive_samples": int(y.sum()),
        "negative_samples": int((1 - y).sum()),
        "test_metrics": metrics,
        "optimal_threshold": float(best_threshold),
        "best_params": {k: str(v) if not isinstance(v, (int, float, str)) else v for k, v in search.best_params_.items()},
        "training_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "retrained_after_legitimacy_score_rebuild": True,
        "dataset_limitation": "PhiUSIIL labels brand login pages as phishing, creating a trivially separable dataset. High accuracy reflects dataset bias, not real-world difficulty.",
    }
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)

    # Final summary
    logger.info("\n" + "=" * 60)
    logger.info("RETRAINING COMPLETE")
    logger.info("=" * 60)
    logger.info("Dataset size:       %d", len(feature_df))
    logger.info("Final features:     %d", len(feature_cols))
    logger.info("Best threshold:     %.4f", best_threshold)
    logger.info("Test Accuracy:      %.4f", metrics["accuracy"])
    logger.info("Test Precision:     %.4f", metrics["precision"])
    logger.info("Test Recall:        %.4f", metrics["recall"])
    logger.info("Test F1:            %.4f", metrics["f1"])
    logger.info("Test ROC-AUC:       %.4f", metrics["roc_auc"])
    logger.info("Test PR-AUC:        %.4f", metrics["pr_auc"])
    logger.info("Test MCC:           %.4f", metrics["mcc"])
    logger.info("Test Balanced Acc:  %.4f", metrics["balanced_accuracy"])
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
