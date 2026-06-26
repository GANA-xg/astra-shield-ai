from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from core.config import settings
from db.session import check_database_connection
from graph.connection import check_neo4j_connection
from qdrant.client import check_qdrant_connection

router = APIRouter(tags=["Health"])


@router.get("/health")
def health():
    postgres = check_database_connection()
    neo4j = check_neo4j_connection()
    qdrant = check_qdrant_connection()

    overall = postgres and neo4j and qdrant

    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENV,
        "status": "ready" if overall else "not_ready",
    }


@router.get("/health/live")
def live():
    return {
        "status": "alive"
    }


@router.get("/health/ready")
def ready():
    postgres = check_database_connection()
    neo4j = check_neo4j_connection()
    qdrant = check_qdrant_connection()

    services = {
        "postgres": "healthy" if postgres else "unhealthy",
        "neo4j": "healthy" if neo4j else "unhealthy",
        "qdrant": "healthy" if qdrant else "unhealthy",
    }

    overall = postgres and neo4j and qdrant

    if overall:
        return {
            "status": "ready",
            "services": services,
        }

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "not_ready",
            "services": services,
        },
    )