from pydantic import BaseModel

class CitizenRequest(BaseModel):
    query: str