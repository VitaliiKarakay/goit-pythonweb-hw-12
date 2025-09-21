import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from repository.contacts import ContactRepository
from src.schemas import ContactCreate
from src.database.models import Contact


@pytest.mark.asyncio
async def test_create_contact_success():
    mock_db = AsyncMock()
    contact_data = ContactCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="1234567890"
    )
    user_id = 1
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None
    repo = ContactRepository(mock_db)
    contact = Contact(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="1234567890",
        user_id=user_id
    )
    repo.db.add = MagicMock()
    repo.db.refresh = AsyncMock()
    repo.db.commit = AsyncMock()
    repo.db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=lambda: None))
    result = await repo.create_contact(contact_data, user_id)
    assert result.email == contact_data.email
    assert result.user_id == user_id


@pytest.mark.asyncio
async def test_create_contact_duplicate_email():
    mock_db = AsyncMock()
    contact_data = ContactCreate(
        first_name="Jane",
        last_name="Doe",
        email="jane.doe@example.com",
        phone_number="0987654321"
    )
    user_id = 2
    existing_contact = Contact(
        first_name="Jane",
        last_name="Doe",
        email="jane.doe@example.com",
        phone_number="0987654321",
        user_id=user_id
    )
    mock_db.execute.return_value.scalar_one_or_none.return_value = existing_contact
    repo = ContactRepository(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await repo.create_contact(contact_data, user_id)
    assert exc_info.value.status_code == 409
    assert "already exists" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_contacts_success():
    mock_db = AsyncMock()
    user_id = 1
    contacts = [
        Contact(id=1, first_name="John", last_name="Doe", email="john.doe@example.com", phone_number="1234567890",
                user_id=user_id),
        Contact(id=2, first_name="Jane", last_name="Smith", email="jane.smith@example.com", phone_number="0987654321",
                user_id=user_id)
    ]
    mock_db.execute.side_effect = [
        MagicMock(scalar=lambda: len(contacts)),
        MagicMock(scalars=lambda: MagicMock(all=lambda: contacts))
    ]
    repo = ContactRepository(mock_db)
    result = await repo.get_contacts(user_id=user_id)
    assert result["total_count"] == 2
    assert len(result["contacts"]) == 2
    assert result["contacts"][0].email == "john.doe@example.com"


@pytest.mark.asyncio
async def test_get_contact_by_id_found():
    mock_db = AsyncMock()
    contact = Contact(id=1, first_name="John", last_name="Doe", email="john.doe@example.com", phone_number="1234567890", user_id=1)
    mock_db.execute.return_value.scalar_one_or_none = AsyncMock(return_value=contact)
    repo = ContactRepository(mock_db)
    result = await repo.get_contact_by_id(1)
    result = await result  # Await the coroutine returned by AsyncMock
    assert result.id == 1
    assert result.email == "john.doe@example.com"


@pytest.mark.asyncio
async def test_get_contact_by_id_not_found():
    mock_db = AsyncMock()
    mock_db.execute.return_value.scalar_one_or_none = AsyncMock(return_value=None)
    repo = ContactRepository(mock_db)
    result = await repo.get_contact_by_id(999)
    result = await result  # Await the coroutine returned by AsyncMock
    assert result is None


@pytest.mark.asyncio
async def test_update_contact_success():
    mock_db = AsyncMock()
    contact = Contact(id=1, first_name="John", last_name="Doe", email="john.doe@example.com", phone_number="1234567890",
                      user_id=1)
    mock_db.execute.return_value.scalar_one_or_none.return_value = contact
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None
    repo = ContactRepository(mock_db)
    update_data = MagicMock(dict=lambda exclude_unset: {"first_name": "Johnny"})
    repo.get_contact_by_id = AsyncMock(return_value=contact)
    result = await repo.update_contact(1, update_data)
    assert result.first_name == "Johnny"


@pytest.mark.asyncio
async def test_update_contact_not_found():
    mock_db = AsyncMock()
    repo = ContactRepository(mock_db)
    repo.get_contact_by_id = AsyncMock(return_value=None)
    update_data = MagicMock(dict=lambda exclude_unset: {"first_name": "Johnny"})
    with pytest.raises(HTTPException) as exc_info:
        await repo.update_contact(999, update_data)
    assert exc_info.value.status_code == 404
    assert "Contact not found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_delete_contact_success():
    mock_db = AsyncMock()
    contact = Contact(id=1, first_name="John", last_name="Doe", email="john.doe@example.com", phone_number="1234567890",
                      user_id=1)
    mock_db.execute.return_value.scalar_one_or_none.return_value = contact
    mock_db.delete.return_value = None
    mock_db.commit.return_value = None
    repo = ContactRepository(mock_db)
    repo.get_contact_by_id = AsyncMock(return_value=contact)
    result = await repo.delete_contact(1)
    assert result.id == 1


@pytest.mark.asyncio
async def test_delete_contact_not_found():
    mock_db = AsyncMock()
    repo = ContactRepository(mock_db)
    repo.get_contact_by_id = AsyncMock(return_value=None)
    with pytest.raises(HTTPException) as exc_info:
        await repo.delete_contact(999)
    assert exc_info.value.status_code == 404
    assert "Contact not found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_search_contacts_success():
    contacts = [
        Contact(id=1, first_name="John", last_name="Doe", email="john.doe@example.com", phone_number="1234567890", user_id=1),
        Contact(id=2, first_name="Jane", last_name="Smith", email="jane.smith@example.com", phone_number="0987654321", user_id=1)
    ]
    mock_db = AsyncMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = contacts
    mock_db.execute.return_value.scalars = lambda: mock_scalars
    repo = ContactRepository(mock_db)
    result = await repo.search_contacts("John")
    assert len(result) == 2
    assert any(c.first_name == "John" for c in result)
