"""
Simple API key authentication for sensitive endpoints.

Usage:
    Set API_KEYS environment variable (comma-separated) to enable.
    If no keys are set, all requests pass through (development mode).
"""

import os
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader


API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

VALID_API_KEYS = set(
    k.strip() for k in os.environ.get("API_KEYS", "").split(",") if k.strip()
)


async def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    """
    Verify API key if keys are configured.

    In development mode (no keys configured), all requests pass through.
    """
    if not VALID_API_KEYS:
        return None

    if api_key is None:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Provide X-API-Key header.",
        )

    if api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key.",
        )

    return api_key
