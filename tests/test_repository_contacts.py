import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from src.repository.contacts import ContactRepository
from src.schemas import ContactCreate, ContactUpdate
from src.database.models import Contact


@pytest_asyncio.fixture
def db_session():
    return AsyncMock()


@pytest.mark.asyncio
async def test_create_contact_success(db_session):
    repo = ContactRepository(db_session)
    db_session.execute.return_value.scalar_one_or_none.return_value = None
    db_session.commit.return_value = None
    db_session.refresh.return_value = None
    contact_data = ContactCreate(first_name="John", last_name="Doe", email="john@example.com",
                                 phone_number="1234567890")
    db_session.add.return_value = None
    result_contact = Contact(id=1, first_name="John", last_name="Doe", email="john@example.com",
                             phone_number="1234567890", user_id=1)
    db_session.refresh.return_value = None
    db_session.execute.return_value.scalar_one_or_none.side_effect = [None]
    db_session.refresh.side_effect = lambda contact: None
    db_session.commit.side_effect = lambda: None
    db_session.add.side_effect = lambda contact: None
    repo.db.refresh = AsyncMock()
    repo.db.commit = AsyncMock()
    repo.db.add = AsyncMock()
    repo.db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=lambda: None))
    contact = await repo.create_contact(contact_data, user_id=1)
    assert contact.email == "john@example.com"


@pytest.mark.asyncio
async def test_create_contact_duplicate_email(db_session):
    repo = ContactRepository(db_session)
    db_session.execute.return_value.scalar_one_or_none.return_value = Contact(email="john@example.com", user_id=1)
    contact_data = ContactCreate(first_name="John", last_name="Doe", email="john@example.com",
                                 phone_number="1234567890")
    with pytest.raises(HTTPException) as exc:
        await repo.create_contact(contact_data, user_id=1)
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_get_contacts_success(db_session):
    repo = ContactRepository(db_session)
    contacts_list = [Contact(id=1, first_name="John", last_name="Doe", email="john@example.com", phone_number="1234567890", user_id=1)]
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = contacts_list
    execute_mock = MagicMock()
    execute_mock.scalars.return_value = scalars_mock
    execute_mock.scalar.return_value = len(contacts_list)
    db_session.execute.return_value = execute_mock
    contacts = await repo.get_contacts(user_id=1)
    assert contacts["total_count"] == 1
    assert len(contacts["contacts"]) == 1


@pytest.mark.asyncio
async def test_get_contact_by_id_found(db_session):
    repo = ContactRepository(db_session)
    contact_obj = Contact(id=1, first_name="John", last_name="Doe", email="john@example.com", phone_number="1234567890", user_id=1)
    execute_mock = MagicMock()
    execute_mock.scalar_one_or_none.return_value = contact_obj
    db_session.execute.return_value = execute_mock
    contact = await repo.get_contact_by_id(1)
    assert contact.id == 1


@pytest.mark.asyncio
async def test_get_contact_by_id_not_found(db_session):
    repo = ContactRepository(db_session)
    execute_mock = MagicMock()
    execute_mock.scalar_one_or_none.return_value = None
    db_session.execute.return_value = execute_mock
    contact = await repo.get_contact_by_id(999)
    assert contact is None


@pytest.mark.asyncio
async def test_update_contact_success(db_session):
    repo = ContactRepository(db_session)
    contact = Contact(id=1, first_name="John", last_name="Doe", email="john@example.com", phone_number="1234567890", user_id=1)
    repo.get_contact_by_id = AsyncMock(return_value=contact)
    db_session.commit.return_value = None
    db_session.refresh.return_value = None
    update_data = ContactUpdate(first_name="Jane", last_name="Doe", email="john@example.com", phone_number="1234567890")
    updated_contact = await repo.update_contact(1, update_data)
    assert updated_contact.first_name == "Jane"


@pytest.mark.asyncio
async def test_update_contact_not_found(db_session):
    repo = ContactRepository(db_session)
    repo.get_contact_by_id = AsyncMock(return_value=None)
    update_data = ContactUpdate(first_name="Jane", last_name="Doe", email="john@example.com", phone_number="1234567890")
    with pytest.raises(HTTPException) as exc:
        await repo.update_contact(999, update_data)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_contact_success(db_session):
    repo = ContactRepository(db_session)
    contact = Contact(id=1, first_name="John", last_name="Doe", email="john@example.com", phone_number="1234567890", user_id=1)
    repo.get_contact_by_id = AsyncMock(return_value=contact)
    db_session.delete.return_value = None
    db_session.commit.return_value = None
    deleted_contact = await repo.delete_contact(1)
    assert deleted_contact.id == 1


@pytest.mark.asyncio
async def test_delete_contact_not_found(db_session):
    repo = ContactRepository(db_session)
    repo.get_contact_by_id = AsyncMock(return_value=None)
    with pytest.raises(HTTPException) as exc:
        await repo.delete_contact(999)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_search_contacts_success(db_session):
    repo = ContactRepository(db_session)
    contacts_list = [Contact(id=1, first_name="John", last_name="Doe", email="john@example.com", phone_number="1234567890", user_id=1)]
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = contacts_list
    execute_mock = MagicMock()
    execute_mock.scalars.return_value = scalars_mock
    db_session.execute.return_value = execute_mock
    contacts = await repo.search_contacts("John")
    assert len(contacts) == 1
