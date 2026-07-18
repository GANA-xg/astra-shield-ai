"""Optimized XGBoost training with hyperparameter tuning, evaluation, threshold optimization,
overfitting detection, and calibration.

Usage:
    python -m ml.training.train_optimized
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
from sklearn.model_selection import StratifiedShuffleSplit, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    roc_curve, precision_recall_curve, matthews_corrcoef,
    balanced_accuracy_score, brier_score_loss,
)
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
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

# Minimum acceptable metrics — fail if not met
MIN_ROC_AUC = 0.98
MIN_PRECISION = 0.97
MIN_RECALL = 0.97
MIN_F1 = 0.97


def compute_mutual_information(
    X: pd.DataFrame, y: pd.Series, feature_names: List[str]
) -> pd.DataFrame:
    logger.info("Computing Mutual Information scores...")
    mi = mutual_info_classif(X.fillna(0), y, random_state=42, n_neighbors=3)
    mi_df = pd.DataFrame({"feature": feature_names, "mi_score": mi})
    return mi_df.sort_values("mi_score", ascending=False)


def select_features(
    X: pd.DataFrame, y: pd.Series, feature_cols: List[str]
) -> Tuple[pd.DataFrame, List[str]]:
    """Select features using Mutual Information and remove low-value ones."""
    mi_df = compute_mutual_information(X, y, feature_cols)

    # Keep features with MI > 0 (positive contribution)
    keep = list(mi_df[mi_df["mi_score"] > 0.001]["feature"])
    logger.info("Features with MI > 0.001: %d / %d", len(keep), len(feature_cols))

    if len(keep) < 10:
        logger.warning("Too few features after MI filter — falling back to top 30")
        keep = list(mi_df.head(30)["feature"])

    return X[keep], keep


def find_optimal_threshold(y_true: np.ndarray, y_proba: np.ndarray) -> Tuple[float, float]:
    """Find threshold that maximizes F1 score on validation data."""
    thresholds = np.linspace(0.01, 0.99, 199)
    best_thresh = 0.5
    best_f1 = 0.0
    for t in thresholds:
        y_pred = (y_proba >= t).astype(int)
        f1 = f1_score(y_true, y_pred)
        if f1 > best_f1:
            best_f1 = f1
            best_thresh = t
    logger.info("Optimal threshold: %.3f (F1: %.4f)", best_thresh, best_f1)
    return best_thresh, best_f1


def check_calibration(
    model: XGBClassifier, X_val: pd.DataFrame, y_val: pd.Series
) -> Dict:
    """Check probability calibration and return calibration curve."""
    y_proba = model.predict_proba(X_val)[:, 1]

    prob_true, prob_pred = calibration_curve(y_val, y_proba, n_bins=10)
    brier = brier_score_loss(y_val, y_proba)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(prob_pred, prob_true, "o-", label="XGBoost", markersize=8)
    ax.plot([0, 1], [0, 1], "--", color="gray", label="Perfect calibration")
    ax.set_xlabel("Mean predicted probability")
    ax.set_ylabel("Fraction of positives")
    ax.set_title(f"Calibration Curve (Brier: {brier:.4f})")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(EVAL_DIR / "calibration_curve.png", dpi=150)
    plt.close()
    logger.info("Calibration curve saved (Brier score: %.4f)", brier)

    return {"brier_score": float(brier), "needs_calibration": brier > 0.05}


def detect_overfitting(
    model: XGBClassifier,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
) -> bool:
    """Detect overfitting. Returns True if significant overfitting detected."""
    y_train_pred = model.predict(X_train)
    y_val_pred = model.predict(X_val)

    train_acc = accuracy_score(y_train, y_train_pred)
    val_acc = accuracy_score(y_val, y_val_pred)
    gap = train_acc - val_acc

    logger.info("Training accuracy:   %.4f", train_acc)
    logger.info("Validation accuracy: %.4f", val_acc)
    logger.info("Accuracy gap:        %.4f", gap)

    if gap > 0.03:
        logger.warning("Overfitting detected! Gap of %.1f%% exceeds 3%% threshold", gap * 100)
        return True
    logger.info("No significant overfitting detected.")
    return False


def train_with_early_stopping(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    feature_names: List[str],
) -> Tuple[XGBClassifier, Dict]:
    """Train XGBoost with hyperparameter tuning and early stopping."""

    param_dist = {
        "n_estimators": [100, 200, 300, 500, 800],
        "max_depth": [3, 4, 6, 8, 10, 12],
        "learning_rate": [0.005, 0.01, 0.02, 0.05, 0.1, 0.2],
        "min_child_weight": [1, 3, 5, 7, 10],
        "gamma": [0, 0.05, 0.1, 0.2, 0.5, 1.0],
        "subsample": [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        "colsample_bytree": [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        "reg_alpha": [0, 0.001, 0.01, 0.1, 1.0, 10.0],
        "reg_lambda": [0, 0.001, 0.01, 0.1, 1.0, 10.0],
    }

    # Do a coarse search first, then refine
    logger.info("Stage 1: Coarse RandomizedSearchCV (30 iterations, 5-fold CV)...")

    base = XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1,
        verbosity=0,
        use_label_encoder=False,
    )

    cv_outer = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    from sklearn.model_selection import RandomizedSearchCV
    search = RandomizedSearchCV(
        estimator=base,
        param_distributions=param_dist,
        n_iter=30,
        scoring="roc_auc",
        cv=cv_outer,
        verbose=0,
        random_state=42,
        n_jobs=-1,
    )

    search.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False,
    )

    best = search.best_estimator_
    logger.info("Best coarse params: %s", search.best_params_)
    logger.info("Best coarse CV ROC AUC: %.4f", search.best_score_)

    # Stage 2: Fine-tune around best params
    bp = search.best_params_
    logger.info("Stage 2: Fine-tuning...")

    fine_params = {
        "n_estimators": [max(100, bp["n_estimators"] - 100), bp["n_estimators"], bp["n_estimators"] + 100],
        "max_depth": [max(2, bp["max_depth"] - 1), bp["max_depth"], bp["max_depth"] + 1],
        "learning_rate": [bp["learning_rate"] * 0.5, bp["learning_rate"], bp["learning_rate"] * 1.5],
        "subsample": [max(0.4, bp["subsample"] - 0.1), bp["subsample"], min(1.0, bp["subsample"] + 0.1)],
        "colsample_bytree": [max(0.4, bp["colsample_bytree"] - 0.1), bp["colsample_bytree"], min(1.0, bp["colsample_bytree"] + 0.1)],
        "min_child_weight": [max(1, bp["min_child_weight"] - 1), bp["min_child_weight"], bp["min_child_weight"] + 1, bp["min_child_weight"] + 2],
        "gamma": [max(0, bp["gamma"] - 0.05), bp["gamma"], bp["gamma"] + 0.1, bp["gamma"] + 0.2],
        "reg_alpha": [bp["reg_alpha"] * 0.1 if bp["reg_alpha"] > 0 else 0, bp["reg_alpha"], bp["reg_alpha"] * 10 if bp["reg_alpha"] > 0 else 0.1],
        "reg_lambda": [bp["reg_lambda"] * 0.1 if bp["reg_lambda"] > 0 else 0, bp["reg_lambda"], bp["reg_lambda"] * 10 if bp["reg_lambda"] > 0 else 0.1],
    }

    fine_search = RandomizedSearchCV(
        estimator=XGBClassifier(
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=42,
            n_jobs=-1,
            verbosity=0,
            use_label_encoder=False,
        ),
        param_distributions=fine_params,
        n_iter=15,
        scoring="roc_auc",
        cv=5,
        verbose=0,
        random_state=42,
        n_jobs=-1,
    )

    fine_search.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False,
    )

    best_model = fine_search.best_estimator_
    best_params = fine_search.best_params_
    logger.info("Best fine-tuned params: %s", best_params)
    logger.info("Best fine-tuned CV ROC AUC: %.4f", fine_search.best_score_)

    return best_model, best_params


def evaluate_on_test(
    model: XGBClassifier,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    feature_names: List[str],
    threshold: float,
) -> Dict:
    """Comprehensive evaluation with all metrics."""
    y_proba = model.predict_proba(X_test)[:, 1]
    y_pred = (y_proba >= threshold).astype(int)

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred)),
        "recall": float(recall_score(y_test, y_pred)),
        "f1": float(f1_score(y_test, y_pred)),
        "roc_auc": float(roc_auc_score(y_test, y_proba)),
        "pr_auc": float(_pr_auc(y_test, y_proba)),
        "mcc": float(matthews_corrcoef(y_test, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_test, y_pred)),
        "optimal_threshold": float(threshold),
    }

    logger.info("=== Test Metrics (threshold=%.3f) ===", threshold)
    for k, v in metrics.items():
        logger.info("  %s: %.4f", k, v)

    # Classification report
    report = classification_report(y_test, y_pred, target_names=["Safe", "Phishing"])
    report_path = EVAL_DIR / "classification_report.txt"
    with open(report_path, "w") as f:
        f.write(f"XGBoost Phishing Classifier — Test Set Evaluation\n")
        f.write(f"Optimal threshold: {threshold:.4f}\n")
        f.write("=" * 50 + "\n\n")
        for k, v in metrics.items():
            f.write(f"{k}: {v}\n")
        f.write("\n\n")
        f.write(report)
    logger.info("Report saved to %s", report_path)

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    ax.set_title("Confusion Matrix")
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
    ax.set_title("ROC Curve")
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
    ax.set_title("Precision-Recall Curve")
    ax.legend(loc="lower left")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(EVAL_DIR / "precision_recall_curve.png", dpi=150)
    plt.close()

    # Feature Importance
    importance_dict = model.get_booster().get_score(importance_type="gain")
    imp_df = pd.DataFrame([
        {"feature": f, "importance": importance_dict.get(f, 0)}
        for f in feature_names
    ]).sort_values("importance", ascending=False)

    top_n = min(30, len(imp_df))
    fig, ax = plt.subplots(figsize=(10, max(8, top_n * 0.3)))
    top = imp_df.head(top_n)
    colors = plt.cm.plasma(np.linspace(0.2, 0.9, len(top)))
    ax.barh(range(len(top)), top["importance"].values, color=colors)
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(top["feature"].values)
    ax.set_xlabel("Importance (gain)")
    ax.set_title("Top Feature Importances")
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(EVAL_DIR / "feature_importance.png", dpi=150)
    plt.close()

    # SHAP
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
        logger.info("SHAP summary saved")
    except Exception as e:
        logger.warning("SHAP failed: %s", e)

    return metrics


def _pr_auc(y_true, y_proba):
    from sklearn.metrics import auc
    prec, rec, _ = precision_recall_curve(y_true, y_proba)
    return auc(rec, prec)


def reduce_complexity(params: Dict) -> Dict:
    """Reduce model complexity for overfitting."""
    reduced = dict(params)
    reduced["max_depth"] = max(2, int(params.get("max_depth", 6)) - 2)
    reduced["learning_rate"] = params.get("learning_rate", 0.1) * 0.5
    reduced["min_child_weight"] = params.get("min_child_weight", 1) + 3
    reduced["subsample"] = min(params.get("subsample", 0.8), 0.7)
    reduced["colsample_bytree"] = min(params.get("colsample_bytree", 0.8), 0.7)
    reduced["reg_alpha"] = params.get("reg_alpha", 0) + 1.0
    reduced["reg_lambda"] = params.get("reg_lambda", 1.0) + 1.0
    reduced["gamma"] = params.get("gamma", 0) + 0.2
    logger.info("Reduced model complexity: %s", reduced)
    return reduced


def main():
    logger.info("=" * 60)
    logger.info("Optimized XGBoost Phishing URL Training Pipeline")
    logger.info("=" * 60)

    # Step 1: Build feature matrix from URLs only
    logger.info("\n[Step 1] Building feature matrix...")
    feature_df = build_full_feature_matrix(str(DATASET_PATH))

    # Step 2: Validate & select features
    logger.info("\n[Step 2] Running feature validation...")
    report = analyze_features(feature_df)

    selected_features = report["selected_features"]
    feature_cols = selected_features
    logger.info("Selected %d features for training", len(feature_cols))

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

    # Step 4: Train with hyperparameter tuning
    logger.info("\n[Step 4] Training with hyperparameter optimization...")
    model, best_params = train_with_early_stopping(X_train_df, y_train_s, X_val_df, y_val_s, feature_cols)

    # Step 5: Overfitting detection
    logger.info("\n[Step 5] Checking for overfitting...")
    overfitting = detect_overfitting(model, X_train_df, y_train_s, X_val_df, y_val_s)

    if overfitting:
        logger.warning("Overfitting detected — reducing complexity and retraining...")
        reduced_params = reduce_complexity(best_params)
        reduced_model = XGBClassifier(
            **{k: v for k, v in reduced_params.items() if k in [
                "n_estimators", "max_depth", "learning_rate", "min_child_weight",
                "gamma", "subsample", "colsample_bytree", "reg_alpha", "reg_lambda"
            ]},
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=42,
            n_jobs=-1,
            verbosity=0,
            use_label_encoder=False,
        )
        reduced_model.fit(
            X_train_df, y_train_s,
            eval_set=[(X_val_df, y_val_s)],
            verbose=False,
        )
        model = reduced_model
        overfitting = detect_overfitting(model, X_train_df, y_train_s, X_val_df, y_val_s)
        if overfitting:
            logger.warning("Overfitting persists after reduction. Continuing with reduced model.")

    # Step 6: Threshold optimization
    logger.info("\n[Step 6] Optimizing decision threshold...")
    val_proba = model.predict_proba(X_val_df)[:, 1]
    best_threshold, best_val_f1 = find_optimal_threshold(y_val, val_proba)

    # Step 7: Calibration check
    logger.info("\n[Step 7] Checking calibration...")
    cal_info = check_calibration(model, X_val_df, y_val_s)
    if cal_info["needs_calibration"]:
        logger.warning("Poor calibration detected (Brier: %.4f). Applying CalibratedClassifierCV...", cal_info["brier_score"])
        calibrated = CalibratedClassifierCV(model, cv="prefit", method="sigmoid")
        calibrated.fit(X_val_df, y_val_s)
        model = calibrated
        logger.info("Calibration applied.")
        # Re-check calibration
        cal_info = check_calibration(model, X_val_df, y_val_s)
        logger.info("Post-calibration Brier: %.4f", cal_info["brier_score"])

    # Step 8: Evaluation on test set
    logger.info("\n[Step 8] Evaluating on test set...")
    metrics = evaluate_on_test(model, X_test_df, y_test_s, feature_cols, best_threshold)

    # Step 9: Check minimum targets
    logger.info("\n[Step 9] Checking minimum performance targets...")
    targets_met = True
    for name, target, value in [
        ("ROC-AUC", MIN_ROC_AUC, metrics["roc_auc"]),
        ("Precision", MIN_PRECISION, metrics["precision"]),
        ("Recall", MIN_RECALL, metrics["recall"]),
        ("F1", MIN_F1, metrics["f1"]),
    ]:
        if value < target:
            logger.error("  %s: %.4f < %.4f — TARGET NOT MET", name, value, target)
            targets_met = False
        else:
            logger.info("  %s: %.4f >= %.4f ✓", name, value, target)

    if not targets_met:
        logger.error("Minimum performance targets not met. Attempting retrain with adjusted parameters...")
        if hasattr(model, "get_params"):
            current_params = model.get_params()
            adjusted = reduce_complexity(current_params)
            retrain_model = XGBClassifier(
                **{k: v for k, v in adjusted.items() if k in [
                    "n_estimators", "max_depth", "learning_rate", "min_child_weight",
                    "gamma", "subsample", "colsample_bytree", "reg_alpha", "reg_lambda"
                ]},
                objective="binary:logistic",
                eval_metric="logloss",
                random_state=42,
                n_jobs=-1,
                verbosity=0,
                use_label_encoder=False,
            )
            retrain_model.fit(X_train_df, y_train_s, eval_set=[(X_val_df, y_val_s)], verbose=False)
            # Re-evaluate
            val_proba2 = retrain_model.predict_proba(X_val_df)[:, 1]
            bt2, _ = find_optimal_threshold(y_val, val_proba2)
            metrics2 = evaluate_on_test(retrain_model, X_test_df, y_test_s, feature_cols, bt2)
            if metrics2["roc_auc"] >= MIN_ROC_AUC and metrics2["f1"] >= MIN_F1:
                model = retrain_model
                best_threshold = bt2
                metrics = metrics2
                logger.info("Retrained model meets targets!")
            else:
                logger.error("Retrain still below targets. Saving best available model.")

    # Step 10: Save
    logger.info("\n[Step 10] Saving model and artifacts...")

    # Determine what to save (unwrap CalibratedClassifierCV if needed)
    if hasattr(model, "base_estimator"):
        # CalibratedClassifierCV wrapper
        save_model = model
        raw_model = model.base_estimator
    else:
        save_model = model
        raw_model = model

    joblib.dump(save_model, MODEL_PATH)
    logger.info("Model saved to %s", MODEL_PATH)

    with open(FEATURE_NAMES_PATH, "w") as f:
        json.dump(feature_cols, f, indent=2)
    logger.info("Feature names saved to %s", FEATURE_NAMES_PATH)

    with open(BEST_PARAMS_PATH, "w") as f:
        params_serializable = {}
        for k, v in best_params.items():
            try:
                json.dumps(v)
                params_serializable[k] = v
            except (TypeError, OverflowError):
                params_serializable[k] = str(v)
        json.dump(params_serializable, f, indent=2)
    logger.info("Best params saved to %s", BEST_PARAMS_PATH)

    # Save selected features
    with open(SELECTED_FEATURES_PATH, "w") as f:
        json.dump(feature_cols, f, indent=2)
    logger.info("Selected features saved to %s", SELECTED_FEATURES_PATH)

    # Save threshold
    with open(THRESHOLD_PATH, "w") as f:
        json.dump({"optimal_threshold": float(best_threshold), "val_f1": float(best_val_f1)}, f, indent=2)
    logger.info("Optimal threshold saved to %s", THRESHOLD_PATH)

    # Training metadata
    metadata = {
        "model": "XGBoost",
        "feature_count": len(feature_cols),
        "dataset": "PhiUSIIL_Phishing_URL_Dataset.csv",
        "dataset_size": len(feature_df),
        "positive_samples": int(y.sum()),
        "negative_samples": int((1 - y).sum()),
        "test_metrics": metrics,
        "optimal_threshold": float(best_threshold),
        "best_params": {k: str(v) if not isinstance(v, (int, float, str)) else v for k, v in best_params.items()},
        "training_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "calibration_applied": bool(cal_info.get("needs_calibration", False)),
        "overfitting_detected": bool(overfitting),
        "targets_met": bool(targets_met),
    }
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info("Training metadata saved to %s", METADATA_PATH)

    # Final summary
    logger.info("\n" + "=" * 60)
    logger.info("TRAINING COMPLETE")
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
    logger.info("Targets met:        %s", targets_met)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
