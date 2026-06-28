from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session

from agents.phishing_agent.url_analyzer import analyze_url

from db.database import get_db
from db.crud import (
    save_detection,
    get_detection_history,
    get_detection_stats,
)

router = APIRouter(
    prefix="/api/phishing",
    tags=["Phishing Detection"],
)


class URLRequest(BaseModel):
    url: HttpUrl


class URLResponse(BaseModel):
    url: str
    domain: str
    features: dict
    safe_browsing: dict
    blacklists: dict
    ml_probability: float
    risk_score: int
    risk_level: str
    recommendation: str
    signals: list[str]


@router.post(
    "/analyze-url",
    response_model=URLResponse,
    summary="Analyze a URL for phishing",
)
def analyze_url_endpoint(
    request: URLRequest,
    db: Session = Depends(get_db),
):
    try:
        result = analyze_url(str(request.url))

        save_detection(
            db=db,
            scan_type="url",
            input_text=str(request.url),
            risk_score=result["risk_score"],
            risk_level=result["risk_level"],
            recommendation=result["recommendation"],
            ml_probability=result.get("ml_probability", 0.0),
            signals=result["signals"],
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"URL analysis failed: {str(exc)}",
        )


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "phishing-agent",
    }


@router.get("/history")
def detection_history(
    limit: int = 50,
    db: Session = Depends(get_db),
):
    detections = get_detection_history(db, limit)

    return [
        {
            "id": d.id,
            "scan_type": d.scan_type,
            "input_text": d.input_text,
            "risk_score": d.risk_score,
            "risk_level": d.risk_level,
            "recommendation": d.recommendation,
            "ml_probability": d.ml_probability,
            "signals": d.signals,
            "created_at": d.created_at,
        }
        for d in detections
    ]


@router.get("/stats")
def detection_stats(db: Session = Depends(get_db)):
    return get_detection_stats(db)