

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl

from agents.phishing_agent.url_analyzer import analyze_url

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
def analyze_url_endpoint(request: URLRequest):
    try:
        result = analyze_url(str(request.url))
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