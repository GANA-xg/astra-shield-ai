"""
Pydantic schemas for Scam Call Detection Agent.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class ScamRequest(BaseModel):
    """
    Request schema.
    """

    transcript: str = Field(
        ...,
        description="Phone call transcript"
    )


class ScamResponse(BaseModel):
    """
    Response schema.
    """

    is_scam: bool

    risk_score: int = Field(
        ge=0,
        le=100
    )

    scam_type: str

    confidence: str

    detected_keywords: List[str]

    reason: str

    recommendation: List[str]

    is_digital_arrest_pattern: bool = Field(
        default=False,
        description="True if the transcript matches the digital arrest scam playbook"
    )

    digital_arrest_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score (0-1) for digital arrest scam classification"
    )

    digital_arrest_signals: List[str] = Field(
        default_factory=list,
        description="Specific signals that indicate a digital arrest pattern"
    )
