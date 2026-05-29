from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int]               = mapped_column(Integer, primary_key=True)
    username: Mapped[str]         = mapped_column(String(80), unique=True, nullable=False)
    hashed_password: Mapped[str]  = mapped_column(String(256), nullable=False)
    created_at: Mapped[datetime]  = mapped_column(DateTime, server_default=func.now())

    predictions: Mapped[list["PredictionORM"]] = relationship(back_populates="user")


class PredictionORM(Base):
    __tablename__ = "predictions"

    id: Mapped[int]          = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int]     = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    input_data: Mapped[str]  = mapped_column(Text, nullable=False)
    prediction: Mapped[str]  = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["UserORM"] = relationship(back_populates="predictions")