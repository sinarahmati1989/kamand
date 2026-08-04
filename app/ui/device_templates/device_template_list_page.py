"""
صفحه لیست قالب‌های دستگاه
"""
import logging

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QDialog,
)
from PySide6.QtCore import Qt

from app.ui.base.base_table import AuroraTable
from app.ui.base.confirm_dialog import ConfirmDialog
from app.ui.widgets.workflow_bar import WorkflowBar
from app.ui.widgets.toast import Toast
from app.ui.widgets.lookup_combo import LookupComboBox
from app.services.device_template_service import DeviceTemplateService
from app.services.lookup_service import LookupService
from app.enums.engineering_enums import DeviceTemplateStatus
from app.enums.lookup_categories import LookupCategory
from app.database.session import get_session

logger = logging.getLogger(__name__)

COLUMNS = [
    {"key": "code",          "label": "کد",          "width": 100},
    {"key": "name",          "label": "نام دستگاه",   "width": 220},
    {"key": "template_type", "label": "نوع",          "width": 150},
    {"key": "revision_no",   "label": "Revision",     "width": 80},
    {"key": "cycle_time",    "label": "زمان ساخت",    "width": 110},
    {"key": "status",        "label": "وضعیت"},
]

ENGINEERING_STEPS = [
    ("device_templates", "قالب دستگاه"),
    ("items",            "اقلام"),
    ("bom",              "BOM"),
    ("routing",          "مسیر ساخت"),
]


