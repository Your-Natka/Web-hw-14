import unittest
from app import models, crud
from unittest.mock import MagicMock

class TestRepositoryContacts(unittest.TestCase):
    def setUp(self):
        self.db = MagicMock()
        self.user = models.User(id=1, email="test@example.com")

    def test_create_contact(self):
        contact_data = MagicMock()
        contact = crud.create_contact(self.db, contact_data, self.user.id)
        self.db.add.assert_called_once()
        self.db.commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()
