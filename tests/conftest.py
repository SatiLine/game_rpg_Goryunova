import pytest
from unittest.mock import MagicMock

from src.domain.entities import User
from datetime import datetime


@pytest.fixture
def mock_user_repo():
    repo = MagicMock()
    repo.get_by_username.return_value = None
    return repo


@pytest.fixture
def sample_user() -> User:
    return User(id=1, username="test", hashed_password="hash", created_at=datetime.utcnow())