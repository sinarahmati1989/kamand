"""
Kamand - Department Repository
"""
import logging
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.models.department import Department
from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class DepartmentRepository(BaseRepository[Department]):

    def __init__(self, session: Session):
        super().__init__(session, Department)

    def get_by_code(self, code: str) -> Optional[Department]:
        return (
            self._session.query(Department)
            .filter(Department.code == code.upper())
            .first()
        )

    def search(
        self,
        keyword: str = "",
        department_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[Department]:
        q = self._session.query(Department)

        if keyword:
            kw = f"%{keyword}%"
            q = q.filter(
                or_(
                    Department.name.ilike(kw),
                    Department.code.ilike(kw),
                    Department.manager_name.ilike(kw),
                )
            )

        if department_type:
            q = q.filter(Department.department_type == department_type)

        if status:
            q = q.filter(Department.status == status)

        return q.order_by(Department.code).all()

    def get_next_code(self) -> str:
        result = self._session.query(
            func.max(Department.id)
        ).scalar()
        next_id = (result or 0) + 1
        return f"DEP-{next_id:04d}"

    def get_active_list(self) -> list[Department]:
        """لیست دپارتمان‌های فعال برای ComboBox"""
        return (
            self._session.query(Department)
            .filter(Department.status == "active")
            .order_by(Department.name)
            .all()
        )