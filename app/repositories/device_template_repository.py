"""
Kamand - DeviceTemplate Repository
"""
import logging
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.device_template import DeviceTemplate
from app.models.bom import BOMHeader
from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class DeviceTemplateRepository(BaseRepository[DeviceTemplate]):

    def __init__(self, session: Session):
        super().__init__(session, DeviceTemplate)

    def get_next_code(self) -> str:
        result = self._session.query(func.max(DeviceTemplate.id)).scalar()
        next_id = (result or 0) + 1
        return f"DVT-{next_id:04d}"

    def get_by_code(self, code: str) -> Optional[DeviceTemplate]:
        return (
            self._session.query(DeviceTemplate)
            .filter(DeviceTemplate.code == code.upper())
            .first()
        )

    def search(
        self,
        keyword: str = "",
        template_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[DeviceTemplate]:
        q = self._session.query(DeviceTemplate)

        if keyword:
            kw = f"%{keyword}%"
            q = q.filter(
                or_(
                    DeviceTemplate.name.ilike(kw),
                    DeviceTemplate.code.ilike(kw),
                )
            )

        if template_type:
            q = q.filter(DeviceTemplate.template_type == template_type)

        if status:
            q = q.filter(DeviceTemplate.status == status)

        return q.order_by(DeviceTemplate.code).all()

    def get_with_bom(self, template_id: int) -> Optional[DeviceTemplate]:
        return (
            self._session.query(DeviceTemplate)
            .options(
                joinedload(DeviceTemplate.bom_headers)
                .joinedload(BOMHeader.bom_lines),
            )
            .filter(DeviceTemplate.id == template_id)
            .first()
        )

    def get_active_list(self) -> list[DeviceTemplate]:
        return (
            self._session.query(DeviceTemplate)
            .filter(DeviceTemplate.is_active.is_(True))
            .order_by(DeviceTemplate.name)
            .all()
        )