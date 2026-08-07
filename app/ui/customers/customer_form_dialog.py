"""
Kamand - Customer Form Dialog
دیالوگ افزودن/ویرایش مشتری با ۳ Tab مدرن:
• اطلاعات پایه
• اطلاعات تماس
• اطلاعات مالی
"""
import logging
from decimal import Decimal

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QTextEdit,
    QPushButton, QTabWidget, QWidget, QGroupBox,
    QScrollArea, QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from pydantic import ValidationError as PydanticError

from app.services.customer_service import CustomerService
from app.schemas.customer_schema import (
    CustomerCreateDTO, CustomerUpdateDTO,
)
from app.database.session import get_session
from app.enums.customer_enums import CustomerStatus
from app.enums.lookup_categories import LookupCategory
from app.core.exceptions import DuplicateError
from app.ui.widgets.toast import Toast
from app.ui.widgets.persian_date_edit import PersianDateEdit
from app.ui.widgets.lookup_combo import LookupComboBox
from app.ui.widgets.lookup_combo_with_add import LookupComboBoxWithAdd
from app.ui.widgets.smart_spinbox import SmartSpinBox
from app.ui.widgets.money_widget import MoneyWidget

logger = logging.getLogger(__name__)


class CustomerFormDialog(QDialog):
    """فرم افزودن/ویرایش مشتری با ۳ Tab کامل"""

    def __init__(self, customer_id: int | None = None, parent=None):
        super().__init__(parent)
        self.customer_id = customer_id
        self.is_edit = customer_id is not None

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowTitle(
            "ویرایش مشتری" if self.is_edit else "افزودن مشتری جدید"
        )
        self.setMinimumSize(860, 720)
        self.resize(900, 760)

        self._setup_ui()

        if self.is_edit:
            self._load_data()

    # ═══════════════ Setup ═══════════════

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # عنوان
        title_text = (
            "ویرایش مشتری" if self.is_edit
            else "افزودن مشتری جدید"
        )
        title = QLabel(title_text)
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # کد (فقط در حالت ویرایش)
        if self.is_edit:
            code_wrapper = QWidget()
            ch = QHBoxLayout(code_wrapper)
            ch.setContentsMargins(0, 0, 0, 0)
            ch.setSpacing(8)

            code_lbl = QLabel("کد مشتری:")
            code_lbl.setObjectName("fieldLabel")

            self.code_label = QLabel("—")
            self.code_label.setStyleSheet(
                "color: #6366F1; font-weight: bold; font-size: 14px;"
            )

            ch.addWidget(code_lbl)
            ch.addWidget(self.code_label)
            ch.addStretch()
            layout.addWidget(code_wrapper)

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setObjectName("customerTabs")
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

    # ═══════════════ Helpers ═══════════════

    def _make_field(
        self, label_text: str, widget: QWidget, required: bool = False
    ) -> QWidget:
        wrapper = QWidget()
        v = QVBoxLayout(wrapper)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(6)

        label_full = f"{label_text} *" if required else label_text
        lbl = QLabel(label_full)
        lbl.setObjectName("fieldLabel")
        lbl.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        if required:
            lbl.setStyleSheet(
                "QLabel#fieldLabel { color: #6366F1; font-weight: 600; }"
            )

        v.addWidget(lbl)
        v.addWidget(widget)
        return wrapper

    def _wrap_scroll(self, content: QWidget) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll.setWidget(content)
        return scroll

    def _apply_persian_font(self, text_edit: QTextEdit):
        """فونت Vazirmatn روی QTextEdit"""
        font = QFont("Vazirmatn", 10)
        text_edit.setFont(font)
        text_edit.document().setDefaultFont(font)

    # ═══════════════ Tab 1: اطلاعات پایه ═══════════════

    def _build_basic_tab(self) -> QScrollArea:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # ─── گروه هویت ───
        identity = QGroupBox("🏢  هویت شرکت/مشتری")
        identity.setObjectName("formGroup")
        iv = QVBoxLayout(identity)
        iv.setContentsMargins(14, 20, 14, 14)
        iv.setSpacing(12)

        # کد (فقط در حالت افزودن)
        if not self.is_edit:
            self.code_input = QLineEdit()
            self.code_input.setPlaceholderText(
                "خودکار: CUS-0001 (یا خودتان وارد کنید)"
            )
            self.code_input.setMinimumHeight(36)
            self.code_input.setMaximumWidth(280)

            code_row = QHBoxLayout()
            code_row.addWidget(
                self._make_field("کد مشتری", self.code_input)
            )
            code_row.addStretch()
            iv.addLayout(code_row)
        else:
            self.code_input = None

        # نام + نام تجاری
        row1 = QHBoxLayout()
        row1.setSpacing(12)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("نام رسمی شرکت یا مشتری")
        self.name_input.setMinimumHeight(36)
        row1.addWidget(
            self._make_field("نام شرکت", self.name_input, required=True), 1
        )

        self.trade_name_input = QLineEdit()
        self.trade_name_input.setPlaceholderText(
            "نام تجاری/برند (اختیاری)"
        )
        self.trade_name_input.setMinimumHeight(36)
        row1.addWidget(
            self._make_field("نام تجاری", self.trade_name_input), 1
        )

        iv.addLayout(row1)

        # نوع + سطح
        row2 = QHBoxLayout()
        row2.setSpacing(12)

        self.customer_type_combo = LookupComboBoxWithAdd(
            LookupCategory.CUSTOMER_TYPE.value,
        )
        self.customer_type_combo.setMinimumHeight(36)
        row2.addWidget(
            self._make_field(
                "نوع مشتری", self.customer_type_combo, required=True
            ), 1
        )

        self.tier_combo = LookupComboBox(
            LookupCategory.CUSTOMER_TIER.value,
            allow_empty=False,
        )
        self.tier_combo.setMinimumHeight(36)
        row2.addWidget(self._make_field("سطح مشتری", self.tier_combo), 1)

        iv.addLayout(row2)

        # شناسه ملی + وضعیت
        row3 = QHBoxLayout()
        row3.setSpacing(12)

        self.national_id_input = QLineEdit()
        self.national_id_input.setPlaceholderText(
            "شناسه ملی / کد ملی / کد اقتصادی"
        )
        self.national_id_input.setMinimumHeight(36)
        row3.addWidget(
            self._make_field(
                "شناسه ملی / کد اقتصادی", self.national_id_input
            ), 1
        )

        # وضعیت (فقط در ویرایش)
        if self.is_edit:
            self.status_combo = QComboBox()
            self.status_combo.setMinimumHeight(36)
            for st in CustomerStatus:
                self.status_combo.addItem(st.label, st.value)
            row3.addWidget(
                self._make_field("وضعیت", self.status_combo), 1
            )
        else:
            self.status_combo = None
            row3.addStretch(1)

        iv.addLayout(row3)

        layout.addWidget(identity)

        # ─── گروه همکاری ───
        coop = QGroupBox("🤝  همکاری")
        coop.setObjectName("formGroup")
        cv = QVBoxLayout(coop)
        cv.setContentsMargins(14, 20, 14, 14)
        cv.setSpacing(12)

        self.coop_start_input = PersianDateEdit(allow_empty=True)
        cv.addWidget(
            self._make_field(
                "📅  تاریخ شروع همکاری", self.coop_start_input
            )
        )

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText(
            "یادداشت‌ها، نکات مهم درباره مشتری..."
        )
        self.notes_input.setMinimumHeight(80)
        self.notes_input.setMaximumHeight(110)
        self._apply_persian_font(self.notes_input)
        cv.addWidget(self._make_field("یادداشت‌ها", self.notes_input))

        layout.addWidget(coop)
        layout.addStretch(1)

        return self._wrap_scroll(content)

    # ═══════════════ Tab 2: اطلاعات تماس ═══════════════

    def _build_contact_tab(self) -> QScrollArea:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # ─── مسئول فروش/رابط ───
        person = QGroupBox("👤  شخص رابط")
        person.setObjectName("formGroup")
        pv = QVBoxLayout(person)
        pv.setContentsMargins(14, 20, 14, 14)
        pv.setSpacing(12)

        row1 = QHBoxLayout()
        row1.setSpacing(12)

        self.contact_name_input = QLineEdit()
        self.contact_name_input.setPlaceholderText(
            "نام و نام خانوادگی"
        )
        self.contact_name_input.setMinimumHeight(36)
        row1.addWidget(
            self._make_field("نام رابط", self.contact_name_input), 1
        )

        self.contact_position_input = QLineEdit()
        self.contact_position_input.setPlaceholderText(
            "مثلاً: مدیر خرید"
        )
        self.contact_position_input.setMinimumHeight(36)
        row1.addWidget(
            self._make_field("سمت", self.contact_position_input), 1
        )

        pv.addLayout(row1)

        self.contact_mobile_input = QLineEdit()
        self.contact_mobile_input.setPlaceholderText("09xxxxxxxxx")
        self.contact_mobile_input.setMinimumHeight(36)
        pv.addWidget(
            self._make_field(
                "موبایل رابط", self.contact_mobile_input
            )
        )

        layout.addWidget(person)

        # ─── ارتباط شرکت ───
        contact = QGroupBox("📞  راه‌های ارتباطی شرکت")
        contact.setObjectName("formGroup")
        cv = QVBoxLayout(contact)
        cv.setContentsMargins(14, 20, 14, 14)
        cv.setSpacing(12)

        row2 = QHBoxLayout()
        row2.setSpacing(12)

        self.mobile_input = QLineEdit()
        self.mobile_input.setPlaceholderText("09xxxxxxxxx")
        self.mobile_input.setMinimumHeight(36)
        row2.addWidget(
            self._make_field("موبایل شرکت", self.mobile_input), 1
        )

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("021-xxxxxxxx")
        self.phone_input.setMinimumHeight(36)
        row2.addWidget(
            self._make_field("تلفن ثابت", self.phone_input), 1
        )

        cv.addLayout(row2)

        row3 = QHBoxLayout()
        row3.setSpacing(12)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("example@company.com")
        self.email_input.setMinimumHeight(36)
        row3.addWidget(self._make_field("ایمیل", self.email_input), 1)

        self.website_input = QLineEdit()
        self.website_input.setPlaceholderText("https://www.example.com")
        self.website_input.setMinimumHeight(36)
        row3.addWidget(
            self._make_field("وب‌سایت", self.website_input), 1
        )

        cv.addLayout(row3)
        layout.addWidget(contact)

        # ─── آدرس ───
        addr = QGroupBox("📍  آدرس")
        addr.setObjectName("formGroup")
        av = QVBoxLayout(addr)
        av.setContentsMargins(14, 20, 14, 14)
        av.setSpacing(12)

        row4 = QHBoxLayout()
        row4.setSpacing(12)

        self.province_input = QLineEdit()
        self.province_input.setPlaceholderText("استان")
        self.province_input.setMinimumHeight(36)
        row4.addWidget(self._make_field("استان", self.province_input), 1)

        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("شهر")
        self.city_input.setMinimumHeight(36)
        row4.addWidget(self._make_field("شهر", self.city_input), 1)

        av.addLayout(row4)

        self.address_input = QTextEdit()
        self.address_input.setPlaceholderText("آدرس کامل...")
        self.address_input.setMinimumHeight(70)
        self.address_input.setMaximumHeight(90)
        self._apply_persian_font(self.address_input)
        av.addWidget(self._make_field("آدرس", self.address_input))

        self.postal_code_input = QLineEdit()
        self.postal_code_input.setPlaceholderText("کدپستی ۱۰ رقمی")
        self.postal_code_input.setMinimumHeight(36)
        self.postal_code_input.setMaximumWidth(220)

        postal_row = QHBoxLayout()
        postal_row.addWidget(
            self._make_field("کدپستی", self.postal_code_input)
        )
        postal_row.addStretch()
        av.addLayout(postal_row)

        layout.addWidget(addr)
        layout.addStretch(1)

        return self._wrap_scroll(content)

    # ═══════════════ Tab 3: اطلاعات مالی ═══════════════

    def _build_finance_tab(self) -> QScrollArea:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # ─── شرایط پرداخت ───
        pay = QGroupBox("💳  شرایط پرداخت")
        pay.setObjectName("formGroup")
        pv = QVBoxLayout(pay)
        pv.setContentsMargins(14, 20, 14, 14)
        pv.setSpacing(12)

        row1 = QHBoxLayout()
        row1.setSpacing(12)

        self.payment_terms_combo = LookupComboBoxWithAdd(
            LookupCategory.PAYMENT_TERMS.value,
            allow_empty=True,
        )
        self.payment_terms_combo.setMinimumHeight(36)
        row1.addWidget(
            self._make_field(
                "نوع پرداخت", self.payment_terms_combo
            ), 1
        )

        self.currency_combo = LookupComboBoxWithAdd(
            LookupCategory.CURRENCY.value,
            allow_empty=False,
        )
        self.currency_combo.setMinimumHeight(36)
        self.currency_combo.set_current_code("irr")
        row1.addWidget(
            self._make_field("ارز معاملات", self.currency_combo), 1
        )

        pv.addLayout(row1)

        self.credit_days_input = SmartSpinBox()
        self.credit_days_input.setRange(0, 365)
        self.credit_days_input.setSuffix(" روز")
        self.credit_days_input.setSpecialValueText("—")
        self.credit_days_input.setMinimumHeight(36)
        self.credit_days_input.setMaximumWidth(220)

        days_row = QHBoxLayout()
        days_row.addWidget(
            self._make_field("مدت تسویه", self.credit_days_input)
        )
        days_row.addStretch()
        pv.addLayout(days_row)

        layout.addWidget(pay)

        # ─── سقف اعتبار ───
        credit = QGroupBox("💰  اعتبار مشتری")
        credit.setObjectName("formGroup")
        crv = QVBoxLayout(credit)
        crv.setContentsMargins(14, 20, 14, 14)
        crv.setSpacing(12)

        self.credit_limit_widget = MoneyWidget()
        crv.addWidget(
            self._make_field(
                "سقف اعتبار خرید", self.credit_limit_widget
            )
        )

        layout.addWidget(credit)

        # ─── توضیحات مالی ───
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText(
            "توضیحات مالی، شرایط ویژه، تخفیفات..."
        )
        self.description_input.setMinimumHeight(80)
        self.description_input.setMaximumHeight(110)
        self._apply_persian_font(self.description_input)
        layout.addWidget(
            self._make_field("توضیحات مالی", self.description_input)
        )

        layout.addStretch(1)

        return self._wrap_scroll(content)

    # ═══════════════ Load Data (ویرایش) ═══════════════

    def _load_data(self):
        try:
            with get_session() as session:
                c = CustomerService(session).get_by_id(self.customer_id)

            # کد
            self.code_label.setText(c.code or "—")

            # پایه
            self.name_input.setText(c.name)
            self.trade_name_input.setText(c.trade_name or "")

            if c.customer_type:
                self.customer_type_combo.set_current_code(c.customer_type)

            if c.tier:
                self.tier_combo.set_current_code(c.tier)

            self.national_id_input.setText(c.national_id or "")

            if self.status_combo and c.status:
                idx = self.status_combo.findData(c.status)
                if idx >= 0:
                    self.status_combo.setCurrentIndex(idx)

            self.coop_start_input.set_date(c.cooperation_start)
            self.notes_input.setPlainText(c.notes or "")

            # تماس
            self.contact_name_input.setText(c.contact_name or "")
            self.contact_position_input.setText(c.contact_position or "")
            self.contact_mobile_input.setText(c.contact_mobile or "")
            self.mobile_input.setText(c.mobile or "")
            self.phone_input.setText(c.phone or "")
            self.email_input.setText(c.email or "")
            self.website_input.setText(c.website or "")
            self.province_input.setText(c.province or "")
            self.city_input.setText(c.city or "")
            self.address_input.setPlainText(c.address or "")
            self.postal_code_input.setText(c.postal_code or "")

            # مالی
            if c.payment_terms:
                self.payment_terms_combo.set_current_code(c.payment_terms)
            if c.currency:
                self.currency_combo.set_current_code(c.currency)

            if c.credit_days:
                self.credit_days_input.setValue(c.credit_days)

            if c.credit_limit is not None:
                self.credit_limit_widget.set_amount_and_currency(
                    float(c.credit_limit),
                    c.currency or "irr",
                )

            self.description_input.setPlainText(c.description or "")

        except Exception as e:
            logger.error(
                f"خطا در بارگذاری مشتری: {e}", exc_info=True
            )
            Toast.error(self, f"خطا در بارگذاری: {e}")
            self.reject()

    # ═══════════════ Collect + Save ═══════════════

    def _collect(self) -> dict:
        credit_days_val = self.credit_days_input.value()
        credit_amount, _ = (
            self.credit_limit_widget.get_amount_and_currency()
        )

        data = {
            # پایه
            "name":              self.name_input.text().strip(),
            "trade_name":        self.trade_name_input.text().strip() or None,
            "customer_type":     self.customer_type_combo.get_current_code(),
            "tier":              self.tier_combo.get_current_code() or "b",
            "national_id":       self.national_id_input.text().strip() or None,
            "cooperation_start": self.coop_start_input.get_date(),
            "notes":             self.notes_input.toPlainText().strip() or None,

            # تماس
            "contact_name":     self.contact_name_input.text().strip() or None,
            "contact_position": self.contact_position_input.text().strip() or None,
            "contact_mobile":   self.contact_mobile_input.text().strip() or None,
            "mobile":           self.mobile_input.text().strip() or None,
            "phone":            self.phone_input.text().strip() or None,
            "email":            self.email_input.text().strip() or None,
            "website":          self.website_input.text().strip() or None,
            "province":         self.province_input.text().strip() or None,
            "city":             self.city_input.text().strip() or None,
            "address":          self.address_input.toPlainText().strip() or None,
            "postal_code":      self.postal_code_input.text().strip() or None,

            # مالی
            "payment_terms": self.payment_terms_combo.get_current_code(),
            "currency":      self.currency_combo.get_current_code() or "irr",
            "credit_days":   credit_days_val if credit_days_val > 0 else None,
            "credit_limit":  credit_amount,
            "description":   self.description_input.toPlainText().strip() or None,
        }

        # کد فقط در حالت جدید
        if not self.is_edit and self.code_input:
            data["code"] = self.code_input.text().strip() or None

        # وضعیت فقط در ویرایش
        if self.is_edit and self.status_combo:
            data["status"] = self.status_combo.currentData()

        return data

    def _on_save(self):
        try:
            data = self._collect()

            with get_session() as session:
                svc = CustomerService(session)
                if self.is_edit:
                    # کد و status جدا هستن
                    svc.update(
                        self.customer_id,
                        CustomerUpdateDTO(**data),
                    )
                else:
                    svc.create(CustomerCreateDTO(**data))

            self.accept()

        except PydanticError as e:
            msgs = [
                err["msg"].replace("Value error, ", "")
                for err in e.errors()
            ]
            Toast.error(self, " | ".join(msgs))
        except DuplicateError as e:
            Toast.warning(self, str(e))
        except Exception as e:
            logger.error(
                f"خطا در ذخیره مشتری: {e}", exc_info=True
            )
            Toast.error(self, f"خطا: {e}")