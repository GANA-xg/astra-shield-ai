from pprint import pprint

from agents.phishing_agent.feature_extractor import extract_features
from agents.phishing_agent.xgboost_model import (
    predict_probability,
    predict_label,
)

url = "http://testsafebrowsing.appspot.com/s/phishing.html"

features = extract_features(url)

print("Extracted Features:")
pprint(features)
print()

probability = predict_probability(features)
label = predict_label(features)

print(f"Phishing probability: {probability:.4f}")
print(f"Prediction: {'PHISHING' if label else 'SAFE'}")