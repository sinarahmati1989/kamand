"""
Kamand - Cost Type Service
سرویس مدیریتی نوع هزینه
"""

import logging
from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.cost_type import CostType
from app.repositories.cost_type_repository import CostTypeRepository
from app.schemas.cost_type_schema import CostTypeCreate, CostTypeUpdate
from app.enums.cost_enums import CostStatus

logger = logging.getLogger(__name__)


class CostTypeService:
    """سرویس نوع هزینه"""

    def __init__(self, db: Session):
        self.db = db
        self.repo = CostTypeRepository(db)

    def _normalize_status(self, value: str | CostStatus) -> str:
        if isinstance(value, CostStatus):
            value = value.value

        valid_values = {status.value for status in CostStatus}
        if value not in valid_values:
            raise ValueError("وضعیت انتخاب‌شده معتبر نیست")

        return value

    # ------------------------------------------------------------
    # Read
    # ------------------------------------------------------------

    def get_by_id(self, cost_type_id: int) -> Optional[CostType]:
        return self.repo.get_by_id(cost_type_id)

    def get_all(self) -> List[CostType]:
        return self.repo.get_all()

    def search(
        self,
        query: str = "",
        category: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[CostType]:
        return self.repo.search(query, category, status)

    def get_root_items(self) -> List[CostType]:
        return self.repo.get_root_items()

    def get_children(self, parent_id: int) -> List[CostType]:
        return self.repo.get_children(parent_id)

    # ------------------------------------------------------------
    # Create
    # ------------------------------------------------------------

    def create(self, data: CostTypeCreate) -> CostType:
        """ایجاد نوع هزینه جدید"""
        existing = self.repo.get_by_name(data.name)
        if existing:
            raise ValueError(f"نوع هزینه‌ای با نام «{data.name}» قبلاً ثبت شده است")

        if data.parent_id is not None:
            parent = self.repo.get_by_id(data.parent_id)
            if not parent:
                raise ValueError("نوع هزینه والد یافت نشد")

        code = self.repo.get_next_code()

        cost_type = CostType(
            code=code,
            name=data.name,
            category=data.category,
            cost_behavior=data.cost_behavior,
            unit=data.unit,
            default_amount=data.default_amount,
            allocation_method=data.allocation_method,
            account_code=data.account_code,
            taxable=data.taxable,
            parent_id=data.parent_id,
            description=data.description,
            status=CostStatus.ACTIVE.value,
        )

        self.db.add(cost_type)
        self.db.flush()
        self.db.refresh(cost_type)

        logger.info(f"نوع هزینه جدید ایجاد شد: {code} - {data.name}")
        return cost_type

    # ------------------------------------------------------------
    # Update
    # ------------------------------------------------------------

    def update(self, cost_type_id: int, data: CostTypeUpdate) -> CostType:
        """ویرایش نوع هزینه"""
        cost_type = self.repo.get_by_id(cost_type_id)
        if not cost_type:
            raise ValueError("نوع هزینه یافت نشد")

        if data.name is not None and data.name != cost_type.name:
            existing = self.repo.get_by_name(data.name)
            if existing and existing.id != cost_type_id:
                raise ValueError(f"نوع هزینه‌ای با نام «{data.name}» قبلاً ثبت شده است")

        if data.parent_id is not None:
            if data.parent_id == cost_type_id:
                raise ValueError("نوع هزینه نمی‌تواند والد خودش باشد")

            parent = self.repo.get_by_id(data.parent_id)
            if not parent:
                raise ValueError("نوع هزینه والد یافت نشد")

        update_data = data.model_dump(exclude_unset=True)

        if "status" in update_data and update_data["status"] is not None:
            update_data["status"] = self._normalize_status(update_data["status"])

        for key, value in update_data.items():
            setattr(cost_type, key, value)

        self.db.flush()
        self.db.refresh(cost_type)

        logger.info(f"نوع هزینه ویرایش شد: {cost_type.code}")
        return cost_type

    # ------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------

    def delete(self, cost_type_id: int) -> bool:
        """حذف نوع هزینه"""
        cost_type = self.repo.get_by_id(cost_type_id)
        if not cost_type:
            raise ValueError("نوع هزینه یافت نشد")

        children = self.repo.get_children(cost_type_id)
        if children:
            raise ValueError(
                f"این نوع هزینه دارای {len(children)} زیرنوع است. "
                "ابتدا زیرنوع‌ها را حذف کنید."
            )

        self.db.delete(cost_type)
        self.db.flush()

        logger.info(f"نوع هزینه حذف شد: {cost_type.code}")
        return True

    # ------------------------------------------------------------
    # Change Status
    # ------------------------------------------------------------

    def change_status(self, cost_type_id: int, new_status: str | CostStatus) -> CostType:
        """تغییر وضعیت نوع هزینه"""
        cost_type = self.repo.get_by_id(cost_type_id)
        if not cost_type:
            raise ValueError("نوع هزینه یافت نشد")

        normalized_status = self._normalize_status(new_status)
        cost_type.status = normalized_status

        self.db.flush()
        self.db.refresh(cost_type)

        logger.info(f"وضعیت نوع هزینه {cost_type.code} به {normalized_status} تغییر کرد")
        return cost_type