"""Tests for the Scam Detection Agent."""
import sys
sys.path.insert(0, ".")

from agents.scam_agent.detector import detect_scam
from agents.scam_agent.call_pattern_analyzer import analyze_call_pattern
from agents.scam_agent.alerting import generate_alert
from agents.scam_agent.schemas import ScamResponse


class TestScamDetection:
    def test_detect_otp_scam(self):
        result = detect_scam("Please share your OTP immediately, your account is blocked")
        assert result.is_scam is True
        assert result.risk_score > 40
        assert isinstance(result.scam_type, str)

    def test_detect_safe_message(self):
        result = detect_scam("Hi, how are you doing today?")
        assert result.risk_score < 60

    def test_scam_response_schema(self):
        result = detect_scam("Send your bank OTP now")
        assert hasattr(result, "is_scam")
        assert hasattr(result, "risk_score")
        assert hasattr(result, "scam_type")
        assert hasattr(result, "confidence")
        assert hasattr(result, "recommendation")
        assert hasattr(result, "is_digital_arrest_pattern")
        assert hasattr(result, "digital_arrest_confidence")
        assert hasattr(result, "digital_arrest_signals")


class TestCallPatternAnalyzer:
    def test_digital_arrest_pattern(self):
        transcript = """
        Hello, this is Officer Sharma from the Central Bureau of Investigation.
        Your Aadhaar number has been linked to a drug trafficking case.
        There is an arrest warrant issued in your name.
        You need to stay on this video call and share your screen.
        Don't tell anyone about this call, it is confidential.
        You must transfer 50000 rupees to prove your innocence.
        """
        result = analyze_call_pattern(transcript)
        assert result["is_digital_arrest_pattern"] is True
        assert result["score"] > 50
        assert len(result["matched_rules"]) >= 2

    def test_normal_call_not_flagged(self):
        transcript = "Hello, I am calling from your bank about your account statement."
        result = analyze_call_pattern(transcript)
        assert result["is_digital_arrest_pattern"] is False
        assert result["score"] < 30

    def test_metadata_boost(self):
        transcript = "Send money now"
        result = analyze_call_pattern(
            transcript,
            call_duration_seconds=1800,
            mentioned_screen_share=True,
            told_to_stay_on_line=True,
            told_not_to_contact_others=True,
        )
        assert result["score"] > 0


class TestAlerting:
    def test_generate_alert(self):
        resp = ScamResponse(
            is_scam=True, risk_score=85, scam_type="Digital Arrest Scam",
            confidence="High", detected_keywords=["cbi"],
            reason="Impersonating CBI", recommendation=["Hang up"],
            is_digital_arrest_pattern=True, digital_arrest_confidence=0.75,
            digital_arrest_signals=["Authority impersonation"],
        )
        alert = generate_alert(resp, transcript="test transcript")
        assert alert["alert_generated"] is True
        assert "alert_payload" in alert
        assert "dispatch" in alert
