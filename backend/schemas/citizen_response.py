from pydantic import BaseModel
from typing import List, Optional


class CitizenResponse(BaseModel):
    response: str
    category: str
    risk_level: str
    source: str
    recommended_actions: List[str]
