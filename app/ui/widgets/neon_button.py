"""
Neon Button + Primary Button
دکمه‌های Aurora Glass
"""

from PySide6.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt


class NeonButton(QPushButton):
    """دکمه با گرادیانت Aurora و سایه رنگی (نسخه اصلی)"""

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setObjectName("NeonButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(48)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(139, 92, 246, 120))
        shadow.setOffset(0, 6)
        self.setGraphicsEffect(shadow)


class PrimaryButton(QPushButton):
    """
    دکمه اصلی حرفه‌ای — Solid Indigo با Hover State
    مناسب برای دکمه‌های Call-to-Action
    """

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setObjectName("PrimaryButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(54)

        # فونت پروژه
        try:
            from app.ui.font_manager import FontManager
            self._font_family = FontManager.font_family()
        except Exception:
            self._font_family = "Tahoma"

        # سایه Indigo قوی
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setColor(QColor(99, 102, 241, 110))
        shadow.setOffset(0, 10)
        self.setGraphicsEffect(shadow)

        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet(f"""
            QPushButton#PrimaryButton {{
                font-family: "{self._font_family}";
                background-color: #6366F1;
                color: #FFFFFF;
                border: none;
                border-radius: 14px;
                font-size: 16px;
                font-weight: 700;
                padding: 0px 20px;
                letter-spacing: 0.3px;
            }}
            
            QPushButton#PrimaryButton:hover {{
                background-color: #4F46E5;
            }}
            
            QPushButton#PrimaryButton:pressed {{
                background-color: #4338CA;
            }}
            
            QPushButton#PrimaryButton:disabled {{
                background-color: #A5B4FC;
                color: #E0E7FF;
            }}
        """)