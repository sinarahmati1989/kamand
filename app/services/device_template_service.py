"""
Kamand - DeviceTemplate Service
"""
import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.enums.engineering_enums import DeviceTemplateStatus
from app.models.device_template import DeviceTemplate
from app.repositories.device_template_repository import DeviceTemplateRepository
from app.schemas.device_template_schema import DeviceTemplateCreate, DeviceTemplateUpdate

logger = logging.getLogger(__name__)


class DeviceTemplateService:

    def __init__(self, session: Session):
        self.session = session
        self.repo = DeviceTemplateRepository(session)

    def create(self, data: DeviceTemplateCreate) -> DeviceTemplate:
        # اگه کاربر کد وارد کرده از همون استفاده کن، وگرنه خودکار
        code = data.code if data.code else self.repo.get_next_code()

        # چک تکراری نبودن
        if self.repo.get_by_code(code):
            raise ValueError(f"کد «{code}» قبلاً ثبت شده است")

        template = DeviceTemplate(
            code=code,
            name=data.name,
            template_type=data.template_type,
            revision_no=data.revision_no,
            description=data.description,
            technical_notes=data.technical_notes,
            default_uom=data.default_uom,
            estimated_weight=data.estimated_weight,
            estimated_cycle_time=data.estimated_cycle_time,
            status=DeviceTemplateStatus.DRAFT.value,
            is_active=True,
        )
        return self.repo.create(template)

    def update(self, template_id: int, data: DeviceTemplateUpdate) -> DeviceTemplate:
        template = self.repo.get_by_id(template_id)
        if not template:
            raise ValueError("قالب دستگاه یافت نشد")

        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(template, field, value)

        return self.repo.update(template)

    def delete(self, template_id: int) -> None:
        template = self.repo.get_by_id(template_id)
        if not template:
            raise ValueError("قالب دستگاه یافت نشد")
        self.repo.delete(template)

    def get_by_id(self, template_id: int) -> Optional[DeviceTemplate]:
        return self.repo.get_by_id(template_id)

    def search(
        self,
        keyword: str = "",
        template_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[DeviceTemplate]:
        return self.repo.search(keyword, template_type, status)

    def change_status(self, template_id: int, new_status: str) -> DeviceTemplate:
        template = self.repo.get_by_id(template_id)
        if not template:
            raise ValueError("قالب دستگاه یافت نشد")
        template.status = new_status
        return self.repo.update(template)

    def get_active_list(self) -> list[DeviceTemplate]:
        return self.repo.get_active_list()