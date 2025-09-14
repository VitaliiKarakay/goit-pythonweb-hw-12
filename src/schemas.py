from datetime import date
from typing import Optional, List

from pydantic import BaseModel, EmailStr


class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: Optional[date] = None
    additional_info: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(ContactBase):
    pass


class ContactResponse(ContactBase):
    id: int


class ContactListResponse(BaseModel):
    total_count: int
    skip: int
    limit: int
    contacts: List[ContactResponse]