class DeviceTemplateListPage(QWidget):
    """صفحه مدیریت قالب‌های دستگاه"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        # WorkflowBar
        self._workflow_bar = WorkflowBar(ENGINEERING_STEPS)
        self._workflow_bar.set_active("device_templates")
        self._workflow_bar.step_clicked.connect(self._on_workflow_step)
        layout.addWidget(self._workflow_bar)

        layout.addLayout(self._build_header())
        layout.addWidget(self._build_table())
        layout.addLayout(self._build_actions())

    def _build_header(self) -> QHBoxLayout:
        row = QHBoxLayout()

        title = QLabel("قالب‌های دستگاه")
        title.setObjectName("pageTitle")

        self._type_filter = LookupComboBox(
            LookupCategory.DEVICE_TEMPLATE_TYPE.value,
            allow_empty=True,
        )
        self._type_filter.setItemText(0, "همه انواع")
        self._type_filter.setFixedWidth(160)
        self._type_filter.setFixedHeight(38)
        self._type_filter.currentIndexChanged.connect(self._on_filter_change)

        self._status_filter = QComboBox()
        self._status_filter.setFixedWidth(140)
        self._status_filter.setFixedHeight(38)
        self._status_filter.addItem("همه وضعیت‌ها", None)
        for st in DeviceTemplateStatus:
            self._status_filter.addItem(st.label, st.value)
        self._status_filter.currentIndexChanged.connect(self._on_filter_change)

        self._search = QLineEdit()
        self._search.setPlaceholderText("جستجو در نام، کد...")
        self._search.setObjectName("searchInput")
        self._search.setFixedWidth(240)
        self._search.textChanged.connect(self._on_search)

        add_btn = QPushButton("+ قالب جدید")
        add_btn.setObjectName("neonButton")
        add_btn.setFixedHeight(38)
        add_btn.setMinimumWidth(140)
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
        edit_btn.setFixedWidth(110)
        edit_btn.clicked.connect(self._on_edit_selected)

        status_btn = QPushButton("تغییر وضعیت")
        status_btn.setObjectName("warningButton")
        status_btn.setFixedWidth(140)
        status_btn.clicked.connect(self._on_toggle_status)

        delete_btn = QPushButton("حذف")
        delete_btn.setObjectName("warningButton")
        delete_btn.setFixedWidth(90)
        delete_btn.clicked.connect(self._on_delete_selected)

        row.addStretch()
        row.addWidget(edit_btn)
        row.addWidget(status_btn)
        row.addWidget(delete_btn)
        return row

    # ─────────────────────────── Workflow ────────────────────────

    def _on_workflow_step(self, key: str):
        """ناوبری به مرحله دیگر Workflow"""
        # پیدا کردن MainWindow و navigate کردن
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, "_navigate_to"):
                parent._navigate_to(key)
                return
            parent = parent.parent()

    # ─────────────────────────── Data ────────────────────────────

    def refresh(self):
        self._load(
            keyword=self._search.text() if hasattr(self, "_search") else "",
            template_type=self._type_filter.currentData()
            if hasattr(self, "_type_filter") else None,
            status=self._status_filter.currentData()
            if hasattr(self, "_status_filter") else None,
        )

    def _load(self, keyword="", template_type=None, status=None):
        try:
            with get_session() as session:
                svc = DeviceTemplateService(session)
                lookup_svc = LookupService(session)
                items = svc.search(keyword.strip(), template_type, status)
                type_map = lookup_svc.get_code_to_label_map(
                    LookupCategory.DEVICE_TEMPLATE_TYPE.value
                )

            rows = []
            for t in items:
                cycle = "—"
                if t.estimated_cycle_time:
                    cycle = f"{t.estimated_cycle_time} دقیقه"

                rows.append({
                    "id":          t.id,
                    "code":        t.code,
                    "name":        t.name,
                    "template_type": type_map.get(
                        t.template_type, t.template_type or "—"
                    ),
                    "revision_no": f"Rev.{t.revision_no:02d}",
                    "cycle_time":  cycle,
                    "status":      DeviceTemplateStatus(t.status).label
                                   if t.status else "—",
                })

            self._table.load_data(rows)
            logger.info(f"قالب‌های دستگاه بارگذاری شد. تعداد: {len(rows)}")

        except Exception as e:
            logger.error(f"خطا در بارگذاری قالب‌ها: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _on_search(self, _):
        self.refresh()

    def _on_filter_change(self, _):
        self.refresh()

    # ─────────────────────────── CRUD ────────────────────────────

    def _on_add(self):
        from app.ui.device_templates.device_template_form_dialog import (
            DeviceTemplateFormDialog,
        )
        dlg = DeviceTemplateFormDialog(parent=self)
        if dlg.exec():
            self.refresh()
            Toast.success(self, "قالب دستگاه با موفقیت ثبت شد")

    def _on_edit(self, template_id: int):
        from app.ui.device_templates.device_template_form_dialog import (
            DeviceTemplateFormDialog,
        )
        dlg = DeviceTemplateFormDialog(template_id=template_id, parent=self)
        if dlg.exec():
            self.refresh()
            Toast.success(self, "قالب دستگاه ویرایش شد")

    def _on_edit_selected(self):
        oid = self._table.get_selected_id()
        if oid is None:
            Toast.warning(self, "یک قالب را انتخاب کنید")
            return
        self._on_edit(oid)

    def _on_toggle_status(self):
        oid = self._table.get_selected_id()
        if oid is None:
            Toast.warning(self, "یک قالب را انتخاب کنید")
            return
        try:
            with get_session() as session:
                svc = DeviceTemplateService(session)
                item = svc.get_by_id(oid)
            if not item:
                Toast.error(self, "قالب یافت نشد")
                return

            # چرخش: draft → approved → obsolete → draft
            cycle = {
                DeviceTemplateStatus.DRAFT.value:        DeviceTemplateStatus.APPROVED.value,
                DeviceTemplateStatus.UNDER_REVIEW.value: DeviceTemplateStatus.APPROVED.value,
                DeviceTemplateStatus.APPROVED.value:     DeviceTemplateStatus.OBSOLETE.value,
                DeviceTemplateStatus.OBSOLETE.value:     DeviceTemplateStatus.DRAFT.value,
            }
            new_status = cycle.get(item.status, DeviceTemplateStatus.DRAFT.value)

            with get_session() as session:
                svc = DeviceTemplateService(session)
                svc.change_status(oid, new_status)

            label = DeviceTemplateStatus(new_status).label
            self.refresh()
            Toast.info(self, f"وضعیت به «{label}» تغییر کرد")

        except Exception as e:
            Toast.error(self, f"خطا: {e}")

    def _on_delete(self, template_id: int):
        try:
            with get_session() as session:
                svc = DeviceTemplateService(session)
                item = svc.get_by_id(template_id)
            if not item:
                Toast.error(self, "قالب یافت نشد")
                return

            dlg = ConfirmDialog(
                parent=self,
                title="تأیید حذف",
                message=f"قالب «{item.name}» حذف شود؟",
                confirm_text="بله، حذف کن",
                cancel_text="انصراف",
                dangerous=True,
            )
            if dlg.exec() != QDialog.DialogCode.Accepted:
                return

            with get_session() as session:
                svc = DeviceTemplateService(session)
                svc.delete(template_id)

            Toast.success(self, "قالب حذف شد")
            self.refresh()

        except ValueError as e:
            Toast.warning(self, str(e))
        except Exception as e:
            logger.error(f"خطا در حذف: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _on_delete_selected(self):
        oid = self._table.get_selected_id()
        if oid is None:
            Toast.warning(self, "یک قالب را انتخاب کنید")
            return
        self._on_delete(oid)