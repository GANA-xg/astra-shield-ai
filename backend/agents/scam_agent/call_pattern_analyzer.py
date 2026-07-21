"""Digital Arrest Scam Call Pattern Analyzer.

Rule-based scoring for the specific "digital arrest" scam playbook:
- Impersonating CBI/ED/Customs/Police
- Fabricated claims about Aadhaar/parcel linked to crime
- Pressure to stay on video call
- Isolation instructions (don't tell anyone)
- Request for money transfer "to prove innocence"

Each rule returns a weighted score. The total is mapped to a confidence level.
"""

from typing import Dict, List, Optional, Tuple


# --- Rule definitions ---
# Each rule: (name, weight, description)

IMPERSONATION_KEYWORDS = {
    "cbi": 15, "central bureau": 15, "ed": 10, "enforcement directorate": 15,
    "customs": 10, "police": 8, "cyber crime": 12, "cybercrime": 12,
    "crime branch": 12, "investigation officer": 15, "superintendent": 10,
    "commissioner": 10, "narcotics": 10, "intelligence bureau": 15,
    "ministry of home": 12, "mha": 12, "finance ministry": 10,
    "tax department": 10, "income tax": 10, "gst": 8,
}

CRIME_FABRICATION_KEYWORDS = {
    "aadhaar linked": 15, "aadhaar is linked": 15, "parcel linked": 12,
    "passport linked": 12, "sim card linked": 12, "bank account linked": 12,
    "your number was used": 15, "your name was found": 15,
    "fake passport": 15, "drug trafficking": 15, "money laundering": 15,
    "terrorist": 18, "crime case": 12, "fir filed": 15,
    "court notice": 12, "warrant": 15, "arrest warrant": 18,
    "red corner notice": 18, "interpol": 15,
}

PRESSURE_TACTICS = {
    "stay on call": 12, "don't hang up": 12, "don't disconnect": 12,
    "keep the line": 10, "don't put down": 10, "video call": 8,
    "turn on camera": 8, "share screen": 10, "install anydesk": 15,
    "install teamviewer": 15, "remote access": 12, "screen sharing": 10,
    "whatsapp video": 8, "google meet": 8, "zoom call": 8,
}

ISOLATION_INSTRUCTIONS = {
    "don't tell anyone": 15, "don't tell your family": 15,
    "this is confidential": 10, "don't inform": 12,
    "don't discuss": 12, "keep this secret": 15,
    "your family will be involved": 15, "they will arrest your family": 18,
    "don't contact your lawyer": 15, "don't call anyone": 12,
    "alone": 5,
}

MONEY_REQUEST = {
    "transfer money": 15, "send money": 15, "pay fine": 12,
    "prove innocence": 18, "clear your name": 15, "settlement": 10,
    "account will be unfrozen": 15, "deposit": 8, "upi": 8,
    "gift card": 12, "google pay": 8, "phonepe": 8, "paytm": 8,
    "bitcoin": 15, "crypto": 15, "wallet": 10,
    "verify your account": 10, "account verification": 10,
    "zero balance": 12, "new account": 10,
}


def analyze_call_pattern(
    transcript: str,
    caller_number: Optional[str] = None,
    claimed_identity: Optional[str] = None,
    call_duration_seconds: Optional[int] = None,
    mentioned_screen_share: Optional[bool] = None,
    mentioned_video_call: Optional[bool] = None,
    time_of_day: Optional[str] = None,
    told_to_stay_on_line: Optional[bool] = None,
    told_not_to_contact_others: Optional[bool] = None,
) -> Dict:
    """Analyze a call transcript for digital arrest scam patterns.

    Returns:
        Dict with:
          - score (0-100)
          - confidence (LOW/MEDIUM/HIGH/VERY_HIGH)
          - matched_rules: list of {rule, score, detail}
          - is_digital_arrest_pattern: bool
    """
    transcript_lower = transcript.lower()
    matched_rules = []
    total_score = 0.0

    def _check_keywords(keyword_map: Dict[str, int], rule_name: str):
        nonlocal total_score
        found = []
        for keyword, weight in keyword_map.items():
            if keyword in transcript_lower:
                found.append(keyword)
        if found:
            rule_score = min(sum(keyword_map[k] for k in found), 25)
            total_score += rule_score
            matched_rules.append({
                "rule": rule_name,
                "score": rule_score,
                "detail": f"Found {len(found)} indicator(s): {', '.join(found[:5])}",
            })

    # 1. Impersonation of authorities
    _check_keywords(IMPERSONATION_KEYWORDS, "authority_impersonation")

    # 2. Crime fabrication
    _check_keywords(CRIME_FABRICATION_KEYWORDS, "crime_fabrication")

    # 3. Pressure tactics
    _check_keywords(PRESSURE_TACTICS, "pressure_tactics")
    if mentioned_screen_share:
        total_score += 10
        matched_rules.append({
            "rule": "screen_share_mentioned",
            "score": 10,
            "detail": "Screen sharing was mentioned in the call",
        })
    if told_to_stay_on_line:
        total_score += 12
        matched_rules.append({
            "rule": "stay_on_line",
            "score": 12,
            "detail": "Victim was told to stay on the line continuously",
        })

    # 4. Isolation instructions
    _check_keywords(ISOLATION_INSTRUCTIONS, "isolation_instructions")
    if told_not_to_contact_others:
        total_score += 15
        matched_rules.append({
            "rule": "isolation_explicit",
            "score": 15,
            "detail": "Victim was explicitly told not to contact others",
        })

    # 5. Money transfer requests
    _check_keywords(MONEY_REQUEST, "money_request")

    # 6. Call metadata signals
    if call_duration_seconds and call_duration_seconds > 1800:
        total_score += 5
        matched_rules.append({
            "rule": "long_duration",
            "score": 5,
            "detail": f"Call lasted {call_duration_seconds // 60} minutes (unusually long)",
        })

    if time_of_day in ("late_night", "early_morning"):
        total_score += 3
        matched_rules.append({
            "rule": "suspicious_timing",
            "score": 3,
            "detail": f"Call occurred during {time_of_day} hours",
        })

    # Cap at 100
    total_score = min(total_score, 100.0)

    # Determine confidence band
    if total_score >= 70:
        confidence = "VERY_HIGH"
    elif total_score >= 45:
        confidence = "HIGH"
    elif total_score >= 20:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    is_digital_arrest = total_score >= 30

    return {
        "score": round(total_score, 2),
        "confidence": confidence,
        "is_digital_arrest_pattern": is_digital_arrest,
        "matched_rules": matched_rules,
    }
