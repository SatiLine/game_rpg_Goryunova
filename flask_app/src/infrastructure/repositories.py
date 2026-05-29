import json
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from src.domain.entities import Prediction, User
from src.infrastructure.orm_models import PredictionORM, UserORM

logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_username(self, username: str) -> User | None:
        row = self._session.query(UserORM).filter_by(username=username).first()
        if row is None:
            return None
        return User(
            id=row.id,
            username=row.username,
            hashed_password=row.hashed_password,
            created_at=row.created_at,
        )

    def create(self, username: str, hashed_password: str) -> User:
        row = UserORM(username=username, hashed_password=hashed_password)
        self._session.add(row)
        self._session.flush()
        logger.info("Создан пользователь: %s", username)
        return User(
            id=row.id,
            username=row.username,
            hashed_password=row.hashed_password,
            created_at=row.created_at or datetime.utcnow(),
        )


class PredictionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        user_id: int,
        input_data: dict[str, object],
        prediction: dict[str, object],
    ) -> Prediction:
        row = PredictionORM(
            user_id=user_id,
            input_data=json.dumps(input_data, ensure_ascii=False),
            prediction=json.dumps(prediction, ensure_ascii=False),
        )
        self._session.add(row)
        self._session.flush()
        return Prediction(
            id=row.id,
            user_id=row.user_id,
            input_data=input_data,
            prediction=prediction,
            created_at=row.created_at or datetime.utcnow(),
        )

    def get_by_user(self, user_id: int, limit: int = 20) -> list[Prediction]:
        rows = (
            self._session.query(PredictionORM)
            .filter_by(user_id=user_id)
            .order_by(PredictionORM.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            Prediction(
                id=r.id,
                user_id=r.user_id,
                input_data=json.loads(r.input_data),
                prediction=json.loads(r.prediction),
                created_at=r.created_at,
            )
            for r in rows
        ]