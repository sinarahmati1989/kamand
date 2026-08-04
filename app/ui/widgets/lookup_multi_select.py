"""
LookupMultiSelect — چند انتخابی از Lookup با دکمه افزودن سریع
"""
from typing import List, Optional
from PySide6.QtWidgets import (
    QGroupBox, QGridLayout, QCheckBox, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel
)
from PySide6.QtCore import Qt, Signal
import logging

from app.database.session import get_session
from app.services.lookup_service import LookupService
from app.ui.widgets.quick_add_lookup_dialog import QuickAddLookupDialog

logger = logging.getLogger(__name__)


class LookupMultiSelect(QWidget):
    """
    چند انتخابی از Lookup با CheckBox + دکمه افزودن سریع
    
    Args:
        category: نام دسته Lookup
        title: عنوان GroupBox (اگه None، GroupBox نمی‌سازه)
        columns: تعداد ستون‌های چیدمان
        allow_quick_add: نمایش دکمه افزودن سریع
    """

    selection_changed = Signal(list)  # لیست code های انتخاب‌شده
    items_reloaded = Signal()  # وقتی آیتم‌ها reload شدن

    def __init__(
        self,
        category: str,
        title: Optional[str] = None,
        columns: int = 2,
        allow_quick_add: bool = True,
        parent=None
    ):
        super().__init__(parent)
        self.category = category
        self.title = title
        self.columns = columns
        self.allow_quick_add = allow_quick_add

        self._checkboxes: dict[str, QCheckBox] = {}

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._setup_ui()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        if self.title:
            self._container = QGroupBox()
            self._container.setObjectName("formGroup")

            # عنوان با دکمه افزودن
            self._build_group_with_header(outer)
        else:
            self._container = QWidget()
            self._grid = QGridLayout(self._container)
            self._grid.setSpacing(10)
            self._grid.setContentsMargins(0, 0, 0, 0)
            outer.addWidget(self._container)

        self.load_items()

    def _build_group_with_header(self, outer_layout):
        """ساخت GroupBox با عنوان سفارشی + دکمه ➕"""
        # چون QGroupBox عنوان داخلی داره، تیتر رو بالاش می‌ذاریم
        self._container.setTitle(self.title)

        # Layout داخلی
        inner = QVBoxLayout(self._container)
        inner.setContentsMargins(14, 20, 14, 14)
        inner.setSpacing(10)

        # هدر با دکمه افزودن
        if self.allow_quick_add:
            header = QHBoxLayout()
            header.setContentsMargins(0, 0, 0, 4)

            add_btn = QPushButton("➕  افزودن جدید")
            add_btn.setObjectName("quickAddBtn")
            add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            add_btn.setFixedHeight(28)
            add_btn.setStyleSheet("""
                QPushButton#quickAddBtn {
                    background: rgba(99, 102, 241, 0.1);
                    color: #6366F1;
                    border: 1px dashed rgba(99, 102, 241, 0.4);
                    border-radius: 6px;
                    padding: 2px 12px;
                    font-family: "Segoe UI", "B Nazanin", sans-serif;
                    font-size: 11px;
                    font-weight: 600;
                }
                QPushButton#quickAddBtn:hover {
                    background: rgba(99, 102, 241, 0.2);
                    border-color: #6366F1;
                }
            """)
            add_btn.clicked.connect(self._on_quick_add)

            header.addStretch()
            header.addWidget(add_btn)
            inner.addLayout(header)

        # Grid برای چک‌باکس‌ها
        self._grid_widget = QWidget()
        self._grid = QGridLayout(self._grid_widget)
        self._grid.setSpacing(10)
        self._grid.setContentsMargins(0, 0, 0, 0)
        inner.addWidget(self._grid_widget)

        outer_layout.addWidget(self._container)

    def load_items(self):
        """بارگذاری آیتم‌ها"""
        # پاک کردن قبلی‌ها
        for cb in self._checkboxes.values():
            cb.deleteLater()
        self._checkboxes.clear()

        try:
            with get_session() as session:
                svc = LookupService(session)
                items = svc.get_by_category(
                    self.category,
                    active_only=True,
                    include_children=False
                )
        except Exception as e:
            logger.error(f"خطا در بارگذاری LookupMultiSelect '{self.category}': {e}")
            return

        row, col = 0, 0
        for item in items:
            cb = QCheckBox(item.label_fa)
            cb.setMinimumHeight(28)
            cb.stateChanged.connect(self._on_state_changed)
            self._checkboxes[item.code] = cb
            self._grid.addWidget(cb, row, col)

            col += 1
            if col >= self.columns:
                col = 0
                row += 1

        self.items_reloaded.emit()

    def _on_state_changed(self, _state):
        self.selection_changed.emit(self.get_selected_codes())

    def _on_quick_add(self):
        """باز کردن دیالوگ افزودن سریع"""
        # ذخیره انتخاب‌های فعلی
        selected = self.get_selected_codes()

        dlg = QuickAddLookupDialog(
            category=self.category,
            parent=self
        )

        if dlg.exec():
            # بازخوانی
            self.load_items()
            # بازیابی انتخاب‌های قبلی + انتخاب مورد جدید
            self.set_selected_codes(selected)

            # پیدا کردن آیتم جدید و تیک زدنش
            new_code = dlg.code_input.text().strip().lower()
            if new_code in self._checkboxes:
                self._checkboxes[new_code].setChecked(True)

    # ══════════════════════════════════════════════════════════════
    # Public API
    # ══════════════════════════════════════════════════════════════

    def get_selected_codes(self) -> List[str]:
        return [
            code for code, cb in self._checkboxes.items()
            if cb.isChecked()
        ]

    def set_selected_codes(self, codes: List[str]):
        for code, cb in self._checkboxes.items():
            cb.setChecked(code in codes)

    def clear_selection(self):
        for cb in self._checkboxes.values():
            cb.setChecked(False)

    def refresh(self):
        selected = self.get_selected_codes()
        self.load_items()
        self.set_selected_codes(selected)

    def get_all_codes(self) -> List[str]:
        return list(self._checkboxes.keys())