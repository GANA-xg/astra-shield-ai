# Currency Detection CNN - Evaluation Report

## Overview
Indian Currency Counterfeit Detection using EfficientNetB3 transfer learning.
Binary classification (genuine/fake) with optional denomination detection.

## Architecture
- **Base Model**: EfficientNetB3 (ImageNet pretrained, frozen)
- **Classification Head**: GlobalAvgPool → BatchNorm → Dense(256, relu) → Dropout(0.4) → Dense(1, sigmoid)
- **Denomination Head** (optional): Dense(128, relu) → Dense(7, softmax) for ₹10/20/50/100/200/500/2000

## Features
- **CNN Prediction**: End-to-end image classification via EfficientNetB3
- **Visual Feature Extraction**: Sharpness scoring (Laplacian variance), security thread detection (Hough lines)
- **Grad-CAM Visualization**: Class activation mapping for explainable predictions
- **Multi-class Output**: Genuine/fake classification + denomination detection

## Training
- **Optimizer**: Adam (lr=1e-3 with reduce-on-plateau)
- **Loss**: Binary crossentropy
- **Callbacks**: Early stopping (patience=5), model checkpointing
- **Input**: 224×224 RGB images, EfficientNet preprocessing

## Limitations
- Requires actual currency dataset for training (not included in repo)
- Model file `best_model.keras` not present until trained
- Current placeholder architecture outputs random predictions without training data

## Dataset Requirements
```
data-dir/
  train/
    genuine/   # Genuine currency note images
    fake/      # Counterfeit currency note images
  validation/
    genuine/
    fake/
  test/
    genuine/
    fake/
```

## Usage
```bash
# Retrain with dataset
python -m models.currency_cnn.retrain --data-dir /path/to/dataset --epochs 20

# Predict
python -m models.currency_cnn.predict /path/to/image.jpg

# Predict with Grad-CAM
python -m models.currency_cnn.predict /path/to/image.jpg --gradcam
```

## API Endpoints
- `POST /currency/predict` - Analyze currency image (multipart file upload)
  - Query param: `include_gradcam=true` for heatmap overlay
  - Returns: prediction, confidence, denomination, visual features, optional Grad-CAM
