"""
Kamand - Work Center Repository
"""
import logging
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func

from app.models.work_center import WorkCenter
from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class WorkCenterRepository(BaseRepository[WorkCenter]):

    def __init__(self, session: Session):
        super().__init__(session, WorkCenter)

    def get_by_code(self, code: str) -> Optional[WorkCenter]:
        return (
            self._session.query(WorkCenter)
            .filter(WorkCenter.code == code.upper())
            .first()
        )

    def search(
        self,
        keyword: str = "",
        work_center_type: Optional[str] = None,
        department_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> list[WorkCenter]:
        q = (
            self._session.query(WorkCenter)
            .options(joinedload(WorkCenter.department))
        )

        if keyword:
            kw = f"%{keyword}%"
            q = q.filter(
                or_(
                    WorkCenter.name.ilike(kw),
                    WorkCenter.code.ilike(kw),
                )
            )

        if work_center_type:
            q = q.filter(WorkCenter.work_center_type == work_center_type)

        if department_id:
            q = q.filter(WorkCenter.department_id == department_id)

        if status:
            q = q.filter(WorkCenter.status == status)

        return q.order_by(WorkCenter.code).all()

    def get_next_code(self) -> str:
        result = self._session.query(
            func.max(WorkCenter.id)
        ).scalar()
        next_id = (result or 0) + 1
        return f"WC-{next_id:04d}"

    def get_active_list(self) -> list[WorkCenter]:
        """لیست مراکز کار فعال برای ComboBox"""
        return (
            self._session.query(WorkCenter)
            .filter(WorkCenter.status == "active")
            .order_by(WorkCenter.name)
            .all()
        )

    def get_by_department(self, department_id: int) -> list[WorkCenter]:
        """مراکز کار یک دپارتمان"""
        return (
            self._session.query(WorkCenter)
            .filter(
                WorkCenter.department_id == department_id,
                WorkCenter.status == "active",
            )
            .order_by(WorkCenter.name)
            .all()
        )