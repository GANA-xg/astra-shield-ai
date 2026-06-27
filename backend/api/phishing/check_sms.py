

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import re

router = APIRouter(
    prefix="/api/phishing",
    tags=["Phishing Detection"],
)

SUSPICIOUS_KEYWORDS = {
    "verify", "urgent", "bank", "otp", "password", "click",
    "login", "account", "gift", "reward", "winner", "prize",
    "update", "limited", "suspended", "confirm", "crypto",
}

URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")


class SMSRequest(BaseModel):
    message: str


class SMSResponse(BaseModel):
    message: str
    contains_url: bool
    urls: list[str]
    keyword_count: int
    risk_score: int
    risk_level: str
    recommendation: str
    signals: list[str]


@router.post("/check-sms", response_model=SMSResponse)
def check_sms(request: SMSRequest):
    text = request.message.strip()

    if not text:
        raise HTTPException(status_code=400, detail="SMS message cannot be empty")

    urls = URL_PATTERN.findall(text)
    contains_url = len(urls) > 0

    lower = text.lower()
    keyword_count = sum(word in lower for word in SUSPICIOUS_KEYWORDS)

    score = 0
    signals = []

    if contains_url:
        score += 40
        signals.append("Contains URL")

    if keyword_count:
        score += min(keyword_count * 10, 40)
        signals.append(f"Contains {keyword_count} suspicious keyword(s)")

    if "otp" in lower:
        score += 10
        signals.append("Mentions OTP")

    score = min(score, 100)

    if score >= 80:
        level = "CRITICAL"
        recommendation = "Block immediately"
    elif score >= 60:
        level = "HIGH"
        recommendation = "Likely phishing"
    elif score >= 30:
        level = "MEDIUM"
        recommendation = "Proceed with caution"
    else:
        level = "LOW"
        recommendation = "Likely safe"

    return {
        "message": text,
        "contains_url": contains_url,
        "urls": urls,
        "keyword_count": keyword_count,
        "risk_score": score,
        "risk_level": level,
        "recommendation": recommendation,
        "signals": signals,
    }