"""
Kamand - WeightWidget
ورود وزن با انتخاب واحد (گرم / کیلوگرم / تن)

قرارداد ذخیره‌سازی:
- در DB همیشه به کیلوگرم (kg) ذخیره می‌شود
- کاربر می‌تواند با هر واحد وارد و مشاهده کند
- تبدیل خودکار در get_value() و set_value()

استفاده:
    w = WeightWidget()
    w.set_value_kg(2.5)          # نمایش: 2.5 kg
    kg = w.get_value_kg()        # همیشه kg برمی‌گرداند
"""
from decimal import Decimal
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QComboBox

from app.ui.widgets.smart_spinbox import SmartDoubleSpinBox


# نسبت هر واحد به کیلوگرم (base = kg)
UNIT_TO_KG = {
    "gr":  Decimal("0.001"),   # 1 گرم = 0.001 kg
    "kg":  Decimal("1"),        # 1 kg = 1 kg
    "ton": Decimal("1000"),     # 1 تن = 1000 kg
}

UNIT_LABELS = {
    "gr":  "گرم",
    "kg":  "کیلوگرم",
    "ton": "تن",
}


class WeightWidget(QWidget):
    """ورود وزن با واحد قابل انتخاب — ذخیره همیشه به kg"""

    valueChanged = Signal()

    def __init__(
        self,
        default_unit: str = "kg",
        max_value: float = 999_999,
        decimals: int = 4,
        parent=None,
    ):
        super().__init__(parent)
        self._default_unit = default_unit
        self._setup_ui(max_value, decimals)
        self._set_unit(default_unit)

    def _setup_ui(self, max_value: float, decimals: int):
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # ComboBox واحد
        self.unit_combo = QComboBox()
        for code, label in UNIT_LABELS.items():
            self.unit_combo.addItem(label, code)
        self.unit_combo.setMinimumHeight(36)
        self.unit_combo.setMaximumWidth(110)
        self.unit_combo.currentIndexChanged.connect(self._on_unit_changed)

        # SpinBox عدد
        self.spin = SmartDoubleSpinBox()
        self.spin.setRange(0, max_value)
        self.spin.setDecimals(decimals)
        self.spin.setSpecialValueText("—")
        self.spin.setMinimumHeight(36)
        self.spin.valueChanged.connect(lambda _: self.valueChanged.emit())

        layout.addWidget(self.unit_combo)
        layout.addWidget(self.spin, 1)

    def _set_unit(self, code: str):
        idx = self.unit_combo.findData(code)
        if idx >= 0:
            self.unit_combo.setCurrentIndex(idx)

    def _on_unit_changed(self, _idx: int):
        """تغییر واحد → عدد نمایشی رو تبدیل کن"""
        self.valueChanged.emit()

    def _current_unit(self) -> str:
        return self.unit_combo.currentData() or "kg"

    # ═══ API عمومی ═══

    def get_value_kg(self) -> Optional[Decimal]:
        """
        مقدار فعلی رو به کیلوگرم برمی‌گرداند.
        اگر صفر باشد → None
        """
        val = self.spin.value()
        if val <= 0:
            return None
        unit = self._current_unit()
        ratio = UNIT_TO_KG.get(unit, Decimal("1"))
        return Decimal(str(val)) * ratio

    def set_value_kg(self, kg_value: Optional[float | Decimal]):
        """
        مقدار رو به kg بگیر → با واحد مناسب نمایش بده.
        اگر None باشد → صفر
        """
        if kg_value is None:
            self.spin.setValue(0)
            return

        kg = Decimal(str(kg_value))

        # انتخاب هوشمند واحد نمایش
        if kg >= Decimal("1000"):
            unit = "ton"
        elif kg >= Decimal("1"):
            unit = "kg"
        else:
            unit = "gr"

        self._set_unit(unit)
        ratio = UNIT_TO_KG.get(unit, Decimal("1"))
        display_val = float(kg / ratio)
        self.spin.setValue(display_val)

    def clear(self):
        self.spin.setValue(0)
        self._set_unit(self._default_unit)