from .classifier import classify_query

def generate_advice(query: str):
    category = classify_query(query)

    result = {
        "category": category,
        "risk_level": "LOW",
        "advice": [],
        "recommended_actions": []
    }

    if category == "OTP Fraud":
        result["risk_level"] = "HIGH"
        result["advice"] = [
            "Never share OTP with anyone.",
            "Banks never ask for OTP."
        ]
        result["recommended_actions"] = [
            "Contact your bank immediately if shared.",
            "Monitor transactions."
        ]

    elif category == "UPI Scam":
        result["risk_level"] = "HIGH"
        result["advice"] = [
            "Never share your UPI PIN.",
            "Receiving money does not require entering a PIN."
        ]
        result["recommended_actions"] = [
            "Disable UPI temporarily if compromised.",
            "Contact your bank."
        ]

    else:
        result["risk_level"] = "MEDIUM"
        result["advice"] = [
            "Be cautious when sharing personal information online."
        ]
        result["recommended_actions"] = [
            "Verify identities before making payments."
        ]

    return result