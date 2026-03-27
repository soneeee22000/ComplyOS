"""Simple API key authentication for protecting LLM-backed endpoints."""

import os
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

COMPLYOS_API_KEY = os.getenv("COMPLYOS_API_KEY", "")


async def verify_api_key(api_key: str | None = Security(API_KEY_HEADER)) -> str:
    """Verify the API key from request header.

    If COMPLYOS_API_KEY is not set (empty), auth is disabled (dev mode).
    If set, requests must include a matching X-API-Key header.
    """
    if not COMPLYOS_API_KEY:
        return "dev-mode"

    if not api_key or api_key != COMPLYOS_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

    return api_key
