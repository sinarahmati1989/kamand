"""
Kamand - Routing Repository
عملیات دیتابیس برای RoutingHeader و RoutingOperation
"""
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models.routing import RoutingHeader, RoutingOperation
from app.repositories.base_repository import BaseRepository
import logging

logger = logging.getLogger(__name__)


class RoutingHeaderRepository(BaseRepository[RoutingHeader]):

    def __init__(self, session: Session):
        super().__init__(session, RoutingHeader)

    def get_by_template(self, device_template_id: int) -> list[RoutingHeader]:
        return (
            self._session.query(RoutingHeader)
            .filter(RoutingHeader.device_template_id == device_template_id)
            .order_by(RoutingHeader.revision_no.desc())
            .all()
        )

    def get_with_operations(self, routing_header_id: int) -> Optional[RoutingHeader]:
        return (
            self._session.query(RoutingHeader)
            .options(
                joinedload(RoutingHeader.routing_operations)
                .joinedload(RoutingOperation.operation),
                joinedload(RoutingHeader.routing_operations)
                .joinedload(RoutingOperation.department),
                joinedload(RoutingHeader.routing_operations)
                .joinedload(RoutingOperation.work_center),
                joinedload(RoutingHeader.routing_operations)
                .joinedload(RoutingOperation.machine),
                joinedload(RoutingHeader.device_template),
            )
            .filter(RoutingHeader.id == routing_header_id)
            .first()
        )

    def get_latest_by_template(
        self, device_template_id: int
    ) -> Optional[RoutingHeader]:
        return (
            self._session.query(RoutingHeader)
            .filter(RoutingHeader.device_template_id == device_template_id)
            .order_by(RoutingHeader.revision_no.desc())
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
        q = self._session.query(RoutingHeader).filter(
            RoutingHeader.device_template_id == device_template_id,
            RoutingHeader.revision_no == revision_no,
        )
        if exclude_id:
            q = q.filter(RoutingHeader.id != exclude_id)
        return q.first() is not None


class RoutingOperationRepository(BaseRepository[RoutingOperation]):

    def __init__(self, session: Session):
        super().__init__(session, RoutingOperation)

    def get_by_header(self, routing_header_id: int) -> list[RoutingOperation]:
        return (
            self._session.query(RoutingOperation)
            .options(
                joinedload(RoutingOperation.operation),
                joinedload(RoutingOperation.department),
                joinedload(RoutingOperation.work_center),
                joinedload(RoutingOperation.machine),
            )
            .filter(RoutingOperation.routing_header_id == routing_header_id)
            .order_by(RoutingOperation.step_no, RoutingOperation.id)
            .all()
        )

    def get_max_step_no(self, routing_header_id: int) -> int:
        result = (
            self._session.query(func.max(RoutingOperation.step_no))
            .filter(RoutingOperation.routing_header_id == routing_header_id)
            .scalar()
        )
        return result or 0