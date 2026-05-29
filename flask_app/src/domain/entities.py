from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class User:
    id: int
    username: str
    hashed_password: str
    created_at: datetime


@dataclass
class Prediction:
    id: int
    user_id: int
    input_data: dict[str, object]
    prediction: dict[str, object]
    created_at: datetime