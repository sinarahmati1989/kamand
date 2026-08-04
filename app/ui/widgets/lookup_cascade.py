"""
LookupCascadeSelect — انتخاب آبشاری چند سطحی
─────────────────────────────────────────────
پشتیبانی از ۲ یا ۳ سطح دسته‌بندی

استفاده ۲ سطحی (زیرشاخه):
    cascade = LookupCascadeSelect(
        category="supplier_subcategory",
        parent_category="supplier_type"
    )
    parent_multi.selection_changed.connect(cascade.update_parents)

استفاده ۳ سطحی (جزئیات):
    detail = LookupCascadeSelect(
        category="supplier_specialization",
        parent_category="supplier_subcategory"
    )
    cascade.selection_changed.connect(detail.update_from_dict)
"""
from typing import List, Dict, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QGridLayout, QCheckBox, QPushButton
)
from PySide6.QtCore import Qt, Signal
import logging

from app.database.session import get_session
from app.services.lookup_service import LookupService
from app.ui.widgets.quick_add_lookup_dialog import QuickAddLookupDialog

logger = logging.getLogger(__name__)


class LookupCascadeSelect(QWidget):
    """
    نمایش آبشاری آیتم‌ها به تفکیک والدها
    
    Args:
        category: نام دسته این سطح (مثل "supplier_subcategory")
        parent_category: نام دسته والدها (مثل "supplier_type")
        columns: تعداد ستون‌های چیدمان
        allow_quick_add: نمایش دکمه افزودن سریع
        group_icon: آیکون GroupBox (پیش‌فرض: 🎯)
        group_title_prefix: پیشوند عنوان GroupBox
    """

    # Signal — {parent_code: [child_codes]}
    selection_changed = Signal(dict)

    def __init__(
        self,
        category: str,
        parent_category: str,
        columns: int = 2,
        allow_quick_add: bool = True,
        group_icon: str = "🎯",
        group_title_prefix: str = "حوزه‌های تخصصی",
        parent=None
    ):
        super().__init__(parent)
        self.category = category
        self.parent_category = parent_category
        self.columns = columns
        self.allow_quick_add = allow_quick_add
        self.group_icon = group_icon
        self.group_title_prefix = group_title_prefix

        # {parent_code: {child_code: checkbox}}
        self._checkboxes: Dict[str, Dict[str, QCheckBox]] = {}
        # {parent_code: {"group": QGroupBox, ...}}
        self._groups: Dict[str, dict] = {}
        # کش والدها (code → Lookup object)
        self._parents_cache: Dict[str, object] = {}

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(12)

        self._load_parents_cache()

    def _load_parents_cache(self):
        """کش والدها"""
        try:
            with get_session() as session:
                svc = LookupService(session)
                parents = svc.get_by_category(
                    self.parent_category,
                    active_only=False,
                    include_children=True  # همه سطوح والد
                )
                self._parents_cache = {p.code: p for p in parents}
        except Exception as e:
            logger.error(f"خطا در کش والدها '{self.parent_category}': {e}")

    # ══════════════════════════════════════════════════════════════
    # API عمومی: آپدیت لیست والدها
    # ══════════════════════════════════════════════════════════════

    def update_parents(self, parent_codes: List[str]):
        """
        وقتی والدهای انتخاب‌شده از یه لیست ساده تغییر کردن
        (استفاده در LookupMultiSelect)
        """
        self._load_parents_cache()

        current_codes = set(self._groups.keys())
        new_codes = set(parent_codes)

        # حذف والدهای غیرفعال
        to_remove = current_codes - new_codes
        for code in to_remove:
            self._remove_group(code)

        # اضافه کردن والدهای جدید
        to_add = new_codes - current_codes
        for code in to_add:
            self._add_group(code)

        self._emit_change()

    def update_from_dict(self, parents_dict: Dict[str, List[str]]):
        """
        وقتی والدهای انتخاب‌شده به صورت dict میان
        (استفاده در LookupCascadeSelect پدر — سطح ۲ به سطح ۳)
        
        parents_dict: {level2_parent_code: [level2_child_codes]}
        فقط child_codes (Level 2) به عنوان والدهای این سطح در نظر گرفته می‌شن
        """
        # همه فرزندان همه والدها رو flatten می‌کنیم
        all_parent_codes = []
        for parent_code, child_codes in parents_dict.items():
            all_parent_codes.extend(child_codes)

        # حالا مثل update_parents عمل کن
        self.update_parents(all_parent_codes)

    # ══════════════════════════════════════════════════════════════
    # ساخت/حذف GroupBox
    # ══════════════════════════════════════════════════════════════

    def _add_group(self, parent_code: str):
        """اضافه کردن GroupBox برای یه والد"""
        if parent_code in self._groups:
            return

        parent = self._parents_cache.get(parent_code)
        if not parent:
            logger.warning(f"والد '{parent_code}' در کش پیدا نشد")
            return

        # خواندن فرزندان
        try:
            with get_session() as session:
                svc = LookupService(session)
                children = svc.get_by_category(
                    self.category,
                    active_only=True,
                    parent_id=parent.id
                )
        except Exception as e:
            logger.error(f"خطا در بارگذاری فرزندان '{parent_code}': {e}")
            return

        # اگه هیچ فرزندی نداره و quick_add هم فعال نیست، اصلاً GroupBox نساز
        if not children and not self.allow_quick_add:
            return

        # ساخت GroupBox
        group = QGroupBox(
            f"{self.group_icon}  {self.group_title_prefix} — {parent.label_fa}"
        )
        group.setObjectName("formGroup")

        inner = QVBoxLayout(group)
        inner.setContentsMargins(14, 20, 14, 14)
        inner.setSpacing(10)

        # هدر با دکمه افزودن
        if self.allow_quick_add:
            header = QHBoxLayout()
            header.setContentsMargins(0, 0, 0, 4)

            add_btn = QPushButton("➕  افزودن جدید")
            add_btn.setObjectName("quickAddBtn")
            add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            add_btn.setFixedHeight(26)
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
            add_btn.clicked.connect(
                lambda: self._on_quick_add(parent_code)
            )

            header.addStretch()
            header.addWidget(add_btn)
            inner.addLayout(header)

        # اگه هیچ فرزندی نداره، پیام راهنما
        if not children:
            from PySide6.QtWidgets import QLabel
            empty_lbl = QLabel(
                "هنوز گزینه‌ای اضافه نشده. با دکمه بالا اضافه کنید."
            )
            empty_lbl.setStyleSheet(
                "color: #94A3B8; font-size: 12px; padding: 8px; "
                "text-align: center;"
            )
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            inner.addWidget(empty_lbl)
            self._groups[parent_code] = {"group": group, "grid": None, "grid_widget": None}
            self._checkboxes[parent_code] = {}
            self._layout.addWidget(group)
            return

        # Grid برای چک‌باکس‌ها
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(8)
        grid.setContentsMargins(0, 0, 0, 0)
        inner.addWidget(grid_widget)

        child_checkboxes = {}
        row, col = 0, 0
        for child in children:
            cb = QCheckBox(child.label_fa)
            cb.setMinimumHeight(26)
            cb.stateChanged.connect(self._on_state_changed)
            child_checkboxes[child.code] = cb
            grid.addWidget(cb, row, col)
            col += 1
            if col >= self.columns:
                col = 0
                row += 1

        self._groups[parent_code] = {
            "group": group,
            "grid": grid,
            "grid_widget": grid_widget
        }
        self._checkboxes[parent_code] = child_checkboxes
        self._layout.addWidget(group)

    def _remove_group(self, parent_code: str):
        """حذف GroupBox یه والد"""
        if parent_code not in self._groups:
            return

        group_info = self._groups.pop(parent_code)
        group = group_info["group"]
        self._checkboxes.pop(parent_code, None)
        self._layout.removeWidget(group)
        group.deleteLater()

    def _reload_group(self, parent_code: str):
        """بازخوانی فقط یک GroupBox"""
        if parent_code not in self._groups:
            return
        self._remove_group(parent_code)
        self._add_group(parent_code)

    # ══════════════════════════════════════════════════════════════
    # افزودن سریع
    # ══════════════════════════════════════════════════════════════

    def _on_quick_add(self, parent_code: str):
        """افزودن سریع فرزند برای این والد"""
        parent = self._parents_cache.get(parent_code)
        if not parent:
            return

        # ذخیره انتخاب‌های فعلی
        selected = self.get_selected_codes()

        dlg = QuickAddLookupDialog(
            category=self.category,
            parent_id=parent.id,
            parent_label=parent.label_fa,
            parent=self
        )

        if dlg.exec():
            # بازخوانی این GroupBox
            self._reload_group(parent_code)
            # بازیابی انتخاب‌های قبلی
            self.set_selected_codes(selected)

            # تیک زدن آیتم جدید
            new_code = dlg.code_input.text().strip().lower()
            if parent_code in self._checkboxes:
                if new_code in self._checkboxes[parent_code]:
                    self._checkboxes[parent_code][new_code].setChecked(True)

    # ══════════════════════════════════════════════════════════════
    # Events
    # ══════════════════════════════════════════════════════════════

    def _on_state_changed(self, _state):
        self._emit_change()

    def _emit_change(self):
        self.selection_changed.emit(self.get_selected_codes())

    # ══════════════════════════════════════════════════════════════
    # Public API
    # ══════════════════════════════════════════════════════════════

    def get_selected_codes(self) -> Dict[str, List[str]]:
        """
        کدهای انتخاب‌شده به تفکیک والد
        
        مثال:
            {"raw_material_فلزات": ["استیل_304", "آهن_st37"], ...}
        """
        result = {}
        for parent_code, children in self._checkboxes.items():
            checked = [code for code, cb in children.items() if cb.isChecked()]
            if checked:
                result[parent_code] = checked
        return result

    def set_selected_codes(self, data: Dict[str, List[str]]):
        """
        انتخاب کدها به تفکیک والد
        
        Args:
            data: {parent_code: [child_codes]}
        """
        for parent_code, child_codes in data.items():
            if parent_code in self._checkboxes:
                for child_code, cb in self._checkboxes[parent_code].items():
                    cb.setChecked(child_code in child_codes)

    def clear_all(self):
        """حذف همه GroupBox ها"""
        for code in list(self._groups.keys()):
            self._remove_group(code)