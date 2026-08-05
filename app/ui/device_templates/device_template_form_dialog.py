"""
دیالوگ افزودن/ویرایش تعریف دستگاه
"""
import logging

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QTextEdit,
    QPushButton, QWidget, QGroupBox,
    QScrollArea, QFrame, QDoubleSpinBox, QSpinBox,
)
from PySide6.QtCore import Qt

from app.services.device_template_service import DeviceTemplateService
from app.schemas.device_template_schema import (
    DeviceTemplateCreate, DeviceTemplateUpdate,
)
from app.database.session import get_session
from app.enums.engineering_enums import DeviceTemplateStatus
from app.enums.lookup_categories import LookupCategory
from app.ui.widgets.lookup_combo_with_add import LookupComboBoxWithAdd
from app.ui.widgets.toast import Toast

logger = logging.getLogger(__name__)


# واحدهای زمان و ضرایب تبدیل به دقیقه
TIME_UNITS = [
    ("minute", "دقیقه", 1),
    ("hour",   "ساعت",  60),
    ("day",    "روز",   60 * 8),      # روز کاری = 8 ساعت
    ("week",   "هفته",  60 * 8 * 5),  # هفته کاری = 5 روز
]


class DeviceTemplateFormDialog(QDialog):
    """فرم افزودن/ویرایش تعریف دستگاه"""

    def __init__(self, template_id: int | None = None, parent=None):
        super().__init__(parent)
        self.template_id = template_id
        self.is_edit = template_id is not None

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowTitle(
            "ویرایش تعریف دستگاه" if self.is_edit else "تعریف دستگاه جدید"
        )
        self.setMinimumSize(640, 580)
        self.resize(680, 620)

        self._setup_ui()

        if self.is_edit:
            self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # عنوان
        title_text = (
            "ویرایش تعریف دستگاه" if self.is_edit else "تعریف دستگاه جدید"
        )
        title = QLabel(title_text)
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # ردیف کد
        code_row = QHBoxLayout()
        code_lbl = QLabel("کد دستگاه:")
        code_lbl.setObjectName("fieldLabel")
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText(
            "خودکار: DVT-0001  (یا خودتان وارد کنید)"
        )
        self.code_input.setMinimumHeight(36)
        self.code_input.setMaximumWidth(260)
        if self.is_edit:
            self.code_input.setReadOnly(True)
            self.code_input.setStyleSheet(
                "color: #6366F1; font-weight: bold; font-size: 14px;"
                "padding: 6px 12px; background: rgba(255,255,255,0.85);"
                "border: 1.5px solid rgba(99,102,241,0.25); border-radius: 8px;"
            )
        code_row.addWidget(code_lbl)
        code_row.addWidget(self.code_input)
        code_row.addStretch()
        layout.addLayout(code_row)

        # محتوا داخل scroll
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)

        # ── گروه اطلاعات پایه ─────────────────────────────────────
        basic = QGroupBox("اطلاعات پایه")
        basic.setObjectName("formGroup")
        bv = QVBoxLayout(basic)
        bv.setContentsMargins(14, 20, 14, 14)
        bv.setSpacing(12)

        # نام دستگاه
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(
            "مثال: پمپ هیدرولیک 160 تن — سری آلفا"
        )
        self.name_input.setMinimumHeight(36)
        bv.addWidget(
            self._field("نام دستگاه", self.name_input, required=True)
        )

        # نوع دستگاه + Revision
        row1 = QHBoxLayout()
        row1.setSpacing(12)

        self.type_combo = LookupComboBoxWithAdd(
            LookupCategory.DEVICE_TEMPLATE_TYPE.value,
            allow_empty=True,
        )
        self.type_combo.setMinimumHeight(36)
        row1.addWidget(self._field("نوع دستگاه", self.type_combo), 2)

        self.revision_spin = QSpinBox()
        self.revision_spin.setRange(1, 99)
        self.revision_spin.setValue(1)
        self.revision_spin.setMinimumHeight(36)
        self.revision_spin.setPrefix("Rev. ")
        self.revision_spin.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        row1.addWidget(self._field("Revision", self.revision_spin), 1)

        bv.addLayout(row1)

        # وضعیت — فقط در ویرایش
        if self.is_edit:
            self.status_combo = QComboBox()
            self.status_combo.setMinimumHeight(36)
            for st in DeviceTemplateStatus:
                self.status_combo.addItem(st.label, st.value)
            bv.addWidget(self._field("وضعیت", self.status_combo))
        else:
            self.status_combo = None

        content_layout.addWidget(basic)

        # ── گروه مشخصات فنی ───────────────────────────────────────
        tech = QGroupBox("مشخصات فنی")
        tech.setObjectName("formGroup")
        tv = QVBoxLayout(tech)
        tv.setContentsMargins(14, 20, 14, 14)
        tv.setSpacing(12)

        row2 = QHBoxLayout()
        row2.setSpacing(12)

        # ── وزن ────────────────────────────────────────
        self.weight_spin = QDoubleSpinBox()
        self.weight_spin.setRange(0, 99999)
        self.weight_spin.setDecimals(2)
        self.weight_spin.setSpecialValueText("—")
        self.weight_spin.setSuffix("  kg")
        self.weight_spin.setMinimumHeight(36)
        self.weight_spin.setSingleStep(0.5)
        self.weight_spin.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        row2.addWidget(self._field("وزن تقریبی", self.weight_spin), 1)

        # ── زمان ساخت (با واحد) ───────────────────────
        time_widget = self._build_time_field()
        row2.addWidget(
            self._field("زمان ساخت استاندارد", time_widget), 1
        )

        tv.addLayout(row2)
        content_layout.addWidget(tech)

        # ── توضیحات ───────────────────────────────────────────────
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText(
            "توضیحات کلی دستگاه، کاربرد، ویژگی‌های اصلی..."
        )
        self.description_input.setMinimumHeight(75)
        self.description_input.setMaximumHeight(95)
        self.description_input.setStyleSheet("""
            QTextEdit {
                font-family: "Vazirmatn", "Segoe UI", "B Nazanin";
                font-size: 13px;
            }
        """)
        content_layout.addWidget(
            self._field("توضیحات", self.description_input)
        )

        self.tech_notes_input = QTextEdit()
        self.tech_notes_input.setPlaceholderText(
            "نکات مهندسی، استانداردها، محدودیت‌های طراحی..."
        )
        self.tech_notes_input.setMinimumHeight(75)
        self.tech_notes_input.setMaximumHeight(95)
        self.tech_notes_input.setStyleSheet("""
            QTextEdit {
                font-family: "Vazirmatn", "Segoe UI", "B Nazanin";
                font-size: 13px;
            }
        """)
        content_layout.addWidget(
            self._field("نکات مهندسی", self.tech_notes_input)
        )

        content_layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        # دکمه‌ها
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        save_btn = QPushButton("ذخیره")
        save_btn.setObjectName("primaryButton")
        save_btn.setFixedSize(130, 42)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._on_save)

        cancel_btn = QPushButton("انصراف")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.setFixedSize(110, 42)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)

        btn_row.addStretch(1)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _build_time_field(self) -> QWidget:
        """
        ساخت فیلد ترکیبی زمان ساخت:
        [عدد] [واحد: دقیقه/ساعت/روز/هفته]
        """
        wrapper = QWidget()
        h = QHBoxLayout(wrapper)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)

        self.time_value_spin = QDoubleSpinBox()
        self.time_value_spin.setRange(0, 99999)
        self.time_value_spin.setDecimals(2)
        self.time_value_spin.setSpecialValueText("—")
        self.time_value_spin.setMinimumHeight(36)
        self.time_value_spin.setSingleStep(0.5)
        self.time_value_spin.setLayoutDirection(
            Qt.LayoutDirection.LeftToRight
        )

        self.time_unit_combo = QComboBox()
        self.time_unit_combo.setMinimumHeight(36)
        self.time_unit_combo.setFixedWidth(90)
        for code, label, _ in TIME_UNITS:
            self.time_unit_combo.addItem(label, code)
        # پیش‌فرض: ساعت (خیلی معمول‌تره)
        self.time_unit_combo.setCurrentIndex(1)

        h.addWidget(self.time_value_spin, 2)
        h.addWidget(self.time_unit_combo, 1)
        return wrapper

    def _field(
        self, label_text: str, widget: QWidget, required: bool = False
    ) -> QWidget:
        wrapper = QWidget()
        v = QVBoxLayout(wrapper)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(5)
        lbl = QLabel(f"{label_text} *" if required else label_text)
        lbl.setObjectName("fieldLabel")
        lbl.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        v.addWidget(lbl)
        v.addWidget(widget)
        return wrapper

    # ── تبدیل واحد زمان ────────────────────────────────────────────

    def _get_time_multiplier(self, unit_code: str) -> int:
        """گرفتن ضریب تبدیل واحد زمان به دقیقه"""
        for code, _, mult in TIME_UNITS:
            if code == unit_code:
                return mult
        return 1

    def _minutes_to_best_unit(self, minutes: int) -> tuple[float, str]:
        """
        تبدیل دقیقه به بهترین واحد نمایش:
        - < 60 دقیقه → دقیقه
        - < 8 ساعت → ساعت
        - < 5 روز → روز
        - بقیه → هفته
        """
        if minutes < 60:
            return (minutes, "minute")
        elif minutes < 60 * 8:
            return (round(minutes / 60, 2), "hour")
        elif minutes < 60 * 8 * 5:
            return (round(minutes / (60 * 8), 2), "day")
        else:
            return (round(minutes / (60 * 8 * 5), 2), "week")

    def _load_data(self):
        try:
            with get_session() as session:
                svc = DeviceTemplateService(session)
                t = svc.get_by_id(self.template_id)
                if not t:
                    raise ValueError("تعریف دستگاه یافت نشد")

                self.code_input.setText(t.code)
                self.name_input.setText(t.name or "")

                if t.template_type:
                    self.type_combo.set_current_code(t.template_type)

                self.revision_spin.setValue(t.revision_no or 1)

                if self.status_combo:
                    idx = self.status_combo.findData(t.status)
                    if idx >= 0:
                        self.status_combo.setCurrentIndex(idx)

                if t.estimated_weight:
                    self.weight_spin.setValue(float(t.estimated_weight))

                # زمان ساخت: تبدیل از دقیقه به بهترین واحد
                if t.estimated_cycle_time:
                    value, unit = self._minutes_to_best_unit(
                        t.estimated_cycle_time
                    )
                    self.time_value_spin.setValue(value)
                    idx = self.time_unit_combo.findData(unit)
                    if idx >= 0:
                        self.time_unit_combo.setCurrentIndex(idx)

                if t.description:
                    self.description_input.setPlainText(t.description)

                if t.technical_notes:
                    self.tech_notes_input.setPlainText(t.technical_notes)

        except Exception as e:
            logger.error(f"خطا در بارگذاری: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _collect(self) -> dict:
        weight_val = self.weight_spin.value()

        # تبدیل زمان به دقیقه
        time_val = self.time_value_spin.value()
        time_unit = self.time_unit_combo.currentData()
        cycle_minutes = None
        if time_val > 0:
            multiplier = self._get_time_multiplier(time_unit)
            cycle_minutes = int(round(time_val * multiplier))

        return {
            "code":                 self.code_input.text().strip() or None,
            "name":                 self.name_input.text().strip(),
            "template_type":        self.type_combo.get_current_code() or None,
            "revision_no":          self.revision_spin.value(),
            "estimated_weight":     weight_val if weight_val > 0 else None,
            "estimated_cycle_time": 