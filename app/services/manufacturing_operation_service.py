"""
Kamand - Manufacturing Operation Service
سرویس مدیریتی عملیات ساخت
"""

import logging
from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.manufacturing_operation import ManufacturingOperation
from app.repositories.manufacturing_operation_repository import (
    ManufacturingOperationRepository
)
from app.schemas.manufacturing_operation_schema import (
    ManufacturingOperationCreate,
    ManufacturingOperationUpdate,
)
from app.enums.operation_enums import OperationStatus
from app.core.exceptions import NotFoundError, DuplicateError

logger = logging.getLogger(__name__)


class ManufacturingOperationService:
    """سرویس عملیات ساخت"""

    def __init__(self, db: Session):
        self.db = db
        self.repo = ManufacturingOperationRepository(db)

    # ---------- Helpers ----------

    def _normalize_status(self, value: str | OperationStatus) -> str:
        if isinstance(value, OperationStatus):
            value = value.value
        valid = {st.value for st in OperationStatus}
        if value not in valid:
            raise ValueError("وضعیت انتخاب‌شده معتبر نیست")
        return value

    def _find_or_raise(self, operation_id: int) -> ManufacturingOperation:
        op = self.repo.get_by_id(operation_id)
        if not op:
            raise NotFoundError(f"عملیات با شناسه {operation_id} یافت نشد")
        return op

    # ---------- Read ----------

    def get_by_id(self, operation_id: int) -> Optional[ManufacturingOperation]:
        return self.repo.get_by_id(operation_id)

    def get_all(self) -> List[ManufacturingOperation]:
        return self.repo.get_all_ordered()

    def search(
        self,
        query: str = "",
        operation_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[ManufacturingOperation]:
        return self.repo.search(query, operation_type, status)

    # ---------- Create ----------

    def create(self, data: ManufacturingOperationCreate) -> ManufacturingOperation:
        """ایجاد عملیات ساخت جدید"""
        if self.repo.get_by_name(data.name):
            raise DuplicateError(f"عملیاتی با نام «{data.name}» قبلاً ثبت شده است")

        code = self.repo.get_next_code()

        op = ManufacturingOperation(
            code=code,
            name=data.name,
            operation_type=data.operation_type,
            description=data.description,

            is_outsourced=data.is_outsourced,
            requires_qc=data.requires_qc,
            requires_machine=data.requires_machine,
            is_bottleneck=data.is_bottleneck,

            setup_time=data.setup_time,
            setup_time_unit=data.setup_time_unit,
            cycle_time=data.cycle_time,
            cycle_time_unit=data.cycle_time_unit,

            capacity_per_hour=data.capacity_per_hour,
            default_operator_count=data.default_operator_count,
            efficiency_percent=data.efficiency_percent,
            oee_target=data.oee_target,

            hourly_rate=data.hourly_rate,
            currency=data.currency,

            skill_level=data.skill_level,
            required_skills_description=data.required_skills_description,

            required_tools=data.required_tools,
            safety_notes=data.safety_notes,
            notes=data.notes,

            status=OperationStatus.ACTIVE.value,
        )

        self.db.add(op)
        self.db.flush()
        self.db.refresh(op)

        logger.info(f"عملیات ساخت جدید ایجاد شد: {code} - {data.name}")
        return op

    # ---------- Update ----------

    def update(
        self, operation_id: int, data: ManufacturingOperationUpdate
    ) -> ManufacturingOperation:
        """ویرایش عملیات ساخت"""
        op = self._find_or_raise(operation_id)

        if data.name is not None and data.name != op.name:
            existing = self.repo.get_by_name(data.name)
            if existing and existing.id != operation_id:
                raise DuplicateError(f"عملیاتی با نام «{data.name}» قبلاً ثبت شده است")

        update_data = data.model_dump(exclude_unset=True)

        if "status" in update_data and update_data["status"] is not None:
            update_data["status"] = self._normalize_status(update_data["status"])

        for key, value in update_data.items():
            setattr(op, key, value)

        self.db.flush()
        self.db.refresh(op)

        logger.info(f"عملیات ساخت ویرایش شد: {op.code}")
        return op

    # ---------- Delete ----------

    def delete(self, operation_id: int) -> bool:
        """حذف عملیات ساخت"""
        op = self._find_or_raise(operation_id)
        self.db.delete(op)
        self.db.flush()
        logger.info(f"عملیات ساخت حذف شد: {op.code}")
        return True

    # ---------- Change Status ----------

    def change_status(
        self, operation_id: int, new_status: str | OperationStatus
    ) -> ManufacturingOperation:
        """تغییر وضعیت عملیات ساخت"""
        op = self._find_or_raise(operation_id)
        normalized = self._normalize_status(new_status)
        op.status = normalized
        self.db.flush()
        self.db.refresh(op)
        logger.info(f"وضعیت عملیات {op.code} → {normalized}")
        return op