"""
LookupComboBox — ComboBox که خودش از Lookup Service داده می‌خونه
─────────────────────────────────────────────────────────────
استفاده:
    combo = LookupComboBox("supplier_tier")
    combo.set_current_code("A")   # انتخاب پیش‌فرض
    selected_code = combo.get_current_code()
"""
from typing import Optional
from PySide6.QtWidgets import QComboBox
from PySide6.QtCore import Qt
import logging

from app.database.session import get_session
from app.services.lookup_service import LookupService

logger = logging.getLogger(__name__)


class LookupComboBox(QComboBox):
    """
    ComboBox که مقادیر رو از جدول Lookup می‌خونه
    
    Args:
        category: نام دسته Lookup (مثل "supplier_tier")
        allow_empty: آیا اجازه بده هیچ چیز انتخاب نشه (— انتخاب کنید —)
        parent_id: فقط زیرشاخه‌های این والد رو نشون بده
    """

    def __init__(
        self,
        category: str,
        allow_empty: bool = False,
        parent_id: Optional[int] = None,
        parent=None
    ):
        super().__init__(parent)
        self.category = category
        self.allow_empty = allow_empty
        self.parent_id = parent_id
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.load_items()

    def load_items(self):
        """بارگذاری آیتم‌ها از Lookup Service"""
        self.clear()

        if self.allow_empty:
            self.addItem("— انتخاب کنید —", None)

        try:
            with get_session() as session:
                svc = LookupService(session)
                items = svc.get_by_category(
                    self.category,
                    active_only=True,
                    parent_id=self.parent_id,
                    include_children=(self.parent_id is not None)
                )

            for item in items:
                # هر آیتم: text = label_fa, data = code
                self.addItem(item.label_fa, item.code)

            logger.debug(f"LookupComboBox: {len(items)} آیتم برای '{self.category}' بارگذاری شد")

        except Exception as e:
            logger.error(f"خطا در بارگذاری LookupComboBox '{self.category}': {e}")

    # ══════════════════════════════════════════════════════════════
    # Public API
    # ══════════════════════════════════════════════════════════════

    def get_current_code(self) -> Optional[str]:
        """کد آیتم انتخاب شده"""
        return self.currentData()

    def get_current_label(self) -> str:
        """لیبل آیتم انتخاب شده"""
        return self.currentText()

    def set_current_code(self, code: Optional[str]) -> bool:
        """
        انتخاب آیتم با کد
        
        Returns:
            True اگه پیدا شد، False وگرنه
        """
        if code is None:
            if self.allow_empty:
                self.setCurrentIndex(0)
            return True

        idx = self.findData(code)
        if idx >= 0:
            self.setCurrentIndex(idx)
            return True
        return False

    def refresh(self):
        """بازخوانی آیتم‌ها از DB (بعد از تغییر)"""
        current_code = self.get_current_code()
        self.load_items()
        if current_code:
            self.set_current_code(current_code)

    def set_parent_id(self, parent_id: Optional[int]):
        """تغییر والد و بارگذاری مجدد"""
        self.parent_id = parent_id
        self.load_items()