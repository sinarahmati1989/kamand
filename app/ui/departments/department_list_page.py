"""
صفحه لیست دپارتمان‌ها
"""
import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QDialog,
)
from PySide6.QtCore import Qt

from app.ui.base.base_table import AuroraTable
from app.ui.base.confirm_dialog import ConfirmDialog
from app.ui.departments.department_form_dialog import DepartmentFormDialog
from app.ui.widgets.toast import Toast
from app.ui.widgets.lookup_combo import LookupComboBox
from app.services.department_service import DepartmentService
from app.services.lookup_service import LookupService
from app.enums.department_enums import DepartmentStatus
from app.enums.lookup_categories import LookupCategory
from app.database.session import get_session

logger = logging.getLogger(__name__)

COLUMNS = [
    {"key": "id",              "label": "شناسه",       "width": 60},
    {"key": "code",            "label": "کد",          "width": 100},
    {"key": "name",            "label": "نام دپارتمان",  "width": 220},
    {"key": "department_type", "label": "نوع",         "width": 150},
    {"key": "manager_name",    "label": "مسئول",        "width": 150},
    {"key": "location",        "label": "موقعیت",       "width": 150},
    {"key": "status",          "label": "وضعیت"},
]


class DepartmentListPage(QWidget):
    """صفحه مدیریت دپارتمان‌ها"""

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

        title = QLabel("دپارتمان‌ها")
        title.setObjectName("pageTitle")

        self._type_filter = LookupComboBox(
            LookupCategory.DEPARTMENT_TYPE.value,
            allow_empty=True
        )
        self._type_filter.setItemText(0, "همه انواع")
        self._type_filter.setFixedWidth(160)
        self._type_filter.setFixedHeight(38)
        self._type_filter.currentIndexChanged.connect(self._on_filter_change)

        self._status_filter = __import__(
            "PySide6.QtWidgets", fromlist=["QComboBox"]
        ).QComboBox()
        self._status_filter.setFixedWidth(130)
        self._status_filter.setFixedHeight(38)
        self._status_filter.addItem("همه وضعیت‌ها", None)
        for st in DepartmentStatus:
            self._status_filter.addItem(st.label, st.value)
        self._status_filter.currentIndexChanged.connect(self._on_filter_change)

        self._search = QLineEdit()
        self._search.setPlaceholderText("جستجو در نام، کد یا مسئول...")
        self._search.setObjectName("searchInput")
        self._search.setFixedWidth(260)
        self._search.textChanged.connect(self._on_search)

        add_btn = QPushButton("افزودن دپارتمان")
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
            return DepartmentStatus(code).label
        except Exception:
            return code

    def refresh(self):
        self._load(
            keyword=self._search.text(),
            department_type=self._type_filter.currentData(),
            status=self._status_filter.currentData(),
        )

    def _load(self, keyword="", department_type=None, status=None):
        try:
            with get_session() as session:
                svc = DepartmentService(session)
                lookup_svc = LookupService(session)
                items = svc.search(keyword.strip(), department_type, status)
                type_map = lookup_svc.get_code_to_label_map(
                    LookupCategory.DEPARTMENT_TYPE.value
                )

            rows = []
            for d in items:
                rows.append({
                    "id": d.id,
                    "code": d.code,
                    "name": d.name,
                    "department_type": type_map.get(d.department_type, d.department_type or "—"),
                    "manager_name": d.manager_name or "—",
                    "location": d.location or "—",
                    "status": self._status_label(d.status),
                })

            self._table.load_data(rows)
            logger.info(f"دپارتمان‌ها بارگذاری شد. تعداد: {len(rows)}")

        except Exception as e:
            logger.error(f"خطا در بارگذاری دپارتمان‌ها: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _on_search(self, _):
        self.refresh()

    def _on_filter_change(self, _):
        self.refresh()

    def _on_add(self):
        dlg = DepartmentFormDialog(parent=self)
        if dlg.exec():
            self.refresh()
            Toast.success(self, "دپارتمان با موفقیت ثبت شد")

    def _on_edit(self, dept_id: int):
        dlg = DepartmentFormDialog(department_id=dept_id, parent=self)
        if dlg.exec():
            self.refresh()
            Toast.success(self, "دپارتمان ویرایش شد")

    def _on_edit_selected(self):
        oid = self._table.get_selected_id()
        if oid is None:
            Toast.warning(self, "یک دپارتمان را انتخاب کنید")
            return
        self._on_edit(oid)

    def _on_toggle_selected(self):
        oid = self._table.get_selected_id()
        if oid is None:
            Toast.warning(self, "یک دپارتمان را انتخاب کنید")
            return
        try:
            with get_session() as session:
                svc = DepartmentService(session)
                item = svc.get_by_id(oid)
            if not item:
                Toast.error(self, "دپارتمان یافت نشد")
                return
            new_status = (
                DepartmentStatus.INACTIVE.value
                if item.status == DepartmentStatus.ACTIVE.value
                else DepartmentStatus.ACTIVE.value
            )
            with get_session() as session:
                svc = DepartmentService(session)
                svc.change_status(oid, new_status)
            self.refresh()
            Toast.info(self, "وضعیت دپارتمان تغییر کرد")
        except Exception as e:
            Toast.error(self, f"خطا: {e}")

    def _on_delete(self, dept_id: int):
        try:
            with get_session() as session:
                svc = DepartmentService(session)
                item = svc.get_by_id(dept_id)
            if not item:
                Toast.error(self, "دپارتمان یافت نشد")
                return

            dlg = ConfirmDialog(
                parent=self,
                title="تأیید حذف",
                message=f"دپارتمان «{item.name}» حذف شود؟",
                confirm_text="بله، حذف کن",
                cancel_text="انصراف",
                dangerous=True
            )
            if dlg.exec() != QDialog.DialogCode.Accepted:
                return

            with get_session() as session:
                svc = DepartmentService(session)
                svc.delete(dept_id)

            Toast.success(self, "دپارتمان حذف شد")
            self.refresh()

        except ValueError as e:
            Toast.warning(self, str(e))
        except Exception as e:
            logger.error(f"خطا در حذف: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _on_delete_selected(self):
        oid = self._table.get_selected_id()
        if oid is None:
            Toast.warning(self, "یک دپارتمان را انتخاب کنید")
            return
        self._on_delete(oid)
