"""
صفحه لیست تأمین‌کنندگان — Lookup Ready
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QDialog,
)
from PySide6.QtCore import Qt
import logging

from app.ui.base.base_table import AuroraTable
from app.ui.base.confirm_dialog import ConfirmDialog
from app.ui.suppliers.supplier_form_dialog import SupplierFormDialog
from app.ui.widgets.toast import Toast
from app.services.supplier_service import SupplierService
from app.services.lookup_service import LookupService
from app.enums.supplier_enums import SupplierStatus
from app.database.session import get_session
from app.core.exceptions import NotFoundError

logger = logging.getLogger(__name__)

# ── ستون‌های جدول ─────────────────────────────────────────────────
COLUMNS = [
    {"key": "id",             "label": "شناسه",       "width": 60},
    {"key": "code",           "label": "کد",          "width": 100},
    {"key": "name",           "label": "نام شرکت",    "width": 200},
    {"key": "trade_name",     "label": "نام تجاری",   "width": 140},
    {"key": "supplier_types", "label": "نوع",         "width": 180},
    {"key": "tier",           "label": "سطح",         "width": 120},
    {"key": "contact_name",   "label": "مسئول فروش",  "width": 130},
    {"key": "mobile",         "label": "موبایل",      "width": 120},
    {"key": "status",         "label": "وضعیت"},
]


class SupplierListPage(QWidget):
    """صفحه مدیریت تأمین‌کنندگان"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._setup_ui()
        self.refresh()

    # ══════════════════════════════════════════════════════════════════
    # Setup
    # ══════════════════════════════════════════════════════════════════

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        layout.addLayout(self._build_header())
        layout.addWidget(self._build_table())
        layout.addLayout(self._build_actions())

    def _build_header(self) -> QHBoxLayout:
        row = QHBoxLayout()

        title = QLabel("تأمین‌کنندگان")
        title.setObjectName("pageTitle")

        self._search = QLineEdit()
        self._search.setPlaceholderText("🔍  جستجو در نام، کد، تلفن، ایمیل...")
        self._search.setObjectName("searchInput")
        self._search.setFixedWidth(300)
        self._search.textChanged.connect(self._on_search)

        add_btn = QPushButton("＋  افزودن تأمین‌کننده")
        add_btn.setObjectName("neonButton")
        add_btn.setFixedWidth(180)
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

        edit_btn = QPushButton("✏️  ویرایش")
        edit_btn.setObjectName("secondaryButton")
        edit_btn.setFixedWidth(130)
        edit_btn.clicked.connect(self._on_edit_selected)

        toggle_btn = QPushButton("🔄  تغییر وضعیت")
        toggle_btn.setObjectName("warningButton")
        toggle_btn.setFixedWidth(150)
        toggle_btn.clicked.connect(self._on_toggle_selected)

        row.addStretch()
        row.addWidget(edit_btn)
        row.addWidget(toggle_btn)
        return row

    # ══════════════════════════════════════════════════════════════════
    # Data
    # ══════════════════════════════════════════════════════════════════

    def refresh(self):
        """بارگذاری مجدد لیست"""
        self._load(keyword=self._search.text())

    def _load(self, keyword: str = ""):
        """واکشی داده و نمایش در جدول"""
        try:
            with get_session() as session:
                svc = SupplierService(session)
                suppliers = svc.search(keyword) if keyword.strip() else svc.get_all()

                # کش کردن لیبل‌ها از Lookup
                lookup_svc = LookupService(session)
                type_map = lookup_svc.get_code_to_label_map("supplier_type")
                tier_map = lookup_svc.get_code_to_label_map("supplier_tier")

            rows = []
            for s in suppliers:
                # تبدیل انواع به لیبل فارسی (از Lookup)
                types_list = s.supplier_types or []
                types_persian = "، ".join(
                    type_map.get(t, t) for t in types_list
                ) if types_list else "—"

                # تبدیل سطح به لیبل فارسی (از Lookup)
                tier_code = (s.tier or "").lower()
                tier_label = tier_map.get(tier_code, s.tier or "—")

                rows.append({
                    "id":             s.id,
                    "code":           s.code,
                    "name":           s.name,
                    "trade_name":     s.trade_name or "—",
                    "supplier_types": types_persian,
                    "tier":           tier_label,
                    "contact_name":   s.contact_name or "—",
                    "mobile":         s.mobile or "—",
                    "status":         SupplierStatus.to_persian(s.status),
                })

            self._table.load_data(rows)
            logger.info(f"✅ لیست تأمین‌کنندگان بارگذاری شد. تعداد: {len(rows)}")

        except Exception as e:
            logger.error(f"خطا در بارگذاری تأمین‌کنندگان: {e}", exc_info=True)
            Toast.error(self, f"خطا در بارگذاری: {e}")

    # ══════════════════════════════════════════════════════════════════
    # Handlers
    # ══════════════════════════════════════════════════════════════════

    def _on_search(self, text: str):
        self._load(keyword=text)

    def _on_add(self):
        dlg = SupplierFormDialog(parent=self)
        if dlg.exec():
            self.refresh()
            Toast.success(self, "تأمین‌کننده با موفقیت ثبت شد")

    def _on_edit(self, supplier_id: int):
        dlg = SupplierFormDialog(supplier_id=supplier_id, parent=self)
        if dlg.exec():
            self.refresh()
            Toast.success(self, "تأمین‌کننده ویرایش شد")

    def _on_edit_selected(self):
        sid = self._table.get_selected_id()
        if sid is None:
            Toast.warning(self, "یک تأمین‌کننده انتخاب کنید")
            return
        self._on_edit(sid)

    def _on_toggle_status(self, supplier_id: int):
        """تغییر وضعیت تأمین‌کننده"""
        logger.info(f"🔄 درخواست تغییر وضعیت تأمین‌کننده ID={supplier_id}")

        try:
            # مرحله ۱: خواندن وضعیت فعلی
            with get_session() as session:
                svc = SupplierService(session)
                supplier = svc.get_by_id(supplier_id)

            current = supplier.status
            active_val = SupplierStatus.ACTIVE.value
            is_active = current == active_val

            logger.info(
                f"  ↳ نام: {supplier.name} | وضعیت: {current} | فعال؟ {is_active}"
            )

            # مرحله ۲: اگه فعاله، تأیید بگیر
            if is_active:
                if not self._confirm_deactivate(supplier.name):
                    logger.info("  ↳ کاربر لغو کرد")
                    return
                new_status = SupplierStatus.INACTIVE
            else:
                new_status = SupplierStatus.ACTIVE

            # مرحله ۳: تغییر وضعیت
            with get_session() as session:
                svc = SupplierService(session)
                svc.change_status(supplier_id, new_status)

            # مرحله ۴: پیام و refresh
            if is_active:
                Toast.info(self, "تأمین‌کننده غیرفعال شد")
            else:
                Toast.success(self, "تأمین‌کننده فعال شد")

            self.refresh()

        except NotFoundError as e:
            logger.error(f"تأمین‌کننده پیدا نشد: {e}")
            Toast.error(self, str(e))
        except Exception as e:
            logger.error(f"❌ خطا در تغییر وضعیت: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _on_toggle_selected(self):
        sid = self._table.get_selected_id()
        if sid is None:
            Toast.warning(self, "یک تأمین‌کننده انتخاب کنید")
            return
        self._on_toggle_status(sid)

    # ══════════════════════════════════════════════════════════════════
    # Confirm Dialog
    # ══════════════════════════════════════════════════════════════════

    def _confirm_deactivate(self, name: str) -> bool:
        """دیالوگ تأیید غیرفعال‌سازی"""
        dlg = ConfirmDialog(
            parent=self,
            title="تأیید غیرفعال‌سازی",
            message=f"تأمین‌کننده «{name}» غیرفعال شود؟",
            confirm_text="بله، غیرفعال کن",
            cancel_text="انصراف",
            dangerous=True
        )
        result = dlg.exec() == QDialog.DialogCode.Accepted
        logger.info(f"  ↳ کاربر انتخاب کرد: {'بله' if result else 'خیر'}")
        return result