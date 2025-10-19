import os
import time
import pytest
import requests
import io  # для BytesIO
from unittest.mock import patch  # для моків

# --------------------------
# Налаштування для Docker
# --------------------------
DOCKERIZED = os.getenv("DOCKERIZED", "0") == "1"
BASE_URL = "http://web:8080" if DOCKERIZED else "http://127.0.0.1:8080"
MAILHOG_URL = "http://mailhog:8025" if DOCKERIZED else "http://127.0.0.1:8025"

EMAIL = f"testuser{int(time.time())}@example.com"
PASSWORD = "password123"

# ---------------------------
# Мок Cloudinary
# ---------------------------
@pytest.fixture(autouse=True)
def mock_cloudinary_upload():
    with patch("app.routes.contacts.upload_avatar_file") as mock_upload:
        mock_upload.return_value = "http://cloudinary.fake/test_avatar.png"
        yield mock_upload
        print("Cloudinary upload mocked!")

# ---------------------------
# Токен
# ---------------------------
@pytest.fixture(scope="module")
def token():
    resp = requests.post(f"{BASE_URL}/auth/register", json={"email": EMAIL, "password": PASSWORD})
    assert resp.status_code == 200

    login_resp = requests.post(f"{BASE_URL}/auth/token", data={"username": EMAIL, "password": PASSWORD})
    assert login_resp.status_code == 200
    return login_resp.json()["access_token"]

@pytest.fixture(scope="module")
def headers(token):
    return {"Authorization": f"Bearer {token}"}

# ---------------------------
# Contact
# ---------------------------
@pytest.fixture(scope="module")
def contact_id(headers):
    contact_data = {
        "name": "Test Contact",
        "email": f"contact{int(time.time())}@example.com",
        "phone": "1234567890"
    }
    resp = requests.post(f"{BASE_URL}/contacts/", json=contact_data, headers=headers)
    assert resp.status_code == 201  # змінив на 201
    return resp.json()["id"]

# ---------------------------
# Файл аватара
# ---------------------------
@pytest.fixture(scope="module")
def avatar_file():
    return io.BytesIO(b"fake image data for testing")

# ---------------------------
# Тести
# ---------------------------
def test_register_and_login(token):
    assert token is not None
    assert isinstance(token, str)

def test_create_contact(contact_id):
    assert contact_id is not None
    assert isinstance(contact_id, int)

def test_upload_avatar(headers, contact_id, avatar_file):
    files = {"file": ("test_avatar.png", avatar_file, "image/png")}
    resp = requests.put(f"{BASE_URL}/contacts/{contact_id}/avatar", files=files, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert "avatar_url" in data
    assert data["avatar_url"] == "http://cloudinary.fake/test_avatar.png"