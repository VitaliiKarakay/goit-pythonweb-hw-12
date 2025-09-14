import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError

logger = logging.getLogger(__name__)


async def integrity_exception_handler(request: Request, exc: IntegrityError):
    logger.error(f"Database Integrity Error: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={"detail": "Record already exists with provided unique value."},
    )


async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"General Exception Occurred: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please contact support."},
    )


async def validation_exception_handler(request: Request, exc: ValidationError):
    logger.error(f"Validation Failed: {exc.errors()}")
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()},
    )


async def not_found_exception_handler(request: Request, exc: HTTPException):
    logger.warning(
        f"Resource Not Found: URL={request.url} - Detail={exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail or "The requested resource does not exist."},
    )
