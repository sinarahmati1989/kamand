"""
Kamand - Machine Repository
"""
import logging
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func

from app.models.machine import Machine
from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class MachineRepository(BaseRepository[Machine]):

    def __init__(self, session: Session):
        super().__init__(session, Machine)

    def get_by_code(self, code: str) -> Optional[Machine]:
        return (
            self._session.query(Machine)
            .filter(Machine.code == code.upper())
            .first()
        )

    def search(
        self,
        keyword: str = "",
        machine_type: Optional[str] = None,
        department_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> list[Machine]:
        q = (
            self._session.query(Machine)
            .options(
                joinedload(Machine.department),
                joinedload(Machine.work_center),
            )
        )

        if keyword:
            kw = f"%{keyword}%"
            q = q.filter(
                or_(
                    Machine.name.ilike(kw),
                    Machine.code.ilike(kw),
                    Machine.brand.ilike(kw),
                    Machine.model.ilike(kw),
                    Machine.serial_number.ilike(kw),
                )
            )

        if machine_type:
            q = q.filter(Machine.machine_type == machine_type)

        if department_id:
            q = q.filter(Machine.department_id == department_id)

        if status:
            q = q.filter(Machine.status == status)

        return q.order_by(Machine.code).all()

    def get_next_code(self) -> str:
        result = self._session.query(
            func.max(Machine.id)
        ).scalar()
        next_id = (result or 0) + 1
        return f"MCH-{next_id:04d}"

    def get_active_list(self) -> list[Machine]:
        """لیست ماشین‌های فعال برای ComboBox"""
        return (
            self._session.query(Machine)
            .filter(Machine.status == "active")
            .order_by(Machine.name)
            .all()
        )