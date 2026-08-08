"""
Kamand - MoneyWidget
ورود مبلغ با انتخاب ارز

قرارداد ذخیره‌سازی:
- ریال و مشتقات (هزار/میلیون/میلیارد ریال) → همیشه به ریال ذخیره می‌شود
- دلار / یورو → با مقدار خودشون + currency جدا ذخیره می‌شود
"""
from decimal import Decimal
from typing import Optional, Tuple

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout

from app.ui.widgets.smart_spinbox import SmartDoubleSpinBox
from app.ui.widgets.lookup_combo_with_add import LookupComboBoxWithAdd
from app.enums.lookup_categories import LookupCategory


# نسبت هر ارز به ریال — با code های واقعی از DB
CURRENCY_TO_RIAL = {
    "irr":          Decimal("1"),
    "hzar_ryal":    Decimal("1_000"),
    "mylyvn_ryal":  Decimal("1_000_000"),
    "mylyard_ryal": Decimal("1_000_000_000"),
}

FOREIGN_CURRENCIES = {"usd", "eur"}

# پیش‌فرض نمایش
DEFAULT_DISPLAY_CURRENCY = "mylyvn_ryal"


class MoneyWidget(QWidget):
    """ورود مبلغ + ارز"""

    valueChanged = Signal()

    def __init__(
        self,
        default_currency: str = DEFAULT_DISPLAY_CURRENCY,
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

        # ComboBox ارز
        self.currency_combo = LookupComboBoxWithAdd(
            LookupCategory.CURRENCY.value,
        )
        self.currency_combo.setMinimumHeight(36)
        self.currency_combo.setMinimumWidth(180)
        self.currency_combo.setMaximumWidth(220)

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

    # ─── API عمومی ───

    def get_amount_and_currency(self) -> Tuple[Optional[Decimal], str]:
        """
        Returns:
            (amount, currency)
            - برای ریال و مشتقات: amount به ریال + currency = "irr"
            - برای دلار/یورو:      amount اصلی + currency = "usd"/"eur"
        """
        val = self.spin.value()
        currency = self._current_currency()

        if val <= 0:
            return (None, currency)

        if currency in FOREIGN_CURRENCIES:
            return (Decimal(str(val)), currency)

        ratio = CURRENCY_TO_RIAL.get(currency, Decimal("1"))
        rial_amount = Decimal(str(val)) * ratio
        return (rial_amount, "irr")

    def set_amount_and_currency(
        self,
        amount: Optional[float | Decimal],
        currency: str = "irr",
    ):
        """
        نمایش مقدار در widget با انتخاب هوشمند واحد نمایش

        Args:
            amount:   مقدار عددی
            currency: "irr" یا "usd" یا "eur"
        """
        if amount is None or amount == 0:
            self.spin.setValue(0)
            self.currency_combo.set_current_code(currency or "irr")
            return

        amt = Decimal(str(amount))

        # ارزهای خارجی — همون رو نمایش بده
        if currency in FOREIGN_CURRENCIES:
            self.currency_combo.set_current_code(currency)
            self.spin.setValue(float(amt))
            return

        # ─── ریال یا مشتقاتش ───

        # اول همه رو به ریال تبدیل کن
        if currency == "irr":
            rial = amt
        else:
            ratio = CURRENCY_TO_RIAL.get(currency, Decimal("1"))
            rial = amt * ratio

        # انتخاب هوشمند واحد نمایش
        if rial >= Decimal("1_000_000_000"):
            display_unit = "mylyard_ryal"
        elif rial >= Decimal("1_000_000"):
            display_unit = "mylyvn_ryal"
        elif rial >= Decimal("1_000"):
            display_unit = "hzar_ryal"
        else:
            display_unit = "irr"

        ratio = CURRENCY_TO_RIAL.get(display_unit, Decimal("1"))
        display_val = float(rial / ratio)

        # اول currency رو تنظیم کن، بعد value رو
        self.currency_combo.set_current_code(display_unit)
        self.spin.setValue(display_val)

    def clear(self):
        self.spin.setValue(0)
        self.currency_combo.set_current_code(self._default_currency)