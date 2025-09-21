from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """
    Base class for SQLAlchemy models.
    """


class Contact(Base):
    """
    ORM model representing a contact.

    Attributes:
        id (int): Primary key.
        first_name (str): First name of the contact.
        last_name (str): Last name of the contact.
        email (str): Email address (unique).
        phone_number (str): Phone number.
        birthday (datetime): Birthday (optional).
        additional_info (str): Additional information (optional).
        user_id (int): Foreign key to the user who owns the contact.
    """

    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone_number = Column(String(20), nullable=False)
    birthday = Column(DateTime, nullable=True)
    additional_info = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)


class User(Base):
    """
    ORM model representing a user.

    Attributes:
        id (int): Primary key.
        email (str): Email address (unique).
        hashed_password (str): Hashed password.
        is_active (bool): User active status.
        avatar (str): Avatar URL (optional).
        created_at (datetime): Account creation timestamp.
        updated_at (datetime): Last update timestamp.
        is_verified (bool): Email verification status.
        verification_token (str): Token for email verification (optional).
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    avatar = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(255), nullable=True)
