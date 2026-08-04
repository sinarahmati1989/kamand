"""
Base Repository — CRUD عمومی
همه Repository ها از اینجا ارث می‌برن
"""
from typing import TypeVar, Generic, Type
from sqlalchemy.orm import Session
from app.database.base import Base
import logging

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):

    def __init__(self, session: Session, model: Type[ModelType]):
        self._session = session
        self._model = model

    # ─────────────────────────── Read ────────────────────────────────

    def get_all(self) -> list[ModelType]:
        return self._session.query(self._model).all()

    def get_by_id(self, record_id: int) -> ModelType | None:
        return (
            self._session
            .query(self._model)
            .filter_by(id=record_id)
            .first()
        )

    # ─────────────────────────── Write ───────────────────────────────

    def create(self, record: ModelType) -> ModelType:
        self._session.add(record)
        self._session.flush()
        self._session.refresh(record)
        return record

    def update(self, record: ModelType) -> ModelType:
        self._session.flush()
        self._session.refresh(record)
        return record

    def delete(self, record: ModelType) -> None:
        self._session.delete(record)
        self._session.flush()