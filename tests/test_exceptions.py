import pytest
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
from src.exceptions import integrity_exception_handler, general_exception_handler, validation_exception_handler, \
    not_found_exception_handler
import pydantic


class DummyRequest:
    url = "http://test/api"


class DummyModel(pydantic.BaseModel):
    field: str


@pytest.mark.asyncio
async def test_integrity_exception_handler():
    exc = IntegrityError("duplicate key", None, None)
    response = await integrity_exception_handler(DummyRequest(), exc)
    assert isinstance(response, JSONResponse)
    assert response.status_code == 400
    assert "detail" in response.body.decode()


@pytest.mark.asyncio
async def test_general_exception_handler():
    exc = Exception("Some error")
    response = await general_exception_handler(DummyRequest(), exc)
    assert isinstance(response, JSONResponse)
    assert response.status_code == 500
    assert "Internal server error" in response.body.decode()


@pytest.mark.asyncio
async def test_validation_exception_handler():
    class DummyModel(pydantic.BaseModel):
        field: str
    try:
        DummyModel(field=123)
    except ValidationError as exc:
        response = await validation_exception_handler(DummyRequest(), exc)
        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        assert "detail" in response.body.decode()


@pytest.mark.asyncio
async def test_not_found_exception_handler():
    exc = HTTPException(status_code=404, detail="Not found")
    response = await not_found_exception_handler(DummyRequest(), exc)
    assert isinstance(response, JSONResponse)
    assert response.status_code == 404
    assert "Not found" in response.body.decode()
