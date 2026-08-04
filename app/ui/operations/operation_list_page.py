"""
صفحه لیست عملیات ساخت
"""

import logging

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QDialog,
)
from PySide6.QtCore import Qt

from app.ui.base.base_table import AuroraTable
from app.ui.base.confirm_dialog import ConfirmDialog
from app.ui.operations.operation_form_dialog import OperationFormDialog
from app.ui.widgets.toast import Toast
from app.ui.widgets.lookup_combo import LookupComboBox
from app.services.manufacturing_operation_service import ManufacturingOperationService
from app.services.lookup_service import LookupService
from app.enums.operation_enums import OperationStatus
from app.enums.lookup_categories import LookupCategory
from app.database.session import get_session

logger = logging.getLogger(__name__)


COLUMNS = [
    {"key": "id",              "label": "شناسه",         "width": 60},
    {"key": "code",            "label": "کد",            "width": 100},
    {"key": "name",            "label": "نام عملیات",    "width": 200},
    {"key": "operation_type",  "label": "نوع",           "width": 130},
    {"key": "setup_time",      "label": "زمان راه‌اندازی", "width": 130},
    {"key": "cycle_time",      "label": "زمان تولید",    "width": 130},
    {"key": "hourly_rate",     "label": "نرخ ساعتی",     "width": 130},
    {"key": "flags",           "label": "ویژگی‌ها",       "width": 140},
    {"key": "status",          "label": "وضعیت"},
]


