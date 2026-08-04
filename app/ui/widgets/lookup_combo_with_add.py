"""
LookupComboBoxWithAdd — ComboBox با دکمه «+ افزودن سریع»
────────────────────────────────────────────────────────────
یک ComboBox که کنارش دکمه‌ی افزودن سریع دارد.
پس از افزودن، خودکار refresh شده و آیتم جدید انتخاب می‌شود.

استفاده:
    combo = LookupComboBoxWithAdd("operation_type")
    combo.set_current_code("machining")
    code = combo.get_current_code()
"""
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton
)
from PySide6.QtCore import Qt, Signal

from app.ui.widgets.lookup_combo import LookupComboBox
from app.ui.widgets.quick_add_lookup_dialog import QuickAddLookupDialog


class LookupComboBoxWithAdd(QWidget):
    """
    ComboBox + دکمه افزودن سریع

    Args:
        category: نام دسته Lookup (مثل "operation_type")
        allow_empty: اجازه اضافه کردن گزینه «انتخاب نشده»
        parent_id: فقط زیرشاخه‌های این والد را نمایش بده
    """

    currentIndexChanged = Signal(int)  # forward از combo داخلی

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
        self._setup_ui()

    # ---------- Setup ----------

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # ComboBox داخلی
        self.combo = LookupComboBox(
            category=self.category,
            allow_empty=self.allow_empty,
            parent_id=self.parent_id,
        )
        self.combo.currentIndexChanged.connect(self.currentIndexChanged.emit)
        layout.addWidget(self.combo, 1)

        # دکمه + افزودن سریع
        self.add_btn = QPushButton("+")
        self.add_btn.setObjectName("lookupAddBtn")
        self.add_btn.setFixedSize(36, 36)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.setToolTip("افزودن گزینه جدید")
        self.add_btn.setStyleSheet("""
            QPushButton#lookupAddBtn {
                background-color: #6366F1;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
                padding: 0;
            }
            QPushButton#lookupAddBtn:hover {
                background-color: #4F46E5;
            }
            QPushButton#lookupAddBtn:pressed {
                background-color: #4338CA;
            }
        """)
        self.add_btn.clicked.connect(self._on_add_clicked)
        layout.addWidget(self.add_btn)

    # ---------- Handler ----------

    def _on_add_clicked(self):
        """باز کردن دیالوگ افزودن سریع"""
        dlg = QuickAddLookupDialog(
            category=self.category,
            parent_id=self.parent_id,
            parent=self
        )
        dlg.lookup_added.connect(self._on_lookup_added)
        dlg.exec()

    def _on_lookup_added(self, code: str, label_fa: str):
        """بعد از افزودن، refresh و انتخاب آیتم جدید"""
        self.combo.refresh()
        self.combo.set_current_code(code)

    # ---------- Public API (forward به combo داخلی) ----------

    def get_current_code(self) -> Optional[str]:
        return self.combo.get_current_code()

    def get_current_label(self) -> str:
        return self.combo.get_current_label()

    def set_current_code(self, code: Optional[str]) -> bool:
        return self.combo.set_current_code(code)

    def refresh(self):
        self.combo.refresh()

    def set_parent_id(self, parent_id: Optional[int]):
        self.parent_id = parent_id
        self.combo.set_parent_id(parent_id)

    def setMinimumHeight(self, h: int):
        super().setMinimumHeight(h)
        self.combo.setMinimumHeight(h)
        # دکمه هم متناسب
        btn_size = max(h, 32)
        self.add_btn.setFixedSize(btn_size, btn_size)

    def setFixedHeight(self, h: int):
        super().setFixedHeight(h)
        self.combo.setFixedHeight(h)
        self.add_btn.setFixedSize(h, h)

    def setEnabled(self, enabled: bool):
        super().setEnabled(enabled)
        self.combo.setEnabled(enabled)
        self.add_btn.setEnabled(enabled)

    def setItemText(self, index: int, text: str):
        """forward برای سازگاری با LookupComboBox"""
        self.combo.setItemText(index, text)

    def currentData(self):
        """forward برای سازگاری"""
        return self.combo.currentData()

    def findData(self, data):
        """forward برای سازگاری"""
        return self.combo.findData(data)

    def setCurrentIndex(self, index: int):
        """forward برای سازگاری"""
        self.combo.setCurrentIndex(index)