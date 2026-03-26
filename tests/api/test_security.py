"""Tests for API key security dependency."""

import pytest
from fastapi import HTTPException

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from api.security import require_api_key
from settings import settings


@pytest.mark.api
@pytest.mark.asyncio
async def test_require_api_key_success():
    original = settings.valid_api_key
    try:
        settings.valid_api_key = "test-key"
        result = await require_api_key("test-key")
        assert result is None
    finally:
        settings.valid_api_key = original


@pytest.mark.api
@pytest.mark.asyncio
async def test_require_api_key_missing_header():
    with pytest.raises(HTTPException) as exc:
        await require_api_key(None)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Unauthorized"


@pytest.mark.api
@pytest.mark.asyncio
async def test_require_api_key_invalid_key():
    original = settings.valid_api_key
    try:
        settings.valid_api_key = "valid-key"
        with pytest.raises(HTTPException) as exc:
            await require_api_key("invalid-key")

        assert exc.value.status_code == 401
        assert exc.value.detail == "Unauthorized"
    finally:
        settings.valid_api_key = original
