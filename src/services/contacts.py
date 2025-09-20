from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.schemas import ContactCreate, ContactUpdate


class ContactService:
    def __init__(self, db: AsyncSession):
        self.repo = ContactRepository(db)

    async def create_contact(self, contact_data: ContactCreate, user_id: int):
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
        return await self.repo.get_contacts(skip, limit, first_name, last_name, email, user_id)

    async def get_contact_by_id(self, contact_id: int):
        return await self.repo.get_contact_by_id(contact_id)

    async def get_upcoming_birthdays(self, days: int, skip: int, limit: int):
        return await self.repo.get_upcoming_birthdays(days, skip, limit)

    async def update_contact(self, contact_id: int, contact_data: ContactUpdate):
        return await self.repo.update_contact(contact_id, contact_data)

    async def delete_contact(self, contact_id: int):
        return await self.repo.delete_contact(contact_id)

    async def search_contacts(self, query: str):
        return await self.repo.search_contacts(query)
