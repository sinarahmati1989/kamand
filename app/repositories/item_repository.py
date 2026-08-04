"""
Kamand - Item Repository
"""
import logging
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.item import Item
from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class ItemRepository(BaseRepository[Item]):

    def __init__(self, session: Session):
        super().__init__(session, Item)

    def get_next_code(self) -> str:
        result = self._session.query(func.max(Item.id)).scalar()
        next_id = (result or 0) + 1
        return f"ITM-{next_id:04d}"

    def get_by_code(self, code: str) -> Optional[Item]:
        return (
            self._session.query(Item)
            .filter(Item.code == code.upper())
            .first()
        )

    def search(
        self,
        keyword: str = "",
        item_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[Item]:
        q = self._session.query(Item)

        if keyword:
            kw = f"%{keyword}%"
            q = q.filter(
                or_(
                    Item.name.ilike(kw),
                    Item.code.ilike(kw),
                    Item.part_no.ilike(kw),
                    Item.manufacturer.ilike(kw),
                    Item.drawing_no.ilike(kw),
                )
            )

        if item_type:
            q = q.filter(Item.item_type == item_type)

        if status:
            q = q.filter(Item.status == status)

        return q.order_by(Item.code).all()

    def get_active_list(self) -> list[Item]:
        return (
            self._session.query(Item)
            .filter(Item.is_active.is_(True))
            .order_by(Item.name)
            .all()
        )