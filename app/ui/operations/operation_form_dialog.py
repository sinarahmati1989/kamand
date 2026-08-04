"""
دیالوگ افزودن/ویرایش عملیات ساخت
"""

from decimal import Decimal
import logging

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QCheckBox, QTextEdit,
    QPushButton, QWidget, QGroupBox, QDoubleSpinBox, QSpinBox,
    QScrollArea, QFrame, QTabWidget
)
from PySide6.QtCore import Qt

from app.services.manufacturing_operation_service import ManufacturingOperationService
from app.schemas.manufacturing_operation_schema import (
    ManufacturingOperationCreate, ManufacturingOperationUpdate
)
from app.database.session import get_session
from app.enums.operation_enums import OperationStatus
from app.enums.lookup_categories import LookupCategory
from app.ui.widgets.lookup_combo_with_add import LookupComboBoxWithAdd
from app.ui.widgets.toast import Toast

logger = logging.getLogger(__name__)


class OperationFormDialog(QDialog):
    """فرم افزودن/ویرایش عملیات ساخت"""

    def __init__(self, operation_id: int | None = None, parent=None):
        super().__init__(parent)
        self.operation_id = operation_id
        self.is_edit = operation_id is not None

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowTitle("ویرایش عملیات ساخت" if self.is_edit else "افزودن عملیات ساخت جدید")
        self.setMinimumSize(760, 720)
        self.resize(820, 760)

        self._setup_ui()

        if self.is_edit:
            self._load_data()

    # ---------- Setup ----------

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title_text = "ویرایش عملیات ساخت" if self.is_edit else "افزودن عملیات ساخت جدید"
        title = QLabel(title_text)
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # کد در حالت ویرایش
        if self.is_edit:
            code_row = QHBoxLayout()
            code_lbl = QLabel("کد عملیات:")
            code_lbl.setObjectName("fieldLabel")

            self.code_label = QLabel("—")
            self.code_label.setStyleSheet(
                "color: #6366F1; font-weight: bold; font-size: 14px; "
                "padding: 6px 12px; background: rgba(255,255,255,0.85); "
                "border: 1.5px solid rgba(99,102,241,0.25); border-radius: 8px;"
            )

            code_row.addWidget(code_lbl)
            code_row.addWidget(self.code_label)
            code_row.addStretch()
            layout.addLayout(code_row)

        # تب‌ها
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_basic_tab(), "اطلاعات پایه")
        self.tabs.addTab(self._build_time_tab(), "زمان و ظرفیت")
        self.tabs.addTab(self._build_cost_tab(), "هزینه و مهارت")
        self.tabs.addTab(self._build_notes_tab(), "یادداشت‌ها")
        layout.addWidget(self.tabs, 1)

        # دکمه‌ها
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        save_btn = QPushButton("ذخیره")
        save_btn.setObjectName("neonButton")
        save_btn.setFixedSize(140, 42)
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

    # ---------- Helper ----------

    def _make_field(self, label_text: str, widget: QWidget, required: bool = False) -> QWidget:
        wrapper = QWidget()
        v = QVBoxLayout(wrapper)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(6)

        label_full = f"{label_text} *" if required else label_text
        lbl = QLabel(label_full)
        lbl.setObjectName("fieldLabel")
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        v.addWidget(lbl)
        v.addWidget(widget)
        return wrapper

    def _wrap_scroll(self, content: QWidget) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(content)
        return scroll

    # ---------- Tab 1: Basic ----------

    def _build_basic_tab(self) -> QScrollArea:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # ردیف بالا: نام + نوع
        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("مثال: تراشکاری بیرونی محور")
        self.name_input.setMinimumHeight(36)
        top_row.addWidget(self._make_field("نام عملیات", self.name_input, required=True), 2)

        self.type_combo = LookupComboBoxWithAdd(LookupCategory.OPERATION_TYPE.value)
        self.type_combo.setMinimumHeight(36)
        top_row.addWidget(self._make_field("نوع عملیات", self.type_combo, required=True), 1)

        layout.addLayout(top_row)

        # توضیحات
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("توضیحات کامل عملیات...")
        self.description_input.setMinimumHeight(90)
        self.description_input.setMaximumHeight(120)
        layout.addWidget(self._make_field("توضیحات", self.description_input))

        # ویژگی‌ها
        features_group = QGroupBox("ویژگی‌های عملیات")
        features_group.setObjectName("formGroup")
        fv = QVBoxLayout(features_group)
        fv.setContentsMargins(14, 20, 14, 14)
        fv.setSpacing(10)

        self.outsourced_cb = QCheckBox("این عملیات برون‌سپاری می‌شود")
        self.outsourced_cb.setMinimumHeight(28)
        fv.addWidget(self.outsourced_cb)

        self.qc_cb = QCheckBox("پس از عملیات نیاز به کنترل کیفیت دارد")
        self.qc_cb.setMinimumHeight(28)
        fv.addWidget(self.qc_cb)

        self.machine_cb = QCheckBox("نیاز به ماشین دارد (اگر خیر، عملیات دستی است)")
        self.machine_cb.setMinimumHeight(28)
        self.machine_cb.setChecked(True)
        fv.addWidget(self.machine_cb)

        self.bottleneck_cb = QCheckBox("این عملیات گلوگاه تولید است")
        self.bottleneck_cb.setMinimumHeight(28)
        fv.addWidget(self.bottleneck_cb)

        layout.addWidget(features_group)

        # وضعیت
        status_row = QHBoxLayout()
        self.status_combo = QComboBox()
        self.status_combo.setMinimumHeight(36)
        for st in OperationStatus:
            self.status_combo.addItem(st.label, st.value)

        if not self.is_edit:
            self.status_combo.setCurrentIndex(0)
            self.status_combo.setEnabled(False)
            self.status_combo.setToolTip("وضعیت رکورد جدید به‌صورت پیش‌فرض «فعال» ثبت می‌شود.")

        status_row.addWidget(self._make_field("وضعیت", self.status_combo))
        status_row.addStretch()
        layout.addLayout(status_row)

        layout.addStretch(1)
        return self._wrap_scroll(content)

    # ---------- Tab 2: Time & Capacity ----------

    def _build_time_tab(self) -> QScrollArea:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # زمان‌ها
        time_group = QGroupBox("زمان‌های عملیات")
        time_group.setObjectName("formGroup")
        tv = QVBoxLayout(time_group)
        tv.setContentsMargins(14, 20, 14, 14)
        tv.setSpacing(12)

        # Setup Time
        setup_row = QHBoxLayout()
        setup_row.setSpacing(12)

        self.setup_time_input = QDoubleSpinBox()
        self.setup_time_input.setRange(0, 99999)
        self.setup_time_input.setDecimals(2)
        self.setup_time_input.setSpecialValueText("—")
        self.setup_time_input.setMinimumHeight(36)
        setup_row.addWidget(self._make_field("زمان راه‌اندازی", self.setup_time_input), 2)

        self.setup_unit_combo = LookupComboBoxWithAdd(LookupCategory.TIME_UNIT.value)
        self.setup_unit_combo.setMinimumHeight(36)
        self.setup_unit_combo.set_current_code("minute")
        setup_row.addWidget(self._make_field("واحد", self.setup_unit_combo), 1)

        tv.addLayout(setup_row)

        # Cycle Time
        cycle_row = QHBoxLayout()
        cycle_row.setSpacing(12)

        self.cycle_time_input = QDoubleSpinBox()
        self.cycle_time_input.setRange(0, 99999)
        self.cycle_time_input.setDecimals(2)
        self.cycle_time_input.setSpecialValueText("—")
        self.cycle_time_input.setMinimumHeight(36)
        cycle_row.addWidget(self._make_field("زمان تولید یک قطعه", self.cycle_time_input), 2)

        self.cycle_unit_combo = LookupComboBoxWithAdd(LookupCategory.TIME_UNIT.value)
        self.cycle_unit_combo.setMinimumHeight(36)
        self.cycle_unit_combo.set_current_code("minute")
        cycle_row.addWidget(self._make_field("واحد", self.cycle_unit_combo), 1)

        tv.addLayout(cycle_row)
        layout.addWidget(time_group)

        # ظرفیت و راندمان
        cap_group = QGroupBox("ظرفیت و راندمان")
        cap_group.setObjectName("formGroup")
        cv = QVBoxLayout(cap_group)
        cv.setContentsMargins(14, 20, 14, 14)
        cv.setSpacing(12)

        row1 = QHBoxLayout()
        row1.setSpacing(12)

        self.capacity_input = QDoubleSpinBox()
        self.capacity_input.setRange(0, 999999)
        self.capacity_input.setDecimals(2)
        self.capacity_input.setSpecialValueText("—")
        self.capacity_input.setMinimumHeight(36)
        row1.addWidget(self._make_field("ظرفیت در ساعت (قطعه)", self.capacity_input), 1)

        self.operator_input = QSpinBox()
        self.operator_input.setRange(1, 99)
        self.operator_input.setValue(1)
        self.operator_input.setMinimumHeight(36)
        row1.addWidget(self._make_field("تعداد اپراتور پیش‌فرض", self.operator_input), 1)

        cv.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(12)

        self.efficiency_input = QDoubleSpinBox()
        self.efficiency_input.setRange(0, 100)
        self.efficiency_input.setDecimals(2)
        self.efficiency_input.setSuffix(" %")
        self.efficiency_input.setSpecialValueText("—")
        self.efficiency_input.setMinimumHeight(36)
        row2.addWidget(self._make_field("راندمان (%)", self.efficiency_input), 1)

        self.oee_input = QDoubleSpinBox()
        self.oee_input.setRange(0, 100)
        self.oee_input.setDecimals(2)
        self.oee_input.setSuffix(" %")
        self.oee_input.setSpecialValueText("—")
        self.oee_input.setMinimumHeight(36)
        row2.addWidget(self._make_field("هدف OEE (%)", self.oee_input), 1)

        cv.addLayout(row2)
        layout.addWidget(cap_group)

        layout.addStretch(1)
        return self._wrap_scroll(content)

    # ---------- Tab 3: Cost & Skill ----------

    def _build_cost_tab(self) -> QScrollArea:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # هزینه
        cost_group = QGroupBox("هزینه عملیات")
        cost_group.setObjectName("formGroup")
        cv = QVBoxLayout(cost_group)
        cv.setContentsMargins(14, 20, 14, 14)
        cv.setSpacing(12)

        cost_row = QHBoxLayout()
        cost_row.setSpacing(12)

        self.hourly_rate_input = QDoubleSpinBox()
        self.hourly_rate_input.setRange(0, 999_999_999_999)
        self.hourly_rate_input.setDecimals(0)
        self.hourly_rate_input.setGroupSeparatorShown(True)
        self.hourly_rate_input.setSpecialValueText("—")
        self.hourly_rate_input.setMinimumHeight(36)
        cost_row.addWidget(self._make_field("نرخ ساعتی", self.hourly_rate_input), 2)

        self.currency_combo = LookupComboBoxWithAdd(LookupCategory.CURRENCY.value)
        self.currency_combo.setMinimumHeight(36)
        self.currency_combo.set_current_code("irr")
        cost_row.addWidget(self._make_field("ارز", self.currency_combo), 1)

        cv.addLayout(cost_row)
        layout.addWidget(cost_group)

        # مهارت
        skill_group = QGroupBox("مهارت لازم")
        skill_group.setObjectName("formGroup")
        sv = QVBoxLayout(skill_group)
        sv.setContentsMargins(14, 20, 14, 14)
        sv.setSpacing(12)

        self.skill_combo = LookupComboBoxWithAdd(
            LookupCategory.SKILL_LEVEL.value,
            allow_empty=True
        )
        self.skill_combo.setMinimumHeight(36)
        sv.addWidget(self._make_field("سطح مهارت", self.skill_combo))

        self.skill_desc_input = QTextEdit()
        self.skill_desc_input.setPlaceholderText(
            "توضیح مهارت‌های لازم برای این عملیات...\n"
            "مثال: آشنایی با برنامه‌نویسی CNC، خواندن نقشه فنی"
        )
        self.skill_desc_input.setMinimumHeight(80)
        self.skill_desc_input.setMaximumHeight(120)
        sv.addWidget(self._make_field("توضیح مهارت‌ها", self.skill_desc_input))

        layout.addWidget(skill_group)

        layout.addStretch(1)
        return self._wrap_scroll(content)

    # ---------- Tab 4: Notes ----------

    def _build_notes_tab(self) -> QScrollArea:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        self.tools_input = QTextEdit()
        self.tools_input.setPlaceholderText("ابزار و تجهیزات لازم برای این عملیات...")
        self.tools_input.setMinimumHeight(80)
        self.tools_input.setMaximumHeight(110)
        layout.addWidget(self._make_field("ابزار لازم", self.tools_input))

        self.safety_input = QTextEdit()
        self.safety_input.setPlaceholderText(
            "نکات ایمنی...\n"
            "مثال: استفاده از عینک ایمنی، دستکش نسوز، ماسک"
        )
        self.safety_input.setMinimumHeight(80)
        self.safety_input.setMaximumHeight(110)
        layout.addWidget(self._make_field("نکات ایمنی", self.safety_input))

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("یادداشت‌های اضافی...")
        self.notes_input.setMinimumHeight(80)
        self.notes_input.setMaximumHeight(110)
        layout.addWidget(self._make_field("یادداشت‌ها", self.notes_input))

        layout.addStretch(1)
        return self._wrap_scroll(content)

    # ---------- Load Data ----------

    def _load_data(self):
        try:
            with get_session() as session:
                svc = ManufacturingOperationService(session)
                op = svc.get_by_id(self.operation_id)

                if not op:
                    raise ValueError("عملیات یافت نشد")

                self.code_label.setText(op.code)

                # Tab 1
                self.name_input.setText(op.name or "")
                self.type_combo.set_current_code(op.operation_type)
                if op.description:
                    self.description_input.setPlainText(op.description)

                self.outsourced_cb.setChecked(bool(op.is_outsourced))
                self.qc_cb.setChecked(bool(op.requires_qc))
                self.machine_cb.setChecked(bool(op.requires_machine))
                self.bottleneck_cb.setChecked(bool(op.is_bottleneck))

                if op.status:
                    idx = self.status_combo.findData(op.status)
                    if idx >= 0:
                        self.status_combo.setCurrentIndex(idx)

                # Tab 2
                if op.setup_time is not None:
                    self.setup_time_input.setValue(float(op.setup_time))
                self.setup_unit_combo.set_current_code(op.setup_time_unit or "minute")

                if op.cycle_time is not None:
                    self.cycle_time_input.setValue(float(op.cycle_time))
                self.cycle_unit_combo.set_current_code(op.cycle_time_unit or "minute")

                if op.capacity_per_hour is not None:
                    self.capacity_input.setValue(float(op.capacity_per_hour))
                self.operator_input.setValue(op.default_operator_count or 1)

                if op.efficiency_percent is not None:
                    self.efficiency_input.setValue(float(op.efficiency_percent))
                if op.oee_target is not None:
                    self.oee_input.setValue(float(op.oee_target))

                # Tab 3
                if op.hourly_rate is not None:
                    self.hourly_rate_input.setValue(float(op.hourly_rate))
                self.currency_combo.set_current_code(op.currency or "irr")

                if op.skill_level:
                    self.skill_combo.set_current_code(op.skill_level)
                if op.required_skills_description:
                    self.skill_desc_input.setPlainText(op.required_skills_description)

                # Tab 4
                if op.required_tools:
                    self.tools_input.setPlainText(op.required_tools)
                if op.safety_notes:
                    self.safety_input.setPlainText(op.safety_notes)
                if op.notes:
                    self.notes_input.setPlainText(op.notes)

        except Exception as e:
            logger.error(f"خطا در بارگذاری عملیات: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    # ---------- Collect & Save ----------

    def _collect_data(self) -> dict:
        setup_val = self.setup_time_input.value()
        cycle_val = self.cycle_time_input.value()
        capacity_val = self.capacity_input.value()
        efficiency_val = self.efficiency_input.value()
        oee_val = self.oee_input.value()
        hourly_val = self.hourly_rate_input.value()

        skill_code = self.skill_combo.get_current_code()

        return {
            "name": self.name_input.text().strip(),
            "operation_type": self.type_combo.get_current_code(),
            "description": self.description_input.toPlainText().strip() or None,

            "is_outsourced": self.outsourced_cb.isChecked(),
            "requires_qc": self.qc_cb.isChecked(),
            "requires_machine": self.machine_cb.isChecked(),
            "is_bottleneck": self.bottleneck_cb.isChecked(),

            "setup_time": Decimal(str(setup_val)) if setup_val > 0 else None,
            "setup_time_unit": self.setup_unit_combo.get_current_code() or "minute",
            "cycle_time": Decimal(str(cycle_val)) if cycle_val > 0 else None,
            "cycle_time_unit": self.cycle_unit_combo.get_current_code() or "minute",

            "capacity_per_hour": Decimal(str(capacity_val)) if capacity_val > 0 else None,
            "default_operator_count": self.operator_input.value(),
            "efficiency_percent": Decimal(str(efficiency_val)) if efficiency_val > 0 else None,
            "oee_target": Decimal(str(oee_val)) if oee_val > 0 else None,

            "hourly_rate": Decimal(str(hourly_val)) if hourly_val > 0 else None,
            "currency": self.currency_combo.get_current_code() or "irr",

            "skill_level": skill_code if skill_code else None,
            "required_skills_description": self.skill_desc_input.toPlainText().strip() or None,

            "required_tools": self.tools_input.toPlainText().strip() or None,
            "safety_notes": self.safety_input.toPlainText().strip() or None,
            "notes": self.notes_input.toPlainText().strip() or None,
        }

    def _validate(self, data: dict) -> str | None:
        if not data.get("name"):
            return "نام عملیات الزامی است"
        if len(data["name"]) < 2:
            return "نام عملیات باید حداقل ۲ کاراکتر باشد"
        if not data.get("operation_type"):
            return "انتخاب نوع عملیات الزامی است"
        return None

    def _on_save(self):
        try:
            data = self._collect_data()

            error = self._validate(data)
            if error:
                Toast.warning(self, error)
                return

            with get_session() as session:
                svc = ManufacturingOperationService(session)

                if self.is_edit:
                    data["status"] = self.status_combo.currentData()
                    schema = ManufacturingOperationUpdate(**data)
                    svc.update(self.operation_id, schema)
                else:
                    schema = ManufacturingOperationCreate(**data)
                    svc.create(schema)

            self.accept()

        except ValueError as e:
            Toast.warning(self, str(e))
        except Exception as e:
            logger.error(f"خطا در ذخیره عملیات: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")