"""
Pydantic schemas for Scam Call Detection Agent.
"""

from pydantic import BaseModel, Field
from typing import List


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