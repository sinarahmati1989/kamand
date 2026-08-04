"""
Kamand - Department Service
"""
import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.models.department import Department
from app.repositories.department_repository import DepartmentRepository
from app.schemas.department_schema import DepartmentCreate, DepartmentUpdate
from app.enums.department_enums import DepartmentStatus

logger = logging.getLogger(__name__)


class DepartmentService:

    def __init__(self, session: Session):
        self.session = session
        self.repo = DepartmentRepository(session)

    def create(self, data: DepartmentCreate) -> Department:
        code = self.repo.get_next_code()

        if self.repo.get_by_code(code):
            raise ValueError(f"کد '{code}' قبلاً ثبت شده است")

        dept = Department(
            code=code,
            name=data.name,
            department_type=data.department_type,
            manager_name=data.manager_name,
            location=data.location,
            phone=data.phone,
            notes=data.notes,
            status=DepartmentStatus.ACTIVE.value,
        )
        return self.repo.create(dept)

    def update(self, dept_id: int, data: DepartmentUpdate) -> Department:
        dept = self.repo.get_by_id(dept_id)
        if not dept:
            raise ValueError("دپارتمان یافت نشد")

        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(dept, field, value)

        return self.repo.update(dept)

    def delete(self, dept_id: int) -> None:
        dept = self.repo.get_by_id(dept_id)
        if not dept:
            raise ValueError("دپارتمان یافت نشد")
        self.repo.delete(dept)

    def get_by_id(self, dept_id: int) -> Optional[Department]:
        return self.repo.get_by_id(dept_id)

    def search(
        self,
        keyword: str = "",
        department_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[Department]:
        return self.repo.search(keyword, department_type, status)

    def change_status(self, dept_id: int, new_status: str) -> Department:
        dept = self.repo.get_by_id(dept_id)
        if not dept:
            raise ValueError("دپارتمان یافت نشد")
        dept.status = new_status
        return self.repo.update(dept)

    def get_active_list(self) -> list[Department]:
        return self.repo.get_active_list()