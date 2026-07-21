from pydantic import BaseModel
from typing import List, Optional


class CitizenRequest(BaseModel):
    query: str
    history: Optional[List[dict]] = None
