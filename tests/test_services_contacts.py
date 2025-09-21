import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from src.services.contacts import ContactService
from src.schemas import ContactCreate, ContactUpdate
from src.database.models import Contact


@pytest_asyncio.fixture
def repo():
    repo = AsyncMock()
    repo.create_contact = AsyncMock()
    repo.get_contacts = AsyncMock()
    repo.get_contact_by_id = AsyncMock()
    repo.get_upcoming_birthdays = AsyncMock()
    repo.update_contact = AsyncMock()
    return repo


@pytest.mark.asyncio
async def test_create_contact_success(repo):
    service = ContactService.__new__(ContactService)
    service.repo = repo
    repo.create_contact.return_value = Contact(id=1, first_name="John", last_name="Doe", email="john@example.com",
                                               phone_number="1234567890", user_id=1)
    contact_data = ContactCreate(first_name="John", last_name="Doe", email="john@example.com",
                                 phone_number="1234567890")
    contact = await service.create_contact(contact_data, user_id=1)
    assert contact.email == "john@example.com"


@pytest.mark.asyncio
async def test_create_contact_value_error(repo):
    service = ContactService.__new__(ContactService)
    service.repo = repo
    repo.create_contact.side_effect = ValueError("Invalid data")
    contact_data = ContactCreate(first_name="John", last_name="Doe", email="john@example.com",
                                 phone_number="1234567890")
    with pytest.raises(HTTPException) as exc:
        await service.create_contact(contact_data, user_id=1)
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_get_contacts_success(repo):
    service = ContactService.__new__(ContactService)
    service.repo = repo
    repo.get_contacts.return_value = {"total_count": 1, "skip": 0, "limit": 100, "contacts": [
        Contact(id=1, first_name="John", last_name="Doe", email="john@example.com", phone_number="1234567890",
                user_id=1)]}
    contacts = await service.get_contacts(0, 100, None, None, None, 1)
    assert contacts["total_count"] == 1
    assert len(contacts["contacts"]) == 1


@pytest.mark.asyncio
async def test_get_contact_by_id_found(repo):
    service = ContactService.__new__(ContactService)
    service.repo = repo
    repo.get_contact_by_id.return_value = Contact(id=1, first_name="John", last_name="Doe", email="john@example.com",
                                                  phone_number="1234567890", user_id=1)
    contact = await service.get_contact_by_id(1)
    assert contact.id == 1


@pytest.mark.asyncio
async def test_get_contact_by_id_not_found(repo):
    service = ContactService.__new__(ContactService)
    service.repo = repo
    repo.get_contact_by_id.return_value = None
    contact = await service.get_contact_by_id(999)
    assert contact is None


@pytest.mark.asyncio
async def test_get_upcoming_birthdays(repo):
    service = ContactService.__new__(ContactService)
    service.repo = repo
    repo.get_upcoming_birthdays.return_value = {"total_count": 1, "skip": 0, "limit": 100, "contacts": [
        Contact(id=1, first_name="John", last_name="Doe", email="john@example.com", phone_number="1234567890",
                user_id=1)]}
    result = await service.get_upcoming_birthdays(7, 0, 100)
    assert result["total_count"] == 1
    assert len(result["contacts"]) == 1


@pytest.mark.asyncio
async def test_update_contact_success(repo):
    service = ContactService.__new__(ContactService)
    service.repo = repo
    repo.update_contact.return_value = Contact(id=1, first_name="Jane", last_name="Doe", email="john@example.com",
                                               phone_number="1234567890", user_id=1)
    update_data = ContactUpdate(first_name="Jane", last_name="Doe", email="john@example.com", phone_number="1234567890")
    updated_contact = await service.update_contact(1, update_data)
    assert updated_contact.first_name == "Jane"


@pytest.mark.asyncio
async def test_update_contact_not_found(repo):
    service = ContactService.__new__(ContactService)
    service.repo = repo
    repo.update_contact.return_value = None
    update_data = ContactUpdate(first_name="Jane", last_name="Doe", email="john@example.com", phone_number="1234567890")
    updated_contact = await service.update_contact(999, update_data)
    assert updated_contact is None
