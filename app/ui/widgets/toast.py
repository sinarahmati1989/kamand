"""
Toast Notification
پیام‌های سریع (Success / Error / Info / Warning)
"""

from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QColor


class Toast(QWidget):
    """پیام Toast شناور"""
    
    STYLES = {
        "success": {"bg": "#10B981", "icon": "✅"},
        "error":   {"bg": "#EF4444", "icon": "❌"},
        "warning": {"bg": "#F59E0B", "icon": "⚠️"},
        "info":    {"bg": "#3B82F6", "icon": "ℹ️"},
    }
    
    def __init__(self, parent, message: str, kind: str = "info", duration: int = 3000):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        
        style = self.STYLES.get(kind, self.STYLES["info"])
        
        # Container
        container = QWidget(self)
        container.setStyleSheet(f"""
            background-color: {style['bg']};
            border-radius: 12px;
        """)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect(container)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        container.setGraphicsEffect(shadow)
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)
        
        icon = QLabel(style["icon"])
        icon.setStyleSheet("color: white; font-size: 18px; background: transparent;")
        
        text = QLabel(message)
        text.setStyleSheet("color: white; font-size: 14px; font-weight: 600; background: transparent;")
        text.setWordWrap(True)
        
        layout.addWidget(icon)
        layout.addWidget(text, 1)
        
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(container)
        
        self.adjustSize()
        self._position()
        
        # Auto close
        QTimer.singleShot(duration, self.close)
    
    def _position(self):
        """موقعیت بالای پنجره پدر"""
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() + 60
            self.move(x, y)
    
    @classmethod
    def success(cls, parent, message: str, duration: int = 3000):
        toast = cls(parent, message, "success", duration)
        toast.show()
        return toast
    
    @classmethod
    def error(cls, parent, message: str, duration: int = 3000):
        toast = cls(parent, message, "error", duration)
        toast.show()
        return toast
    
    @classmethod
    def warning(cls, parent, message: str, duration: int = 3000):
        toast = cls(parent, message, "warning", duration)
        toast.show()
        return toast
    
    @classmethod
    def info(cls, parent, message: str, duration: int = 3000):
        toast = cls(parent, message, "info", duration)
        toast.show()
        return toast