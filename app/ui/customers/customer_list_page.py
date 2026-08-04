"""
صفحه لیست مشتریان
"""
import logging

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QDialog,
)
from PySide6.QtCore import Qt

from app.ui.base.confirm_dialog import ConfirmDialog
from app.ui.base.base_table import AuroraTable
from app.ui.customers.customer_form_dialog import CustomerFormDialog
from app.ui.widgets.toast import Toast
from app.services.customer_service import CustomerService
from app.services.lookup_service import LookupService
from app.enums.customer_enums import CustomerStatus
from app.enums.lookup_categories import LookupCategory
from app.database.session import get_session
from app.core.exceptions import NotFoundError

logger = logging.getLogger(__name__)


COLUMNS = [
    {"key": "id",            "label": "کد",           "width": 60},
    {"key": "name",          "label": "نام شرکت",     "width": 180},
    {"key": "trade_name",    "label": "نام تجاری",    "width": 140},
    {"key": "customer_type", "label": "نوع",          "width": 90},
    {"key": "contact_name",  "label": "شخص رابط",     "width": 130},
    {"key": "mobile",        "label": "موبایل",       "width": 120},
    {"key": "status",        "label": "وضعیت"},
]


class CustomerListPage(QWidget):
    """صفحه مدیریت مشتریان"""

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

        title = QLabel("مشتریان")
        title.setObjectName("pageTitle")

        self._search = QLineEdit()
        self._search.setPlaceholderText("جست‌وجو در نام، تلفن، ایمیل...")
        self._search.setObjectName("searchInput")
        self._search.setFixedWidth(280)
        self._search.textChanged.connect(self._on_search)

        add_btn = QPushButton("افزودن مشتری")
        add_btn.setObjectName("neonButton")
        add_btn.setFixedWidth(160)
        add_btn.clicked.connect(self._on_add)

        row.addWidget(title)
        row.addStretch()
        row.addWidget(self._search)
        row.addWidget(add_btn)
        return row

    def _build_table(self) -> AuroraTable:
        self._table = AuroraTable(COLUMNS, parent=self)
        self._table.edit_requested.connect(self._on_edit)
        self._table.delete_requested.connect(self._on_toggle_status)
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

        row.addStretch()
        row.addWidget(edit_btn)
        row.addWidget(toggle_btn)
        return row

    # ---------- Helpers ----------

    def _status_label(self, status_code: str | None) -> str:
        if not status_code:
            return "—"
        try:
            return CustomerStatus(status_code).label
        except Exception:
            return status_code

    # ---------- Data ----------

    def refresh(self):
        self._load(keyword=self._search.text())

    def _load(self, keyword: str = ""):
        try:
            with get_session() as session:
                svc = CustomerService(session)
                lookup_svc = LookupService(session)

                customers = svc.search(keyword) if keyword.strip() else svc.get_all()
                type_map = lookup_svc.get_code_to_label_map(
                    LookupCategory.CUSTOMER_TYPE.value
                )

            rows = []
            for c in customers:
                rows.append({
                    "id":            c.id,
                    "name":          c.name,
                    "trade_name":    c.trade_name or "—",
                    "customer_type": type_map.get(c.customer_type, c.customer_type or "—"),
                    "contact_name":  c.contact_name or "—",
                    "mobile":        c.mobile or c.contact_mobile or "—",
                    "status":        self._status_label(c.status),
                })

            self._table.load_data(rows)
            logger.info(f"لیست مشتریان بارگذاری شد. تعداد: {len(rows)}")

        except Exception as e:
            logger.error(f"خطا در بارگذاری مشتریان: {e}", exc_info=True)
            Toast.error(self, f"خطا در بارگذاری: {e}")

    # ---------- Handlers ----------

    def _on_search(self, text: str):
        self._load(keyword=text)

    def _on_add(self):
        dlg = CustomerFormDialog(parent=self)
        if dlg.exec():
            self.refresh()
            Toast.success(self, "مشتری با موفقیت ثبت شد")

    def _on_edit(self, customer_id: int):
        dlg = CustomerFormDialog(customer_id=customer_id, parent=self)
        if dlg.exec():
            self.refresh()
            Toast.success(self, "مشتری ویرایش شد")

    def _on_edit_selected(self):
        cid = self._table.get_selected_id()
        if cid is None:
            Toast.warning(self, "یک مشتری انتخاب کنید")
            return
        self._on_edit(cid)

    def _on_toggle_status(self, customer_id: int):
        """تغییر وضعیت مشتری"""
        try:
            with get_session() as session:
                svc = CustomerService(session)
                customer = svc.get_by_id(customer_id)

            is_active = customer.status == CustomerStatus.ACTIVE.value

            if is_active:
                if not self._confirm_deactivate(customer.name):
                    return
                new_status = CustomerStatus.INACTIVE.value
            else:
                new_status = CustomerStatus.ACTIVE.value

            with get_session() as session:
                svc = CustomerService(session)
                svc.change_status(customer_id, new_status)

            if is_active:
                Toast.info(self, "مشتری غیرفعال شد")
            else:
                Toast.success(self, "مشتری فعال شد")

            self.refresh()

        except NotFoundError as e:
            Toast.error(self, str(e))
        except Exception as e:
            logger.error(f"خطا در تغییر وضعیت: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _on_toggle_selected(self):
        cid = self._table.get_selected_id()
        if cid is None:
            Toast.warning(self, "یک مشتری انتخاب کنید")
            return
        self._on_toggle_status(cid)

    # ---------- Confirm Dialog ----------

    def _confirm_deactivate(self, name: str) -> bool:
        dlg = ConfirmDialog(
            parent=self,
            title="تأیید غیرفعال‌سازی",
            message=f"مشتری «{name}» غیرفعال شود؟",
            confirm_text="بله، غیرفعال کن",
            cancel_text="انصراف",
            dangerous=True
        )
        return dlg.exec() == QDialog.DialogCode.Accepted