"""
Kamand - SmartSpinBox (v2)
QDoubleSpinBox / QSpinBox با رفتار درست:
- تک‌کلیک روی input → cursor + selectAll
- تایپ فوری
- Wheel غیرفعال
"""
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QDoubleSpinBox, QSpinBox


class SmartDoubleSpinBox(QDoubleSpinBox):
    """QDoubleSpinBox با focus/select صحیح در تک‌کلیک"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setKeyboardTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        # مهم: کلیک روی lineEdit → مستقیم focus بگیره
        self.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.UpDownArrows)

    def wheelEvent(self, event):
        """جلوگیری از تغییر با scroll"""
        event.ignore()

    def mousePressEvent(self, event):
        """کلیک روی widget → مستقیم focus بده به lineEdit"""
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            le = self.lineEdit()
            if le is not None:
                le.setFocus(Qt.FocusReason.MouseFocusReason)
                # با تاخیر کم selectAll — تا Qt پردازش کنه
                QTimer.singleShot(0, le.selectAll)

    def focusInEvent(self, event):
        """focus → selectAll"""
        super().focusInEvent(event)
        le = self.lineEdit()
        if le is not None:
            QTimer.singleShot(0, le.selectAll)


class SmartSpinBox(QSpinBox):
    """QSpinBox (int) با focus/select صحیح"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setKeyboardTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)

    def wheelEvent(self, event):
        event.ignore()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            le = self.lineEdit()
            if le is not None:
                le.setFocus(Qt.FocusReason.MouseFocusReason)
                QTimer.singleShot(0, le.selectAll)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        le = self.lineEdit()
        if le is not None:
            QTimer.singleShot(0, le.selectAll)