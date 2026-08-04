"""
صفحه لیست ماشین‌آلات
"""
import logging

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QDialog,
)
from PySide6.QtCore import Qt

from app.ui.base.base_table import AuroraTable
from app.ui.base.confirm_dialog import ConfirmDialog
from app.ui.machines.machine_form_dialog import MachineFormDialog
from app.ui.widgets.toast import Toast
from app.ui.widgets.lookup_combo import LookupComboBox
from app.services.machine_service import MachineService
from app.services.lookup_service import LookupService
from app.enums.machine_enums import MachineStatus
from app.enums.lookup_categories import LookupCategory
from app.database.session import get_session

logger = logging.getLogger(__name__)

COLUMNS = [
    {"key": "id",           "label": "شناسه",     "width": 60},
    {"key": "code",         "label": "کد",        "width": 100},
    {"key": "name",         "label": "نام ماشین",   "width": 200},
    {"key": "machine_type", "label": "نوع",       "width": 130},
    {"key": "brand",        "label": "برند",       "width": 110},
    {"key": "model",        "label": "مدل",       "width": 110},
    {"key": "department",   "label": "دپارتمان",    "width": 140},
    {"key": "work_center",  "label": "مرکز کار",   "width": 140},
    {"key": "status",       "label": "وضعیت"},
]


