"""
Kamand - Manufacturing Operation Repository
ریپازیتوری عملیات ساخت
"""

from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.repositories.base_repository import BaseRepository
from app.models.manufacturing_operation import ManufacturingOperation


class ManufacturingOperationRepository(BaseRepository[ManufacturingOperation]):
    """عملیات دیتابیس برای عملیات ساخت"""

    def __init__(self, session: Session):
        super().__init__(session, ManufacturingOperation)

    def get_by_code(self, code: str) -> Optional[ManufacturingOperation]:
        return (
            self._session.query(ManufacturingOperation)
            .filter(ManufacturingOperation.code == code)
            .first()
        )

    def get_by_name(self, name: str) -> Optional[ManufacturingOperation]:
        return (
            self._session.query(ManufacturingOperation)
            .filter(ManufacturingOperation.name == name)
            .first()
        )

    def get_next_code(self) -> str:
        last = (
            self._session.query(ManufacturingOperation)
            .order_by(ManufacturingOperation.id.desc())
            .first()
        )
        if last and last.code and last.code.startswith("OP-"):
            try:
                num = int(last.code.split("-")[1])
                return f"OP-{num + 1:04d}"
            except (ValueError, IndexError):
                pass
        return "OP-0001"

    def search(
        self,
        query: str = "",
        operation_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[ManufacturingOperation]:
        q = self._session.query(ManufacturingOperation)

        if query:
            term = f"%{query.strip()}%"
            q = q.filter(
                or_(
                    ManufacturingOperation.code.ilike(term),
                    ManufacturingOperation.name.ilike(term),
                    ManufacturingOperation.description.ilike(term),
                )
            )

        if operation_type:
            q = q.filter(ManufacturingOperation.operation_type == operation_type)

        if status:
            q = q.filter(ManufacturingOperation.status == status)

        return q.order_by(ManufacturingOperation.code).all()

    def get_all_ordered(self) -> List[ManufacturingOperation]:
        return (
            self._session.query(ManufacturingOperation)
            .order_by(ManufacturingOperation.code)
            .all()
        )