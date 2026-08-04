"""
دیالوگ افزودن/ویرایش ماشین‌آلات
"""
import logging
from decimal import Decimal

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QTextEdit,
    QPushButton, QWidget, QGroupBox,
    QScrollArea, QFrame, QDoubleSpinBox, QSpinBox,
    QTabWidget,
)
from PySide6.QtCore import Qt

from app.services.machine_service import MachineService
from app.services.department_service import DepartmentService
from app.services.work_center_service import WorkCenterService
from app.schemas.machine_schema import MachineCreate, MachineUpdate
from app.database.session import get_session
from app.enums.machine_enums import MachineStatus
from app.enums.lookup_categories import LookupCategory
from app.ui.widgets.lookup_combo_with_add import LookupComboBoxWithAdd
from app.ui.widgets.persian_date_edit import PersianDateEdit
from app.ui.widgets.toast import Toast

logger = logging.getLogger(__name__)


class MachineFormDialog(QDialog):
    """فرم افزودن/ویرایش ماشین‌آلات"""

    def __init__(self, machine_id: int | None = None, parent=None):
        super().__init__(parent)
        self.machine_id = machine_id
        self.is_edit = machine_id is not None

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowTitle(
            "ویرایش ماشین" if self.is_edit else "افزودن ماشین جدید"
        )
        self.setMinimumSize(720, 680)
        self.resize(760, 720)

        self._setup_ui()

        if self.is_edit:
            self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title_text = "ویرایش ماشین" if self.is_edit else "افزودن ماشین جدید"
        title = QLabel(title_text)
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        if self.is_edit:
            code_row = QHBoxLayout()
            code_lbl = QLabel("کد ماشین:")
            code_lbl.setObjectName("fieldLabel")
            self.code_label = QLabel("—")
            self.code_label.setStyleSheet(
                "color: #6366F1; font-weight: bold; font-size: 14px;"
                "padding: 6px 12px; background: rgba(255,255,255,0.85);"
                "border: 1.5px solid rgba(99,102,241,0.25); border-radius: 8px;"
            )
            code_row.addWidget(code_lbl)
            code_row.addWidget(self.code_label)
            code_row.addStretch()
            layout.addLayout(code_row)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_basic_tab(), "اطلاعات پایه")
        self.tabs.addTab(self._build_location_tab(), "موقعیت و ظرفیت")
        self.tabs.addTab(self._build_maintenance_tab(), "سرویس و نگهداری")
        layout.addWidget(self.tabs, 1)

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

    def _make_field(self, label_text: str, widget: QWidget, required: bool = False) -> QWidget:
        wrapper = QWidget()
        v = QVBoxLayout(wrapper)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(6)

        lbl = QLabel(f"{label_text} *" if required else label_text)
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

    # ──────────────────────────────────────────────────────────
    # Tab 1: اطلاعات پایه
    # ──────────────────────────────────────────────────────────

    def _build_basic_tab(self) -> QScrollArea:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        row1 = QHBoxLayout()
        row1.setSpacing(12)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("مثال: تراش CNC شماره ۱، دستگاه جوش MIG")
        self.name_input.setMinimumHeight(36)
        row1.addWidget(self._make_field("نام ماشین", self.name_input, required=True), 2)

        self.type_combo = LookupComboBoxWithAdd(
            LookupCategory.MACHINE_TYPE.value,
            allow_empty=True
        )
        self.type_combo.setMinimumHeight(36)
        row1.addWidget(self._make_field("نوع ماشین", self.type_combo), 1)

        layout.addLayout(row1)

        spec_group = QGroupBox("مشخصات دستگاه")
        spec_group.setObjectName("formGroup")
        sv = QVBoxLayout(spec_group)
        sv.setContentsMargins(14, 20, 14, 14)
        sv.setSpacing(12)

        row2 = QHBoxLayout()
        row2.setSpacing(12)

        self.brand_input = QLineEdit()
        self.brand_input.setPlaceholderText("مثال: HAAS، Mazak، Fanuc")
        self.brand_input.setMinimumHeight(36)
        row2.addWidget(self._make_field("برند/سازنده", self.brand_input), 1)

        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("مدل دستگاه")
        self.model_input.setMinimumHeight(36)
        row2.addWidget(self._make_field("مدل", self.model_input), 1)

        sv.addLayout(row2)

        row3 = QHBoxLayout()
        row3.setSpacing(12)

        self.serial_input = QLineEdit()
        self.serial_input.setPlaceholderText("شماره سریال")
        self.serial_input.setMinimumHeight(36)
        row3.addWidget(self._make_field("شماره سریال", self.serial_input), 2)

        self.year_spin = QSpinBox()
        self.year_spin.setRange(1900, 2100)
        self.year_spin.setSpecialValueText("—")
        self.year_spin.setValue(1900)
        self.year_spin.setMinimumHeight(36)
        self.year_spin.setToolTip("در صورت نیاز سال ساخت را وارد کنید")
        row3.addWidget(self._make_field("سال ساخت", self.year_spin), 1)

        sv.addLayout(row3)
        layout.addWidget(spec_group)

        self.status_combo = QComboBox()
        self.status_combo.setMinimumHeight(36)
        for st in MachineStatus:
            self.status_combo.addItem(st.label, st.value)

        if not self.is_edit:
            self.status_combo.setEnabled(False)
            self.status_combo.setToolTip(
                "وضعیت رکورد جدید به‌صورت پیش‌فرض «فعال» ثبت می‌شود."
            )

        status_row = QHBoxLayout()
        status_row.addWidget(self._make_field("وضعیت", self.status_combo))
        status_row.addStretch()
        layout.addLayout(status_row)

        layout.addStretch(1)
        return self._wrap_scroll(content)

    # ──────────────────────────────────────────────────────────
    # Tab 2: موقعیت و ظرفیت
    # ──────────────────────────────────────────────────────────

    def _build_location_tab(self) -> QScrollArea:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        loc_group = QGroupBox("موقعیت در کارگاه")
        loc_group.setObjectName("formGroup")
        lv = QVBoxLayout(loc_group)
        lv.setContentsMargins(14, 20, 14, 14)
        lv.setSpacing(12)

        self.dept_combo = QComboBox()
        self.dept_combo.setMinimumHeight(36)
        self.dept_combo.currentIndexChanged.connect(self._on_dept_changed)
        self._load_departments()
        lv.addWidget(self._make_field("دپارتمان", self.dept_combo))

        self.wc_combo = QComboBox()
        self.wc_combo.setMinimumHeight(36)
        self._load_work_centers(department_id=None)
        lv.addWidget(self._make_field("مرکز کار", self.wc_combo))

        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("مثال: سالن A، ردیف ۲، جایگاه ۵")
        self.location_input.setMinimumHeight(36)
        lv.addWidget(self._make_field("موقعیت دقیق", self.location_input))

        layout.addWidget(loc_group)

        cap_group = QGroupBox("ظرفیت و نرخ ساعتی")
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
        row1.addWidget(
            self._make_field("ظرفیت تولید در ساعت", self.capacity_input), 1
        )

        cv.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(12)

        self.hourly_rate_input = QDoubleSpinBox()
        self.hourly_rate_input.setRange(0, 999_999_999)
        self.hourly_rate_input.setDecimals(0)
        self.hourly_rate_input.setGroupSeparatorShown(True)
        self.hourly_rate_input.setSpecialValueText("—")
        self.hourly_rate_input.setMinimumHeight(36)
        row2.addWidget(self._make_field("نرخ ساعتی", self.hourly_rate_input), 2)

        self.currency_combo = LookupComboBoxWithAdd(LookupCategory.CURRENCY.value)
        self.currency_combo.setMinimumHeight(36)
        self.currency_combo.set_current_code("irr")
        row2.addWidget(self._make_field("ارز", self.currency_combo), 1)

        cv.addLayout(row2)
        layout.addWidget(cap_group)

        layout.addStretch(1)
        return self._wrap_scroll(content)

    # ──────────────────────────────────────────────────────────
    # Tab 3: سرویس و نگهداری
    # ──────────────────────────────────────────────────────────

    def _build_maintenance_tab(self) -> QScrollArea:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        maint_group = QGroupBox("برنامه سرویس دوره‌ای")
        maint_group.setObjectName("formGroup")
        mv = QVBoxLayout(maint_group)
        mv.setContentsMargins(14, 20, 14, 14)
        mv.setSpacing(12)

        row1 = QHBoxLayout()
        row1.setSpacing(12)

        self.last_maint_date = PersianDateEdit()
        self.last_maint_date.setToolTip("تاریخ آخرین سرویس به‌صورت شمسی")
        row1.addWidget(
            self._make_field("تاریخ آخرین سرویس", self.last_maint_date), 1
        )

        self.next_maint_date = PersianDateEdit()
        self.next_maint_date.setToolTip("تاریخ سرویس بعدی به‌صورت شمسی")
        row1.addWidget(
            self._make_field("تاریخ سرویس بعدی", self.next_maint_date), 1
        )

        mv.addLayout(row1)

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(0, 3650)
        self.interval_spin.setValue(0)
        self.interval_spin.setSpecialValueText("—")
        self.interval_spin.setSuffix(" روز")
        self.interval_spin.setMinimumHeight(36)

        interval_row = QHBoxLayout()
        interval_row.addWidget(
            self._make_field("فاصله سرویس‌دهی", self.interval_spin)
        )
        interval_row.addStretch()
        mv.addLayout(interval_row)

        layout.addWidget(maint_group)

        self.tech_notes_input = QTextEdit()
        self.tech_notes_input.setPlaceholderText(
            "مشخصات فنی ماشین...\n"
            "مثال: توان موتور ۱۵ کیلووات، دور ماکزیمم ۶۰۰۰ RPM، ابعاد ۲×۳ متر"
        )
        self.tech_notes_input.setMinimumHeight(90)
        self.tech_notes_input.setMaximumHeight(130)
        layout.addWidget(self._make_field("مشخصات فنی", self.tech_notes_input))

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText(
            "یادداشت‌های سرویس، تعمیرات یا نکات مهم...\n"
            "مثال: تعویض بلبرینگ در مهر ۱۴۰۳، نیاز به بررسی دوره‌ای سیستم خنک‌کننده"
        )
        self.notes_input.setMinimumHeight(80)
        self.notes_input.setMaximumHeight(110)
        layout.addWidget(self._make_field("یادداشت‌ها", self.notes_input))

        layout.addStretch(1)
        return self._wrap_scroll(content)

    # ──────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────

    def _load_departments(self):
        self.dept_combo.clear()
        self.dept_combo.addItem("— انتخاب دپارتمان —", None)
        try:
            with get_session() as session:
                svc = DepartmentService(session)
                depts = svc.get_active_list()
            for dept in depts:
                self.dept_combo.addItem(f"{dept.code} — {dept.name}", dept.id)
        except Exception as e:
            logger.error(f"خطا در بارگذاری دپارتمان‌ها: {e}")

    def _load_work_centers(self, department_id: int | None):
        self.wc_combo.clear()
        self.wc_combo.addItem("— انتخاب مرکز کار —", None)
        try:
            with get_session() as session:
                svc = WorkCenterService(session)
                if department_id:
                    wcs = svc.get_by_department(department_id)
                else:
                    wcs = svc.get_active_list()
            for wc in wcs:
                self.wc_combo.addItem(f"{wc.code} — {wc.name}", wc.id)
        except Exception as e:
            logger.error(f"خطا در بارگذاری مراکز کار: {e}")

    def _on_dept_changed(self, _idx: int):
        dept_id = self.dept_combo.currentData()
        self._load_work_centers(dept_id)

    def _load_data(self):
        try:
            with get_session() as session:
                svc = MachineService(session)
                machine = svc.get_by_id(self.machine_id)
                if not machine:
                    raise ValueError("ماشین یافت نشد")

                # Tab 1
                self.code_label.setText(machine.code)
                self.name_input.setText(machine.name or "")
                if machine.machine_type:
                    self.type_combo.set_current_code(machine.machine_type)
                self.brand_input.setText(machine.brand or "")
                self.model_input.setText(machine.model or "")
                self.serial_input.setText(machine.serial_number or "")
                if machine.manufacture_year:
                    self.year_spin.setValue(machine.manufacture_year)
                else:
                    self.year_spin.setValue(1900)

                idx = self.status_combo.findData(machine.status)
                if idx >= 0:
                    self.status_combo.setCurrentIndex(idx)

                # Tab 2
                if machine.department_id:
                    dept_idx = self.dept_combo.findData(machine.department_id)
                    if dept_idx >= 0:
                        self.dept_combo.setCurrentIndex(dept_idx)
                        self._load_work_centers(machine.department_id)

                if machine.work_center_id:
                    wc_idx = self.wc_combo.findData(machine.work_center_id)
                    if wc_idx >= 0:
                        self.wc_combo.setCurrentIndex(wc_idx)

                self.location_input.setText(machine.location or "")

                if machine.capacity_per_hour is not None:
                    self.capacity_input.setValue(float(machine.capacity_per_hour))

                if machine.hourly_rate is not None:
                    self.hourly_rate_input.setValue(float(machine.hourly_rate))

                self.currency_combo.set_current_code(machine.currency or "irr")

                # Tab 3
                self.last_maint_date.set_date(machine.last_maintenance_date)
                self.next_maint_date.set_date(machine.next_maintenance_date)

                if machine.maintenance_interval_days:
                    self.interval_spin.setValue(machine.maintenance_interval_days)
                else:
                    self.interval_spin.setValue(0)

                if machine.technical_notes:
                    self.tech_notes_input.setPlainText(machine.technical_notes)

                if machine.notes:
                    self.notes_input.setPlainText(machine.notes)

        except Exception as e:
            logger.error(f"خطا در بارگذاری ماشین: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _collect_data(self) -> dict:
        cap_val = self.capacity_input.value()
        rate_val = self.hourly_rate_input.value()
        interval_val = self.interval_spin.value()
        year_val = self.year_spin.value()

        return {
            "name": self.name_input.text().strip(),
            "machine_type": self.type_combo.get_current_code() or None,
            "brand": self.brand_input.text().strip() or None,
            "model": self.model_input.text().strip() or None,
            "serial_number": self.serial_input.text().strip() or None,
            "manufacture_year": year_val if year_val > 1900 else None,
            "department_id": self.dept_combo.currentData(),
            "work_center_id": self.wc_combo.currentData(),
            "location": self.location_input.text().strip() or None,
            "capacity_per_hour": Decimal(str(cap_val)) if cap_val > 0 else None,
            "hourly_rate": Decimal(str(rate_val)) if rate_val > 0 else None,
            "currency": self.currency_combo.get_current_code() or "irr",
            "last_maintenance_date": self.last_maint_date.get_date(),
            "next_maintenance_date": self.next_maint_date.get_date(),
            "maintenance_interval_days": interval_val if interval_val > 0 else None,
            "technical_notes": self.tech_notes_input.toPlainText().strip() or None,
            "notes": self.notes_input.toPlainText().strip() or None,
        }

    def _validate(self, data: dict) -> str | None:
        if not data.get("name"):
            return "نام ماشین الزامی است"
        if len(data["name"]) < 2:
            return "نام ماشین باید حداقل ۲ کاراکتر باشد"

        last_date = data.get("last_maintenance_date")
        next_date = data.get("next_maintenance_date")
        if last_date and next_date and next_date < last_date:
            return "تاریخ سرویس بعدی نمی‌تواند قبل از تاریخ آخرین سرویس باشد"

        return None

    def _on_save(self):
        try:
            data = self._collect_data()
            error = self._validate(data)
            if error:
                Toast.warning(self, error)
                return

            with get_session() as session:
                svc = MachineService(session)
                if self.is_edit:
                    data["status"] = self.status_combo.currentData()
                    svc.update(self.machine_id, MachineUpdate(**data))
                else:
                    svc.create(MachineCreate(**data))

            self.accept()

        except ValueError as e:
            Toast.warning(self, str(e))
        except Exception as e:
            logger.error(f"خطا در ذخیره ماشین: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")