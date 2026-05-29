from unittest.mock import MagicMock
from datetime import datetime

from src.domain.entities import User
from src.services.auth_service import AuthService


def _make_user() -> User:
    from werkzeug.security import generate_password_hash
    return User(id=1, username="alice", hashed_password=generate_password_hash("secret"), created_at=datetime.utcnow())


def test_register_success(mock_user_repo: MagicMock) -> None:
    mock_user_repo.create.return_value = _make_user()
    service = AuthService(mock_user_repo)
    user = service.register("alice", "secret")
    assert user is not None
    assert user.username == "alice"
    mock_user_repo.create.assert_called_once()


def test_register_duplicate(mock_user_repo: MagicMock) -> None:
    mock_user_repo.get_by_username.return_value = _make_user()
    service = AuthService(mock_user_repo)
    result = service.register("alice", "secret")
    assert result is None


def test_authenticate_wrong_password(mock_user_repo: MagicMock) -> None:
    mock_user_repo.get_by_username.return_value = _make_user()
    service = AuthService(mock_user_repo)
    result = service.authenticate("alice", "wrongpassword")
    assert result is None


def test_authenticate_success(mock_user_repo: MagicMock) -> None:
    mock_user_repo.get_by_username.return_value = _make_user()
    service = AuthService(mock_user_repo)
    result = service.authenticate("alice", "secret")
    assert result is not None