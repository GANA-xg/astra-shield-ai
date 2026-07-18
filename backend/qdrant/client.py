from core.config import settings

_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client
    try:
        from qdrant_client import QdrantClient

        _client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
        )
    except Exception:
        _client = None
    return _client


def check_qdrant_connection() -> bool:
    """
    Verify that the application can connect to Qdrant.
    """
    c = _get_client()
    if c is None:
        return False
    try:
        c.get_collections()
        return True
    except Exception:
        return False


def close_qdrant_connection() -> None:
    """
    Placeholder for symmetry with other services.
    QdrantClient does not require an explicit close.
    """
    pass
