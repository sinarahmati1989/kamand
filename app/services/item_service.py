"""
Kamand - Item Service
"""
import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.enums.engineering_enums import ItemStatus
from app.models.item import Item
from app.repositories.item_repository import ItemRepository
from app.schemas.item_schema import ItemCreate, ItemUpdate

logger = logging.getLogger(__name__)


class ItemService:

    def __init__(self, session: Session):
        self.session = session
        self.repo = ItemRepository(session)

    def create(self, data: ItemCreate) -> Item:
        # اگه کاربر کد وارد کرده از همون استفاده کن، وگرنه خودکار
        code = data.code if data.code else self.repo.get_next_code()

        # چک تکراری نبودن
        if self.repo.get_by_code(code):
            raise ValueError(f"کد «{code}» قبلاً ثبت شده است")

        item = Item(
            code=code,
            name=data.name,
            item_type=data.item_type,
            uom=data.uom,
            specification=data.specification,
            drawing_no=data.drawing_no,
            part_no=data.part_no,
            manufacturer=data.manufacturer,
            manufacturer_part_no=data.manufacturer_part_no,
            weight=data.weight,
            material_grade=data.material_grade,
            surface_treatment=data.surface_treatment,
            standard_cost=data.standard_cost,
            currency=data.currency,
            notes=data.notes,
            status=ItemStatus.ACTIVE.value,
            is_active=True,
        )
        return self.repo.create(item)

    def update(self, item_id: int, data: ItemUpdate) -> Item:
        item = self.repo.get_by_id(item_id)
        if not item:
            raise ValueError("قلم یافت نشد")

        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(item, field, value)

        return self.repo.update(item)

    def delete(self, item_id: int) -> None:
        item = self.repo.get_by_id(item_id)
        if not item:
            raise ValueError("قلم یافت نشد")
        self.repo.delete(item)

    def get_by_id(self, item_id: int) -> Optional[Item]:
        return self.repo.get_by_id(item_id)

    def search(
        self,
        keyword: str = "",
        item_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[Item]:
        return self.repo.search(keyword, item_type, status)

    def change_status(self, item_id: int, new_status: str) -> Item:
        item = self.repo.get_by_id(item_id)
        if not item:
            raise ValueError("قلم یافت نشد")
        item.status = new_status
        return self.repo.update(item)

    def get_active_list(self) -> list[Item]:
        return self.repo.get_active_list()