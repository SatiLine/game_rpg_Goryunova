from typing import Protocol

from src.domain.entities import Prediction, User


class UserRepositoryProtocol(Protocol):
    def get_by_username(self, username: str) -> User | None: ...
    def create(self, username: str, hashed_password: str) -> User: ...


class PredictionRepositoryProtocol(Protocol):
    def create(
        self,
        user_id: int,
        input_data: dict[str, object],
        prediction: dict[str, object],
    ) -> Prediction: ...

    def get_by_user(self, user_id: int, limit: int = 20) -> list[Prediction]: ...
