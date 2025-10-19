import os
import time
import quopri
import pytest
import requests

# --------------------------
# Налаштування для Docker
# --------------------------
DOCKERIZED = os.getenv("DOCKERIZED", "0") == "1"
BASE_URL = "http://web:8080" if DOCKERIZED else "http://127.0.0.1:8080"
MAILHOG_URL = "http://mailhog:8025" if DOCKERIZED else "http://127.0.0.1:8025"

EMAIL = f"testuser{int(time.time())}@example.com"
PASSWORD = "password123"

@pytest.fixture(scope="module")
def token():
    # 1️⃣ Реєстрація користувача
    resp = requests.post(f"{BASE_URL}/auth/register", json={"email": EMAIL, "password": PASSWORD})
    assert resp.status_code == 200

    # 2️⃣ Login
    login_resp = requests.post(f"{BASE_URL}/auth/token", data={"username": EMAIL, "password": PASSWORD})
    assert login_resp.status_code == 200
    return login_resp.json()["access_token"]

@pytest.fixture(scope="module")
def headers(token):
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="module")
def contact_id(headers):
    contact_data = {"name": "Test Contact"}
    resp = requests.post(f"{BASE_URL}/contacts/", json=contact_data, headers=headers)
    assert resp.status_code == 200
    return resp.json()["id"]

def test_register_and_login(token):
    # Тест наявності токена
    assert token is not None
    assert isinstance(token, str)

def test_create_contact(contact_id):
    # Тест наявності contact_id
    assert contact_id is not None
    assert isinstance(contact_id, int)

def test_upload_avatar(headers, contact_id):
    avatar_path = "test_avatar.png"
    if not os.path.exists(avatar_path):
        pytest.skip("Avatar file not found")
    with open(avatar_path, "rb") as f:
        files = {"file": ("test_avatar.png", f, "image/png")}
        resp = requests.put(f"{BASE_URL}/contacts/{contact_id}/avatar", files=files, headers=headers)
        assert resp.status_code == 200
        assert "avatar_url" in resp.json()
