"""
Service تأمین‌کننده — منطق کسب‌وکار
"""
import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from app.repositories.supplier_repository import SupplierRepository
from app.models.supplier import Supplier
from app.schemas.supplier_schema import SupplierCreate, SupplierUpdate
from app.enums.supplier_enums import SupplierStatus
from app.core.exceptions import NotFoundError, DuplicateError

logger = logging.getLogger(__name__)


class SupplierService:
    """سرویس مدیریت تأمین‌کنندگان"""

    def __init__(self, session: Session):
        self.session = session
        self.repo = SupplierRepository(session)

    # ──────────────────────────────────────────────

    def generate_next_code(self) -> str:
        """تولید کد بعدی: SUP-0001, SUP-0002, ..."""
        max_num = self.repo.get_max_code_number()
        next_num = max_num + 1
        return f"SUP-{next_num:04d}"

    # ── CRUD ────────────────────────────────────────

    def get_all(self) -> List[Supplier]:
        return self.repo.get_all()

    def get_by_id(self, supplier_id: int) -> Supplier:
        supplier = self.repo.get_by_id(supplier_id)
        if not supplier:
            raise NotFoundError(f"تأمین‌کننده با شناسه {supplier_id} یافت نشد")
        return supplier

    def search(self, keyword: str) -> List[Supplier]:
        return self.repo.search(keyword)

    def create(self, data: SupplierCreate) -> Supplier:
        """ایجاد تأمین‌کننده جدید"""
        # بررسی تکراری نبودن نام
        existing = self.repo.find_by_name(data.name)
        if existing:
            raise DuplicateError(f"تأمین‌کننده‌ای با نام «{data.name}» قبلاً ثبت شده")

        # تولید کد خودکار
        code = self.generate_next_code()

        supplier = Supplier(
            code=code,
            **data.model_dump()
        )

        self.session.add(supplier)
        self.session.commit()
        self.session.refresh(supplier)

        logger.info(f"✅ تأمین‌کننده ایجاد شد: {supplier.code} — {supplier.name}")
        return supplier

    def update(self, supplier_id: int, data: SupplierUpdate) -> Supplier:
        """ویرایش تأمین‌کننده"""
        supplier = self.get_by_id(supplier_id)

        update_data = data.model_dump(exclude_unset=True)

        # بررسی تکراری نبودن نام (اگه تغییر کرده)
        if "name" in update_data and update_data["name"] != supplier.name:
            existing = self.repo.find_by_name(update_data["name"])
            if existing and existing.id != supplier_id:
                raise DuplicateError(f"تأمین‌کننده‌ای با نام «{update_data['name']}» قبلاً ثبت شده")

        for key, value in update_data.items():
            setattr(supplier, key, value)

        self.session.commit()
        self.session.refresh(supplier)

        logger.info(f"✅ تأمین‌کننده ویرایش شد: {supplier.code}")
        return supplier

    def change_status(self, supplier_id: int, new_status: SupplierStatus) -> Supplier:
        """تغییر وضعیت"""
        supplier = self.get_by_id(supplier_id)

        old_status = supplier.status
        supplier.status = new_status.value if isinstance(new_status, SupplierStatus) else new_status

        self.session.commit()
        self.session.refresh(supplier)

        logger.info(f"🔄 وضعیت {supplier.code}: {old_status} → {supplier.status}")
        return supplier

    def get_stats(self) -> dict:
        """آمار کلی"""
        all_suppliers = self.repo.get_all()
        return {
            "total":  len(all_suppliers),
            "active": sum(1 for s in all_suppliers if s.status == SupplierStatus.ACTIVE.value),
            "under_review": sum(1 for s in all_suppliers if s.status == SupplierStatus.UNDER_REVIEW.value),
            "blocked": sum(1 for s in all_suppliers if s.status == SupplierStatus.BLOCKED.value),
        }