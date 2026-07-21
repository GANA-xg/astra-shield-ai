from fastapi import APIRouter

from schemas.citizen_request import CitizenRequest
from schemas.citizen_response import CitizenResponse
from agents.citizen_agent.advisor import get_citizen_advice

router = APIRouter(
    prefix="/citizen",
    tags=["Citizen Safety Assistant"],
)


@router.post("/advice", response_model=CitizenResponse)
async def get_advice(request: CitizenRequest):
    result = get_citizen_advice(request.query, history=request.history)
    return CitizenResponse(
        response=result["response"],
        category=result["category"],
        risk_level=result["risk_level"],
        source=result["source"],
        recommended_actions=result.get("recommended_actions", []),
    )
