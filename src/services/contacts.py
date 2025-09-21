from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.schemas import ContactCreate, ContactUpdate


class ContactService:
    """
    Service class for business logic related to contacts.

    Args:
        db (AsyncSession): SQLAlchemy async session.
    """

    def __init__(self, db: AsyncSession):
        self.repo = ContactRepository(db)

    async def create_contact(self, contact_data: ContactCreate, user_id: int):
        """
        Create a new contact for a user.

        Args:
            contact_data (ContactCreate): Data for the new contact.
            user_id (int): ID of the user who owns the contact.

        Returns:
            Contact: Created contact instance.

        Raises:
            HTTPException: If contact creation fails.
        """
        try:
            return await self.repo.create_contact(contact_data, user_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_contacts(
        self,
        skip: int,
        limit: int,
        first_name: Optional[str],
        last_name: Optional[str],
        email: Optional[str],
        user_id: int,
    ):
        """
        Get a list of contacts for a user with optional filters.

        Args:
            skip (int): Number of records to skip.
            limit (int): Max number of records to return.
            first_name (Optional[str]): Filter by first name.
            last_name (Optional[str]): Filter by last name.
            email (Optional[str]): Filter by email.
            user_id (int): ID of the user who owns the contacts.

        Returns:
            dict: Dictionary with total_count, skip, limit, contacts.
        """
        return await self.repo.get_contacts(skip, limit, first_name, last_name, email, user_id)

    async def get_contact_by_id(self, contact_id: int):
        """
        Get a contact by its ID.

        Args:
            contact_id (int): ID of the contact.

        Returns:
            Contact: Contact instance or None if not found.
        """
        return await self.repo.get_contact_by_id(contact_id)

    async def get_upcoming_birthdays(self, days: int, skip: int, limit: int):
        """
        Get contacts with upcoming birthdays within a specified number of days.

        Args:
            days (int): Number of days ahead to check for birthdays.
            skip (int): Number of records to skip.
            limit (int): Max number of records to return.

        Returns:
            dict: Dictionary with total_count, skip, limit, contacts.
        """
        return await self.repo.get_upcoming_birthdays(days, skip, limit)

    async def update_contact(self, contact_id: int, contact_data: ContactUpdate):
        """
        Update an existing contact.

        Args:
            contact_id (int): ID of the contact to update.
            contact_data (ContactUpdate): Updated contact data.

        Returns:
            Contact: Updated contact instance or None if not found.
        """
        return await self.repo.update_contact(contact_id, contact_data)

    async def delete_contact(self, contact_id: int):
        """
        Delete a contact by its ID.

        Args:
            contact_id (int): ID of the contact to delete.

        Returns:
            Contact: Deleted contact instance or None if not found.
        """
        return await self.repo.delete_contact(contact_id)

    async def search_contacts(self, query: str):
        """
        Search contacts by query string (first name, last name, or email).

        Args:
            query (str): Search query string.

        Returns:
            list: List of matching contacts.
        """
        return await self.repo.search_contacts(query)
