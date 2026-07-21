from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.responses import FileResponse
import tempfile, os

from agents.fraud_graph_agent.service import fraud_graph_service
from agents.fraud_graph_agent.analyzer import fraud_analyzer
from agents.fraud_graph_agent.schemas import RiskResponse
from agents.fraud_graph_agent.evidence_export import generate_evidence_package, render_evidence_pdf
from db.database import get_db
from db.models import EvidenceLog
from core.logging import logger
from core.auth import verify_api_key


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
def money_mules(_: str = Security(verify_api_key)):
    return fraud_graph_service.get_money_mules()


@router.get("/shared-device/{device_id}")
def shared_device(device_id: str, _: str = Security(verify_api_key)):
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


@router.get("/risk/{account_number}", response_model=RiskResponse)
def get_risk(account_number: str, _: str = Security(verify_api_key)):
    """Compute risk score for a single account."""
    try:
        return fraud_analyzer.analyze_account(account_number)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk analysis failed: {str(e)}")


@router.get("/risk/{account_number}/detailed")
def get_risk_detailed(account_number: str, _: str = Security(verify_api_key)):
    """Compute detailed risk breakdown for an account."""
    try:
        return fraud_analyzer.analyze_account_detailed(account_number)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk analysis failed: {str(e)}")


@router.get("/risk-all")
def get_all_risks(_: str = Security(verify_api_key)):
    """Compute risk scores for all accounts in the graph."""
    return fraud_analyzer.analyze_all_accounts()


@router.get("/evidence/{account_number}")
def get_evidence_package(account_number: str, _: str = Security(verify_api_key)):
    """Generate a court-admissible evidence package as a downloadable PDF."""
    try:
        evidence = generate_evidence_package(account_number)
        pdf_path = render_evidence_pdf(evidence)

        # Log the evidence generation for auditability
        try:
            db = next(get_db())
            if db is not None:
                log = EvidenceLog(
                    case_id=evidence["case_id"],
                    account_number=account_number,
                    risk_score=evidence["risk_assessment"]["score"],
                    risk_level=evidence["risk_assessment"]["risk"],
                    integrity_hash=evidence["integrity_hash"],
                    entity_count=len(evidence["entities"]),
                    relationship_count=len(evidence["relationships"]),
                    requested_by="api",
                )
                db.add(log)
                db.commit()
        except Exception as log_err:
            logger.warning("Failed to log evidence generation: %s", log_err)

        return FileResponse(
            path=pdf_path,
            filename=f"evidence_{account_number}_{evidence['case_id']}.pdf",
            media_type="application/pdf",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evidence generation failed: {str(e)}")


@router.get("/evidence/{account_number}/json")
def get_evidence_json(account_number: str, _: str = Security(verify_api_key)):
    """Generate a court-admissible evidence package as structured JSON."""
    try:
        evidence = generate_evidence_package(account_number)

        # Log the evidence generation
        try:
            db = next(get_db())
            if db is not None:
                log = EvidenceLog(
                    case_id=evidence["case_id"],
                    account_number=account_number,
                    risk_score=evidence["risk_assessment"]["score"],
                    risk_level=evidence["risk_assessment"]["risk"],
                    integrity_hash=evidence["integrity_hash"],
                    entity_count=len(evidence["entities"]),
                    relationship_count=len(evidence["relationships"]),
                    requested_by="api",
                )
                db.add(log)
                db.commit()
        except Exception as log_err:
            logger.warning("Failed to log evidence generation: %s", log_err)

        return evidence
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evidence generation failed: {str(e)}")
