"""
Service layer for currency counterfeit detection.
"""

from models.currency_cnn.predict import predict_currency


def analyze_currency(image_path: str):
    """
    Analyze a currency image using the trained CNN.
    """

    return predict_currency(image_path)