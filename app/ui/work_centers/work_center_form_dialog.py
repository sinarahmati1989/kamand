"""
دیالوگ افزودن/ویرایش مرکز کار
"""
import logging
from decimal import Decimal

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QTextEdit,
    QPushButton, QWidget, QGroupBox,
    QScrollArea, QFrame, QDoubleSpinBox, QSpinBox,
)
from PySide6.QtCore import Qt

from app.services.work_center_service import WorkCenterService
from app.services.department_service import DepartmentService
from app.schemas.work_center_schema import WorkCenterCreate, WorkCenterUpdate
from app.database.session import get_session
from app.enums.work_center_enums import WorkCenterStatus
from app.enums.lookup_categories import LookupCategory
from app.ui.widgets.lookup_combo_with_add import LookupComboBoxWithAdd
from app.ui.widgets.toast import Toast

logger = logging.getLogger(__name__)


class WorkCenterFormDialog(QDialog):
    """فرم افزودن/ویرایش مرکز کار"""

    def __init__(self, work_center_id: int | None = None, parent=None):
        super().__init__(parent)
        self.work_center_id = work_center_id
        self.is_edit = work_center_id is not None

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowTitle(
            "ویرایش مرکز کار" if self.is_edit else "افزودن مرکز کار جدید"
        )
        self.setMinimumSize(580, 600)
        self.resize(620, 640)

        self._dept_id_map: dict[int, int] = {}  # combo_index → dept.id

        self._setup_ui()

        if self.is_edit:
            self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # عنوان
        title_text = "ویرایش مرکز کار" if self.is_edit else "افزودن مرکز کار جدید"
        title = QLabel(title_text)
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # کد در ویرایش
        if self.is_edit:
            code_row = QHBoxLayout()
            code_lbl = QLabel("کد مرکز کار:")
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

        # Content
        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(16)

        # ── اطلاعات پایه ──
        basic_group = QGroupBox("اطلاعات پایه")
        basic_group.setObjectName("formGroup")
        bv = QVBoxLayout(basic_group)
        bv.setContentsMargins(14, 20, 14, 14)
        bv.setSpacing(12)

        # نام + نوع
        row1 = QHBoxLayout()
        row1.setSpacing(12)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("مثال: مرکز تراشکاری ۱، خط مونتاژ A")
        self.name_input.setMinimumHeight(36)
        row1.addWidget(self._make_field("نام مرکز کار", self.name_input, required=True), 2)

        self.type_combo = LookupComboBoxWithAdd(
            LookupCategory.WORK_CENTER_TYPE.value,
            allow_empty=True
        )
        self.type_combo.setMinimumHeight(36)
        row1.addWidget(self._make_field("نوع", self.type_combo), 1)

        bv.addLayout(row1)

        # دپارتمان
        self.dept_combo = QComboBox()
        self.dept_combo.setMinimumHeight(36)
        self._load_departments()
        bv.addWidget(self._make_field("دپارتمان مربوطه", self.dept_combo))

        cl.addWidget(basic_group)

        # ── ظرفیت و شیفت ──
        cap_group = QGroupBox("ظرفیت و شیفت")
        cap_group.setObjectName("formGroup")
        cv = QVBoxLayout(cap_group)
        cv.setContentsMargins(14, 20, 14, 14)
        cv.setSpacing(12)

        row2 = QHBoxLayout()
        row2.setSpacing(12)

        self.capacity_input = QDoubleSpinBox()
        self.capacity_input.setRange(0, 999999)
        self.capacity_input.setDecimals(2)
        self.capacity_input.setSpecialValueText("—")
        self.capacity_input.setMinimumHeight(36)
        row2.addWidget(
            self._make_field("ظرفیت در ساعت", self.capacity_input), 2
        )

        self.cap_unit_input = QLineEdit()
        self.cap_unit_input.setPlaceholderText("قطعه / کیلوگرم / متر")
        self.cap_unit_input.setMinimumHeight(36)
        row2.addWidget(self._make_field("واحد ظرفیت", self.cap_unit_input), 1)

        cv.addLayout(row2)

        self.shift_spin = QSpinBox()
        self.shift_spin.setRange(1, 5)
        self.shift_spin.setValue(1)
        self.shift_spin.setMinimumHeight(36)
        self.shift_spin.setSuffix(" شیفت")

        shift_row = QHBoxLayout()
        shift_row.addWidget(self._make_field("تعداد شیفت‌های کاری", self.shift_spin))
        shift_row.addStretch()
        cv.addLayout(shift_row)

        cl.addWidget(cap_group)

        # ── موقعیت و یادداشت ──
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("مثال: سالن B، ردیف ۳")
        self.location_input.setMinimumHeight(36)
        cl.addWidget(self._make_field("موقعیت در کارگاه", self.location_input))

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("یادداشت‌های اضافی...")
        self.notes_input.setMinimumHeight(70)
        self.notes_input.setMaximumHeight(100)
        cl.addWidget(self._make_field("یادداشت‌ها", self.notes_input))

        # ── وضعیت ──
        self.status_combo = QComboBox()
        self.status_combo.setMinimumHeight(36)
        for st in WorkCenterStatus:
            self.status_combo.addItem(st.label, st.value)
        if not self.is_edit:
            self.status_combo.setEnabled(False)
            self.status_combo.setToolTip(
                "وضعیت رکورد جدید به‌صورت پیش‌فرض «فعال» ثبت می‌شود."
            )

        status_row = QHBoxLayout()
        status_row.addWidget(self._make_field("وضعیت", self.status_combo))
        status_row.addStretch()
        cl.addLayout(status_row)

        cl.addStretch(1)

        # Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
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

    def _load_departments(self):
        """لود لیست دپارتمان‌های فعال در ComboBox"""
        self.dept_combo.clear()
        self.dept_combo.addItem("— انتخاب دپارتمان —", None)
        self._dept_items: list = [None]  # dept.id per index

        try:
            with get_session() as session:
                svc = DepartmentService(session)
                depts = svc.get_active_list()

            for dept in depts:
                self.dept_combo.addItem(f"{dept.code} — {dept.name}", dept.id)
                self._dept_items.append(dept.id)

        except Exception as e:
            logger.error(f"خطا در بارگذاری دپارتمان‌ها: {e}")

    def _set_dept_by_id(self, dept_id: int | None):
        if dept_id is None:
            self.dept_combo.setCurrentIndex(0)
            return
        idx = self.dept_combo.findData(dept_id)
        if idx >= 0:
            self.dept_combo.setCurrentIndex(idx)

    def _load_data(self):
        try:
            with get_session() as session:
                svc = WorkCenterService(session)
                wc = svc.get_by_id(self.work_center_id)
                if not wc:
                    raise ValueError("مرکز کار یافت نشد")

                self.code_label.setText(wc.code)
                self.name_input.setText(wc.name or "")
                if wc.work_center_type:
                    self.type_combo.set_current_code(wc.work_center_type)
                self._set_dept_by_id(wc.department_id)

                if wc.capacity_per_hour is not None:
                    self.capacity_input.setValue(float(wc.capacity_per_hour))
                self.cap_unit_input.setText(wc.capacity_unit or "")
                self.shift_spin.setValue(wc.shift_count or 1)
                self.location_input.setText(wc.location or "")
                if wc.notes:
                    self.notes_input.setPlainText(wc.notes)

                idx = self.status_combo.findData(wc.status)
                if idx >= 0:
                    self.status_combo.setCurrentIndex(idx)

        except Exception as e:
            logger.error(f"خطا در بارگذاری مرکز کار: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _collect_data(self) -> dict:
        cap_val = self.capacity_input.value()
        return {
            "name": self.name_input.text().strip(),
            "department_id": self.dept_combo.currentData(),
            "work_center_type": self.type_combo.get_current_code() or None,
            "capacity_per_hour": Decimal(str(cap_val)) if cap_val > 0 else None,
            "capacity_unit": self.cap_unit_input.text().strip() or None,
            "shift_count": self.shift_spin.value(),
            "location": self.location_input.text().strip() or None,
            "notes": self.notes_input.toPlainText().strip() or None,
        }

    def _validate(self, data: dict) -> str | None:
        if not data.get("name"):
            return "نام مرکز کار الزامی است"
        if len(data["name"]) < 2:
            return "نام مرکز کار باید حداقل ۲ کاراکتر باشد"
        return None

    def _on_save(self):
        try:
            data = self._collect_data()
            error = self._validate(data)
            if error:
                Toast.warning(self, error)
                return

            with get_session() as session:
                svc = WorkCenterService(session)
                if self.is_edit:
                    data["status"] = self.status_combo.currentData()
                    svc.update(self.work_center_id, WorkCenterUpdate(**data))
                else:
                    svc.create(WorkCenterCreate(**data))

            self.accept()

        except ValueError as e:
            Toast.warning(self, str(e))
        except Exception as e:
            logger.error(f"خطا در ذخیره مرکز کار: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")