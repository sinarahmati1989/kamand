"""
دیالوگ افزودن / ویرایش مشتری
"""
import logging

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit,
    QComboBox, QFrame, QTabWidget, QWidget,
)
from PySide6.QtCore import Qt
from pydantic import ValidationError as PydanticError

from app.services.customer_service import CustomerService
from app.schemas.customer_schema import CustomerCreateDTO, CustomerUpdateDTO
from app.enums.customer_enums import CustomerStatus
from app.enums.lookup_categories import LookupCategory
from app.database.session import get_session
from app.core.exceptions import DuplicateError
from app.ui.widgets.lookup_combo import LookupComboBox
from app.ui.widgets.toast import Toast

logger = logging.getLogger(__name__)


class CustomerFormDialog(QDialog):
    """دیالوگ فرم مشتری — دو تب: اطلاعات اصلی / تماس"""

    def __init__(self, customer_id: int | None = None, parent=None):
        super().__init__(parent)
        self._customer_id = customer_id
        self._is_edit = customer_id is not None

        self.setWindowTitle("ویرایش مشتری" if self._is_edit else "افزودن مشتری")
        self.setModal(True)
        self.setMinimumWidth(520)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self._setup_ui()

        if self._is_edit:
            self._load_data()

    # ---------- Setup ----------

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        title = QLabel("ویرایش مشتری" if self._is_edit else "افزودن مشتری جدید")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setObjectName("separator")
        layout.addWidget(sep)

        tabs = QTabWidget()
        tabs.addTab(self._build_main_tab(), "اطلاعات اصلی")
        tabs.addTab(self._build_contact_tab(), "اطلاعات تماس")
        layout.addWidget(tabs)

        layout.addLayout(self._build_buttons())

    def _build_main_tab(self) -> QWidget:
        tab = QWidget()
        form = QFormLayout(tab)
        form.setSpacing(12)
        form.setContentsMargins(12, 16, 12, 16)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._name = QLineEdit()
        self._name.setPlaceholderText("نام رسمی شرکت یا مشتری *")
        self._name.setObjectName("formInput")

        self._trade_name = QLineEdit()
        self._trade_name.setPlaceholderText("نام تجاری (اختیاری)")
        self._trade_name.setObjectName("formInput")

        self._customer_type = LookupComboBox(LookupCategory.CUSTOMER_TYPE.value)
        self._customer_type.setObjectName("formCombo")

        self._national_id = QLineEdit()
        self._national_id.setPlaceholderText("شناسه ملی / کد ملی")
        self._national_id.setObjectName("formInput")

        self._notes = QTextEdit()
        self._notes.setPlaceholderText("توضیحات داخلی...")
        self._notes.setObjectName("formTextArea")
        self._notes.setMaximumHeight(80)

        form.addRow("نام شرکت *", self._name)
        form.addRow("نام تجاری", self._trade_name)
        form.addRow("نوع مشتری", self._customer_type)
        form.addRow("شناسه ملی", self._national_id)
        form.addRow("توضیحات", self._notes)

        # وضعیت — فقط در ویرایش
        if self._is_edit:
            self._status = QComboBox()
            self._status.setObjectName("formCombo")
            for cs in CustomerStatus:
                self._status.addItem(cs.label, cs.value)
            form.addRow("وضعیت", self._status)
        else:
            self._status = None

        return tab

    def _build_contact_tab(self) -> QWidget:
        tab = QWidget()
        form = QFormLayout(tab)
        form.setSpacing(12)
        form.setContentsMargins(12, 16, 12, 16)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._contact_name = QLineEdit()
        self._contact_name.setPlaceholderText("نام و نام خانوادگی")
        self._contact_name.setObjectName("formInput")

        self._contact_title = QLineEdit()
        self._contact_title.setPlaceholderText("مثال: مدیر خرید")
        self._contact_title.setObjectName("formInput")

        self._contact_mobile = QLineEdit()
        self._contact_mobile.setPlaceholderText("موبایل رابط")
        self._contact_mobile.setObjectName("formInput")

        self._phone = QLineEdit()
        self._phone.setPlaceholderText("تلفن ثابت شرکت")
        self._phone.setObjectName("formInput")

        self._mobile = QLineEdit()
        self._mobile.setPlaceholderText("موبایل شرکت")
        self._mobile.setObjectName("formInput")

        self._email = QLineEdit()
        self._email.setPlaceholderText("ایمیل رسمی")
        self._email.setObjectName("formInput")

        self._address = QTextEdit()
        self._address.setPlaceholderText("آدرس کامل...")
        self._address.setObjectName("formTextArea")
        self._address.setMaximumHeight(72)

        self._postal_code = QLineEdit()
        self._postal_code.setPlaceholderText("کدپستی ۱۰ رقمی")
        self._postal_code.setObjectName("formInput")

        form.addRow("نام رابط", self._contact_name)
        form.addRow("سمت رابط", self._contact_title)
        form.addRow("موبایل رابط", self._contact_mobile)
        form.addRow("--- تماس شرکت ---", QLabel(""))
        form.addRow("تلفن ثابت", self._phone)
        form.addRow("موبایل", self._mobile)
        form.addRow("ایمیل", self._email)
        form.addRow("--- آدرس ---", QLabel(""))
        form.addRow("آدرس", self._address)
        form.addRow("کدپستی", self._postal_code)

        return tab

    def _build_buttons(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)

        save_btn = QPushButton("ذخیره")
        save_btn.setObjectName("neonButton")
        save_btn.setFixedWidth(140)
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._on_save)

        cancel_btn = QPushButton("انصراف")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.setFixedWidth(110)
        cancel_btn.clicked.connect(self.reject)

        row.addWidget(save_btn)
        row.addWidget(cancel_btn)
        row.addStretch()
        return row

    # ---------- Data ----------

    def _load_data(self):
        try:
            with get_session() as session:
                c = CustomerService(session).get_by_id(self._customer_id)

            self._name.setText(c.name)
            self._trade_name.setText(c.trade_name or "")
            self._national_id.setText(c.national_id or "")
            self._notes.setPlainText(c.notes or "")
            self._contact_name.setText(c.contact_name or "")
            self._contact_title.setText(c.contact_title or "")
            self._contact_mobile.setText(c.contact_mobile or "")
            self._phone.setText(c.phone or "")
            self._mobile.setText(c.mobile or "")
            self._email.setText(c.email or "")
            self._address.setPlainText(c.address or "")
            self._postal_code.setText(c.postal_code or "")

            self._customer_type.set_current_code(c.customer_type)

            if self._status and c.status:
                idx = self._status.findData(c.status)
                if idx >= 0:
                    self._status.setCurrentIndex(idx)

        except Exception as e:
            logger.error(f"خطا در بارگذاری مشتری: {e}")
            Toast.error(self, f"خطا در بارگذاری: {e}")
            self.reject()

    def _collect(self) -> dict:
        data = {
            "name":           self._name.text().strip(),
            "trade_name":     self._trade_name.text().strip() or None,
            "customer_type":  self._customer_type.get_current_code(),
            "national_id":    self._national_id.text().strip() or None,
            "notes":          self._notes.toPlainText().strip() or None,
            "contact_name":   self._contact_name.text().strip() or None,
            "contact_title":  self._contact_title.text().strip() or None,
            "contact_mobile": self._contact_mobile.text().strip() or None,
            "phone":          self._phone.text().strip() or None,
            "mobile":         self._mobile.text().strip() or None,
            "email":          self._email.text().strip() or None,
            "address":        self._address.toPlainText().strip() or None,
            "postal_code":    self._postal_code.text().strip() or None,
        }
        if self._is_edit and self._status:
            data["status"] = self._status.currentData()
        return data

    # ---------- Save ----------

    def _on_save(self):
        data = self._collect()
        try:
            with get_session() as session:
                svc = CustomerService(session)
                if self._is_edit:
                    svc.update(self._customer_id, CustomerUpdateDTO(**data))
                else:
                    svc.create(CustomerCreateDTO(**data))
            self.accept()

        except PydanticError as e:
            msgs = [err["msg"].replace("Value error, ", "") for err in e.errors()]
            Toast.error(self, " | ".join(msgs))
        except DuplicateError as e:
            Toast.warning(self, str(e))
        except Exception as e:
            logger.error(f"خطا در ذخیره مشتری: {e}")
            Toast.error(self, f"خطا در ذخیره: {e}")