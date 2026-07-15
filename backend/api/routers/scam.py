from fastapi import APIRouter, HTTPException

from agents.scam_agent.detector import detect_scam
from agents.scam_agent.schemas import ScamRequest, ScamResponse

router = APIRouter(
    prefix="/scam",
    tags=["Scam Detection"],
)


@router.post("/analyze", response_model=ScamResponse)
async def analyze_scam(request: ScamRequest):
    try:
        return detect_scam(request.transcript)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))