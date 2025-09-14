from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_, extract
from datetime import date, timedelta

from src.database.models import Contact
from src.schemas import ContactCreate, ContactUpdate


class ContactRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_contact(self, contact_data: ContactCreate) -> Contact:
        existing_contact_stmt = select(
            Contact).filter_by(email=contact_data.email)
        existing_contact_result = await self.db.execute(existing_contact_stmt)
        existing_contact = existing_contact_result.scalar_one_or_none()

        if existing_contact:
            raise HTTPException(
                status_code=400,
                detail=f"Contact with email {contact_data.email} already exists.",
            )

        contact = Contact(**contact_data.model_dump())
        self.db.add(contact)

        try:
            await self.db.commit()
            await self.db.refresh(contact)
            return contact
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Contact with email {contact_data.email} already exists.",
            )

    async def get_contacts(
        self,
        skip: int = 0,
        limit: int = 100,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
    ):
        stmt = select(Contact)

        filters = []
        if first_name:
            filters.append(Contact.first_name.ilike(f"%{first_name}%"))
        if last_name:
            filters.append(Contact.last_name.ilike(f"%{last_name}%"))
        if email:
            filters.append(Contact.email.ilike(f"%{email}%"))

        if filters:
            stmt = stmt.where(and_(*filters))

        stmt = stmt.offset(skip).limit(limit)

        total_count_stmt = select(func.count()).select_from(Contact)
        if filters:
            total_count_stmt = total_count_stmt.where(and_(*filters))

        total_count_result = await self.db.execute(total_count_stmt)
        total_count = total_count_result.scalar()

        result = await self.db.execute(stmt)
        contacts = result.scalars().all()

        return {
            "total_count": total_count,
            "skip": skip,
            "limit": limit,
            "contacts": contacts,
        }

    async def get_contact_by_id(self, contact_id: int) -> Optional[Contact]:
        stmt = select(Contact).filter_by(id=contact_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_contact(
        self, contact_id: int, contact_data: ContactUpdate
    ) -> Optional[Contact]:
        contact = await self.get_contact_by_id(contact_id)
        if contact is None:
            raise HTTPException(status_code=404, detail="Contact not found")

        for key, value in contact_data.dict(exclude_unset=True).items():
            setattr(contact, key, value)

        try:
            await self.db.commit()
            await self.db.refresh(contact)
            return contact
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=400, detail="Failed to update contact.")

    async def delete_contact(self, contact_id: int) -> Optional[Contact]:
        contact = await self.get_contact_by_id(contact_id)
        if contact is None:
            raise HTTPException(status_code=404, detail="Contact not found")

        try:
            await self.db.delete(contact)
            await self.db.commit()
            return contact
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=400, detail="Failed to delete contact.")

    async def search_contacts(self, query: str) -> List[Contact]:
        stmt = select(Contact).filter(
            (Contact.first_name.ilike(f"%{query}%"))
            | (Contact.last_name.ilike(f"%{query}%"))
            | (Contact.email.ilike(f"%{query}%"))
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_upcoming_birthdays(self, days: int, skip: int, limit: int):
        today = date.today()
        future_date = today + timedelta(days=days)

        stmt = (
            select(Contact)
            .filter(
                (
                    (extract("month", Contact.birthday) == today.month)
                    & (extract("day", Contact.birthday) >= today.day)
                )
                | (
                    (extract("month", Contact.birthday) == future_date.month)
                    & (extract("day", Contact.birthday) <= future_date.day)
                )
            )
            .offset(skip)
            .limit(limit)
        )

        total_count_stmt = (
            select(func.count())
            .select_from(Contact)
            .filter(
                (
                    (extract("month", Contact.birthday) == today.month)
                    & (extract("day", Contact.birthday) >= today.day)
                )
                | (
                    (extract("month", Contact.birthday) == future_date.month)
                    & (extract("day", Contact.birthday) <= future_date.day)
                )
            )
        )

        total_count_result = await self.db.execute(total_count_stmt)
        total_count = total_count_result.scalar()

        result = await self.db.execute(stmt)
        contacts = result.scalars().all()

        return {
            "total_count": total_count,
            "skip": skip,
            "limit": limit,
            "contacts": contacts,
        }
