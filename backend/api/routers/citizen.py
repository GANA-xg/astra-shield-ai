from fastapi import APIRouter

from schemas.citizen_request import CitizenRequest
from schemas.citizen_response import CitizenResponse
from agents.citizen_agent.advisor import generate_advice

router = APIRouter(
    prefix="/citizen",
    tags=["Citizen Safety Assistant"]
)

@router.post("/advice", response_model=CitizenResponse)
async def get_advice(request: CitizenRequest):
    return generate_advice(request.query)