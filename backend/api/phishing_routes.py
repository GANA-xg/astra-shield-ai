from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session

from agents.phishing_agent.url_analyzer import analyze_url

from core.logging import logger
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
    ml_classification: str | None = None
    ml_top_contributors: list[dict] | None = None
    classification: str
    risk_score: int
    risk_level: str
    confidence: float
    ml_score: float
    google_safe_browsing: str
    virus_total: str
    ssl_status: str
    domain_age: str
    brand_similarity: str
    signals: list[str]
    recommendation: str
    explanations: list[str]


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

        try:
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
        except Exception as save_err:
            # DB persistence is non-critical
            logger.warning(f"Failed to save detection: {save_err}")

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
    try:
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
    except Exception as exc:
        logger.warning(f"Failed to fetch history: {exc}")
        return {"error": "Database unavailable", "detections": []}


@router.get("/stats")
def detection_stats(db: Session = Depends(get_db)):
    try:
        return get_detection_stats(db)
    except Exception as exc:
        logger.warning(f"Failed to fetch stats: {exc}")
        return {"error": "Database unavailable", "total_scans": 0}