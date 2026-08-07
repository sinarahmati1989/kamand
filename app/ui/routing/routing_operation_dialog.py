"""
Kamand - Routing Operation Dialog
افزودن/ویرایش عملیات در مسیر ساخت
"""
import logging
from decimal import Decimal
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QCheckBox,
    QTextEdit, QFrame, QComboBox,
)
from PySide6.QtCore import Qt

from app.ui.widgets.smart_spinbox import SmartDoubleSpinBox, SmartSpinBox
from app.ui.widgets.toast import Toast
from app.services.routing_service import RoutingService
from app.services.manufacturing_operation_service import ManufacturingOperationService
from app.services.department_service import DepartmentService
from app.services.work_center_service import WorkCenterService
from app.services.machine_service import MachineService
from app.database.session import get_session

logger = logging.getLogger(__name__)


class RoutingOperationDialog(QDialog):
    """دیالوگ افزودن/ویرایش عملیات Routing"""

    def __init__(
        self,
        routing_header_id: int,
        op_id: Optional[int] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.routing_header_id = routing_header_id
        self.op_id = op_id
        self._is_edit = op_id is not None

        self._all_operations = []
        self._all_departments = []
        self._all_work_centers = []
        self._all_machines = []

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowTitle(
            "ویرایش عملیات" if self._is_edit else "افزودن عملیات"
        )
        self.setMinimumWidth(620)
        self.setModal(True)

        self._setup_ui()
        self._load_data()

        if self._is_edit:
            self._load_op_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel(
            "ویرایش عملیات" if self._is_edit else "افزودن عملیات به مسیر ساخت"
        )
        title.setStyleSheet("font-size: 15px; font-weight: 700; color: #1E293B;")
        layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: rgba(99, 102, 241, 0.15);")
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )

        # نوع عملیات
        self._op_combo = QComboBox()
        self._op_combo.setFixedHeight(36)
        self._op_combo.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        form.addRow("عملیات *:", self._op_combo)

        # دپارتمان
        self._dept_combo = QComboBox()
        self._dept_combo.setFixedHeight(36)
        self._dept_combo.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._dept_combo.currentIndexChanged.connect(self._on_dept_changed)
        form.addRow("دپارتمان:", self._dept_combo)

        # مرکز کار
        self._wc_combo = QComboBox()
        self._wc_combo.setFixedHeight(36)
        self._wc_combo.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._wc_combo.currentIndexChanged.connect(self._on_wc_changed)
        form.addRow("مرکز کار:", self._wc_combo)

        # ماشین
        self._machine_combo = QComboBox()
        self._machine_combo.setFixedHeight(36)
        self._machine_combo.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._machine_combo.currentIndexChanged.connect(self._on_machine_changed)
        form.addRow("ماشین:", self._machine_combo)

        # زمان آماده‌سازی
        self._setup_time = SmartDoubleSpinBox()
        self._setup_time.setFixedHeight(36)
        self._setup_time.setRange(0, 99999)
        self._setup_time.setDecimals(1)
        self._setup_time.setSuffix("  دقیقه")
        self._setup_time.setSingleStep(5)
        self._setup_time.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        form.addRow("زمان آماده‌سازی:", self._setup_time)

        # زمان سیکل
        self._cycle_time = SmartDoubleSpinBox()
        self._cycle_time.setFixedHeight(36)
        self._cycle_time.setRange(0, 99999)
        self._cycle_time.setDecimals(1)
        self._cycle_time.setSuffix("  دقیقه")
        self._cycle_time.setSingleStep(5)
        self._cycle_time.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        form.addRow("زمان سیکل:", self._cycle_time)

        # تعداد نیروی کار
        self._labor = SmartSpinBox()
        self._labor.setFixedHeight(36)
        self._labor.setRange(1, 50)
        self._labor.setValue(1)
        self._labor.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        form.addRow("تعداد نیروی کار:", self._labor)

        # نرخ ساعتی
        self._rate_lbl = QLabel("— (از ماشین)")
        self._rate_lbl.setStyleSheet(
            "color: #6366F1; font-weight: 600; font-size: 13px;"
        )
        form.addRow("نرخ ساعتی (ریال):", self._rate_lbl)

        self._hourly_rate = SmartDoubleSpinBox()
        self._hourly_rate.setFixedHeight(36)
        self._hourly_rate.setRange(0, 999_999_999_999)
        self._hourly_rate.setDecimals(0)
        self._hourly_rate.setGroupSeparatorShown(True)
        self._hourly_rate.setSingleStep(100_000)
        self._hourly_rate.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self._hourly_rate.setVisible(False)
        form.addRow("نرخ دستی:", self._hourly_rate)

        # برون‌سپاری
        self._outsourced = QCheckBox("این عملیات برون‌سپاری می‌شود")
        form.addRow("", self._outsourced)

        # یادداشت
        self._notes = QTextEdit()
        self._notes.setFixedHeight(64)
        self._notes.setPlaceholderText("یادداشت...")
        form.addRow("یادداشت:", self._notes)

        layout.addLayout(form)

        # دکمه‌ها
        btn_row = QHBoxLayout()

        cancel_btn = QPushButton("انصراف")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.setFixedHeight(40)
        cancel_btn.setFixedWidth(110)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton(
            "ذخیره تغییرات" if self._is_edit else "افزودن به Routing"
        )
        save_btn.setObjectName("neonButton")
        save_btn.setFixedHeight(40)
        save_btn.setMinimumWidth(160)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._on_save)

        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _load_data(self):
        try:
            with get_session() as session:
                op_svc   = ManufacturingOperationService(session)
                dept_svc = DepartmentService(session)
                wc_svc   = WorkCenterService(session)
                mch_svc  = MachineService(session)

                self._all_operations  = op_svc.search("", None, "active")
                self._all_departments = dept_svc.get_active_list()
                self._all_work_centers = wc_svc.get_active_list()
                self._all_machines    = mch_svc.get_active_list()

            self._op_combo.addItem("— انتخاب عملیات —", None)
            for op in self._all_operations:
                self._op_combo.addItem(f"{op.code}  —  {op.name}", op.id)

            self._dept_combo.addItem("— انتخاب نشده —", None)
            for d in self._all_departments:
                self._dept_combo.addItem(f"{d.code}  —  {d.name}", d.id)

            self._fill_wc_combo(None)
            self._fill_machine_combo(None, None)

        except Exception as e:
            logger.error(f"خطا در بارگذاری داده: {e}", exc_info=True)

    def _fill_wc_combo(self, dept_id: Optional[int]):
        self._wc_combo.blockSignals(True)
        self._wc_combo.clear()
        self._wc_combo.addItem("— انتخاب نشده —", None)
        for wc in self._all_work_centers:
            if dept_id is None or wc.department_id == dept_id:
                self._wc_combo.addItem(f"{wc.code}  —  {wc.name}", wc.id)
        self._wc_combo.blockSignals(False)

    def _fill_machine_combo(
        self,
        dept_id: Optional[int],
        wc_id: Optional[int]
    ):
        self._machine_combo.blockSignals(True)
        self._machine_combo.clear()
        self._machine_combo.addItem("— انتخاب نشده —", None)
        for m in self._all_machines:
            if wc_id is not None and m.work_center_id != wc_id:
                continue
            if wc_id is None and dept_id is not None:
                if m.department_id != dept_id:
                    continue
            self._machine_combo.addItem(f"{m.code}  —  {m.name}", m.id)
        self._machine_combo.blockSignals(False)

    def _on_dept_changed(self, _idx: int):
        dept_id = self._dept_combo.currentData()
        self._fill_wc_combo(dept_id)
        self._fill_machine_combo(dept_id, None)
        self._update_rate_display()

    def _on_wc_changed(self, _idx: int):
        dept_id = self._dept_combo.currentData()
        wc_id   = self._wc_combo.currentData()
        self._fill_machine_combo(dept_id, wc_id)
        self._update_rate_display()

    def _on_machine_changed(self, _idx: int):
        self._update_rate_display()

    def _update_rate_display(self):
        mach_id = self._machine_combo.currentData()
        if mach_id:
            machine = next(
                (m for m in self._all_machines if m.id == mach_id), None
            )
            if machine and machine.hourly_rate:
                rate = float(machine.hourly_rate)
                self._rate_lbl.setText(f"{rate:,.0f} ریال/ساعت")
                self._hourly_rate.setVisible(False)
                return

        self._rate_lbl.setText("— (دستی وارد کنید)")
        self._hourly_rate.setVisible(True)

    def _load_op_data(self):
        try:
            with get_session() as session:
                svc = RoutingService(session)
                op = svc.get_operation_by_id(self.op_id)
            if not op:
                return

            for i in range(self._op_combo.count()):
                if self._op_combo.itemData(i) == op.operation_id:
                    self._op_combo.setCurrentIndex(i)
                    break

            if op.department_id:
                for i in range(self._dept_combo.count()):
                    if self._dept_combo.itemData(i) == op.department_id:
                        self._dept_combo.setCurrentIndex(i)
                        break

            if op.work_center_id:
                for i in range(self._wc_combo.count()):
                    if self._wc_combo.itemData(i) == op.work_center_id:
                        self._wc_combo.setCurrentIndex(i)
                        break

            if op.machine_id:
                for i in range(self._machine_combo.count()):
                    if self._machine_combo.itemData(i) == op.machine_id:
                        self._machine_combo.setCurrentIndex(i)
                        break

            self._setup_time.setValue(float(op.setup_time_min or 0))
            self._cycle_time.setValue(float(op.cycle_time_min or 0))
            self._labor.setValue(op.labor_count or 1)

            if op.hourly_rate:
                self._hourly_rate.setValue(float(op.hourly_rate))
                self._hourly_rate.setVisible(True)

            self._outsourced.setChecked(op.is_outsourced)
            self._notes.setPlainText(op.notes or "")

        except Exception as e:
            logger.error(f"خطا در بارگذاری عملیات: {e}", exc_info=True)

    def _get_hourly_rate(self) -> Optional[Decimal]:
        mach_id = self._machine_combo.currentData()
        if mach_id:
            machine = next(
                (m for m in self._all_machines if m.id == mach_id), None
            )
            if machine and machine.hourly_rate:
                return Decimal(str(machine.hourly_rate))

        val = self._hourly_rate.value()
        return Decimal(str(val)) if val > 0 else None

    def _on_save(self):
        op_id = self._op_combo.currentData()
        if not op_id:
            Toast.warning(self, "یک عملیات انتخاب کنید")
            return

        setup  = Decimal(str(self._setup_time.value()))
        cycle  = Decimal(str(self._cycle_time.value()))
        labor  = self._labor.value()
        rate   = self._get_hourly_rate()
        outsrc = self._outsourced.isChecked()
        notes  = self._notes.toPlainText().strip()

        dept_id = self._dept_combo.currentData()
        wc_id   = self._wc_combo.currentData()
        mach_id = self._machine_combo.currentData()

        try:
            with get_session() as session:
                svc = RoutingService(session)
                if self._is_edit:
                    svc.update_operation(
                        op_id=self.op_id,
                        operation_id=op_id,
                        department_id=dept_id,
                        work_center_id=wc_id,
                        machine_id=mach_id,
                        setup_time_min=setup,
                        cycle_time_min=cycle,
                        labor_count=labor,
                        hourly_rate=rate,
                        is_outsourced=outsrc,
                        notes=notes,
                    )
                else:
                    svc.add_operation(
                        routing_header_id=self.routing_header_id,
                        operation_id=op_id,
                        department_id=dept_id,
                        work_center_id=wc_id,
                        machine_id=mach_id,
                        setup_time_min=setup,
                        cycle_time_min=cycle,
                        labor_count=labor,
                        hourly_rate=rate,
                        is_outsourced=outsrc,
                        notes=notes,
                    )
            self.accept()

        except ValueError as e:
            Toast.warning(self, str(e))
        except Exception as e:
            logger.error(f"خطا در ذخیره: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")