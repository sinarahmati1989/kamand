"""
Kamand - BOM Repository
عملیات دیتابیس برای BOMHeader و BOMLine
"""
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models.bom import BOMHeader, BOMLine
from app.repositories.base_repository import BaseRepository
import logging

logger = logging.getLogger(__name__)


class BOMHeaderRepository(BaseRepository[BOMHeader]):

    def __init__(self, session: Session):
        super().__init__(session, BOMHeader)

    def get_by_template(self, device_template_id: int) -> list[BOMHeader]:
        return (
            self._session.query(BOMHeader)
            .filter(BOMHeader.device_template_id == device_template_id)
            .order_by(BOMHeader.revision_no.desc())
            .all()
        )

    def get_with_lines(self, bom_header_id: int) -> Optional[BOMHeader]:
        return (
            self._session.query(BOMHeader)
            .options(
                joinedload(BOMHeader.bom_lines).joinedload(BOMLine.item),
                joinedload(BOMHeader.device_template),
            )
            .filter(BOMHeader.id == bom_header_id)
            .first()
        )

    def get_latest_by_template(self, device_template_id: int) -> Optional[BOMHeader]:
        return (
            self._session.query(BOMHeader)
            .filter(BOMHeader.device_template_id == device_template_id)
            .order_by(BOMHeader.revision_no.desc())
            .first()
        )

    def get_next_revision(self, device_template_id: int) -> int:
        latest = self.get_latest_by_template(device_template_id)
        return (latest.revision_no + 1) if latest else 1

    def exists_revision(
        self,
        device_template_id: int,
        revision_no: int,
        exclude_id: Optional[int] = None,
    ) -> bool:
        q = self._session.query(BOMHeader).filter(
            BOMHeader.device_template_id == device_template_id,
            BOMHeader.revision_no == revision_no,
        )
        if exclude_id:
            q = q.filter(BOMHeader.id != exclude_id)
        return q.first() is not None


class BOMLineRepository(BaseRepository[BOMLine]):

    def __init__(self, session: Session):
        super().__init__(session, BOMLine)

    def get_by_header(self, bom_header_id: int) -> list[BOMLine]:
        return (
            self._session.query(BOMLine)
            .options(joinedload(BOMLine.item))
            .filter(BOMLine.bom_header_id == bom_header_id)
            .order_by(BOMLine.sort_order, BOMLine.id)
            .all()
        )

    def get_max_sort_order(self, bom_header_id: int) -> int:
        result = (
            self._session.query(func.max(BOMLine.sort_order))
            .filter(BOMLine.bom_header_id == bom_header_id)
            .scalar()
        )
        return result or 0