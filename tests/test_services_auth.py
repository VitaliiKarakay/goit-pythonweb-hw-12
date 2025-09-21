import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest
from src.services.auth import create_access_token, decode_access_token
from unittest.mock import AsyncMock
from fastapi import HTTPException, status
from src.services.auth import get_current_user


@pytest.mark.parametrize("user_id", [1, 42, 100])
def test_create_access_token(user_id):
    token = create_access_token({"sub": str(user_id)})
    assert isinstance(token, str)
    payload = decode_access_token(token)
    assert payload["sub"] == str(user_id)
    assert "exp" in payload


def test_decode_access_token_valid():
    token = create_access_token({"sub": "1"})
    payload = decode_access_token(token)
    assert payload["sub"] == "1"


def test_decode_access_token_invalid():
    payload = decode_access_token("invalid.token")
    assert payload is None


@pytest.mark.asyncio
async def test_get_current_user_success(monkeypatch):
    pass  # Удалено по запросу


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(monkeypatch):
    db = AsyncMock()
    monkeypatch.setattr("src.services.auth.decode_access_token", lambda t: None)
    with pytest.raises(HTTPException) as exc:
        await get_current_user("invalid.token", db)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.detail == "Invalid token"


@pytest.mark.asyncio
async def test_get_current_user_user_not_found(monkeypatch):
    pass  # Удалено по запросу
