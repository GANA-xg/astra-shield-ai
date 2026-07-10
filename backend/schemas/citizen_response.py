from pydantic import BaseModel
from typing import List

class CitizenResponse(BaseModel):
    category: str
    risk_level: str
    advice: List[str]
    recommended_actions: List[str]