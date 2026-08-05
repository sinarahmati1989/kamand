"""
Toast Notification
پیام‌های سریع (Success / Error / Info / Warning)
"""
from PySide6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QVBoxLayout,
    QGraphicsDropShadowEffect, QFrame,
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QFont


class Toast(QWidget):
    """پیام Toast شناور در بالای صفحه"""

    STYLES = {
        "success": {"bg": "#10B981", "icon": "✓", "border": "#059669"},
        "error":   {"bg": "#EF4444", "icon": "✕", "border": "#DC2626"},
        "warning": {"bg": "#F59E0B", "icon": "!", "border": "#D97706"},
        "info":    {"bg": "#3B82F6", "icon": "i", "border": "#2563EB"},
    }

    def __init__(
        self,
        parent,
        message: str,
        kind: str = "info",
        duration: int = 3000,
    ):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        style = self.STYLES.get(kind, self.STYLES["info"])

        # عرض ثابت و مناسب
        self.setFixedWidth(420)
        self.setMinimumHeight(60)

        # ── Container با پس‌زمینه رنگی ─────────────────────────────
        container = QFrame(self)
        container.setObjectName("toastContainer")
        container.setStyleSheet(f"""
            QFrame#toastContainer {{
                background-color: {style['bg']};
                border: none;
                border-radius: 10px;
            }}
        """)

        # سایه
        shadow = QGraphicsDropShadowEffect(container)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 90))
        shadow.setOffset(0, 6)
        container.setGraphicsEffect(shadow)

        # چیدمان داخلی
        inner = QHBoxLayout(container)
        inner.setContentsMargins(18, 14, 18, 14)
        inner.setSpacing(14)

        # ── آیکون در دایره سفید ────────────────────────────────────
        icon_label = QLabel(style["icon"])
        icon_label.setFixedSize(32, 32)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"""
            QLabel {{
                background-color: rgba(255, 255, 255, 0.25);
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 16px;
                border: 2px solid rgba(255, 255, 255, 0.4);
            }}
        """)

        # ── متن پیام ───────────────────────────────────────────────
        text_label = QLabel(message)
        text_label.setStyleSheet("""
            QLabel {
                color: white;
                font-family: "Segoe UI", "B Nazanin", sans-serif;
                font-size: 14px;
                font-weight: 600;
                background: transparent;
                border: none;
            }
        """)
        text_label.setWordWrap(True)
        text_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        inner.addWidget(icon_label, 0)
        inner.addWidget(text_label, 1)

        # چیدمان بیرونی
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(container)

        # موقعیت‌دهی بعد از رسم کامل
        QTimer.singleShot(0, self._position)

        # بستن خودکار
        QTimer.singleShot(duration, self._fade_out)

    def _position(self):
        """موقعیت بالای پنجره والد — وسط افقی"""
        self.adjustSize()
        if self.parent():
            parent = self.parent()
            # پیدا کردن پنجره اصلی
            while parent.parent() is not None:
                parent = parent.parent()

            geo = parent.geometry()
            x = geo.x() + (geo.width() - self.width()) // 2
            y = geo.y() + 80
            self.move(x, y)

    def _fade_out(self):
        """محو شدن نرم"""
        self._anim = QPropertyAnimation(self, b"windowOpacity")
        self._anim.setDuration(300)
        self._anim.setStartValue(1.0)
        self._anim.setEndValue(0.0)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._anim.finished.connect(self.close)
        self._anim.start()

    @classmethod
    def success(cls, parent, message: str, duration: int = 3000):
        t = cls(parent, message, "success", duration)
        t.show()
        return t

    @classmethod
    def error(cls, parent, message: str, duration: int = 4000):
        t = cls(parent, message, "error", duration)
        t.show()
        return t

    @classmethod
    def warning(cls, parent, message: str, duration: int = 3500):
        t = cls(parent, message, "warning", duration)
        t.show()
        return t

    @classmethod
    def info(cls, parent, message: str, duration: int = 3000):
        t = cls(parent, message, "info", duration)
        t.show()
        return t