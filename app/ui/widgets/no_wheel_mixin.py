"""
No-Wheel Widgets — ComboBox و SpinBox بدون واکنش به scroll
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QComboBox, QSpinBox, QDoubleSpinBox


class NoWheelComboBox(QComboBox):
    """QComboBox که با scroll wheel مقدارش عوض نمی‌شود"""

    def wheelEvent(self, event: QWheelEvent):
        # فقط وقتی focus داره اجازه بده
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()


class NoWheelSpinBox(QSpinBox):
    """QSpinBox که با scroll wheel مقدارش عوض نمی‌شود"""

    def wheelEvent(self, event: QWheelEvent):
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()


class NoWheelDoubleSpinBox(QDoubleSpinBox):
    """QDoubleSpinBox که با scroll wheel مقدارش عوض نمی‌شود"""

    def wheelEvent(self, event: QWheelEvent):
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()