class OperationListPage(QWidget):
    """صفحه مدیریت عملیات ساخت"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._setup_ui()
        self.refresh()

    # ---------- Setup ----------

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        layout.addLayout(self._build_header())
        layout.addWidget(self._build_table())
        layout.addLayout(self._build_actions())

    def _build_header(self) -> QHBoxLayout:
        row = QHBoxLayout()

        title = QLabel("عملیات ساخت")
        title.setObjectName("pageTitle")

        self._type_filter = LookupComboBox(
            LookupCategory.OPERATION_TYPE.value,
            allow_empty=True
        )
        self._type_filter.setItemText(0, "همه انواع")
        self._type_filter.setFixedWidth(170)
        self._type_filter.setFixedHeight(38)
        self._type_filter.currentIndexChanged.connect(self._on_filter_change)

        self._status_filter = QComboBox()
        self._status_filter.setFixedWidth(130)
        self._status_filter.setFixedHeight(38)
        self._status_filter.addItem("همه وضعیت‌ها", None)
        for st in OperationStatus:
            self._status_filter.addItem(st.label, st.value)
        self._status_filter.currentIndexChanged.connect(self._on_filter_change)

        self._search = QLineEdit()
        self._search.setPlaceholderText("جست‌وجو در نام، کد یا توضیحات...")
        self._search.setObjectName("searchInput")
        self._search.setFixedWidth(280)
        self._search.textChanged.connect(self._on_search)

        add_btn = QPushButton("افزودن عملیات")
        add_btn.setObjectName("neonButton")
        add_btn.setFixedWidth(160)
        add_btn.clicked.connect(self._on_add)

        row.addWidget(title)
        row.addStretch()
        row.addWidget(self._type_filter)
        row.addWidget(self._status_filter)
        row.addWidget(self._search)
        row.addWidget(add_btn)
        return row

    def _build_table(self) -> AuroraTable:
        self._table = AuroraTable(COLUMNS, parent=self)
        self._table.edit_requested.connect(self._on_edit)
        self._table.delete_requested.connect(self._on_delete)
        return self._table

    def _build_actions(self) -> QHBoxLayout:
        row = QHBoxLayout()

        edit_btn = QPushButton("ویرایش")
        edit_btn.setObjectName("secondaryButton")
        edit_btn.setFixedWidth(130)
        edit_btn.clicked.connect(self._on_edit_selected)

        toggle_btn = QPushButton("تغییر وضعیت")
        toggle_btn.setObjectName("warningButton")
        toggle_btn.setFixedWidth(150)
        toggle_btn.clicked.connect(self._on_toggle_selected)

        delete_btn = QPushButton("حذف")
        delete_btn.setObjectName("warningButton")
        delete_btn.setFixedWidth(110)
        delete_btn.clicked.connect(self._on_delete_selected)

        row.addStretch()
        row.addWidget(edit_btn)
        row.addWidget(toggle_btn)
        row.addWidget(delete_btn)
        return row

    # ---------- Helpers ----------

    def _status_label(self, status_code: str | None) -> str:
        if not status_code:
            return "—"
        try:
            return OperationStatus(status_code).label
        except Exception:
            return status_code

    def _format_time(self, value, unit_label: str) -> str:
        if value is None:
            return "—"
        v = float(value)
        if v.is_integer():
            return f"{v:,.0f} {unit_label}"
        return f"{v:,.2f} {unit_label}"

    def _format_money(self, value, currency_label: str) -> str:
        if value is None:
            return "—"
        v = float(value)
        return f"{v:,.0f} {currency_label}"

    def _build_flags(self, op) -> str:
        flags = []
        if op.is_outsourced:
            flags.append("برون‌سپاری")
        if op.requires_qc:
            flags.append("QC")
        if op.is_bottleneck:
            flags.append("گلوگاه")
        if not op.requires_machine:
            flags.append("دستی")
        return " | ".join(flags) if flags else "—"

    # ---------- Data ----------

    def refresh(self):
        self._load(
            keyword=self._search.text(),
            operation_type=self._type_filter.currentData(),
            status=self._status_filter.currentData(),
        )

    def _load(self, keyword: str = "", operation_type=None, status=None):
        try:
            with get_session() as session:
                op_svc = ManufacturingOperationService(session)
                lookup_svc = LookupService(session)

                items = op_svc.search(keyword.strip(), operation_type, status)

                type_map = lookup_svc.get_code_to_label_map(
                    LookupCategory.OPERATION_TYPE.value
                )
                time_map = lookup_svc.get_code_to_label_map(
                    LookupCategory.TIME_UNIT.value
                )
                currency_map = lookup_svc.get_code_to_label_map(
                    LookupCategory.CURRENCY.value
                )

            rows = []
            for op in items:
                setup_unit_label = time_map.get(op.setup_time_unit, op.setup_time_unit or "")
                cycle_unit_label = time_map.get(op.cycle_time_unit, op.cycle_time_unit or "")
                currency_label = currency_map.get(op.currency, op.currency or "")

                rows.append({
                    "id": op.id,
                    "code": op.code,
                    "name": op.name,
                    "operation_type": type_map.get(op.operation_type, op.operation_type or "—"),
                    "setup_time": self._format_time(op.setup_time, setup_unit_label),
                    "cycle_time": self._format_time(op.cycle_time, cycle_unit_label),
                    "hourly_rate": self._format_money(op.hourly_rate, currency_label),
                    "flags": self._build_flags(op),
                    "status": self._status_label(op.status),
                })

            self._table.load_data(rows)
            logger.info(f"لیست عملیات ساخت بارگذاری شد. تعداد: {len(rows)}")

        except Exception as e:
            logger.error(f"خطا در بارگذاری عملیات: {e}", exc_info=True)
            Toast.error(self, f"خطا در بارگذاری: {e}")

    # ---------- Handlers ----------

    def _on_search(self, _text: str):
        self.refresh()

    def _on_filter_change(self, _idx: int):
        self.refresh()

    def _on_add(self):
        dlg = OperationFormDialog(parent=self)
        if dlg.exec():
            self.refresh()
            Toast.success(self, "عملیات ساخت با موفقیت ثبت شد")

    def _on_edit(self, op_id: int):
        dlg = OperationFormDialog(operation_id=op_id, parent=self)
        if dlg.exec():
            self.refresh()
            Toast.success(self, "عملیات ساخت ویرایش شد")

    def _on_edit_selected(self):
        oid = self._table.get_selected_id()
        if oid is None:
            Toast.warning(self, "یک عملیات را انتخاب کنید")
            return
        self._on_edit(oid)

    def _on_toggle_status(self, op_id: int):
        try:
            with get_session() as session:
                svc = ManufacturingOperationService(session)
                item = svc.get_by_id(op_id)

            if not item:
                Toast.error(self, "عملیات یافت نشد")
                return

            is_active = item.status == OperationStatus.ACTIVE.value

            if is_active:
                if not self._confirm_deactivate(item.name):
                    return
                new_status = OperationStatus.INACTIVE.value
            else:
                new_status = OperationStatus.ACTIVE.value

            with get_session() as session:
                svc = ManufacturingOperationService(session)
                svc.change_status(op_id, new_status)

            if is_active:
                Toast.info(self, "عملیات غیرفعال شد")
            else:
                Toast.success(self, "عملیات فعال شد")

            self.refresh()

        except Exception as e:
            logger.error(f"خطا در تغییر وضعیت: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _on_toggle_selected(self):
        oid = self._table.get_selected_id()
        if oid is None:
            Toast.warning(self, "یک عملیات را انتخاب کنید")
            return
        self._on_toggle_status(oid)

    def _on_delete(self, op_id: int):
        try:
            with get_session() as session:
                svc = ManufacturingOperationService(session)
                item = svc.get_by_id(op_id)

            if not item:
                Toast.error(self, "عملیات یافت نشد")
                return

            dlg = ConfirmDialog(
                parent=self,
                title="تأیید حذف",
                message=f"عملیات «{item.name}» حذف شود؟",
                confirm_text="بله، حذف کن",
                cancel_text="انصراف",
                dangerous=True
            )

            if dlg.exec() != QDialog.DialogCode.Accepted:
                return

            with get_session() as session:
                svc = ManufacturingOperationService(session)
                svc.delete(op_id)

            Toast.success(self, "عملیات حذف شد")
            self.refresh()

        except ValueError as e:
            Toast.warning(self, str(e))
        except Exception as e:
            logger.error(f"خطا در حذف: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _on_delete_selected(self):
        oid = self._table.get_selected_id()
        if oid is None:
            Toast.warning(self, "یک عملیات را انتخاب کنید")
            return
        self._on_delete(oid)

    # ---------- Confirm ----------

    def _confirm_deactivate(self, name: str) -> bool:
        dlg = ConfirmDialog(
            parent=self,
            title="تأیید غیرفعال‌سازی",
            message=f"عملیات «{name}» غیرفعال شود؟",
            confirm_text="بله، غیرفعال کن",
            cancel_text="انصراف",
            dangerous=True
        )
        return dlg.exec() == QDialog.DialogCode.Accepted