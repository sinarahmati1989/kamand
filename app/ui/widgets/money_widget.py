"""
Kamand - MoneyWidget
ورود مبلغ با انتخاب ارز

قرارداد ذخیره‌سازی:
- ریال و مشتقاتش (هزار/میلیون/میلیارد ریال) → همیشه به ریال ذخیره می‌شن
- دلار / یورو → با مقدار خودشون + currency جدا ذخیره می‌شن

get_amount_and_currency() برمی‌گرداند:
    (amount_in_base_unit, currency_code)

مثال:
    کاربر تایپ می‌کنه: 500 میلیون ریال
    ذخیره: (500_000_000, "irr")

    کاربر تایپ می‌کنه: 1000 دلار
    ذخیره: (1000, "usd")
"""
from decimal import Decimal
from typing import Optional, Tuple

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout

from app.ui.widgets.smart_spinbox import SmartDoubleSpinBox
from app.ui.widgets.lookup_combo_with_add import LookupComboBoxWithAdd
from app.enums.lookup_categories import LookupCategory


# نسبت هر واحد به ریال (base = irr)
CURRENCY_TO_RIAL = {
    "irr":   Decimal("1"),
    "irr_k": Decimal("1_000"),           # 1 هزار ریال = 1,000 ریال
    "irr_m": Decimal("1_000_000"),       # 1 میلیون ریال = 1,000,000 ریال
    "irr_b": Decimal("1_000_000_000"),   # 1 میلیارد ریال = 1,000,000,000 ریال
}

# ارزهای غیر-ریالی — تبدیل نمی‌شن، خودشون ذخیره می‌شن
FOREIGN_CURRENCIES = {"usd", "eur"}


class MoneyWidget(QWidget):
    """ورود مبلغ + ارز — ریالی به ریال، خارجی به خودشون"""

    valueChanged = Signal()

    def __init__(
        self,
        default_currency: str = "irr_m",  # میلیون ریال — معقول‌ترین
        max_value: float = 999_999_999_999,
        parent=None,
    ):
        super().__init__(parent)
        self._default_currency = default_currency
        self._setup_ui(max_value)
        self.currency_combo.set_current_code(default_currency)

    def _setup_ui(self, max_value: float):
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # ComboBox ارز (Lookup — قابل توسعه)
        self.currency_combo = LookupComboBoxWithAdd(
            LookupCategory.CURRENCY.value,
        )
        self.currency_combo.setMinimumHeight(36)
        self.currency_combo.setMinimumWidth(140)
        self.currency_combo.setMaximumWidth(180)

        # SpinBox مبلغ
        self.spin = SmartDoubleSpinBox()
        self.spin.setRange(0, max_value)
        self.spin.setDecimals(2)
        self.spin.setSingleStep(1)
        self.spin.setGroupSeparatorShown(True)
        self.spin.setSpecialValueText("—")
        self.spin.setMinimumHeight(36)
        self.spin.valueChanged.connect(lambda _: self.valueChanged.emit())

        layout.addWidget(self.currency_combo)
        layout.addWidget(self.spin, 1)

    def _current_currency(self) -> str:
        return self.currency_combo.get_current_code() or "irr"

    # ═══ API عمومی ═══

    def get_amount_and_currency(self) -> Tuple[Optional[Decimal], str]:
        """
        برمی‌گرداند: (مبلغ به base_unit, currency_code)

        - اگر ریالی: (rial_amount, "irr")
        - اگر خارجی: (foreign_amount, "usd"/"eur")
        - اگر صفر: (None, currency_code)
        """
        val = self.spin.value()
        currency = self._current_currency()

        if val <= 0:
            return (None, currency)

        # ارز خارجی → همون مقدار و همون currency
        if currency in FOREIGN_CURRENCIES:
            return (Decimal(str(val)), currency)

        # ارز ریالی → تبدیل به ریال
        ratio = CURRENCY_TO_RIAL.get(currency, Decimal("1"))
        rial_amount = Decimal(str(val)) * ratio
        return (rial_amount, "irr")

    def set_amount_and_currency(
        self,
        amount: Optional[float | Decimal],
        currency: str = "irr",
    ):
        """
        مبلغ و ارز رو ست کن.

        - اگر ریال باشه → با هوشمندی به بهترین واحد نمایش تبدیل می‌شه
        - اگر خارجی باشه → همون‌طور نمایش
        """
        if amount is None or amount == 0:
            self.spin.setValue(0)
            self.currency_combo.set_current_code(currency or "irr")
            return

        amt = Decimal(str(amount))

        # ارز خارجی → مستقیم
        if currency in FOREIGN_CURRENCIES:
            self.currency_combo.set_current_code(currency)
            self.spin.setValue(float(amt))
            return

        # ارز ریالی → همیشه به ریال میاد
        # اگر currency قدیمی چیز دیگه‌ای بود، تبدیل کن به ریال
        if currency == "irr":
            rial = amt
        else:
            ratio = CURRENCY_TO_RIAL.get(currency, Decimal("1"))
            rial = amt * ratio

        # انتخاب هوشمند واحد نمایش
        if rial >= Decimal("1_000_000_000"):     # >= میلیارد ریال
            display_unit = "irr_b"
        elif rial >= Decimal("1_000_000"):       # >= میلیون ریال
            display_unit = "irr_m"
        elif rial >= Decimal("1_000"):           # >= هزار ریال
            display_unit = "irr_k"
        else:
            display_unit = "irr"

        ratio = CURRENCY_TO_RIAL.get(display_unit, Decimal("1"))
        display_val = float(rial / ratio)

        self.currency_combo.set_current_code(display_unit)
        self.spin.setValue(display_val)

    def clear(self):
        self.spin.setValue(0)
        self.currency_combo.set_current_code(self._default_currency)