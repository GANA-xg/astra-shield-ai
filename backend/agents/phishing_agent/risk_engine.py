def get_risk_level(score):
    if score >= 70:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 30:
        return "MEDIUM"
    return "LOW"


def get_recommendation(score):
    if score >= 70:
        return "Block immediately"
    if score >= 30:
        return "Proceed with caution"
    return "Appears safe"


def calculate_risk(
    features,
    ml_probability=None,
    blacklist_results=None,
    safe_browsing_result=None,
    llm_result=None,
):
    age = features.get("domain_age_days")
    tld = features.get("tld")
    brand = features.get("brand")

    score = 0
    signals = []

    # Feature-based signals
    if features.get("whois_failed"):
        # WHOIS may be unavailable for legitimate domains, so don't penalize it.
        signals.append("WHOIS information unavailable")

    if age is not None and age < 30:
        score += 40
        signals.append(f"New domain: {age} days old")

    if features.get("suspicious_tld"):
        score += 25
        signals.append(f"Suspicious TLD: {tld}")

    if features.get("brand_impersonation"):
        score += 35
        signals.append(f"Possible {brand} impersonation")

    if features.get("ip_url"):
        score += 30
        signals.append("IP-based URL")

    # ML Model
    if ml_probability is not None:
        if ml_probability >= 0.95:
            score += 40
        elif ml_probability >= 0.85:
            score += 30
        elif ml_probability >= 0.70:
            score += 20

        if ml_probability >= 0.70:
            signals.append(f"ML model confidence: {ml_probability:.0%}")

    # Blacklist
    if blacklist_results and any(blacklist_results.values()):
        score += 50
        detected = [
            name
            for name, flagged in blacklist_results.items()
            if flagged
        ]

        signals.append(
            f"Listed in: {', '.join(detected)}"
        )

    # Google Safe Browsing
    if (
        safe_browsing_result
        and safe_browsing_result.get("malicious", False)
    ):
        score += 60
        threat = safe_browsing_result.get("threat_type", "MALICIOUS")
        signals.append(f"Detected by Google Safe Browsing ({threat})")

    # LLM Verification
    if (
        llm_result
        and llm_result.get("verdict", "").lower() == "phishing"
    ):
        score += 20
        signals.append("LLM classified as phishing")

    final_score = min(score, 100)

    risk_level = get_risk_level(final_score)
    recommendation = get_recommendation(final_score)

    return {
        "risk_score": final_score,
        "risk_level": risk_level,
        "signals": signals,
        "recommendation": recommendation,
    }