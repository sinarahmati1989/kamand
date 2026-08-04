"""
دیالوگ افزودن/ویرایش تأمین‌کننده — با پشتیبانی ۳ سطح دسته‌بندی
─────────────────────────────────────────────────
Level 1: نوع تأمین‌کننده
Level 2: زیرشاخه‌ها
Level 3: جزئیات تخصصی
"""
from decimal import Decimal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QCheckBox, QTextEdit,
    QPushButton, QTabWidget, QWidget, QGroupBox,
    QSpinBox, QDoubleSpinBox, QScrollArea, QFrame
)
from PySide6.QtCore import Qt
import logging

from app.services.supplier_service import SupplierService
from app.schemas.supplier_schema import SupplierCreate, SupplierUpdate
from app.database.session import get_session
from app.enums.supplier_enums import SupplierStatus
from app.core.exceptions import DuplicateError
from app.ui.widgets.toast import Toast
from app.ui.widgets.persian_date_edit import PersianDateEdit
from app.ui.widgets.lookup_combo import LookupComboBox
from app.ui.widgets.lookup_multi_select import LookupMultiSelect
from app.ui.widgets.lookup_cascade import LookupCascadeSelect

logger = logging.getLogger(__name__)


class SupplierFormDialog(QDialog):
    """فرم افزودن/ویرایش تأمین‌کننده — ۳ سطح دسته‌بندی"""

    def __init__(self, supplier_id: int | None = None, parent=None):
        super().__init__(parent)
        self.supplier_id = supplier_id
        self.is_edit = supplier_id is not None

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowTitle(
            "ویرایش تأمین‌کننده" if self.is_edit else "افزودن تأمین‌کننده جدید"
        )
        self.setMinimumSize(860, 750)
        self.resize(900, 780)

        self._setup_ui()

        if self.is_edit:
            self._load_data()

    # ══════════════════════════════════════════════════════════════════
    # Setup
    # ══════════════════════════════════════════════════════════════════

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # عنوان
        title_text = (
            "✏️  ویرایش تأمین‌کننده" if self.is_edit
            else "➕  افزودن تأمین‌کننده جدید"
        )
        title = QLabel(title_text)
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setObjectName("supplierTabs")
        self.tabs.addTab(self._build_basic_tab(),   "📋  اطلاعات پایه")
        self.tabs.addTab(self._build_contact_tab(), "📞  اطلاعات تماس")
        self.tabs.addTab(self._build_finance_tab(), "💰  اطلاعات مالی")
        layout.addWidget(self.tabs, 1)

        # دکمه‌ها
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        save_btn = QPushButton("💾  ذخیره")
        save_btn.setObjectName("neonButton")
        save_btn.setFixedSize(140, 42)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._on_save)

        cancel_btn = QPushButton("انصراف")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.setFixedSize(110, 42)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)

        btn_row.addStretch(1)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    # ══════════════════════════════════════════════════════════════════
    # Helper: ساخت فیلد
    # ══════════════════════════════════════════════════════════════════

    def _make_field(self, label_text: str, widget: QWidget, required: bool = False) -> QWidget:
        wrapper = QWidget()
        v = QVBoxLayout(wrapper)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(6)

        label_full = f"{label_text} *" if required else label_text
        lbl = QLabel(label_full)
        lbl.setObjectName("fieldLabel")
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        if required:
            lbl.setStyleSheet("QLabel#fieldLabel { color: #6366F1; font-weight: 600; }")

        v.addWidget(lbl)
        v.addWidget(widget)
        return wrapper

    def _wrap_scroll(self, content: QWidget) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(content)
        return scroll

    # ══════════════════════════════════════════════════════════════════
    # تب ۱: اطلاعات پایه — ۳ سطح دسته‌بندی
    # ══════════════════════════════════════════════════════════════════

    def _build_basic_tab(self) -> QScrollArea:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # ═══ نام + نام تجاری ═══
        row1 = QHBoxLayout()
        row1.setSpacing(12)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("نام کامل شرکت")
        self.name_input.setMinimumHeight(36)
        row1.addWidget(self._make_field("نام شرکت", self.name_input, required=True), 1)

        self.trade_name_input = QLineEdit()
        self.trade_name_input.setPlaceholderText("نام تجاری/برند (اختیاری)")
        self.trade_name_input.setMinimumHeight(36)
        row1.addWidget(self._make_field("نام تجاری", self.trade_name_input), 1)

        layout.addLayout(row1)

        # ═══ کد (فقط ویرایش) ═══
        if self.is_edit:
            code_wrapper = QWidget()
            ch = QHBoxLayout(code_wrapper)
            ch.setContentsMargins(0, 0, 0, 0)
            ch.setSpacing(8)

            code_lbl = QLabel("کد تأمین‌کننده:")
            code_lbl.setObjectName("fieldLabel")

            self.code_label = QLabel("—")
            self.code_label.setStyleSheet(
                "color: #6366F1; font-weight: bold; font-size: 14px;"
            )

            ch.addWidget(code_lbl)
            ch.addWidget(self.code_label)
            ch.addStretch()
            layout.addWidget(code_wrapper)

        # ═══ Level 1: نوع تأمین‌کننده ═══
        self.types_widget = LookupMultiSelect(
            category="supplier_type",
            title="📦  نوع تأمین‌کننده (چند مورد قابل انتخاب)",
            columns=2,
            allow_quick_add=True
        )
        self.types_widget.selection_changed.connect(self._on_types_changed)
        layout.addWidget(self.types_widget)

        # ═══ Level 2: زیرشاخه‌ها ═══
        self.subcategories_widget = LookupCascadeSelect(
            category="supplier_subcategory",
            parent_category="supplier_type",
            columns=2,
            allow_quick_add=True,
            group_icon="🎯",
            group_title_prefix="زیرشاخه‌ها"
        )
        self.subcategories_widget.selection_changed.connect(self._on_subcategories_changed)
        layout.addWidget(self.subcategories_widget)

        # ═══ Level 3: جزئیات تخصصی ═══
        self.specializations_widget = LookupCascadeSelect(
            category="supplier_specialization",
            parent_category="supplier_subcategory",
            columns=2,
            allow_quick_add=True,
            group_icon="✨",
            group_title_prefix="جزئیات تخصصی"
        )
        layout.addWidget(self.specializations_widget)

        # ═══ توضیحات تخصصی ═══
        self.specialty_input = QTextEdit()
        self.specialty_input.setPlaceholderText(
            "توضیحات دقیق درباره حوزه فعالیت... مثلاً:\n"
            "ورق استیل 304 ضخامت ۱ تا ۱۰ میلی‌متر\n"
            "برشکاری لیزر تا ۳۰ میلی‌متر"
        )
        self.specialty_input.setMinimumHeight(80)
        self.specialty_input.setMaximumHeight(100)
        layout.addWidget(
            self._make_field("📝  توضیحات تخصصی", self.specialty_input)
        )

        # ═══ سطح + وضعیت ═══
        row2 = QHBoxLayout()
        row2.setSpacing(12)

        self.tier_combo = LookupComboBox("supplier_tier", allow_empty=False)
        self.tier_combo.setMinimumHeight(36)
        row2.addWidget(self._make_field("سطح", self.tier_combo), 1)

        self.status_combo = QComboBox()
        self.status_combo.setMinimumHeight(36)
        for status in SupplierStatus:
            self.status_combo.addItem(
                SupplierStatus.to_persian(status.value), status.value
            )
        row2.addWidget(self._make_field("وضعیت", self.status_combo), 1)

        layout.addLayout(row2)

        # ═══ تاریخ شروع همکاری ═══
        self.coop_start_input = PersianDateEdit(allow_empty=True)
        layout.addWidget(
            self._make_field("📅  شروع همکاری", self.coop_start_input)
        )

        layout.addStretch(1)
        return self._wrap_scroll(content)

    # ── Handlers: تغییر سطوح ──

    def _on_types_changed(self, selected_codes: list):
        """Level 1 تغییر کرد → Level 2 آپدیت"""
        self.subcategories_widget.update_parents(selected_codes)
        # چون Level 2 تغییر کرد، Level 3 هم پاک شه
        self.specializations_widget.update_from_dict(
            self.subcategories_widget.get_selected_codes()
        )

    def _on_subcategories_changed(self, selected_dict: dict):
        """Level 2 تغییر کرد → Level 3 آپدیت"""
        self.specializations_widget.update_from_dict(selected_dict)

    # ══════════════════════════════════════════════════════════════════
    # تب ۲: اطلاعات تماس
    # ══════════════════════════════════════════════════════════════════

    def _build_contact_tab(self) -> QScrollArea:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # مسئول فروش
        person_group = QGroupBox("👤  مسئول فروش")
        person_group.setObjectName("formGroup")
        pv = QVBoxLayout(person_group)
        pv.setContentsMargins(14, 20, 14, 14)
        pv.setSpacing(12)

        person_row = QHBoxLayout()
        person_row.setSpacing(12)

        self.contact_name_input = QLineEdit()
        self.contact_name_input.setPlaceholderText("نام و نام خانوادگی")
        self.contact_name_input.setMinimumHeight(36)
        person_row.addWidget(self._make_field("نام", self.contact_name_input), 1)

        self.contact_position_input = QLineEdit()
        self.contact_position_input.setPlaceholderText("مثلاً: مدیر فروش")
        self.contact_position_input.setMinimumHeight(36)
        person_row.addWidget(self._make_field("سمت", self.contact_position_input), 1)

        pv.addLayout(person_row)
        layout.addWidget(person_group)

        # راه‌های ارتباطی
        contact_group = QGroupBox("📞  راه‌های ارتباطی")
        contact_group.setObjectName("formGroup")
        cv = QVBoxLayout(contact_group)
        cv.setContentsMargins(14, 20, 14, 14)
        cv.setSpacing(12)

        row1 = QHBoxLayout()
        row1.setSpacing(12)

        self.mobile_input = QLineEdit()
        self.mobile_input.setPlaceholderText("09xxxxxxxxx")
        self.mobile_input.setMinimumHeight(36)
        row1.addWidget(self._make_field("موبایل", self.mobile_input), 1)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("021-xxxxxxxx")
        self.phone_input.setMinimumHeight(36)
        row1.addWidget(self._make_field("تلفن ثابت", self.phone_input), 1)

        cv.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(12)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("example@company.com")
        self.email_input.setMinimumHeight(36)
        row2.addWidget(self._make_field("ایمیل", self.email_input), 1)

        self.website_input = QLineEdit()
        self.website_input.setPlaceholderText("https://www.example.com")
        self.website_input.setMinimumHeight(36)
        row2.addWidget(self._make_field("وب‌سایت", self.website_input), 1)

        cv.addLayout(row2)
        layout.addWidget(contact_group)

        # آدرس
        addr_group = QGroupBox("📍  آدرس")
        addr_group.setObjectName("formGroup")
        av = QVBoxLayout(addr_group)
        av.setContentsMargins(14, 20, 14, 14)
        av.setSpacing(12)

        loc_row = QHBoxLayout()
        loc_row.setSpacing(12)

        self.province_input = QLineEdit()
        self.province_input.setPlaceholderText("استان")
        self.province_input.setMinimumHeight(36)
        loc_row.addWidget(self._make_field("استان", self.province_input), 1)

        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("شهر")
        self.city_input.setMinimumHeight(36)
        loc_row.addWidget(self._make_field("شهر", self.city_input), 1)

        av.addLayout(loc_row)

        self.office_address_input = QTextEdit()
        self.office_address_input.setPlaceholderText("آدرس دفتر مرکزی")
        self.office_address_input.setMinimumHeight(70)
        self.office_address_input.setMaximumHeight(80)
        av.addWidget(self._make_field("آدرس دفتر", self.office_address_input))

        self.factory_address_input = QTextEdit()
        self.factory_address_input.setPlaceholderText("آدرس کارخانه (در صورت وجود)")
        self.factory_address_input.setMinimumHeight(70)
        self.factory_address_input.setMaximumHeight(80)
        av.addWidget(self._make_field("آدرس کارخانه", self.factory_address_input))

        layout.addWidget(addr_group)
        layout.addStretch(1)

        return self._wrap_scroll(content)

    # ══════════════════════════════════════════════════════════════════
    # تب ۳: اطلاعات مالی
    # ══════════════════════════════════════════════════════════════════

    def _build_finance_tab(self) -> QScrollArea:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # بانکی و مالیاتی
        bank_group = QGroupBox("🏦  اطلاعات بانکی و مالیاتی")
        bank_group.setObjectName("formGroup")
        bv = QVBoxLayout(bank_group)
        bv.setContentsMargins(14, 20, 14, 14)
        bv.setSpacing(12)

        self.national_id_input = QLineEdit()
        self.national_id_input.setPlaceholderText("14xxxxxxxxxx")
        self.national_id_input.setMinimumHeight(36)
        bv.addWidget(self._make_field("شناسه ملی / کد اقتصادی", self.national_id_input))

        row1 = QHBoxLayout()
        row1.setSpacing(12)

        self.account_number_input = QLineEdit()
        self.account_number_input.setPlaceholderText("شماره حساب یا IBAN")
        self.account_number_input.setMinimumHeight(36)
        row1.addWidget(self._make_field("شماره حساب", self.account_number_input), 1)

        self.bank_name_input = QLineEdit()
        self.bank_name_input.setPlaceholderText("مثلاً: بانک ملت")
        self.bank_name_input.setMinimumHeight(36)
        row1.addWidget(self._make_field("نام بانک", self.bank_name_input), 1)

        bv.addLayout(row1)
        layout.addWidget(bank_group)

        # شرایط پرداخت
        pay_group = QGroupBox("💳  شرایط پرداخت")
        pay_group.setObjectName("formGroup")
        pv = QVBoxLayout(pay_group)
        pv.setContentsMargins(14, 20, 14, 14)
        pv.setSpacing(12)

        row1 = QHBoxLayout()
        row1.setSpacing(12)

        self.payment_terms_combo = LookupComboBox("payment_terms", allow_empty=True)
        self.payment_terms_combo.setMinimumHeight(36)
        row1.addWidget(self._make_field("نوع پرداخت", self.payment_terms_combo), 1)

        self.currency_combo = LookupComboBox("currency", allow_empty=False)
        self.currency_combo.setMinimumHeight(36)
        row1.addWidget(self._make_field("ارز معامله", self.currency_combo), 1)

        pv.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(12)

        self.credit_days_input = QSpinBox()
        self.credit_days_input.setRange(0, 365)
        self.credit_days_input.setSuffix(" روز")
        self.credit_days_input.setSpecialValueText("—")
        self.credit_days_input.setMinimumHeight(36)
        row2.addWidget(self._make_field("مدت تسویه", self.credit_days_input), 1)

        self.credit_limit_input = QDoubleSpinBox()
        self.credit_limit_input.setRange(0, 999_999_999_999)
        self.credit_limit_input.setDecimals(0)
        self.credit_limit_input.setGroupSeparatorShown(True)
        self.credit_limit_input.setSpecialValueText("—")
        self.credit_limit_input.setMinimumHeight(36)
        row2.addWidget(self._make_field("سقف اعتبار خرید", self.credit_limit_input), 1)

        pv.addLayout(row2)
        layout.addWidget(pay_group)

        # قرارداد
        contract_group = QGroupBox("📄  قرارداد")
        contract_group.setObjectName("formGroup")
        cv = QVBoxLayout(contract_group)
        cv.setContentsMargins(14, 20, 14, 14)
        cv.setSpacing(12)

        self.has_contract_cb = QCheckBox("قرارداد فعال دارد")
        self.has_contract_cb.setMinimumHeight(28)
        cv.addWidget(self.has_contract_cb)

        date_row = QHBoxLayout()
        date_row.setSpacing(12)

        self.contract_start_input = PersianDateEdit(allow_empty=True)
        date_row.addWidget(self._make_field("📅  تاریخ شروع", self.contract_start_input), 1)

        self.contract_end_input = PersianDateEdit(allow_empty=True)
        date_row.addWidget(self._make_field("📅  تاریخ پایان", self.contract_end_input), 1)

        cv.addLayout(date_row)
        layout.addWidget(contract_group)

        # توضیحات
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("توضیحات اضافی (اختیاری)")
        self.description_input.setMinimumHeight(70)
        self.description_input.setMaximumHeight(90)
        layout.addWidget(self._make_field("توضیحات", self.description_input))

        layout.addStretch(1)
        return self._wrap_scroll(content)

    # ══════════════════════════════════════════════════════════════════
    # Load Data (ویرایش)
    # ══════════════════════════════════════════════════════════════════

    def _load_data(self):
        try:
            with get_session() as session:
                svc = SupplierService(session)
                sup = svc.get_by_id(self.supplier_id)

                # ── تب ۱ ──
                self.code_label.setText(sup.code)
                self.name_input.setText(sup.name)
                self.trade_name_input.setText(sup.trade_name or "")

                # Level 1: انواع
                types_list = sup.supplier_types or []
                self.types_widget.set_selected_codes(types_list)
                self.subcategories_widget.update_parents(types_list)

                # Level 2: زیرشاخه‌ها
                subs_data = sup.subcategories or {}
                self.subcategories_widget.set_selected_codes(subs_data)
                # حالا Level 3 رو trigger کن
                self.specializations_widget.update_from_dict(subs_data)

                # Level 3: جزئیات
                specs_data = sup.specializations or {}
                self.specializations_widget.set_selected_codes(specs_data)

                # توضیحات تخصصی
                self.specialty_input.setPlainText(sup.specialty_description or "")

                # سطح
                tier_code = (sup.tier or "b").lower()
                self.tier_combo.set_current_code(tier_code)

                # وضعیت
                idx = self.status_combo.findData(sup.status)
                if idx >= 0:
                    self.status_combo.setCurrentIndex(idx)

                # تاریخ شروع همکاری
                self.coop_start_input.set_date(sup.cooperation_start)

                # ── تب ۲ ──
                self.contact_name_input.setText(sup.contact_name or "")
                self.contact_position_input.setText(sup.contact_position or "")
                self.mobile_input.setText(sup.mobile or "")
                self.phone_input.setText(sup.phone or "")
                self.email_input.setText(sup.email or "")
                self.website_input.setText(sup.website or "")
                self.province_input.setText(sup.province or "")
                self.city_input.setText(sup.city or "")
                self.office_address_input.setPlainText(sup.office_address or "")
                self.factory_address_input.setPlainText(sup.factory_address or "")

                # ── تب ۳ ──
                self.national_id_input.setText(sup.national_id or "")
                self.account_number_input.setText(sup.account_number or "")
                self.bank_name_input.setText(sup.bank_name or "")

                if sup.payment_terms:
                    self.payment_terms_combo.set_current_code(sup.payment_terms.lower())

                if sup.credit_days:
                    self.credit_days_input.setValue(sup.credit_days)

                if sup.credit_limit:
                    self.credit_limit_input.setValue(float(sup.credit_limit))

                currency_code = (sup.currency or "irr").lower()
                self.currency_combo.set_current_code(currency_code)

                self.has_contract_cb.setChecked(sup.has_active_contract)
                self.contract_start_input.set_date(sup.contract_start)
                self.contract_end_input.set_date(sup.contract_end)

                self.description_input.setPlainText(sup.description or "")

        except Exception as e:
            logger.error(f"خطا در بارگذاری تأمین‌کننده: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    # ══════════════════════════════════════════════════════════════════
    # ذخیره
    # ══════════════════════════════════════════════════════════════════

    def _collect_data(self) -> dict:
        credit_days_val = self.credit_days_input.value()
        credit_limit_val = self.credit_limit_input.value()

        return {
            "name":       self.name_input.text().strip(),
            "trade_name": self.trade_name_input.text().strip() or None,

            # سه سطح دسته‌بندی
            "supplier_types":   self.types_widget.get_selected_codes(),
            "subcategories":    self.subcategories_widget.get_selected_codes(),
            "specializations":  self.specializations_widget.get_selected_codes(),

            "specialty_description": self.specialty_input.toPlainText().strip() or None,

            "tier":   self.tier_combo.get_current_code() or "b",
            "status": self.status_combo.currentData(),

            "cooperation_start": self.coop_start_input.get_date(),

            "contact_name":     self.contact_name_input.text().strip() or None,
            "contact_position": self.contact_position_input.text().strip() or None,
            "mobile":           self.mobile_input.text().strip() or None,
            "phone":            self.phone_input.text().strip() or None,
            "email":            self.email_input.text().strip() or None,
            "website":          self.website_input.text().strip() or None,
            "province":         self.province_input.text().strip() or None,
            "city":             self.city_input.text().strip() or None,
            "office_address":   self.office_address_input.toPlainText().strip() or None,
            "factory_address":  self.factory_address_input.toPlainText().strip() or None,

            "national_id":    self.national_id_input.text().strip() or None,
            "account_number": self.account_number_input.text().strip() or None,
            "bank_name":      self.bank_name_input.text().strip() or None,
            "payment_terms":  self.payment_terms_combo.get_current_code(),
            "credit_days":    credit_days_val if credit_days_val > 0 else None,
            "credit_limit":   Decimal(str(credit_limit_val)) if credit_limit_val > 0 else None,
            "currency":       self.currency_combo.get_current_code() or "irr",

            "has_active_contract": self.has_contract_cb.isChecked(),
            "contract_start":      self.contract_start_input.get_date() if self.has_contract_cb.isChecked() else None,
            "contract_end":        self.contract_end_input.get_date()   if self.has_contract_cb.isChecked() else None,

            "description": self.description_input.toPlainText().strip() or None,
        }

    def _validate(self, data: dict) -> str | None:
        if not data.get("name"):
            return "نام شرکت الزامی است"
        if len(data["name"]) < 2:
            return "نام شرکت باید حداقل ۲ کاراکتر باشد"
        if not data.get("supplier_types"):
            return "حداقل یک نوع تأمین‌کننده انتخاب کنید"
        return None

    def _on_save(self):
        try:
            data = self._collect_data()

            error = self._validate(data)
            if error:
                Toast.warning(self, error)
                return

            with get_session() as session:
                svc = SupplierService(session)

                if self.is_edit:
                    schema = SupplierUpdate(**data)
                    svc.update(self.supplier_id, schema)
                else:
                    schema = SupplierCreate(**data)
                    svc.create(schema)

            self.accept()

        except DuplicateError as e:
            Toast.warning(self, str(e))
        except Exception as e:
            logger.error(f"خطا در ذخیره تأمین‌کننده: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")