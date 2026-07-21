"""Alert generation for high-confidence digital arrest scam detections.

When the digital arrest confidence crosses a configurable threshold,
generates a structured alert payload and logs it. The actual telecom/MHA
API call is stubbed behind `send_to_mha_stub()`.
"""

import json
import time
from datetime import datetime
from typing import Any, Dict, Optional

from core.logging import logger
from core.risk_config import DIGITAL_ARREST_ALERT_THRESHOLD


def send_to_mha_stub(alert_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Stub for the actual MHA/telecom integration.

    In production, this would:
    1. Authenticate with the MHA Cyber Crime portal API (mha.gov.in)
    2. Submit the alert via their REST API or national cybercrime
       reporting pipeline (https://cybercrime.gov.in)
    3. Require: victim contact (if available), suspected number,
       transcript excerpt, confidence score, timestamp, and a
       digitally signed evidence package reference
    4. Return a tracking ID from the MHA portal

    This stub simulates the API call for hackathon demonstration.
    """
    logger.info("[MHA STUB] Would send alert to MHA: %s", json.dumps(alert_payload, default=str)[:200])
    return {
        "status": "stub_sent",
        "mha_tracking_id": f"MHA-STUB-{int(time.time())}",
        "note": "This is a simulation. Real integration requires MHA API credentials and cert-based auth.",
    }


def generate_alert(scam_response, transcript: str = "", victim_contact: Optional[str] = None) -> Dict[str, Any]:
    """Generate a structured alert when digital arrest confidence is high.

    Args:
        scam_response: A ScamResponse object from detect_scam().
        transcript: The original call transcript (for excerpt).
        victim_contact: Victim's phone number if available.

    Returns:
        Dict with alert payload and dispatch status.
    """
    confidence = getattr(scam_response, "digital_arrest_confidence", 0.0)

    if confidence < DIGITAL_ARREST_ALERT_THRESHOLD:
        return {
            "alert_generated": False,
            "reason": f"Confidence {confidence:.2f} below threshold {DIGITAL_ARREST_ALERT_THRESHOLD}",
        }

    # Build transcript excerpt (first 500 chars)
    excerpt = transcript[:500] if transcript else "Transcript not available"

    alert_payload = {
        "alert_type": "DIGITAL_ARREST_SCAM",
        "priority": "CRITICAL" if confidence >= 0.8 else "HIGH",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "suspected_number": None,  # Would come from call metadata
        "victim_contact": victim_contact,
        "transcript_excerpt": excerpt,
        "confidence": round(confidence, 4),
        "risk_score": getattr(scam_response, "risk_score", 0),
        "scam_type": getattr(scam_response, "scam_type", "Digital Arrest Scam"),
        "signals": getattr(scam_response, "digital_arrest_signals", []),
        "detected_keywords": getattr(scam_response, "detected_keywords", []),
        "recommendation": getattr(scam_response, "recommendation", []),
    }

    # Dispatch to MHA stub
    dispatch_result = send_to_mha_stub(alert_payload)

    return {
        "alert_generated": True,
        "alert_payload": alert_payload,
        "dispatch": dispatch_result,
    }
