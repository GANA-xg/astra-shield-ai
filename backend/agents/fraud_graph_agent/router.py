from pydantic import BaseModel

from fastapi import APIRouter

from agents.fraud_graph_agent.service import (
    fraud_graph_service,
)


class GraphQuery(BaseModel):
    query: str


router = APIRouter(
    prefix="/fraud",
    tags=["Fraud Network"],
)


@router.get("/ping")
def ping():
    return {
        "status": "Fraud Graph Agent Working"
    }


@router.post("/graph")
def graph_analysis(body: GraphQuery):
    return fraud_graph_service.build_graph(body.query)


@router.get("/money-mules")
def money_mules():
    return fraud_graph_service.get_money_mules()

@router.get("/shared-device/{device_id}")
def shared_device(device_id: str):
    return fraud_graph_service.get_people_using_device(device_id)


@router.get("/money-flow/{account_number}")
def money_flow(account_number: str, depth: int = 5):
    return fraud_graph_service.trace_money_flow(
        account_number,
        depth,
    )

@router.get("/shortest-path/{source_account}/{target_account}")
def shortest_path(
    source_account: str,
    target_account: str,
):
    return fraud_graph_service.get_shortest_path(
        source_account,
        target_account,
    )

@router.get("/rings")
def fraud_rings(
    minimum_connections: int = 2,
):
    return fraud_graph_service.get_fraud_rings(
        minimum_connections,
    )