"""
Service — Lookup
منطق کسب‌وکار مدیریت گزینه‌ها
"""
import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from app.repositories.lookup_repository import LookupRepository
from app.models.lookup import Lookup
from app.schemas.lookup_schema import LookupCreate, LookupUpdate
from app.core.exceptions import NotFoundError, DuplicateError

logger = logging.getLogger(__name__)


class LookupService:
    """سرویس مدیریت Lookup ها"""

    def __init__(self, session: Session):
        self.session = session
        self.repo = LookupRepository(session)

    # ══════════════════════════════════════════════════════════════
    # Read
    # ══════════════════════════════════════════════════════════════

    def get_by_id(self, lookup_id: int) -> Lookup:
        lookup = self.repo.get_by_id(lookup_id)
        if not lookup:
            raise NotFoundError(f"Lookup با شناسه {lookup_id} یافت نشد")
        return lookup

    def get_by_category(
        self,
        category: str,
        active_only: bool = True,
        parent_id: Optional[int] = None,
        include_children: bool = False
    ) -> List[Lookup]:
        """گزینه‌های یک دسته"""
        return self.repo.get_by_category(
            category, active_only, parent_id, include_children
        )

    def get_children(self, parent_id: int, active_only: bool = True) -> List[Lookup]:
        """زیرشاخه‌های یک آیتم"""
        return self.repo.get_children(parent_id, active_only)

    def get_code_to_label_map(self, category: str) -> dict[str, str]:
        """
        نگاشت code به label برای یه دسته
        (برای نمایش سریع در جدول‌ها)
        
        مثال: {"manufacturer": "تولیدکننده", ...}
        """
        items = self.repo.get_by_category(
            category, active_only=False, include_children=True
        )
        return {item.code: item.label_fa for item in items}

    def search(self, category: str, keyword: str) -> List[Lookup]:
        return self.repo.search(category, keyword)

    def get_all_categories(self) -> List[str]:
        return self.repo.get_all_categories()

    # ══════════════════════════════════════════════════════════════
    # Create
    # ══════════════════════════════════════════════════════════════

    def create(self, data: LookupCreate, is_system: bool = False) -> Lookup:
        """ایجاد Lookup جدید"""
        # بررسی تکراری نبودن (category, code)
        existing = self.repo.get_by_category_code(data.category, data.code)
        if existing:
            raise DuplicateError(
                f"گزینه‌ای با کد «{data.code}» در دسته «{data.category}» قبلاً ثبت شده"
            )

        # بررسی معتبر بودن parent (اگه داشت)
        if data.parent_id is not None:
            parent = self.repo.get_by_id(data.parent_id)
            if not parent:
                raise NotFoundError(f"والد با شناسه {data.parent_id} یافت نشد")

        lookup = Lookup(
            category=data.category,
            code=data.code,
            label_fa=data.label_fa,
            label_en=data.label_en,
            parent_id=data.parent_id,
            sort_order=data.sort_order,
            is_active=data.is_active,
            is_system=is_system,
            description=data.description,
            extra_data=data.extra_data,
        )

        self.repo.add(lookup)
        logger.info(f"✅ Lookup ایجاد شد: {data.category}/{data.code} — {data.label_fa}")
        return lookup

    # ══════════════════════════════════════════════════════════════
    # Update
    # ══════════════════════════════════════════════════════════════

    def update(self, lookup_id: int, data: LookupUpdate) -> Lookup:
        """ویرایش Lookup"""
        lookup = self.get_by_id(lookup_id)

        update_data = data.model_dump(exclude_unset=True)

        # چک والد
        if "parent_id" in update_data and update_data["parent_id"] is not None:
            if update_data["parent_id"] == lookup_id:
                raise ValueError("یک آیتم نمی‌تواند والد خودش باشد")
            parent = self.repo.get_by_id(update_data["parent_id"])
            if not parent:
                raise NotFoundError("والد یافت نشد")

        for key, value in update_data.items():
            setattr(lookup, key, value)

        self.session.flush()
        self.session.refresh(lookup)
        logger.info(f"✅ Lookup ویرایش شد: {lookup.category}/{lookup.code}")
        return lookup

    # ══════════════════════════════════════════════════════════════
    # Delete
    # ══════════════════════════════════════════════════════════════

    def delete(self, lookup_id: int) -> None:
        """حذف Lookup"""
        lookup = self.get_by_id(lookup_id)

        if lookup.is_system:
            raise ValueError(
                f"«{lookup.label_fa}» یک گزینه سیستمی است و قابل حذف نیست. "
                "می‌توانید آن را غیرفعال کنید."
            )

        # چک فرزندان
        children = self.repo.get_children(lookup_id, active_only=False)
        if children:
            raise ValueError(
                f"این آیتم دارای {len(children)} زیرشاخه است. "
                "ابتدا زیرشاخه‌ها را حذف کنید."
            )

        self.repo.delete(lookup)
        logger.info(f"🗑️ Lookup حذف شد: {lookup.category}/{lookup.code}")

    def toggle_active(self, lookup_id: int) -> Lookup:
        """تغییر وضعیت فعال/غیرفعال"""
        lookup = self.get_by_id(lookup_id)
        lookup.is_active = not lookup.is_active
        self.session.flush()
        self.session.refresh(lookup)

        status = "فعال" if lookup.is_active else "غیرفعال"
        logger.info(f"🔄 وضعیت {lookup.category}/{lookup.code}: {status}")
        return lookup

    # ══════════════════════════════════════════════════════════════
    # Seed (بارگذاری داده‌های اولیه)
    # ══════════════════════════════════════════════════════════════

    def seed_if_not_exists(
        self,
        category: str,
        code: str,
        label_fa: str,
        label_en: Optional[str] = None,
        parent_id: Optional[int] = None,
        sort_order: int = 0,
        description: Optional[str] = None,
    ) -> Lookup:
        """
        اگه آیتم وجود نداره ایجاد کن، وگرنه همون رو برگردون
        (برای seed کردن داده‌های سیستمی)
        """
        existing = self.repo.get_by_category_code(category, code)
        if existing:
            return existing

        lookup = Lookup(
            category=category,
            code=code,
            label_fa=label_fa,
            label_en=label_en,
            parent_id=parent_id,
            sort_order=sort_order,
            is_active=True,
            is_system=True,  # ← داده‌های seed شده system هستن
            description=description,
        )
        self.repo.add(lookup)
        logger.info(f"🌱 Seed: {category}/{code} — {label_fa}")
        return lookup