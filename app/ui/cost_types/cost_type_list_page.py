"""
صفحه لیست انواع هزینه
"""

import logging

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QDialog,
)
from PySide6.QtCore import Qt

from app.ui.base.base_table import AuroraTable
from app.ui.base.confirm_dialog import ConfirmDialog
from app.ui.cost_types.cost_type_form_dialog import CostTypeFormDialog
from app.ui.widgets.toast import Toast
from app.ui.widgets.lookup_combo import LookupComboBox
from app.services.cost_type_service import CostTypeService
from app.services.lookup_service import LookupService
from app.enums.cost_enums import CostStatus
from app.enums.lookup_categories import LookupCategory
from app.database.session import get_session

logger = logging.getLogger(__name__)


COLUMNS = [
    {"key": "id",             "label": "شناسه",          "width": 60},
    {"key": "code",           "label": "کد",             "width": 100},
    {"key": "name",           "label": "نام نوع هزینه",   "width": 180},
    {"key": "category",       "label": "دسته‌بندی",       "width": 120},
    {"key": "behavior",       "label": "رفتار",           "width": 110},
    {"key": "unit",           "label": "واحد",            "width": 90},
    {"key": "allocation",     "label": "روش تخصیص",       "width": 130},
    {"key": "default_amount", "label": "مبلغ پیش‌فرض",    "width": 130},
    {"key": "taxable",        "label": "مالیات",          "width": 80},
    {"key": "account_code",   "label": "کد حسابداری",     "width": 110},
    {"key": "status",         "label": "وضعیت"},
]


