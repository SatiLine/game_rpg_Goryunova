import logging

from werkzeug.security import check_password_hash, generate_password_hash

from src.domain.entities import User
from src.domain.interfaces import UserRepositoryProtocol

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, user_repo: UserRepositoryProtocol) -> None:
        self._repo = user_repo

    def register(self, username: str, password: str) -> User | None:
        if self._repo.get_by_username(username) is not None:
            logger.info("Попытка регистрации занятого логина: %s", username)
            return None
        hashed = generate_password_hash(password)
        user = self._repo.create(username, hashed)
        logger.info("Зарегистрирован: %s (id=%d)", username, user.id)
        return user

    def authenticate(self, username: str, password: str) -> User | None:
        user = self._repo.get_by_username(username)
        if user is None:
            logger.info("Вход: пользователь не найден — %s", username)
            return None
        if not check_password_hash(user.hashed_password, password):
            logger.info("Вход: неверный пароль — %s", username)
            return None
        logger.info("Вход выполнен: %s", username)
        return user
