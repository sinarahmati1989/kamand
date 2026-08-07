# """
MaterialGradeWidget — انتخاب گرید متریال با دسته‌بندی آبشاری
"""
import logging
from typing import Optional

from PySide6.QtWidgets import QWidget, QHBoxLayout, QComboBox, QLabel
from PySide6.QtCore import Qt, Signal

from app.database.session import get_session
from app.services.lookup_service import LookupService

logger = logging.getLogger(__name__)


class MaterialGradeWidget(QWidget):
    """
    انتخاب گرید متریال با دسته‌بندی آبشاری

    UI:  [دسته ▼]  ◀  [گرید ▼]
    DB:  فقط code گرید ذخیره می‌شود (مثل قبل — سازگار با داده‌های قدیمی)

    استفاده:
        w = MaterialGradeWidget()
        w.set_current_code("st37")
        code = w.get_current_code()  # "st37"
    """

    grade_changed = Signal(str)

    # دسته‌بندی‌های ثابت
    CATEGORIES = [
        ("",        "— همه —"),
        ("steel",   "فولاد"),
        ("ss",      "استیل ضدزنگ"),
        ("al",      "آلومینیوم"),
        ("nonfe",   "غیرآهنی"),
        ("plastic", "پلاستیک/لاستیک"),
        ("other",   "سایر"),
    ]

    # نگاشت گرید → دسته
    GRADE_CATEGORY = {
        "st37":      "steel",
        "st52":      "steel",
        "ck45":      "steel",
        "mo40":      "steel",
        "cast_iron": "steel",
        "ss304":     "ss",
        "ss316":     "ss",
        "al6061":    "al",
        "al7075":    "al",
        "brass":     "nonfe",
        "copper":    "nonfe",
        "nylon":     "plastic",
        "teflon":    "plastic",
        "rubber":    "plastic",
        "other":     "other",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._all_grades: list[tuple[str, str]] = []
        self._setup_ui()
        self._load_all_grades()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # ComboBox دسته
        self.cat_combo = QComboBox()
        self.cat_combo.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.cat_combo.setMinimumHeight(36)
        self.cat_combo.setMinimumWidth(130)
        self.cat_combo.setMaximumWidth(160)
        self.cat_combo.setToolTip("دسته متریال")
        for code, label in self.CATEGORIES:
            self.cat_combo.addItem(label, code)
        self.cat_combo.currentIndexChanged.connect(self._on_category_changed)
        layout.addWidget(self.cat_combo)

        # جداکننده
        arrow_lbl = QLabel("◀")
        arrow_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")
        arrow_lbl.setFixedWidth(16)
        layout.addWidget(arrow_lbl)

        # ComboBox گرید
        self.grade_combo = QComboBox()
        self.grade_combo.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.grade_combo.setMinimumHeight(36)
        self.grade_combo.currentIndexChanged.connect(self._on_grade_changed)
        layout.addWidget(self.grade_combo, 1)

    def _load_all_grades(self):
        """بارگذاری همه گریدها از DB"""
        try:
            with get_session() as session:
                svc = LookupService(session)
                items = svc.get_by_category(
                    "material_grade",
                    active_only=True,
                    include_children=True
                )
                self._all_grades = [(item.code, item.label_fa) for item in items]
        except Exception as e:
            logger.error(f"خطا در بارگذاری material_grade: {e}")
            self._all_grades = []

        self._populate_grades("")

    def _populate_grades(self, cat_code: str):
        """پر کردن grade_combo بر اساس دسته"""
        self.grade_combo.blockSignals(True)
        self.grade_combo.clear()
        self.grade_combo.addItem("— انتخاب نشده —", None)

        for code, label in self._all_grades:
            grade_cat = self.GRADE_CATEGORY.get(code, "other")
            if not cat_code or grade_cat == cat_code:
                self.grade_combo.addItem(label, code)

        self.grade_combo.blockSignals(False)

    def _on_category_changed(self, _index: int):
        """تغییر دسته → فیلتر گریدها"""
        cat_code = self.cat_combo.currentData() or ""
        current_grade = self.grade_combo.currentData()
        self._populate_grades(cat_code)
        # سعی کن گرید قبلی رو حفظ کنی
        if current_grade:
            idx = self.grade_combo.findData(current_grade)
            if idx >= 0:
                self.grade_combo.setCurrentIndex(idx)

    def _on_grade_changed(self, _index: int):
        code = self.grade_combo.currentData() or ""
        self.grade_changed.emit(code)

    def get_current_code(self) -> Optional[str]:
        """کد گرید انتخاب‌شده"""
        return self.grade_combo.currentData()

    def set_current_code(self, code: Optional[str]):
        """انتخاب گرید بر اساس کد"""
        if not code:
            self.grade_combo.setCurrentIndex(0)
            return

        # ابتدا دسته مناسب رو انتخاب کن
        cat_code = self.GRADE_CATEGORY.get(code, "")
        cat_idx = self.cat_combo.findData(cat_code)
        if cat_idx >= 0:
            self.cat_combo.blockSignals(True)
            self.cat_combo.setCurrentIndex(cat_idx)
            self.cat_combo.blockSignals(False)
            self._populate_grades(cat_code)

        # حالا گرید رو انتخاب کن
        idx = self.grade_combo.findData(code)
        if idx >= 0:
            self.grade_combo.setCurrentIndex(idx)

    def setMinimumHeight(self, h: int):
        super().setMinimumHeight(h)
        self.cat_combo.setMinimumHeight(h)
        self.grade_combo.setMinimumHeight(h)
