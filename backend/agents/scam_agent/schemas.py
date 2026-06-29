from pydantic import BaseModel
from typing import List


class ScamAnalysis(BaseModel):
    risk_level: str
    confidence: int
    scam_type: str
    red_flags: List[str]
    summary: str
    recommendation: str