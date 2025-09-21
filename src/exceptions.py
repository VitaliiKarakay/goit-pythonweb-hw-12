import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError

logger = logging.getLogger(__name__)


async def integrity_exception_handler(request: Request, exc: IntegrityError):
    """
    Handle database integrity errors (e.g., duplicate records).

    Args:
        request (Request): FastAPI request object.
        exc (IntegrityError): SQLAlchemy integrity error exception.

    Returns:
        JSONResponse: HTTP 400 response with error details.
    """
    logger.error(f"Database Integrity Error: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={"detail": "Record already exists with provided unique value."},
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle general uncaught exceptions.

    Args:
        request (Request): FastAPI request object.
        exc (Exception): Uncaught exception.

    Returns:
        JSONResponse: HTTP 500 response with error details.
    """
    logger.error(f"General Exception Occurred: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please contact support."},
    )


async def validation_exception_handler(request: Request, exc: ValidationError):
    """
    Handle Pydantic validation errors.

    Args:
        request (Request): FastAPI request object.
        exc (ValidationError): Pydantic validation error exception.

    Returns:
        JSONResponse: HTTP 400 response with validation error details.
    """
    logger.error(f"Validation Failed: {exc.errors()}")
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()},
    )


async def not_found_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTP 404 not found exceptions.

    Args:
        request (Request): FastAPI request object.
        exc (HTTPException): HTTP exception with status code 404.

    Returns:
        JSONResponse: HTTP 404 response with error details.
    """
    logger.warning(
        f"Resource Not Found: URL={request.url} - Detail={exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail or "The requested resource does not exist."},
    )
