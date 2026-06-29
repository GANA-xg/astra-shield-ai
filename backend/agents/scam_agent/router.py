from fastapi import APIRouter
from pydantic import BaseModel

from .detector import detect_scam

router = APIRouter(
    prefix="/scam",
    tags=["Scam Detection"],
)


class ScamRequest(BaseModel):
    transcript: str


@router.post("/detect")
def detect(request: ScamRequest):
    """
    Detect whether a call transcript contains scam indicators.
    """
    result = detect_scam(request.transcript)
    return result
