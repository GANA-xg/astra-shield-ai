from qdrant_client import QdrantClient

from core.config import settings


client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
)


def check_qdrant_connection() -> bool:
    """
    Verify that the application can connect to Qdrant.
    """
    try:
        client.get_collections()
        return True
    except Exception:
        return False


def close_qdrant_connection() -> None:
    """
    Placeholder for symmetry with other services.
    QdrantClient does not require an explicit close.
    """
    pass