from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr


class ContactBase(BaseModel):
    """
    Base schema for contact data.

    Attributes:
        first_name (str): First name of the contact.
        last_name (str): Last name of the contact.
        email (EmailStr): Email address.
        phone_number (str): Phone number.
        birthday (Optional[date]): Birthday (optional).
        additional_info (Optional[str]): Additional information (optional).
    """

    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: Optional[date] = None
    additional_info: Optional[str] = None


class ContactCreate(ContactBase):
    """
    Schema for creating a new contact.
    Inherits all fields from ContactBase.
    """

    pass


class ContactUpdate(ContactBase):
    """
    Schema for updating an existing contact.
    Inherits all fields from ContactBase.
    """

    pass


class ContactResponse(ContactBase):
    """
    Schema for returning contact data in responses.

    Attributes:
        id (int): Contact ID.
    """

    id: int


class ContactListResponse(BaseModel):
    """
    Schema for returning a list of contacts with pagination info.

    Attributes:
        total_count (int): Total number of contacts.
        skip (int): Number of records skipped.
        limit (int): Max number of records returned.
        contacts (List[ContactResponse]): List of contacts.
    """

    total_count: int
    skip: int
    limit: int
    contacts: List[ContactResponse]


class UserCreate(BaseModel):
    """
    Schema for user registration data.

    Attributes:
        email (EmailStr): User email address.
        password (str): User password.
    """

    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """
    Schema for user login data.

    Attributes:
        email (EmailStr): User email address.
        password (str): User password.
    """

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """
    Schema for returning user data in responses.

    Attributes:
        id (int): User ID.
        email (EmailStr): User email address.
        is_active (bool): User active status.
        avatar (Optional[str]): Avatar URL (optional).
        created_at (Optional[datetime]): Account creation timestamp.
        is_verified (bool): Email verification status.
        role (str): User role.
    """

    id: int
    email: EmailStr
    is_active: bool
    avatar: Optional[str] = None
    created_at: Optional[datetime] = None
    is_verified: bool
    role: str


class TokenResponse(BaseModel):
    """
    Schema for returning JWT access token.

    Attributes:
        access_token (str): JWT token string.
        token_type (str): Token type (default: "bearer").
    """

    access_token: str
    token_type: str = "bearer"
