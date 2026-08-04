"""
ModernInput — فیلد ورودی زیبا با لیبل
تم Aurora Glass
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import logging

logger = logging.getLogger(__name__)


class ModernInput(QWidget):
    """
    ورودی استاندارد Aurora:
    
    ┌─────────────────┐
    │ لیبل            │
    ├─────────────────┤
    │ [  input    ]   │
    └─────────────────┘
    """

    text_changed = Signal(str)
    return_pressed = Signal()

    def __init__(
        self,
        label: str = "",
        placeholder: str = "",
        is_password: bool = False,
        parent=None
    ):
        super().__init__(parent)
        self._label_text = label
        self._placeholder = placeholder
        self._is_password = is_password

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._setup_ui()

    # ─────────────────────────── UI Setup ────────────────────────────

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # لیبل
        if self._label_text:
            self.label = QLabel(self._label_text)
            self.label.setObjectName("inputLabel")
            font = QFont()
            font.setPointSize(10)
            self.label.setFont(font)
            layout.addWidget(self.label)

        # فیلد ورودی
        self.input = QLineEdit()
        self.input.setObjectName("modernInput")
        self.input.setPlaceholderText(self._placeholder)
        self.input.setFixedHeight(42)
        self.input.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        if self._is_password:
            self.input.setEchoMode(QLineEdit.EchoMode.Password)

        self.input.textChanged.connect(self.text_changed.emit)
        self.input.returnPressed.connect(self.return_pressed.emit)

        layout.addWidget(self.input)

    # ─────────────────────────── Public API ──────────────────────────

    def get_text(self) -> str:
        return self.input.text().strip()

    def set_text(self, text: str):
        self.input.setText(text if text else "")

    def clear(self):
        self.input.clear()

    def set_enabled(self, enabled: bool):
        self.input.setEnabled(enabled)
        if not enabled:
            self.input.setObjectName("modernInputDisabled")
            self.input.style().unpolish(self.input)
            self.input.style().polish(self.input)

    def set_placeholder(self, text: str):
        self.input.setPlaceholderText(text)

    def set_focus(self):
        self.input.setFocus()