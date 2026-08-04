"""
DashboardPage — داشبورد خوش‌آمدگویی
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from app.core.access_control import AccessControl
from app.constants import BRAND_NAME


class StatCard(QFrame):
    """کارت آماری داشبورد"""

    def __init__(self, icon: str, title: str, value: str, parent=None):
        super().__init__(parent)
        self.setObjectName("statCard")
        self.setFixedHeight(110)
        self._setup_ui(icon, title, value)

    def _setup_ui(self, icon: str, title: str, value: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(8)

        top = QHBoxLayout()

        icon_lbl = QLabel(icon)
        icon_font = QFont()
        icon_font.setPointSize(22)
        icon_lbl.setFont(icon_font)
        top.addWidget(icon_lbl)

        top.addStretch()

        value_lbl = QLabel(value)
        value_lbl.setObjectName("statValue")
        value_font = QFont()
        value_font.setPointSize(24)
        value_font.setBold(True)
        value_lbl.setFont(value_font)
        top.addWidget(value_lbl)

        layout.addLayout(top)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("statTitle")
        layout.addWidget(title_lbl)


class DashboardPage(QWidget):
    """صفحه داشبورد"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setObjectName("dashboardPage")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        user = AccessControl.get_current_user()
        name = user.full_name if user else "کاربر"

        welcome = QLabel(f"سلام، {name} عزیز! 👋")
        welcome.setObjectName("welcomeLabel")
        font = QFont()
        font.setPointSize(22)
        font.setBold(True)
        welcome.setFont(font)
        layout.addWidget(welcome)

        subtitle = QLabel(f"به سیستم مدیریت {BRAND_NAME} خوش آمدید")
        subtitle.setObjectName("welcomeSub")
        layout.addWidget(subtitle)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setObjectName("dashSep")
        layout.addWidget(sep)

        # آمار زنده در آخر پروژه اضافه می‌شود
        info = QLabel("📊  آمار زنده در پایان پروژه اضافه خواهد شد")
        info.setObjectName("welcomeSub")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

        layout.addStretch()