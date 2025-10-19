from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ping():
    response = client.get("/contacts/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "Contacts OK"}

def test_get_contacts(client):
    response = client.get("/contacts/")
    assert response.status_code in (200, 401)