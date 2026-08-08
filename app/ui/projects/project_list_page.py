"""
Kamand - Project List Page
صفحه مدیریت پروژه‌ها با AuroraTable
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox,
)
from PySide6.QtCore import Qt
import logging

from app.ui.base.base_table import AuroraTable
from app.ui.base.confirm_dialog import ConfirmDialog
from app.ui.projects.project_form_dialog import ProjectFormDialog
from app.ui.projects.project_detail_dialog import ProjectDetailDialog
from app.ui.widgets.toast import Toast
from app.services.project_service import ProjectService
from app.database.session import get_session

logger = logging.getLogger(__name__)


COLUMNS = [
    {"key": "id",           "label": "شناسه",         "width": 60},
    {"key": "project_no",   "label": "شماره پروژه",  "width": 120},
    {"key": "name",         "label": "نام پروژه",    "width": 240},
    {"key": "customer",     "label": "مشتری",        "width": 180},
    {"key": "contract_no",  "label": "شماره قرارداد", "width": 130},
    {"key": "priority",     "label": "اولویت",       "width": 90},
    {"key": "status",       "label": "وضعیت",        "width": 120},
    {"key": "device_count", "label": "تعداد دستگاه", "width": 100},
    {"key": "delivery",     "label": "تاریخ تحویل"},
]


STATUS_LABELS = {
    "draft":         "پیش‌نویس",
    "confirmed":     "تأیید شده",
    "in_production": "در تولید",
    "delivered":     "تحویل داده شده",
    "cancelled":     "لغو شده",
}

PRIORITY_LABELS = {
    "low":    "پایین",
    "normal": "عادی",
    "high":   "بالا",
    "urgent": "فوری",
}


class ProjectListPage(QWidget):
    """صفحه مدیریت پروژه‌ها"""

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
        layout.addLayout(self._build_filters())
        layout.addWidget(self._build_table())
        layout.addLayout(self._build_actions())

    def _build_header(self) -> QHBoxLayout:
        row = QHBoxLayout()

        title = QLabel("مدیریت پروژه‌ها")
        title.setObjectName("pageTitle")

        self._search = QLineEdit()
        self._search.setPlaceholderText(
            "🔍  جستجو در شماره، نام، قرارداد..."
        )
        self._search.setObjectName("searchInput")
        self._search.setFixedWidth(300)
        self._search.textChanged.connect(self._on_search)

        add_btn = QPushButton("＋  افزودن پروژه")
        add_btn.setObjectName("neonButton")
        add_btn.setFixedWidth(180)
        add_btn.clicked.connect(self._on_add)

        row.addWidget(title)
        row.addStretch()
        row.addWidget(self._search)
        row.addWidget(add_btn)
        return row

    def _build_filters(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)

        lbl = QLabel("فیلتر وضعیت:")
        lbl.setObjectName("fieldLabel")

        self.status_filter = QComboBox()
        self.status_filter.setFixedWidth(180)
        self.status_filter.setFixedHeight(34)
        self.status_filter.addItem("همه وضعیت‌ها", "")
        for code, label in STATUS_LABELS.items():
            self.status_filter.addItem(label, code)
        self.status_filter.currentIndexChanged.connect(self._on_search)

        row.addStretch()
        row.addWidget(lbl)
        row.addWidget(self.status_filter)
        return row

    def _build_table(self) -> AuroraTable:
        self._table = AuroraTable(COLUMNS, parent=self)
        self._table.edit_requested.connect(self._on_view)
        self._table.delete_requested.connect(self._on_delete)
        self._table.row_double_clicked.connect(self._on_view)
        return self._table

    def _build_actions(self) -> QHBoxLayout:
        row = QHBoxLayout()

        view_btn = QPushButton("👁  مشاهده / مدیریت")
        view_btn.setObjectName("secondaryButton")
        view_btn.setFixedWidth(170)
        view_btn.clicked.connect(self._on_view_selected)

        edit_btn = QPushButton("✏  ویرایش")
        edit_btn.setObjectName("secondaryButton")
        edit_btn.setFixedWidth(130)
        edit_btn.clicked.connect(self._on_edit_selected)

        del_btn = QPushButton("🗑  حذف")
        del_btn.setObjectName("warningButton")
        del_btn.setFixedWidth(120)
        del_btn.clicked.connect(self._on_delete_selected)

        row.addStretch()
        row.addWidget(view_btn)
        row.addWidget(edit_btn)
        row.addWidget(del_btn)
        return row

    # ═══ Data ═══

    def refresh(self):
        self._load()

    def _load(self):
        try:
            keyword = self._search.text().strip()
            status = self.status_filter.currentData() or ""

            with get_session() as session:
                svc = ProjectService(session)
                projects = svc.get_all(
                    search=keyword,
                    status=status,
                    limit=500,
                )

            rows = []
            for p in projects:
                # تاریخ تحویل
                delivery_str = "—"
                if p.delivery_date:
                    try:
                        import jdatetime
                        jd = jdatetime.date.fromgregorian(date=p.delivery_date)
                        delivery_str = jd.strftime("%Y/%m/%d")
                    except Exception:
                        delivery_str = str(p.delivery_date)

                rows.append({
                    "id":           p.id,
                    "project_no":   p.project_no,
                    "name":         p.name,
                    "customer":     p.customer.name if p.customer else "—",
                    "contract_no":  p.contract_no or "—",
                    "priority":     PRIORITY_LABELS.get(p.priority, p.priority or "—"),
                    "status":       STATUS_LABELS.get(p.status, p.status),
                    "device_count": len(p.project_devices) if p.project_devices else 0,
                    "delivery":     delivery_str,
                })

            self._table.load_data(rows)
            logger.info(f"✅ لیست پروژه‌ها بارگذاری شد. تعداد: {len(rows)}")

        except Exception as e:
            logger.error(f"خطا در بارگذاری پروژه‌ها: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    # ═══ Handlers ═══

    def _on_search(self, *args):
        self._load()

    def _on_add(self):
        dlg = ProjectFormDialog(parent=self)
        if dlg.exec():
            self.refresh()
            Toast.success(self, "پروژه با موفقیت ایجاد شد")

    def _on_view(self, project_id: int):
        dlg = ProjectDetailDialog(project_id=project_id, parent=self)
        dlg.exec()
        self.refresh()

    def _on_view_selected(self):
        pid = self._table.get_selected_id()
        if pid is None:
            Toast.warning(self, "یک پروژه انتخاب کنید")
            return
        self._on_view(pid)

    def _on_edit(self, project_id: int):
        try:
            with get_session() as session:
                svc = ProjectService(session)
                p = svc.get_by_id(project_id)
                if not p:
                    Toast.error(self, "پروژه یافت نشد")
                    return
                dlg = ProjectFormDialog(project=p, parent=self)
            if dlg.exec():
                self.refresh()
                Toast.success(self, "پروژه ویرایش شد")
        except Exception as e:
            logger.error(f"خطا: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _on_edit_selected(self):
        pid = self._table.get_selected_id()
        if pid is None:
            Toast.warning(self, "یک پروژه انتخاب کنید")
            return
        self._on_edit(pid)

    def _on_delete(self, project_id: int):
        try:
            with get_session() as session:
                svc = ProjectService(session)
                p = svc.get_by_id(project_id)
                if not p:
                    return
                name = p.name

            from PySide6.QtWidgets import QDialog
            dlg = ConfirmDialog(
                parent=self,
                title="تأیید حذف پروژه",
                message=f"آیا از حذف پروژه «{name}» اطمینان دارید؟",
                confirm_text="بله، حذف کن",
                cancel_text="انصراف",
                dangerous=True,
            )
            if dlg.exec() != QDialog.DialogCode.Accepted:
                return

            with get_session() as session:
                svc = ProjectService(session)
                p = svc.get_by_id(project_id)
                svc.delete(p)

            self.refresh()
            Toast.success(self, "پروژه حذف شد")

        except ValueError as e:
            Toast.warning(self, str(e))
        except Exception as e:
            logger.error(f"خطا در حذف: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _on_delete_selected(self):
        pid = self._table.get_selected_id()
        if pid is None:
            Toast.warning(self, "یک پروژه انتخاب کنید")
            return
        self._on_delete(pid)