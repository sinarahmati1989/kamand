"""
CustomerComboBox — انتخاب مشتری از لیست مشتریان
ظاهر یکسان با LookupComboBox
"""
from typing import Optional
from PySide6.QtWidgets import QComboBox
from PySide6.QtCore import Qt
import logging

from app.database.session import get_session
from app.services.customer_service import CustomerService

logger = logging.getLogger(__name__)


class CustomerComboBox(QComboBox):
    """
    ComboBox انتخاب مشتری از جدول مشتریان

    Args:
        allow_empty: آیا اجازه بده گزینه "-- انتخاب مشتری --" باشد
    """

    def __init__(
        self,
        allow_empty: bool = True,
        parent=None
    ):
        super().__init__(parent)
        self.allow_empty = allow_empty
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.load_items()

    def load_items(self):
        """بارگذاری لیست مشتریان از دیتابیس"""
        self.clear()

        if self.allow_empty:
            self.addItem("— انتخاب مشتری —", None)

        try:
            with get_session() as session:
                svc = CustomerService(session)
                customers = svc.get_all()

            for c in customers:
                # نمایش: کد + نام
                display = f"{c.code} — {c.name}" if c.code else c.name
                self.addItem(display, c.id)

            logger.debug(
                f"CustomerComboBox: {len(customers)} مشتری بارگذاری شد"
            )

        except Exception as e:
            logger.error(f"خطا در بارگذاری CustomerComboBox: {e}")

    # ═══ Public API ═══

    def get_current_id(self) -> Optional[int]:
        """ID مشتری انتخاب شده"""
        return self.currentData()

    def get_current_name(self) -> str:
        """نام مشتری انتخاب شده"""
        return self.currentText()

    def set_current_id(self, customer_id: Optional[int]) -> bool:
        """
        انتخاب مشتری با ID

        Returns:
            True اگر پیدا شد، False وگرنه
        """
        if customer_id is None:
            if self.allow_empty:
                self.setCurrentIndex(0)
            return True

        idx = self.findData(customer_id)
        if idx >= 0:
            self.setCurrentIndex(idx)
            return True
        return False

    def refresh(self):
        """بازخوانی لیست مشتریان از DB"""
        current_id = self.get_current_id()
        self.load_items()
        if current_id:
            self.set_current_id(current_id)