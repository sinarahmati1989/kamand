"""
Kamand - Cost Type Repository
ریپازیتوری نوع هزینه
"""

from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.cost_type import CostType


class CostTypeRepository:
    """ریپازیتوری عملیات پایگاه‌داده نوع هزینه"""

    def __init__(self, session: Session):
        self._session = session

    def get_by_id(self, item_id: int) -> Optional[CostType]:
        return self._session.query(CostType).filter(
            CostType.id == item_id
        ).first()

    def get_all(self) -> List[CostType]:
        return self._session.query(CostType).order_by(CostType.code).all()

    def get_by_code(self, code: str) -> Optional[CostType]:
        return self._session.query(CostType).filter(
            CostType.code == code
        ).first()

    def get_by_name(self, name: str) -> Optional[CostType]:
        return self._session.query(CostType).filter(
            CostType.name == name
        ).first()

    def get_next_code(self) -> str:
        last = self._session.query(CostType).order_by(
            CostType.id.desc()
        ).first()

        if last and last.code and last.code.startswith("COST-"):
            try:
                num = int(last.code.split("-")[1])
                return f"COST-{num + 1:04d}"
            except (ValueError, IndexError):
                pass

        return "COST-0001"

    def search(
        self,
        query: str = "",
        category: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[CostType]:
        q = self._session.query(CostType)

        if query:
            term = f"%{query.strip()}%"
            q = q.filter(
                (CostType.code.ilike(term)) |
                (CostType.name.ilike(term)) |
                (CostType.account_code.ilike(term))
            )

        if category:
            q = q.filter(CostType.category == category)

        if status:
            q = q.filter(CostType.status == status)

        return q.order_by(CostType.code).all()

    def get_children(self, parent_id: int) -> List[CostType]:
        return self._session.query(CostType).filter(
            CostType.parent_id == parent_id
        ).order_by(CostType.code).all()

    def get_root_items(self) -> List[CostType]:
        return self._session.query(CostType).filter(
            CostType.parent_id.is_(None)
        ).order_by(CostType.code).all()