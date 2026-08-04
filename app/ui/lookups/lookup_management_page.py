"""
صفحه مدیریت Lookup ها
─────────────────────
کاربر می‌تونه گزینه‌های سیستم رو مدیریت کنه
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QDialog,
)
from PySide6.QtCore import Qt
import logging

from app.ui.base.base_table import AuroraTable
from app.ui.base.confirm_dialog import ConfirmDialog
from app.ui.lookups.lookup_form_dialog import LookupFormDialog
from app.ui.widgets.toast import Toast
from app.services.lookup_service import LookupService
from app.database.session import get_session
from app.enums.lookup_categories import LookupCategory
from app.core.exceptions import NotFoundError

logger = logging.getLogger(__name__)

# ── ستون‌های جدول ─────────────────────────────────────────────────
COLUMNS = [
    {"key": "id",         "label": "شناسه",     "width": 60},
    {"key": "code",       "label": "کد",        "width": 180},
    {"key": "label_fa",   "label": "لیبل فارسی","width": 220},
    {"key": "label_en",   "label": "لیبل انگلیسی","width": 140},
    {"key": "parent",     "label": "والد",      "width": 150},
    {"key": "sort_order", "label": "ترتیب",     "width": 80},
    {"key": "system_tag", "label": "نوع",       "width": 90},
    {"key": "status",     "label": "وضعیت"},
]


class LookupManagementPage(QWidget):
    """صفحه مدیریت گزینه‌های سیستم"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._current_category = None
        self._setup_ui()
        self._load_categories()

    # ══════════════════════════════════════════════════════════════════
    # Setup
    # ══════════════════════════════════════════════════════════════════

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

        title = QLabel("مدیریت داده‌های پایه سیستم")
        title.setObjectName("pageTitle")

        add_btn = QPushButton("＋  افزودن گزینه")
        add_btn.setObjectName("neonButton")
        add_btn.setFixedWidth(160)
        add_btn.clicked.connect(self._on_add)

        row.addWidget(title)
        row.addStretch()
        row.addWidget(add_btn)
        return row

    def _build_filters(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)

        # ── انتخاب دسته ──
        cat_label = QLabel("دسته:")
        cat_label.setObjectName("fieldLabel")

        self._category_combo = QComboBox()
        self._category_combo.setMinimumWidth(240)
        self._category_combo.setFixedHeight(38)
        self._category_combo.currentIndexChanged.connect(self._on_category_change)

        # ── جستجو ──
        self._search = QLineEdit()
        self._search.setPlaceholderText("🔍  جستجو در کد یا لیبل...")
        self._search.setObjectName("searchInput")
        self._search.setFixedWidth(280)
        self._search.textChanged.connect(self._on_search)

        # ── شمارنده ──
        self._counter_label = QLabel("")
        self._counter_label.setStyleSheet(
            "color: #6366F1; font-weight: bold; font-size: 13px; padding: 0 8px;"
        )

        row.addWidget(cat_label)
        row.addWidget(self._category_combo)
        row.addWidget(self._counter_label)
        row.addStretch()
        row.addWidget(self._search)
        return row

    def _build_table(self) -> AuroraTable:
        self._table = AuroraTable(COLUMNS, parent=self)
        self._table.edit_requested.connect(self._on_edit)
        self._table.delete_requested.connect(self._on_delete)
        return self._table

    def _build_actions(self) -> QHBoxLayout:
        row = QHBoxLayout()

        edit_btn = QPushButton("✏️  ویرایش")
        edit_btn.setObjectName("secondaryButton")
        edit_btn.setFixedWidth(130)
        edit_btn.clicked.connect(self._on_edit_selected)

        toggle_btn = QPushButton("🔄  فعال/غیرفعال")
        toggle_btn.setObjectName("warningButton")
        toggle_btn.setFixedWidth(150)
        toggle_btn.clicked.connect(self._on_toggle_selected)

        delete_btn = QPushButton("🗑️  حذف")
        delete_btn.setObjectName("warningButton")
        delete_btn.setFixedWidth(110)
        delete_btn.clicked.connect(self._on_delete_selected)

        row.addStretch()
        row.addWidget(edit_btn)
        row.addWidget(toggle_btn)
        row.addWidget(delete_btn)
        return row

    # ══════════════════════════════════════════════════════════════════
    # Category Loading
    # ══════════════════════════════════════════════════════════════════

    def _load_categories(self):
        """بارگذاری لیست دسته‌ها"""
        self._category_combo.blockSignals(True)
        self._category_combo.clear()

        # دسته‌های شناخته‌شده (از Enum)
        for code, label in LookupCategory.all_categories().items():
            self._category_combo.addItem(f"{label}  ({code})", code)

        self._category_combo.blockSignals(False)

        # بارگذاری اولین دسته
        if self._category_combo.count() > 0:
            self._on_category_change()

    # ══════════════════════════════════════════════════════════════════
    # Data
    # ══════════════════════════════════════════════════════════════════

    def _on_category_change(self, _idx=0):
        self._current_category = self._category_combo.currentData()
        self.refresh()

    def _on_search(self, _text: str):
        self.refresh()

    def refresh(self):
        """بارگذاری مجدد لیست"""
        if not self._current_category:
            return

        keyword = self._search.text().strip()

        try:
            with get_session() as session:
                svc = LookupService(session)

                if keyword:
                    items = svc.search(self._current_category, keyword)
                else:
                    # همه (شامل غیرفعال‌ها و زیرشاخه‌ها)
                    items = svc.get_by_category(
                        self._current_category,
                        active_only=False,
                        include_children=True
                    )

                # کش والدها برای نمایش
                parents_map = {}
                for item in items:
                    if item.parent_id:
                        parent = svc.repo.get_by_id(item.parent_id)
                        if parent:
                            parents_map[item.parent_id] = parent.label_fa

            rows = []
            for item in items:
                parent_label = parents_map.get(item.parent_id, "—") if item.parent_id else "—"
                rows.append({
                    "id":         item.id,
                    "code":       item.code,
                    "label_fa":   item.label_fa,
                    "label_en":   item.label_en or "—",
                    "parent":     parent_label,
                    "sort_order": item.sort_order,
                    "system_tag": "🔒 سیستمی" if item.is_system else "👤 کاربر",
                    "status":     "✅ فعال" if item.is_active else "❌ غیرفعال",
                })

            self._table.load_data(rows)

            # شمارنده
            total = len(items)
            active = sum(1 for i in items if i.is_active)
            self._counter_label.setText(f"📊 {total} گزینه ({active} فعال)")

            logger.info(f"✅ Lookup '{self._current_category}' بارگذاری شد: {total} گزینه")

        except Exception as e:
            logger.error(f"خطا در بارگذاری Lookup: {e}", exc_info=True)
            Toast.error(self, f"خطا در بارگذاری: {e}")

    # ══════════════════════════════════════════════════════════════════
    # Handlers
    # ══════════════════════════════════════════════════════════════════

    def _on_add(self):
        if not self._current_category:
            Toast.warning(self, "ابتدا یک دسته انتخاب کنید")
            return

        dlg = LookupFormDialog(
            category=self._current_category,
            parent=self
        )
        if dlg.exec():
            self.refresh()
            Toast.success(self, "گزینه با موفقیت اضافه شد")

    def _on_edit(self, lookup_id: int):
        dlg = LookupFormDialog(
            category=self._current_category,
            lookup_id=lookup_id,
            parent=self
        )
        if dlg.exec():
            self.refresh()
            Toast.success(self, "گزینه ویرایش شد")

    def _on_edit_selected(self):
        lid = self._table.get_selected_id()
        if lid is None:
            Toast.warning(self, "یک گزینه انتخاب کنید")
            return
        self._on_edit(lid)

    def _on_toggle_selected(self):
        lid = self._table.get_selected_id()
        if lid is None:
            Toast.warning(self, "یک گزینه انتخاب کنید")
            return

        try:
            with get_session() as session:
                svc = LookupService(session)
                item = svc.toggle_active(lid)

            status = "فعال" if item.is_active else "غیرفعال"
            Toast.success(self, f"گزینه {status} شد")
            self.refresh()

        except Exception as e:
            logger.error(f"خطا در toggle: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _on_delete(self, lookup_id: int):
        try:
            with get_session() as session:
                svc = LookupService(session)
                item = svc.get_by_id(lookup_id)

            if item.is_system:
                Toast.warning(
                    self,
                    f"«{item.label_fa}» یک گزینه سیستمی است و قابل حذف نیست"
                )
                return

            dlg = ConfirmDialog(
                parent=self,
                title="تأیید حذف",
                message=f"گزینه «{item.label_fa}» حذف شود؟",
                confirm_text="بله، حذف کن",
                cancel_text="انصراف",
                dangerous=True
            )
            if dlg.exec() != QDialog.DialogCode.Accepted:
                return

            with get_session() as session:
                svc = LookupService(session)
                svc.delete(lookup_id)

            Toast.success(self, "گزینه حذف شد")
            self.refresh()

        except ValueError as e:
            Toast.warning(self, str(e))
        except NotFoundError as e:
            Toast.error(self, str(e))
        except Exception as e:
            logger.error(f"خطا در حذف: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _on_delete_selected(self):
        lid = self._table.get_selected_id()
        if lid is None:
            Toast.warning(self, "یک گزینه انتخاب کنید")
            return
        self._on_delete(lid)