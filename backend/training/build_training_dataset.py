import os
import sys
import pandas as pd
from tqdm import tqdm

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from feature_extractor_ml import extract_features
INPUT_DATASET = os.path.join(
    BASE_DIR,
    "datasets",
    "phishing",
    "PhiUSIIL_Phishing_URL_Dataset.csv",
)

OUTPUT_DATASET = os.path.join(
    BASE_DIR,
    "datasets",
    "phishing",
    "extracted_features.csv",
)

print("Loading dataset...")

df = pd.read_csv(INPUT_DATASET)

rows = []

print("Extracting features...")

for _, row in tqdm(df.iterrows(), total=len(df)):
    url = row["URL"]
    label = row["label"]

    try:
        features = extract_features(url)
        features["label"] = label
        rows.append(features)

    except Exception:
        continue

new_df = pd.DataFrame(rows)

new_df.to_csv(OUTPUT_DATASET, index=False)

print()
print("Finished!")
print(f"Rows: {len(new_df)}")
print(f"Saved to: {OUTPUT_DATASET}")