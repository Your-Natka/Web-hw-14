import unittest
from app.crud import crud
from unittest.mock import MagicMock
from app.models import models

class TestRepositoryAuth(unittest.TestCase):
    def setUp(self):
        self.db = MagicMock()
        self.user = models.User(id=1, email="test@example.com", password="hashed_pwd")

    def test_get_user_by_email(self):
        self.db.query().filter().first.return_value = self.user
        result = crud.get_user_by_email(self.db, "test@example.com")
        self.assertEqual(result.email, "test@example.com")

    def test_password_hash_and_verify(self):
        pwd = "secret123"
        hashed = crud.get_password_hash(pwd)
        self.assertTrue(crud.verify_password(pwd, hashed))

    def test_create_user(self):
        self.db.add = MagicMock()
        self.db.commit = MagicMock()
        self.db.refresh = MagicMock()
        user = crud.create_user(self.db, "user@example.com", "hashed_pass", "user1")
        self.db.add.assert_called_once()
        self.db.commit.assert_called_once()
