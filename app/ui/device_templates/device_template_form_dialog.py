"""
دیالوگ افزودن/ویرایش قالب دستگاه
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
from app.ui.widgets.lookup_combo import LookupComboBox
from app.ui.widgets.toast import Toast

logger = logging.getLogger(__name__)


class DeviceTemplateFormDialog(QDialog):
    """فرم افزودن/ویرایش قالب دستگاه"""

    def __init__(self, template_id: int | None = None, parent=None):
        super().__init__(parent)
        self.template_id = template_id
        self.is_edit = template_id is not None

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowTitle(
            "ویرایش قالب دستگاه" if self.is_edit else "قالب دستگاه جدید"
        )
        self.setMinimumSize(640, 620)
        self.resize(680, 660)

        self._setup_ui()

        if self.is_edit:
            self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # عنوان
        title_text = (
            "ویرایش قالب دستگاه" if self.is_edit else "قالب دستگاه جدید"
        )
        title = QLabel(title_text)
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # کد — هم در افزودن هم ویرایش
        code_row = QHBoxLayout()
        code_lbl = QLabel("کد قالب:")
        code_lbl.setObjectName("fieldLabel")
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText(
            "خودکار: DVT-0001 (یا خودتان وارد کنید)"
        )
        self.code_input.setMinimumHeight(36)
        self.code_input.setMaximumWidth(280)
        if self.is_edit:
            self.code_input.setReadOnly(True)
            self.code_input.setStyleSheet(
                "color: #6366F1; font-weight: bold; font-size: 14px;"
                "padding: 6px 12px; background: rgba(255,255,255,0.85);"
                "border: 1.5px solid rgba(99,102,241,0.25);"
                "border-radius: 8px;"
            )
        code_row.addWidget(code_lbl)
        code_row.addWidget(self.code_input)
        code_row.addStretch()
        layout.addLayout(code_row)

        # اسکرول
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)

        # ── گروه اطلاعات پایه ──
        basic = QGroupBox("اطلاعات پایه")
        basic.setObjectName("formGroup")
        bv = QVBoxLayout(basic)
        bv.setContentsMargins(14, 20, 14, 14)
        bv.setSpacing(12)

        # نام
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(
            "مثال: هیدرولیک اکچویتور ۵۰ تن، پمپ فشار بالا"
        )
        self.name_input.setMinimumHeight(36)
        bv.addWidget(
            self._make_field("نام دستگاه", self.name_input, required=True)
        )

        # ردیف نوع + Revision
        row1 = QHBoxLayout()
        row1.setSpacing(12)

        self.type_combo = LookupComboBoxWithAdd(
            LookupCategory.DEVICE_TEMPLATE_TYPE.value,
            allow_empty=True,
        )
        self.type_combo.setMinimumHeight(36)
        row1.addWidget(
            self._make_field("نوع دستگاه", self.type_combo), 2
        )

        self.revision_spin = QSpinBox()
        self.revision_spin.setRange(1, 99)
        self.revision_spin.setValue(1)
        self.revision_spin.setMinimumHeight(36)
        self.revision_spin.setPrefix("Rev. ")
        row1.addWidget(
            self._make_field("Revision", self.revision_spin), 1
        )
        bv.addLayout(row1)

        # ردیف واحد + وضعیت
        row2 = QHBoxLayout()
        row2.setSpacing(12)

        self.uom_combo = LookupComboBox(
            LookupCategory.UOM.value,
            allow_empty=True,
        )
        self.uom_combo.setMinimumHeight(36)
        row2.addWidget(
            self._make_field("واحد اصلی", self.uom_combo), 1
        )

        self.status_combo = QComboBox()
        self.status_combo.setMinimumHeight(36)
        for st in DeviceTemplateStatus:
            self.status_combo.addItem(st.label, st.value)
        if not self.is_edit:
            self.status_combo.setEnabled(False)
            self.status_combo.setToolTip(
                "وضعیت رکورد جدید پیش‌فرض «پیش‌نویس» است."
            )
        row2.addWidget(
            self._make_field("وضعیت", self.status_combo), 1
        )
        bv.addLayout(row2)

        content_layout.addWidget(basic)

        # ── گروه مشخصات فنی ──
        tech = QGroupBox("مشخصات فنی")
        tech.setObjectName("formGroup")
        tv = QVBoxLayout(tech)
        tv.setContentsMargins(14, 20, 14, 14)
        tv.setSpacing(12)

        row3 = QHBoxLayout()
        row3.setSpacing(12)

        self.weight_spin = QDoubleSpinBox()
        self.weight_spin.setRange(0, 99999)
        self.weight_spin.setDecimals(3)
        self.weight_spin.setSpecialValueText("—")
        self.weight_spin.setSuffix(" kg")
        self.weight_spin.setMinimumHeight(36)
        row3.addWidget(
            self._make_field("وزن تقریبی", self.weight_spin), 1
        )

        self.cycle_time_spin = QSpinBox()
        self.cycle_time_spin.setRange(0, 99999)
        self.cycle_time_spin.setSpecialValueText("—")
        self.cycle_time_spin.setSuffix(" دقیقه")
        self.cycle_time_spin.setMinimumHeight(36)
        row3.addWidget(
            self._make_field("زمان ساخت استاندارد", self.cycle_time_spin), 1
        )
        tv.addLayout(row3)

        content_layout.addWidget(tech)

        # ── توضیحات ──
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("توضیحات کلی دستگاه...")
        self.description_input.setMinimumHeight(80)
        self.description_input.setMaximumHeight(110)
        content_layout.addWidget(
            self._make_field("توضیحات", self.description_input)
        )

        self.tech_notes_input = QTextEdit()
        self.tech_notes_input.setPlaceholderText(
            "نکات مهندسی، استانداردها، محدودیت‌ها..."
        )
        self.tech_notes_input.setMinimumHeight(80)
        self.tech_notes_input.setMaximumHeight(110)
        content_layout.addWidget(
            self._make_field("نکات مهندسی", self.tech_notes_input)
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
        save_btn.setObjectName("neonButton")
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

    def _make_field(
        self, label_text: str, widget: QWidget, required: bool = False
    ) -> QWidget:
        wrapper = QWidget()
        v = QVBoxLayout(wrapper)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(6)
        lbl = QLabel(f"{label_text} *" if required else label_text)
        lbl.setObjectName("fieldLabel")
        lbl.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        v.addWidget(lbl)
        v.addWidget(widget)
        return wrapper

    def _load_data(self):
        try:
            with get_session() as session:
                svc = DeviceTemplateService(session)
                t = svc.get_by_id(self.template_id)
                if not t:
                    raise ValueError("قالب یافت نشد")

                self.code_input.setText(t.code)
                self.name_input.setText(t.name or "")

                if t.template_type:
                    self.type_combo.set_current_code(t.template_type)

                self.revision_spin.setValue(t.revision_no or 1)

                if t.default_uom:
                    self.uom_combo.set_current_code(t.default_uom)

                idx = self.status_combo.findData(t.status)
                if idx >= 0:
                    self.status_combo.setCurrentIndex(idx)

                if t.estimated_weight:
                    self.weight_spin.setValue(float(t.estimated_weight))

                if t.estimated_cycle_time:
                    self.cycle_time_spin.setValue(t.estimated_cycle_time)

                if t.description:
                    self.description_input.setPlainText(t.description)

                if t.technical_notes:
                    self.tech_notes_input.setPlainText(t.technical_notes)

        except Exception as e:
            logger.error(f"خطا در بارگذاری قالب: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _collect_data(self) -> dict:
        weight_val = self.weight_spin.value()
        cycle_val = self.cycle_time_spin.value()

        return {
            "code": self.code_input.text().strip() or None,
            "name": self.name_input.text().strip(),
            "template_type": self.type_combo.get_current_code() or None,
            "revision_no": self.revision_spin.value(),
            "default_uom": self.uom_combo.get_current_code() or None,
            "estimated_weight": weight_val if weight_val > 0 else None,
            "estimated_cycle_time": cycle_val if cycle_val > 0 else None,
            "description": (
                self.description_input.toPlainText().strip() or None
            ),
            "technical_notes": (
                self.tech_notes_input.toPlainText().strip() or None
            ),
        }

    def _validate(self, data: dict) -> str | None:
        if not data.get("name"):
            return "نام دستگاه الزامی است"
        if len(data["name"]) < 2:
            return "نام دستگاه باید حداقل ۲ کاراکتر باشد"
        return None

    def _on_save(self):
        try:
            data = self._collect_data()
            error = self._validate(data)
            if error:
                Toast.warning(self, error)
                return

            with get_session() as session:
                svc = DeviceTemplateService(session)
                if self.is_edit:
                    data["status"] = self.status_combo.currentData()
                    # کد در ویرایش تغییر نمی‌کنه
                    data.pop("code", None)
                    svc.update(
                        self.template_id,
                        DeviceTemplateUpdate(**data),
                    )
                else:
                    svc.create(DeviceTemplateCreate(**data))

            self.accept()

        except ValueError as e:
            Toast.warning(self, str(e))
        except Exception as e:
            logger.error(f"خطا در ذخیره: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")