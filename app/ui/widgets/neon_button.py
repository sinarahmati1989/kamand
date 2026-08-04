"""
Neon Button
دکمه با گرادیانت و افکت
"""

from PySide6.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt


class NeonButton(QPushButton):
    """دکمه با گرادیانت Aurora و سایه رنگی"""
    
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setObjectName("NeonButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(48)
        
        # سایه بنفش
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(139, 92, 246, 120))
        shadow.setOffset(0, 6)
        self.setGraphicsEffect(shadow)