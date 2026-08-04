"""
Base Page — پایه همه صفحات لیستی
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import logging

logger = logging.getLogger(__name__)


class BasePage(QWidget):
    """
    پایه صفحات لیستی

    ساختار:
    ┌─────────────────────────────┐
    │  Header (عنوان + دکمه Add)  │
    ├─────────────────────────────┤
    │  Toolbar (جستجو + ...)      │
    ├─────────────────────────────┤
    │  Content (جدول)             │
    ├─────────────────────────────┤
    │  Footer (info)              │
    └─────────────────────────────┘
    """

    add_requested = Signal()
    refresh_requested = Signal()
    search_changed = Signal(str)

    def __init__(
        self,
        title: str,
        subtitle: str = "",
        add_button_text: str = "افزودن",
        show_add_button: bool = True,
        parent=None,
    ):
        super().__init__(parent)
        self._title = title
        self._subtitle = subtitle
        self._add_button_text = add_button_text
        self._show_add_button = show_add_button

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._setup_ui()

    # ─────────────────────────── UI Setup ────────────────────────────

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        layout.addWidget(self._build_header())
        layout.addWidget(self._build_toolbar())

        self.content_widget = self._build_content()
        layout.addWidget(self.content_widget, stretch=1)

        layout.addWidget(self._build_footer())

    def _build_header(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("pageHeader")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 8)

        # عنوان + زیرعنوان
        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        self.title_label = QLabel(self._title)
        self.title_label.setObjectName("pageTitle")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.title_label.setFont(font)
        title_col.addWidget(self.title_label)

        if self._subtitle:
            self.subtitle_label = QLabel(self._subtitle)
            self.subtitle_label.setObjectName("pageSubtitle")
            title_col.addWidget(self.subtitle_label)

        layout.addLayout(title_col)
        layout.addStretch()

        # دکمه افزودن
        if self._show_add_button:
            self.add_btn = QPushButton(f"+ {self._add_button_text}")
            self.add_btn.setObjectName("primaryButton")
            self.add_btn.setFixedHeight(40)
            self.add_btn.setMinimumWidth(130)
            self.add_btn.clicked.connect(self.add_requested.emit)
            layout.addWidget(self.add_btn)

        return frame

    def _build_toolbar(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("pageToolbar")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("🔍  جستجو...")
        self.search_input.setFixedHeight(38)
        self.search_input.setMaximumWidth(300)
        self.search_input.textChanged.connect(
            lambda t: self.search_changed.emit(t.strip())
        )
        layout.addWidget(self.search_input)

        # فضای اضافه برای فیلترهای سفارشی زیرکلاس
        self.toolbar_extra = QHBoxLayout()
        layout.addLayout(self.toolbar_extra)

        layout.addStretch()

        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setObjectName("iconButton")
        self.refresh_btn.setFixedSize(38, 38)
        self.refresh_btn.setToolTip("بارگذاری مجدد")
        self.refresh_btn.clicked.connect(self.refresh_requested.emit)
        layout.addWidget(self.refresh_btn)

        return frame

    def _build_content(self) -> QWidget:
        """زیرکلاس override می‌کنه"""
        return QWidget()

    def _build_footer(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("pageFooter")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 8, 0, 0)

        self.info_label = QLabel("")
        self.info_label.setObjectName("pageInfo")
        layout.addWidget(self.info_label)

        layout.addStretch()
        return frame

    # ─────────────────────────── Public API ──────────────────────────

    def set_info(self, text: str):
        self.info_label.setText(text)

    def set_title(self, title: str):
        self.title_label.setText(title)

    def get_search_text(self) -> str:
        return self.search_input.text().strip()

    def clear_search(self):
        self.search_input.clear()