class MachineListPage(QWidget):
    """صفحه مدیریت ماشین‌آلات"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        layout.addLayout(self._build_header())
        layout.addWidget(self._build_table())
        layout.addLayout(self._build_actions())

    def _build_header(self) -> QHBoxLayout:
        row = QHBoxLayout()

        title = QLabel("ماشین‌آلات")
        title.setObjectName("pageTitle")

        self._type_filter = LookupComboBox(
            LookupCategory.MACHINE_TYPE.value,
            allow_empty=True
        )
        self._type_filter.setItemText(0, "همه انواع")
        self._type_filter.setFixedWidth(150)
        self._type_filter.setFixedHeight(38)
        self._type_filter.currentIndexChanged.connect(self._on_filter_change)

        self._status_filter = QComboBox()
        self._status_filter.setFixedWidth(130)
        self._status_filter.setFixedHeight(38)
        self._status_filter.addItem("همه وضعیت‌ها", None)
        for st in MachineStatus:
            self._status_filter.addItem(st.label, st.value)
        self._status_filter.currentIndexChanged.connect(self._on_filter_change)

        self._search = QLineEdit()
        self._search.setPlaceholderText("جستجو در نام، کد، برند...")
        self._search.setObjectName("searchInput")
        self._search.setFixedWidth(240)
        self._search.textChanged.connect(self._on_search)

        add_btn = QPushButton("افزودن ماشین")
        add_btn.setObjectName("neonButton")
        add_btn.setFixedWidth(150)
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
        edit_btn.setFixedWidth(120)
        edit_btn.clicked.connect(self._on_edit_selected)

        toggle_btn = QPushButton("تغییر وضعیت")
        toggle_btn.setObjectName("warningButton")
        toggle_btn.setFixedWidth(140)
        toggle_btn.clicked.connect(self._on_toggle_selected)

        delete_btn = QPushButton("حذف")
        delete_btn.setObjectName("warningButton")
        delete_btn.setFixedWidth(100)
        delete_btn.clicked.connect(self._on_delete_selected)

        row.addStretch()
        row.addWidget(edit_btn)
        row.addWidget(toggle_btn)
        row.addWidget(delete_btn)
        return row

    def _status_label(self, code: str | None) -> str:
        if not code:
            return "—"
        try:
            return MachineStatus(code).label
        except Exception:
            return code

    def refresh(self):
        self._load(
            keyword=self._search.text(),
            machine_type=self._type_filter.currentData(),
            status=self._status_filter.currentData(),
        )

    def _load(self, keyword="", machine_type=None, status=None):
        try:
            with get_session() as session:
                svc = MachineService(session)
                lookup_svc = LookupService(session)
                items = svc.search(keyword.strip(), machine_type, status=status)
                type_map = lookup_svc.get_code_to_label_map(
                    LookupCategory.MACHINE_TYPE.value
                )

            rows = []
            for m in items:
                dept_name = "—"
                if m.department:
                    dept_name = m.department.name

                wc_name = "—"
                if m.work_center:
                    wc_name = m.work_center.name

                rows.append({
                    "id": m.id,
                    "code": m.code,
                    "name": m.name,
                    "machine_type": type_map.get(m.machine_type, m.machine_type or "—"),
                    "brand": m.brand or "—",
                    "model": m.model or "—",
                    "department": dept_name,
                    "work_center": wc_name,
                    "status": self._status_label(m.status),
                })

            self._table.load_data(rows)
            logger.info(f"ماشین‌آلات بارگذاری شد. تعداد: {len(rows)}")

        except Exception as e:
            logger.error(f"خطا در بارگذاری ماشین‌آلات: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _on_search(self, _):
        self.refresh()

    def _on_filter_change(self, _):
        self.refresh()

    def _on_add(self):
        dlg = MachineFormDialog(parent=self)
        if dlg.exec():
            self.refresh()
            Toast.success(self, "ماشین با موفقیت ثبت شد")

    def _on_edit(self, machine_id: int):
        dlg = MachineFormDialog(machine_id=machine_id, parent=self)
        if dlg.exec():
            self.refresh()
            Toast.success(self, "ماشین ویرایش شد")

    def _on_edit_selected(self):
        oid = self._table.get_selected_id()
        if oid is None:
            Toast.warning(self, "یک ماشین را انتخاب کنید")
            return
        self._on_edit(oid)

    def _on_toggle_selected(self):
        oid = self._table.get_selected_id()
        if oid is None:
            Toast.warning(self, "یک ماشین را انتخاب کنید")
            return
        try:
            with get_session() as session:
                svc = MachineService(session)
                item = svc.get_by_id(oid)
            if not item:
                Toast.error(self, "ماشین یافت نشد")
                return

            # چرخش وضعیت: active → maintenance → inactive → active
            cycle = {
                MachineStatus.ACTIVE.value:      MachineStatus.MAINTENANCE.value,
                MachineStatus.MAINTENANCE.value: MachineStatus.INACTIVE.value,
                MachineStatus.INACTIVE.value:    MachineStatus.ACTIVE.value,
                MachineStatus.BROKEN.value:      MachineStatus.ACTIVE.value,
            }
            new_status = cycle.get(item.status, MachineStatus.ACTIVE.value)

            with get_session() as session:
                svc = MachineService(session)
                svc.change_status(oid, new_status)

            label = MachineStatus(new_status).label
            self.refresh()
            Toast.info(self, f"وضعیت ماشین به «{label}» تغییر کرد")

        except Exception as e:
            Toast.error(self, f"خطا: {e}")

    def _on_delete(self, machine_id: int):
        try:
            with get_session() as session:
                svc = MachineService(session)
                item = svc.get_by_id(machine_id)
            if not item:
                Toast.error(self, "ماشین یافت نشد")
                return

            dlg = ConfirmDialog(
                parent=self,
                title="تأیید حذف",
                message=f"ماشین «{item.name}» حذف شود؟",
                confirm_text="بله، حذف کن",
                cancel_text="انصراف",
                dangerous=True
            )
            if dlg.exec() != QDialog.DialogCode.Accepted:
                return

            with get_session() as session:
                svc = MachineService(session)
                svc.delete(machine_id)

            Toast.success(self, "ماشین حذف شد")
            self.refresh()

        except ValueError as e:
            Toast.warning(self, str(e))
        except Exception as e:
            logger.error(f"خطا در حذف: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _on_delete_selected(self):
        oid = self._table.get_selected_id()
        if oid is None:
            Toast.warning(self, "یک ماشین را انتخاب کنید")
            return
        self._on_delete(oid)