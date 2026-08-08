"""
Kamand - Project Service
منطق تجاری مدیریت پروژه
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.project import Project, ProjectDevice, ProjectCost
from app.repositories.project_repository import (
    ProjectRepository,
    ProjectDeviceRepository,
    ProjectCostRepository,
)
from app.core.access_control import AccessControl

logger = logging.getLogger(__name__)


class ProjectService:

    def __init__(self, session: Session):
        self._session = session
        self.repo = ProjectRepository(session)
        self.device_repo = ProjectDeviceRepository(session)
        self.cost_repo = ProjectCostRepository(session)

    # ─── Project CRUD ───

    def get_all(
        self,
        search: str = "",
        status: str = "",
        customer_id: int = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Project]:
        return self.repo.get_all_with_filter(
            search=search,
            status=status,
            customer_id=customer_id,
            skip=skip,
            limit=limit,
        )

    def count(
        self,
        search: str = "",
        status: str = "",
        customer_id: int = None,
    ) -> int:
        return self.repo.count_with_filter(
            search=search,
            status=status,
            customer_id=customer_id,
        )

    def get_by_id(self, project_id: int) -> Optional[Project]:
        """گرفتن با تمام روابط (customer + devices + costs)"""
        return self.repo.get_by_id_full(project_id)

    def get_next_project_no(self) -> str:
        return self.repo.get_next_project_no()

    def create(self, data: dict) -> Project:
        if not data.get("project_no"):
            data["project_no"] = self.get_next_project_no()

        user = AccessControl.get_current_user()
        if user:
            data["created_by_id"] = user.id

        project = Project(**data)
        return self.repo.create(project)

    def update(self, project: Project, data: dict) -> Project:
        for key, value in data.items():
            setattr(project, key, value)
        return self.repo.update(project)

    def delete(self, project: Project) -> bool:
        if project.status not in ("draft", "cancelled"):
            raise ValueError(
                "فقط پروژه‌های پیش‌نویس یا لغو شده قابل حذف هستند"
            )
        return self.repo.delete(project)

    def confirm(self, project: Project) -> Project:
        if project.status != "draft":
            raise ValueError("فقط پروژه پیش‌نویس قابل تأیید است")
        user = AccessControl.get_current_user()
        project.status = "confirmed"
        if user:
            project.confirmed_by_id = user.id
        project.confirmed_at = datetime.now()
        return self.repo.update(project)

    def start_production(self, project: Project) -> Project:
        if project.status != "confirmed":
            raise ValueError(
                "فقط پروژه تأیید شده می‌تواند وارد تولید شود"
            )
        project.status = "in_production"
        return self.repo.update(project)

    def deliver(self, project: Project) -> Project:
        if project.status != "in_production":
            raise ValueError("فقط پروژه در تولید قابل تحویل است")
        from datetime import date
        project.status = "delivered"
        project.actual_delivery_date = date.today()
        return self.repo.update(project)

    def cancel(self, project: Project) -> Project:
        if project.status == "delivered":
            raise ValueError("پروژه تحویل داده شده قابل لغو نیست")
        project.status = "cancelled"
        return self.repo.update(project)

    # ─── ProjectDevice ───

    def get_devices(self, project_id: int) -> list[ProjectDevice]:
        return self.device_repo.get_by_project(project_id)

    def add_device(self, project_id: int, data: dict) -> ProjectDevice:
        data["project_id"] = project_id
        device = ProjectDevice(**data)
        return self.device_repo.create(device)

    def update_device(self, device: ProjectDevice, data: dict) -> ProjectDevice:
        for key, value in data.items():
            setattr(device, key, value)
        return self.device_repo.update(device)

    def remove_device(self, device: ProjectDevice) -> bool:
        return self.device_repo.delete(device)

    # ─── ProjectCost ───

    def get_costs(self, project_id: int) -> list[ProjectCost]:
        return self.cost_repo.get_by_project(project_id)

    def add_cost(self, project_id: int, data: dict) -> ProjectCost:
        data["project_id"] = project_id
        user = AccessControl.get_current_user()
        if user:
            data["recorded_by_id"] = user.id
        cost = ProjectCost(**data)
        return self.cost_repo.create(cost)

    def remove_cost(self, cost: ProjectCost) -> bool:
        return self.cost_repo.delete(cost)