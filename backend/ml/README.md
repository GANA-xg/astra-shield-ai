# Phishing URL Detection — XGBoost Model

Production ML pipeline for URL-only phishing detection. No network calls, no page downloads, no WHOIS/DNS — every feature is reproducible from the raw URL string.

## Directory Structure

```
ml/
├── datasets/         # Raw dataset (PhiUSIIL)
├── features/         # Feature extraction modules
│   ├── extractor.py  # Orchestrator — single entry point
│   ├── lexical.py    # Lexical features (~40): entropy, keyword detection, brand similarity
│   ├── domain.py     # Domain features (~25): TLD analysis, punycode, homographs
│   └── security.py   # Security features (~15): HTTPS, shortened URLs, protocol confusion
├── training/         # Training pipeline
│   ├── train_optimized.py   # Full pipeline with CV, tuning, threshold opt, calibration
│   └── validate_features.py # Feature selection: constant/correlated removal, MI scoring
├── models/           # Trained artifacts
│   ├── phishing_xgboost.pkl  # XGBoost model (2.9 MB)
│   ├── feature_names.json    # Feature order for inference
│   ├── optimal_threshold.json # F1-maximizing threshold
│   ├── selected_features.json # Features after validation
│   ├── best_params.json      # Best hyperparameters
│   └── training_metadata.json # Training run metadata
├── evaluation/       # Evaluation artifacts (reports, plots)
│   ├── classification_report.txt
│   ├── confusion_matrix.png
│   ├── roc_curve.png
│   ├── precision_recall_curve.png
│   ├── feature_importance.png
│   ├── calibration_curve.png
│   ├── correlation_matrix.png
│   ├── mutual_information.png
│   └── shap_summary.png
└── predict.py        # Inference module (singleton, SHAP explanations)
```

## Model Performance

| Metric | Value |
|--------|-------|
| Accuracy | 99.78% |
| Precision | 99.65% |
| Recall | 99.97% |
| F1 | 99.81% |
| ROC-AUC | 99.86% |
| MCC | 99.56% |
| Balanced Accuracy | 99.75% |

Trained on 235,370 samples (134,850 phishing, 100,520 safe) from PhiUSIIL dataset. 80 features after validation.

## Known Limitation

The PhiUSIIL dataset labels login pages as phishing (since they target credentials). The model therefore assigns high phishing probabilities to legitimate brand URLs like `https://www.amazon.com/login` because the dataset's label distribution heavily weights `www` + `HTTPS` + brand domains as phishing. In production, this is mitigated by the risk engine which combines ML scores with other signals (Safe Browsing, blacklists, keyword analysis, TLD reputation).

## Usage

### Feature extraction (for training or debugging):
```python
from ml.features.extractor import extract_features
features = extract_features("https://example.com/login")
```

### Prediction:
```python
from ml.predict import load_model, predict

load_model()  # Called once at startup
result = predict("https://example.com/login")
# Returns: phishing_probability, safe_probability, classification,
#          confidence, risk_score, top_contributors (SHAP)
```

### Inference integration:
The model is loaded once at application startup in `api/main.py`. The `ml/predict.py` module's `predict()` function is called from `agents/phishing_agent/url_analyzer.py`.

## Training Pipeline

```bash
python -m ml.training.train_optimized
```

Steps:
1. Feature matrix building (~10K URLs/sec)
2. Feature validation (remove constant/near-constant/highly-correlated)
3. Stratified train/val/test split (60/20/20)
4. Coarse RandomizedSearchCV (30 iterations, 5-fold)
5. Fine-tuning (15 iterations, 5-fold)
6. Overfitting detection (>3% gap → complexity reduction)
7. Threshold optimization (F1-maximizing)
8. Calibration check (Brier score + calibration curve)
9. Test evaluation with all metrics
10. SHAP summary plot generation
