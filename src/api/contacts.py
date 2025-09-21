from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from src.database.db import get_db
from src.schemas import (
    ContactCreate,
    ContactUpdate,
    ContactResponse,
    ContactListResponse,
)
from src.services.auth import get_current_user
from src.services.contacts import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post(
    "/",
    response_model=ContactResponse,
    status_code=201,
    responses={
        400: {"description": "Bad Request"},
        409: {"description": "Conflict"},
        422: {"description": "Validation Error"},
    },
)
async def create_contact(
    contact: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Create a new contact for the current user.

    Args:
        contact (ContactCreate): Contact data to create.
        db (AsyncSession): Database session dependency.
        current_user: Current authenticated user dependency.

    Returns:
        ContactResponse: Created contact data.
    """
    service = ContactService(db)
    return await service.create_contact(contact, user_id=current_user.id)


@router.get("/", response_model=ContactListResponse)
async def get_contacts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, le=500, description="Max number of records to return"),
    first_name: Optional[str] = Query(None, description="Filter by first name"),
    last_name: Optional[str] = Query(None, description="Filter by last name"),
    email: Optional[str] = Query(None, description="Filter by email"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get a list of contacts for the current user with optional filters.

    Args:
        skip (int): Number of records to skip.
        limit (int): Max number of records to return.
        first_name (Optional[str]): Filter by first name.
        last_name (Optional[str]): Filter by last name.
        email (Optional[str]): Filter by email.
        db (AsyncSession): Database session dependency.
        current_user: Current authenticated user dependency.

    Returns:
        ContactListResponse: List of contacts.
    """
    service = ContactService(db)
    return await service.get_contacts(
        skip, limit, first_name, last_name, email, user_id=current_user.id
    )


@router.get("/birthdays/", response_model=ContactListResponse)
async def get_upcoming_birthdays(
    days: int = Query(
        7, ge=1, le=30, description="Number of days ahead to check for birthdays"
    ),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, le=500, description="Max number of records to return"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get contacts with upcoming birthdays within a specified number of days.

    Args:
        days (int): Number of days ahead to check for birthdays.
        skip (int): Number of records to skip.
        limit (int): Max number of records to return.
        db (AsyncSession): Database session dependency.
        current_user: Current authenticated user dependency.

    Returns:
        ContactListResponse: List of contacts with upcoming birthdays.
    """
    service = ContactService(db)
    return await service.get_upcoming_birthdays(days, skip, limit, user_id=current_user.id)


@router.patch(
    "/{contact_id}",
    response_model=ContactResponse,
    responses={400: {"description": "Bad Request"}, 404: {"description": "Not Found"}},
)
async def update_contact(
    contact_id: int,
    contact: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Update an existing contact for the current user.

    Args:
        contact_id (int): ID of the contact to update.
        contact (ContactUpdate): Updated contact data.
        db (AsyncSession): Database session dependency.
        current_user: Current authenticated user dependency.

    Returns:
        ContactResponse: Updated contact data.

    Raises:
        HTTPException: If contact not found (404).
    """
    service = ContactService(db)
    updated_contact = await service.update_contact(contact_id, contact, user_id=current_user.id)
    if updated_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return updated_contact


@router.delete(
    "/{contact_id}",
    response_model=ContactResponse,
    responses={400: {"description": "Bad Request"}, 404: {"description": "Not Found"}},
)
async def delete_contact(
    contact_id: int, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    """
    Delete a contact for the current user.

    Args:
        contact_id (int): ID of the contact to delete.
        db (AsyncSession): Database session dependency.
        current_user: Current authenticated user dependency.

    Returns:
        ContactResponse: Deleted contact data.

    Raises:
        HTTPException: If contact not found (404).
    """
    service = ContactService(db)
    deleted_contact = await service.delete_contact(contact_id, user_id=current_user.id)
    if deleted_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return deleted_contact
