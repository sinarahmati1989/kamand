"""
Kamand - Machine Service
"""
import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.models.machine import Machine
from app.repositories.machine_repository import MachineRepository
from app.schemas.machine_schema import MachineCreate, MachineUpdate
from app.enums.machine_enums import MachineStatus

logger = logging.getLogger(__name__)


class MachineService:

    def __init__(self, session: Session):
        self.session = session
        self.repo = MachineRepository(session)

    def create(self, data: MachineCreate) -> Machine:
        code = self.repo.get_next_code()

        machine = Machine(
            code=code,
            name=data.name,
            machine_type=data.machine_type,
            brand=data.brand,
            model=data.model,
            serial_number=data.serial_number,
            manufacture_year=data.manufacture_year,
            department_id=data.department_id,
            work_center_id=data.work_center_id,
            location=data.location,
            capacity_per_hour=data.capacity_per_hour,
            hourly_rate=data.hourly_rate,
            currency=data.currency,
            last_maintenance_date=data.last_maintenance_date,
            next_maintenance_date=data.next_maintenance_date,
            maintenance_interval_days=data.maintenance_interval_days,
            technical_notes=data.technical_notes,
            notes=data.notes,
            status=MachineStatus.ACTIVE.value,
        )
        return self.repo.create(machine)

    def update(self, machine_id: int, data: MachineUpdate) -> Machine:
        machine = self.repo.get_by_id(machine_id)
        if not machine:
            raise ValueError("ماشین یافت نشد")

        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(machine, field, value)

        return self.repo.update(machine)

    def delete(self, machine_id: int) -> None:
        machine = self.repo.get_by_id(machine_id)
        if not machine:
            raise ValueError("ماشین یافت نشد")
        self.repo.delete(machine)

    def get_by_id(self, machine_id: int) -> Optional[Machine]:
        return self.repo.get_by_id(machine_id)

    def search(
        self,
        keyword: str = "",
        machine_type: Optional[str] = None,
        department_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> list[Machine]:
        return self.repo.search(keyword, machine_type, department_id, status)

    def change_status(self, machine_id: int, new_status: str) -> Machine:
        machine = self.repo.get_by_id(machine_id)
        if not machine:
            raise ValueError("ماشین یافت نشد")
        machine.status = new_status
        return self.repo.update(machine)

    def get_active_list(self) -> list[Machine]:
        return self.repo.get_active_list()