import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from src.main import app

TEST_USER = {
    "email": "testuser@example.com",
    "password": "TestPassword123!"
}

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def get_token(client):
    client.post("/auth/register", json=TEST_USER)
    response = client.post("/auth/login", json=TEST_USER)
    assert response.status_code == 200
    token = response.json()["access_token"]
    return token


@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    class DummyRedis:
        async def get(self, key): return None
        async def set(self, key, value): return True
        async def delete(self, key): return True
        async def expire(self, key, timeout): return True
        async def close(self): return True
    async def dummy_get_redis():
        return DummyRedis()
    monkeypatch.setattr("src.conf.redis_client.get_redis", dummy_get_redis)


def test_healthcheck(client):
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json()["message"] == "The application is up and running!"


def test_create_contact(client, get_token):
    contact_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@integration.com",
        "phone_number": "1234567890"
    }
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.post("/contacts/", json=contact_data, headers=headers)
    assert response.status_code == 201
    assert response.json()["email"] == contact_data["email"]


def test_create_contact_conflict(monkeypatch, client):
    from src.services.contacts import ContactService
    def raise_conflict(self, contact, user_id):
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Contact with email already exists.")
    monkeypatch.setattr(ContactService, "create_contact", raise_conflict)
    response = client.post("/contacts/", json={"first_name": "John", "last_name": "Doe", "email": "john@example.com", "phone_number": "1234567890"})
    assert response.status_code == 401


def test_get_contacts(client, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.get("/contacts/", headers=headers)
    assert response.status_code == 200
    assert "contacts" in response.json()


def test_get_contacts_empty(monkeypatch, client, get_token):
    from src.services.contacts import ContactService
    monkeypatch.setattr(ContactService, "get_contacts", lambda self, *args, **kwargs: {"total_count": 0, "skip": 0, "limit": 100, "contacts": []})
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.get("/contacts/", headers=headers)
    assert response.status_code == 200
    assert response.json()["total_count"] == 0


def test_update_contact(client, get_token):
    # Create contact first
    contact_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@integration.com",
        "phone_number": "9876543210"
    }
    headers = {"Authorization": f"Bearer {get_token}"}
    create_resp = client.post("/contacts/", json=contact_data, headers=headers)
    contact_id = create_resp.json()["id"]
    # Update contact
    update_data = {
        "first_name": "Janet",
        "last_name": "Smith",
        "email": "jane.smith@integration.com",
        "phone_number": "9876543210"
    }
    response = client.put(f"/contacts/{contact_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["first_name"] == "Janet"


def test_update_contact_not_found(monkeypatch, client, get_token):
    from src.services.contacts import ContactService
    monkeypatch.setattr(ContactService, "update_contact", lambda self, contact_id, contact, user_id=None: None)
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.put("/contacts/999", json={"first_name": "Test", "last_name": "Test", "email": "test@test.com", "phone_number": "123"}, headers=headers)
    assert response.status_code == 404
    assert "Contact not found" in response.text


def test_delete_contact(client, get_token):
    # Create contact first
    contact_data = {
        "first_name": "Mark",
        "last_name": "Twain",
        "email": "mark.twain@integration.com",
        "phone_number": "5555555555"
    }
    headers = {"Authorization": f"Bearer {get_token}"}
    create_resp = client.post("/contacts/", json=contact_data, headers=headers)
    contact_id = create_resp.json()["id"]
    # Delete contact
    response = client.delete(f"/contacts/{contact_id}", headers=headers)
    assert response.status_code == 200 or response.status_code == 204


def test_delete_contact_not_found(monkeypatch, client, get_token):
    from src.services.contacts import ContactService
    monkeypatch.setattr(ContactService, "delete_contact", lambda self, contact_id, user_id=None: None)
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.delete("/contacts/999", headers=headers)
    assert response.status_code == 404
    assert "Contact not found" in response.text
