from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from agents.scam_agent.detector import detect_scam
from agents.scam_agent.schemas import ScamRequest, ScamResponse
from agents.scam_agent.alerting import generate_alert

router = APIRouter(
    prefix="/scam",
    tags=["Scam Detection"],
)


class ScamAnalyzeRequest(BaseModel):
    transcript: str
    caller_number: Optional[str] = None
    claimed_identity: Optional[str] = None
    call_duration_seconds: Optional[int] = None
    mentioned_screen_share: Optional[bool] = None
    mentioned_video_call: Optional[bool] = None
    time_of_day: Optional[str] = None
    told_to_stay_on_line: Optional[bool] = None
    told_not_to_contact_others: Optional[bool] = None
    victim_contact: Optional[str] = None


@router.post("/analyze", response_model=ScamResponse)
async def analyze_scam(request: ScamAnalyzeRequest):
    try:
        call_metadata = {}
        for field in ["caller_number", "claimed_identity", "call_duration_seconds",
                       "mentioned_screen_share", "mentioned_video_call", "time_of_day",
                       "told_to_stay_on_line", "told_not_to_contact_others"]:
            val = getattr(request, field, None)
            if val is not None:
                call_metadata[field] = val

        return detect_scam(request.transcript, **call_metadata)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-and-alert")
async def analyze_scam_with_alert(request: ScamAnalyzeRequest):
    """Analyze transcript and generate alert if digital arrest pattern detected."""
    try:
        call_metadata = {}
        for field in ["caller_number", "claimed_identity", "call_duration_seconds",
                       "mentioned_screen_share", "mentioned_video_call", "time_of_day",
                       "told_to_stay_on_line", "told_not_to_contact_others"]:
            val = getattr(request, field, None)
            if val is not None:
                call_metadata[field] = val

        scam_response = detect_scam(request.transcript, **call_metadata)
        alert_result = generate_alert(
            scam_response,
            transcript=request.transcript,
            victim_contact=request.victim_contact,
        )

        return {
            "scam_analysis": scam_response,
            "alert": alert_result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
