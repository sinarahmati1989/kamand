"""
Kamand - Work Center Service
"""
import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.models.work_center import WorkCenter
from app.repositories.work_center_repository import WorkCenterRepository
from app.schemas.work_center_schema import WorkCenterCreate, WorkCenterUpdate
from app.enums.work_center_enums import WorkCenterStatus

logger = logging.getLogger(__name__)


class WorkCenterService:

    def __init__(self, session: Session):
        self.session = session
        self.repo = WorkCenterRepository(session)

    def create(self, data: WorkCenterCreate) -> WorkCenter:
        code = self.repo.get_next_code()

        wc = WorkCenter(
            code=code,
            name=data.name,
            department_id=data.department_id,
            work_center_type=data.work_center_type,
            capacity_per_hour=data.capacity_per_hour,
            capacity_unit=data.capacity_unit,
            shift_count=data.shift_count,
            location=data.location,
            notes=data.notes,
            status=WorkCenterStatus.ACTIVE.value,
        )
        return self.repo.create(wc)

    def update(self, wc_id: int, data: WorkCenterUpdate) -> WorkCenter:
        wc = self.repo.get_by_id(wc_id)
        if not wc:
            raise ValueError("مرکز کار یافت نشد")

        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(wc, field, value)

        return self.repo.update(wc)

    def delete(self, wc_id: int) -> None:
        wc = self.repo.get_by_id(wc_id)
        if not wc:
            raise ValueError("مرکز کار یافت نشد")
        self.repo.delete(wc)

    def get_by_id(self, wc_id: int) -> Optional[WorkCenter]:
        return self.repo.get_by_id(wc_id)

    def search(
        self,
        keyword: str = "",
        work_center_type: Optional[str] = None,
        department_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> list[WorkCenter]:
        return self.repo.search(
            keyword=keyword,
            work_center_type=work_center_type,
            department_id=department_id,
            status=status,
        )

    def change_status(self, wc_id: int, new_status: str) -> WorkCenter:
        wc = self.repo.get_by_id(wc_id)
        if not wc:
            raise ValueError("مرکز کار یافت نشد")
        wc.status = new_status
        return self.repo.update(wc)

    def get_active_list(self) -> list[WorkCenter]:
        return self.repo.get_active_list()

    def get_by_department(self, department_id: int) -> list[WorkCenter]:
        return self.repo.get_by_department(department_id)