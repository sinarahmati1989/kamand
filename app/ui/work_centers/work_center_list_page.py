"""
صفحه لیست مراکز کار
"""
import logging

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QDialog,
)
from PySide6.QtCore import Qt

from app.ui.base.base_table import AuroraTable
from app.ui.base.confirm_dialog import ConfirmDialog
from app.ui.work_centers.work_center_form_dialog import WorkCenterFormDialog
from app.ui.widgets.toast import Toast
from app.ui.widgets.lookup_combo import LookupComboBox
from app.services.work_center_service import WorkCenterService
from app.services.lookup_service import LookupService
from app.enums.work_center_enums import WorkCenterStatus
from app.enums.lookup_categories import LookupCategory
from app.database.session import get_session

logger = logging.getLogger(__name__)

COLUMNS = [
    {"key": "id",               "label": "شناسه",       "width": 60},
    {"key": "code",             "label": "کد",          "width": 100},
    {"key": "name",             "label": "نام مرکز کار",  "width": 200},
    {"key": "work_center_type", "label": "نوع",         "width": 140},
    {"key": "department",       "label": "دپارتمان",      "width": 160},
    {"key": "capacity",         "label": "ظرفیت/ساعت",   "width": 120},
    {"key": "shift_count",      "label": "شیفت",        "width": 80},
    {"key": "location",         "label": "موقعیت",       "width": 140},
    {"key": "status",           "label": "وضعیت"},
]


class WorkCenterListPage(QWidget):
    """صفحه مدیریت مراکز کار"""

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

        title = QLabel("مراکز کار")
        title.setObjectName("pageTitle")

        self._type_filter = LookupComboBox(
            LookupCategory.WORK_CENTER_TYPE.value,
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
        for st in WorkCenterStatus:
            self._status_filter.addItem(st.label, st.value)
        self._status_filter.currentIndexChanged.connect(self._on_filter_change)

        self._search = QLineEdit()
        self._search.setPlaceholderText("جستجو در نام یا کد...")
        self._search.setObjectName("searchInput")
        self._search.setFixedWidth(240)
        self._search.textChanged.connect(self._on_search)

        add_btn = QPushButton("افزودن مرکز کار")
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
            return WorkCenterStatus(code).label
        except Exception:
            return code

    def refresh(self):
        self._load(
            keyword=self._search.text(),
            work_center_type=self._type_filter.currentData(),
            status=self._status_filter.currentData(),
        )

    def _load(self, keyword: str = "", work_center_type=None, status=None):
        try:
            with get_session() as session:
                svc = WorkCenterService(session)
                lookup_svc = LookupService(session)
                items = svc.search(
                    keyword=keyword.strip(),
                    work_center_type=work_center_type,
                    status=status,
                )
                type_map = lookup_svc.get_code_to_label_map(
                    LookupCategory.WORK_CENTER_TYPE.value
                )

            rows = []
            for wc in items:
                dept_name = "—"
                if wc.department:
                    dept_name = wc.department.name

                cap_str = "—"
                if wc.capacity_per_hour is not None:
                    cap_str = f"{float(wc.capacity_per_hour):,.0f}"
                    if wc.capacity_unit:
                        cap_str += f" {wc.capacity_unit}"

                rows.append({
                    "id": wc.id,
                    "code": wc.code,
                    "name": wc.name,
                    "work_center_type": type_map.get(
                        wc.work_center_type, wc.work_center_type or "—"
                    ),
                    "department": dept_name,
                    "capacity": cap_str,
                    "shift_count": f"{wc.shift_count} شیفت",
                    "location": wc.location or "—",
                    "status": self._status_label(wc.status),
                })

            self._table.load_data(rows)
            logger.info(f"مراکز کار بارگذاری شد. تعداد: {len(rows)}")

        except Exception as e:
            logger.error(f"خطا در بارگذاری مراکز کار: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _on_search(self, _):
        self.refresh()

    def _on_filter_change(self, _):
        self.refresh()

    def _on_add(self):
        dlg = WorkCenterFormDialog(parent=self)
        if dlg.exec():
            self.refresh()
            Toast.success(self, "مرکز کار با موفقیت ثبت شد")

    def _on_edit(self, wc_id: int):
        dlg = WorkCenterFormDialog(work_center_id=wc_id, parent=self)
        if dlg.exec():
            self.refresh()
            Toast.success(self, "مرکز کار ویرایش شد")

    def _on_edit_selected(self):
        oid = self._table.get_selected_id()
        if oid is None:
            Toast.warning(self, "یک مرکز کار را انتخاب کنید")
            return
        self._on_edit(oid)

    def _on_toggle_selected(self):
        oid = self._table.get_selected_id()
        if oid is None:
            Toast.warning(self, "یک مرکز کار را انتخاب کنید")
            return
        try:
            with get_session() as session:
                svc = WorkCenterService(session)
                item = svc.get_by_id(oid)

            if not item:
                Toast.error(self, "مرکز کار یافت نشد")
                return

            new_status = (
                WorkCenterStatus.INACTIVE.value
                if item.status == WorkCenterStatus.ACTIVE.value
                else WorkCenterStatus.ACTIVE.value
            )

            with get_session() as session:
                svc = WorkCenterService(session)
                svc.change_status(oid, new_status)

            self.refresh()
            Toast.info(self, "وضعیت مرکز کار تغییر کرد")

        except Exception as e:
            logger.error(f"خطا در تغییر وضعیت مرکز کار: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _on_delete(self, wc_id: int):
        try:
            with get_session() as session:
                svc = WorkCenterService(session)
                item = svc.get_by_id(wc_id)

            if not item:
                Toast.error(self, "مرکز کار یافت نشد")
                return

            dlg = ConfirmDialog(
                parent=self,
                title="تأیید حذف",
                message=f"مرکز کار «{item.name}» حذف شود؟",
                confirm_text="بله، حذف کن",
                cancel_text="انصراف",
                dangerous=True
            )
            if dlg.exec() != QDialog.DialogCode.Accepted:
                return

            with get_session() as session:
                svc = WorkCenterService(session)
                svc.delete(wc_id)

            Toast.success(self, "مرکز کار حذف شد")
            self.refresh()

        except ValueError as e:
            Toast.warning(self, str(e))
        except Exception as e:
            logger.error(f"خطا در حذف مرکز کار: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _on_delete_selected(self):
        oid = self._table.get_selected_id()
        if oid is None:
            Toast.warning(self, "یک مرکز کار را انتخاب کنید")
            return
        self._on_delete(oid)