class CostTypeListPage(QWidget):
    """صفحه مدیریت انواع هزینه"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._setup_ui()
        self.refresh()

    # ------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        layout.addLayout(self._build_header())
        layout.addWidget(self._build_table())
        layout.addLayout(self._build_actions())

    def _build_header(self) -> QHBoxLayout:
        row = QHBoxLayout()

        title = QLabel("انواع هزینه")
        title.setObjectName("pageTitle")

        self._category_filter = LookupComboBox(
            LookupCategory.COST_CATEGORY.value,
            allow_empty=True
        )
        self._category_filter.setItemText(0, "همه دسته‌بندی‌ها")
        self._category_filter.setFixedWidth(160)
        self._category_filter.setFixedHeight(38)
        self._category_filter.currentIndexChanged.connect(self._on_filter_change)

        self._status_filter = QComboBox()
        self._status_filter.setFixedWidth(130)
        self._status_filter.setFixedHeight(38)
        self._status_filter.addItem("همه وضعیت‌ها", None)
        for st in CostStatus:
            self._status_filter.addItem(st.label, st.value)
        self._status_filter.currentIndexChanged.connect(self._on_filter_change)

        self._search = QLineEdit()
        self._search.setPlaceholderText("جست‌وجو بر اساس نام، کد یا کد حسابداری...")
        self._search.setObjectName("searchInput")
        self._search.setFixedWidth(300)
        self._search.textChanged.connect(self._on_search)

        add_btn = QPushButton("افزودن نوع هزینه")
        add_btn.setObjectName("neonButton")
        add_btn.setFixedWidth(170)
        add_btn.clicked.connect(self._on_add)

        row.addWidget(title)
        row.addStretch()
        row.addWidget(self._category_filter)
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

    # ------------------------------------------------------------
    # Data
    # ------------------------------------------------------------

    def refresh(self):
        self._load(
            keyword=self._search.text(),
            category=self._category_filter.currentData(),
            status=self._status_filter.currentData(),
        )

    def _status_label(self, status_code: str | None) -> str:
        if not status_code:
            return "—"

        try:
            return CostStatus(status_code).label
        except Exception:
            return status_code

    def _load(self, keyword: str = "", category=None, status=None):
        try:
            with get_session() as session:
                cost_svc = CostTypeService(session)
                lookup_svc = LookupService(session)

                items = cost_svc.search(keyword.strip(), category, status)

                category_map = lookup_svc.get_code_to_label_map(LookupCategory.COST_CATEGORY.value)
                behavior_map = lookup_svc.get_code_to_label_map(LookupCategory.COST_BEHAVIOR.value)
                unit_map = lookup_svc.get_code_to_label_map(LookupCategory.COST_UNIT.value)
                allocation_map = lookup_svc.get_code_to_label_map(LookupCategory.ALLOCATION_METHOD.value)

            rows = []
            for c in items:
                amount_text = "—"
                if c.default_amount is not None:
                    amount_value = float(c.default_amount)
                    if amount_value.is_integer():
                        amount_text = f"{amount_value:,.0f}"
                    else:
                        amount_text = f"{amount_value:,.2f}"

                rows.append({
                    "id": c.id,
                    "code": c.code,
                    "name": c.name,
                    "category": category_map.get(c.category, c.category or "—"),
                    "behavior": behavior_map.get(c.cost_behavior, c.cost_behavior or "—"),
                    "unit": unit_map.get(c.unit, c.unit or "—"),
                    "allocation": allocation_map.get(c.allocation_method, c.allocation_method or "—"),
                    "default_amount": amount_text,
                    "taxable": "بله" if c.taxable else "خیر",
                    "account_code": c.account_code or "—",
                    "status": self._status_label(c.status),
                })

            self._table.load_data(rows)
            logger.info(f"لیست انواع هزینه بارگذاری شد. تعداد: {len(rows)}")

        except Exception as e:
            logger.error(f"خطا در بارگذاری انواع هزینه: {e}", exc_info=True)
            Toast.error(self, f"خطا در بارگذاری: {e}")

    # ------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------

    def _on_search(self, _text: str):
        self.refresh()

    def _on_filter_change(self, _idx: int):
        self.refresh()

    def _on_add(self):
        dlg = CostTypeFormDialog(parent=self)
        if dlg.exec():
            self.refresh()
            Toast.success(self, "نوع هزینه با موفقیت ثبت شد")

    def _on_edit(self, cost_id: int):
        dlg = CostTypeFormDialog(cost_type_id=cost_id, parent=self)
        if dlg.exec():
            self.refresh()
            Toast.success(self, "نوع هزینه ویرایش شد")

    def _on_edit_selected(self):
        cid = self._table.get_selected_id()
        if cid is None:
            Toast.warning(self, "یک نوع هزینه را انتخاب کنید")
            return
        self._on_edit(cid)

    def _on_toggle_status(self, cost_id: int):
        try:
            with get_session() as session:
                svc = CostTypeService(session)
                item = svc.get_by_id(cost_id)

            if not item:
                Toast.error(self, "نوع هزینه یافت نشد")
                return

            is_active = item.status == CostStatus.ACTIVE.value

            if is_active:
                if not self._confirm_deactivate(item.name):
                    return
                new_status = CostStatus.INACTIVE.value
            else:
                new_status = CostStatus.ACTIVE.value

            with get_session() as session:
                svc = CostTypeService(session)
                svc.change_status(cost_id, new_status)

            if is_active:
                Toast.info(self, "نوع هزینه غیرفعال شد")
            else:
                Toast.success(self, "نوع هزینه فعال شد")

            self.refresh()

        except Exception as e:
            logger.error(f"خطا در تغییر وضعیت: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _on_toggle_selected(self):
        cid = self._table.get_selected_id()
        if cid is None:
            Toast.warning(self, "یک نوع هزینه را انتخاب کنید")
            return
        self._on_toggle_status(cid)

    def _on_delete(self, cost_id: int):
        try:
            with get_session() as session:
                svc = CostTypeService(session)
                item = svc.get_by_id(cost_id)

            if not item:
                Toast.error(self, "نوع هزینه یافت نشد")
                return

            dlg = ConfirmDialog(
                parent=self,
                title="تأیید حذف",
                message=f"نوع هزینه «{item.name}» حذف شود؟",
                confirm_text="بله، حذف کن",
                cancel_text="انصراف",
                dangerous=True
            )

            if dlg.exec() != QDialog.DialogCode.Accepted:
                return

            with get_session() as session:
                svc = CostTypeService(session)
                svc.delete(cost_id)

            Toast.success(self, "نوع هزینه حذف شد")
            self.refresh()

        except ValueError as e:
            Toast.warning(self, str(e))
        except Exception as e:
            logger.error(f"خطا در حذف: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _on_delete_selected(self):
        cid = self._table.get_selected_id()
        if cid is None:
            Toast.warning(self, "یک نوع هزینه را انتخاب کنید")
            return
        self._on_delete(cid)

    # ------------------------------------------------------------
    # Confirm Dialog
    # ------------------------------------------------------------

    def _confirm_deactivate(self, name: str) -> bool:
        dlg = ConfirmDialog(
            parent=self,
            title="تأیید غیرفعال‌سازی",
            message=f"نوع هزینه «{name}» غیرفعال شود؟",
            confirm_text="بله، غیرفعال کن",
            cancel_text="انصراف",
            dangerous=True
        )
        return dlg.exec() == QDialog.DialogCode.Accepted