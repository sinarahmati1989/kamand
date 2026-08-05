"""
ModernInput — فیلد ورودی حرفه‌ای با Focus State
تم Aurora Glass Light — Professional Edition
Override قوی روی QSS عمومی
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit
)
from PySide6.QtCore import Qt, Signal
import logging

logger = logging.getLogger(__name__)


class ModernInput(QWidget):
    """
    ورودی حرفه‌ای با Focus State + فونت Vazirmatn
    """

    text_changed = Signal(str)
    return_pressed = Signal()

    def __init__(
        self,
        label: str = "",
        placeholder: str = "",
        is_password: bool = False,
        height: int = 52,   # 🆕 پارامتر جدید برای ارتفاع دلخواه
        parent=None
    ):
        super().__init__(parent)
        self._label_text = label
        self._placeholder = placeholder
        self._is_password = is_password
        self._height = height

        # فونت پروژه
        try:
            from app.ui.font_manager import FontManager
            self._font_family = FontManager.font_family()
        except Exception:
            self._font_family = "Tahoma"

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._setup_ui()
        self._apply_style()

    # ─────────────────────────── UI Setup ────────────────────────────

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # لیبل
        if self._label_text:
            self.label = QLabel(self._label_text)
            self.label.setObjectName("modernInputLabel")
            layout.addWidget(self.label)

        # فیلد ورودی
        self.input = QLineEdit()
        self.input.setObjectName("modernInputField")
        self.input.setPlaceholderText(self._placeholder)
        self.input.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        if self._is_password:
            self.input.setEchoMode(QLineEdit.EchoMode.Password)

        self.input.textChanged.connect(self.text_changed.emit)
        self.input.returnPressed.connect(self.return_pressed.emit)

        layout.addWidget(self.input)

    def _apply_style(self):
        """
        استایل حرفه‌ای با Focus State و فونت Vazirmatn
        از min-height و max-height استفاده می‌کنیم که Override قوی باشه
        """
        h = self._height
        self.setStyleSheet(f"""
            QLabel#modernInputLabel {{
                font-family: "{self._font_family}";
                color: #334155;
                font-size: 13px;
                font-weight: 600;
                background: transparent;
                padding: 0px 2px;
            }}
            
            QLineEdit#modernInputField {{
                font-family: "{self._font_family}";
                background-color: #F8FAFC;
                border: 1.5px solid #E2E8F0;
                border-radius: 12px;
                padding: 0px 16px;
                font-size: 14px;
                font-weight: 500;
                color: #1E293B;
                min-height: {h}px;
                max-height: {h}px;
                selection-background-color: #C7D2FE;
                selection-color: #1E293B;
            }}
            
            QLineEdit#modernInputField:hover {{
                border: 1.5px solid #CBD5E1;
                background-color: #FFFFFF;
            }}
            
            QLineEdit#modernInputField:focus {{
                border: 2px solid #6366F1;
                background-color: #FFFFFF;
                padding: 0px 15px;
            }}
            
            QLineEdit#modernInputField:disabled {{
                background-color: #F1F5F9;
                color: #94A3B8;
                border: 1.5px solid #E2E8F0;
            }}
        """)

    # ─────────────────────────── Public API ──────────────────────────

    def get_text(self) -> str:
        return self.input.text().strip()

    def set_text(self, text: str):
        self.input.setText(text if text else "")

    def clear(self):
        self.input.clear()

    def set_enabled(self, enabled: bool):
        self.input.setEnabled(enabled)

    def set_placeholder(self, text: str):
        self.input.setPlaceholderText(text)

    def set_focus(self):
        self.input.setFocus()