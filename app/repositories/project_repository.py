"""
Kamand - Project Repository
عملیات پایگاه داده برای پروژه‌ها
"""
from __future__ import annotations

from typing import Optional
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import select, or_, func

from app.models.project import Project, ProjectDevice, ProjectCost
from app.repositories.base_repository import BaseRepository


class ProjectRepository(BaseRepository[Project]):

    def __init__(self, session: Session):
        super().__init__(session, Project)

    def get_by_project_no(self, project_no: str) -> Optional[Project]:
        stmt = (
            select(Project)
            .options(
                joinedload(Project.customer),
                selectinload(Project.project_devices),
            )
            .where(Project.project_no == project_no)
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def get_by_id_full(self, project_id: int) -> Optional[Project]:
        """گرفتن پروژه با تمام روابط (customer + devices)"""
        stmt = (
            select(Project)
            .options(
                joinedload(Project.customer),
                selectinload(Project.project_devices).joinedload(
                    ProjectDevice.device_template
                ),
                selectinload(Project.project_costs),
            )
            .where(Project.id == project_id)
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def get_all_with_filter(
        self,
        search: str = "",
        status: str = "",
        customer_id: int = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Project]:
        stmt = (
            select(Project)
            .options(
                joinedload(Project.customer),
                selectinload(Project.project_devices),
            )
        )

        if search:
            stmt = stmt.where(
                or_(
                    Project.project_no.ilike(f"%{search}%"),
                    Project.name.ilike(f"%{search}%"),
                    Project.contract_no.ilike(f"%{search}%"),
                )
            )

        if status:
            stmt = stmt.where(Project.status == status)

        if customer_id:
            stmt = stmt.where(Project.customer_id == customer_id)

        stmt = stmt.order_by(Project.id.desc()).offset(skip).limit(limit)
        return list(self._session.execute(stmt).scalars().unique().all())

    def count_with_filter(
        self,
        search: str = "",
        status: str = "",
        customer_id: int = None,
    ) -> int:
        stmt = select(func.count()).select_from(Project)

        if search:
            stmt = stmt.where(
                or_(
                    Project.project_no.ilike(f"%{search}%"),
                    Project.name.ilike(f"%{search}%"),
                    Project.contract_no.ilike(f"%{search}%"),
                )
            )

        if status:
            stmt = stmt.where(Project.status == status)

        if customer_id:
            stmt = stmt.where(Project.customer_id == customer_id)

        return self._session.execute(stmt).scalar_one()

    def get_next_project_no(self) -> str:
        """تولید شماره پروژه بعدی — PRJ-0001"""
        stmt = select(func.max(Project.project_no))
        last = self._session.execute(stmt).scalar_one_or_none()
        if not last:
            return "PRJ-0001"
        try:
            num = int(last.split("-")[-1]) + 1
            return f"PRJ-{num:04d}"
        except Exception:
            return "PRJ-0001"


class ProjectDeviceRepository(BaseRepository[ProjectDevice]):

    def __init__(self, session: Session):
        super().__init__(session, ProjectDevice)

    def get_by_project(self, project_id: int) -> list[ProjectDevice]:
        stmt = (
            select(ProjectDevice)
            .options(joinedload(ProjectDevice.device_template))
            .where(ProjectDevice.project_id == project_id)
            .order_by(ProjectDevice.id)
        )
        return list(self._session.execute(stmt).scalars().all())


class ProjectCostRepository(BaseRepository[ProjectCost]):

    def __init__(self, session: Session):
        super().__init__(session, ProjectCost)

    def get_by_project(self, project_id: int) -> list[ProjectCost]:
        stmt = (
            select(ProjectCost)
            .options(joinedload(ProjectCost.cost_type))
            .where(ProjectCost.project_id == project_id)
            .order_by(ProjectCost.id)
        )
        return list(self._session.execute(stmt).scalars().all())