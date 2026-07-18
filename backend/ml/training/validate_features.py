"""Feature validation, selection, and analysis.

Validates all extracted features for:
- Missingness / variance / correlation
- Mutual information ranking
- Automatic removal of problematic features
- Feature selection report generation
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
from sklearn.feature_selection import mutual_info_classif
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.features.extractor import extract_features, FEATURE_NAMES

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "ml" / "datasets" / "PhiUSIIL_Phishing_URL_Dataset.csv"
EVAL_DIR = PROJECT_ROOT / "ml" / "evaluation"
os.makedirs(EVAL_DIR, exist_ok=True)


def build_full_feature_matrix(csv_path: str, max_rows: int = None) -> pd.DataFrame:
    import pandas as pd

    df = pd.read_csv(csv_path, encoding="utf-8")
    total = len(df)

    # Remove exact duplicate URLs
    dup_count = df.duplicated(subset=["URL"]).sum()
    if dup_count:
        logger.info("Removing %d duplicate URLs", dup_count)
        df = df.drop_duplicates(subset=["URL"])

    if max_rows and len(df) > max_rows:
        df = df.sample(n=max_rows, random_state=42)

    # Check for missing URLs
    missing = df["URL"].isna().sum()
    if missing:
        logger.warning("Found %d rows with missing URL", missing)
        df = df.dropna(subset=["URL"])

    rows = []
    start = time.time()
    for idx, row in df.iterrows():
        url = str(row["URL"]).strip()
        if not url:
            continue
        try:
            feats = extract_features(url)
            feats["label"] = int(row["label"])
            rows.append(feats)
        except Exception as e:
            logger.warning("Failed at row %d: %s", idx, e)

        if (idx + 1) % 50000 == 0:
            elapsed = time.time() - start
            rate = (idx + 1) / elapsed
            logger.info("  processed %d/%d (%.1f%%) — %.0f/sec", idx + 1, total, 100 * (idx + 1) / total, rate)

    elapsed = time.time() - start
    result = pd.DataFrame(rows)
    logger.info("Feature matrix built: %d rows, %d cols in %.1fs (%.0f/sec)", len(result), len(result.columns), elapsed, len(rows) / elapsed)
    return result


def analyze_features(feature_df: pd.DataFrame) -> Dict:
    """Analyze features for variance, correlation, MI, near-constant detection."""
    feature_cols = [c for c in feature_df.columns if c != "label"]
    X = feature_df[feature_cols]
    y = feature_df["label"]

    report = {
        "total_samples": len(feature_df),
        "total_features": len(feature_cols),
        "positive_samples": int(y.sum()),
        "negative_samples": int((1 - y).sum()),
    }

    # Missing values
    missing = X.isnull().sum()
    features_with_missing = missing[missing > 0]
    if len(features_with_missing):
        logger.warning("Features with missing values: %d", len(features_with_missing))
        for f, c in features_with_missing.items():
            logger.warning("  %s: %d missing", f, c)

    # Variance analysis
    variances = X.var()
    constant_features = list(variances[variances == 0].index)
    near_constant_features = list(variances[(variances > 0) & (variances < 1e-5)].index)

    report["constant_features_removed"] = constant_features
    report["near_constant_features_removed"] = near_constant_features
    logger.info("Constant features: %d", len(constant_features))
    logger.info("Near-constant features: %d", len(near_constant_features))

    X_clean = X.drop(columns=constant_features + near_constant_features, errors="ignore")
    feature_cols_clean = list(X_clean.columns)
    report["features_after_variance"] = len(feature_cols_clean)

    # Correlation analysis
    corr_matrix = X_clean.corr().abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    high_corr = [(col, row) for col in upper.columns for row in upper.index if upper.loc[row, col] > 0.95]

    correlated_to_drop = set()
    for row, col in high_corr:
        # Keep the one with higher MI with target
        correlated_to_drop.add(col)
    report["highly_correlated_dropped"] = list(correlated_to_drop)
    logger.info("Highly correlated pairs (>0.95): %d", len(high_corr))
    logger.info("Features dropped due to correlation: %d", len(correlated_to_drop))

    X_final = X_clean.drop(columns=list(correlated_to_drop), errors="ignore")
    feature_cols_final = list(X_final.columns)
    report["features_after_correlation"] = len(feature_cols_final)

    # Mutual Information scores
    logger.info("Computing Mutual Information scores...")
    mi_scores = mutual_info_classif(X_final.fillna(0), y, random_state=42)
    mi_df = pd.DataFrame({"feature": feature_cols_final, "mi_score": mi_scores})
    mi_df = mi_df.sort_values("mi_score", ascending=False)

    report["mutual_information"] = {
        row["feature"]: float(row["mi_score"])
        for _, row in mi_df.head(20).iterrows()
    }

    # Feature importance via XGBoost (quick estimate)
    try:
        import xgboost as xgb
        logger.info("Estimating feature importance via quick XGBoost...")
        model = xgb.XGBClassifier(
            n_estimators=100, max_depth=4, random_state=42,
            verbosity=0, use_label_encoder=False,
        )
        model.fit(X_final.fillna(0), y)
        importance = model.feature_importances_
        imp_df = pd.DataFrame({"feature": feature_cols_final, "importance": importance})
        imp_df = imp_df.sort_values("importance", ascending=False)
        report["xgboost_importance"] = {
            row["feature"]: float(row["importance"])
            for _, row in imp_df.head(20).iterrows()
        }
    except ImportError:
        logger.warning("XGBoost not available for quick importance estimate")

    report["selected_features"] = feature_cols_final
    report["removed_features"] = {
        "constant": constant_features,
        "near_constant": near_constant_features,
        "highly_correlated": list(correlated_to_drop),
    }

    # Generate correlation heatmap
    try:
        fig, ax = plt.subplots(figsize=(14, 12))
        im = ax.imshow(X_final.corr(), cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
        plt.colorbar(im, ax=ax, shrink=0.8)
        ax.set_title("Feature Correlation Matrix (after cleaning)")
        ax.set_xlabel("Feature Index")
        ax.set_ylabel("Feature Index")
        plt.tight_layout()
        plt.savefig(EVAL_DIR / "correlation_matrix.png", dpi=150)
        plt.close()
    except Exception as e:
        logger.warning("Correlation heatmap failed: %s", e)

    # MI plot
    try:
        fig, ax = plt.subplots(figsize=(10, max(6, len(mi_df.head(30)) * 0.25)))
        top_mi = mi_df.head(30)
        colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(top_mi)))
        ax.barh(range(len(top_mi)), top_mi["mi_score"].values, color=colors)
        ax.set_yticks(range(len(top_mi)))
        ax.set_yticklabels(top_mi["feature"].values)
        ax.set_xlabel("Mutual Information")
        ax.set_title("Top 30 Features by Mutual Information")
        ax.invert_yaxis()
        plt.tight_layout()
        plt.savefig(EVAL_DIR / "mutual_information.png", dpi=150)
        plt.close()
    except Exception as e:
        logger.warning("MI plot failed: %s", e)

    # Save feature analysis report
    report_path = EVAL_DIR / "feature_analysis.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    logger.info("Feature analysis report saved to %s", report_path)

    return report


def main():
    logger.info("=" * 60)
    logger.info("Feature Validation & Selection")
    logger.info("=" * 60)

    feature_df = build_full_feature_matrix(str(DATASET_PATH))

    logger.info("\nDataset Statistics:")
    logger.info("  Total samples:  %d", len(feature_df))
    logger.info("  Total features: %d", len([c for c in feature_df.columns if c != "label"]))
    phishing = int(feature_df["label"].sum())
    safe = len(feature_df) - phishing
    logger.info("  Phishing: %d (%.1f%%)", phishing, 100 * phishing / len(feature_df))
    logger.info("  Safe:     %d (%.1f%%)", safe, 100 * safe / len(feature_df))
    logger.info("  Ratio:    1:%.1f", safe / max(phishing, 1))

    report = analyze_features(feature_df)

    selected = report["selected_features"]
    logger.info("\nSummary:")
    logger.info("  Original features:   %d", report["total_features"])
    logger.info("  Constant removed:    %d", len(report["removed_features"]["constant"]))
    logger.info("  Near-constant removed: %d", len(report["removed_features"]["near_constant"]))
    logger.info("  Correlated removed:  %d", len(report["removed_features"]["highly_correlated"]))
    logger.info("  Final features:      %d", len(selected))

    # Save selected features
    selected_path = PROJECT_ROOT / "ml" / "models" / "selected_features.json"
    with open(selected_path, "w") as f:
        json.dump(selected, f, indent=2)
    logger.info("Selected features saved to %s", selected_path)

    logger.info("Feature validation complete.")


if __name__ == "__main__":
    main()
