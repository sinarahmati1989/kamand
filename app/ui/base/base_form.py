"""
BaseForm — پایه دیالوگ‌های فرم Aurora
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QPushButton,
    QScrollArea, QWidget,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import logging

logger = logging.getLogger(__name__)


class BaseForm(QDialog):
    """
    پایه فرم‌های افزودن / ویرایش

    ساختار:
    ┌──────────────────────────┐
    │  Header (عنوان)          │
    ├──────────────────────────┤
    │  Body — اسکرول‌پذیر      │
    │  (زیرکلاس اینجا اضافه)  │
    ├──────────────────────────┤
    │  Footer (Cancel | Save)  │
    └──────────────────────────┘
    """

    submitted = Signal(dict)
    cancelled = Signal()

    def __init__(
        self,
        title: str,
        subtitle: str = "",
        save_text: str = "ذخیره",
        cancel_text: str = "انصراف",
        parent=None,
    ):
        super().__init__(parent)
        self._title = title
        self._subtitle = subtitle
        self._save_text = save_text
        self._cancel_text = cancel_text

        self.setModal(True)
        self.setMinimumWidth(480)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setObjectName("baseForm")

        self._setup_ui()
        self._connect_signals()

    # ─────────────────────────── UI Setup ────────────────────────────

    def _setup_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        main.addWidget(self._build_header())
        main.addWidget(self._build_body(), stretch=1)
        main.addWidget(self._build_footer())

    def _build_header(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("formHeader")
        frame.setFixedHeight(72)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(24, 12, 24, 12)
        layout.setSpacing(2)

        self.form_title = QLabel(self._title)
        self.form_title.setObjectName("formTitle")
        font = QFont()
        font.setPointSize(15)
        font.setBold(True)
        self.form_title.setFont(font)
        layout.addWidget(self.form_title)

        if self._subtitle:
            self.form_subtitle = QLabel(self._subtitle)
            self.form_subtitle.setObjectName("formSubtitle")
            layout.addWidget(self.form_subtitle)

        return frame

    def _build_body(self) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setObjectName("formScroll")

        container = QWidget()
        container.setObjectName("formContainer")

        self.form_layout = QVBoxLayout(container)
        self.form_layout.setContentsMargins(24, 20, 24, 20)
        self.form_layout.setSpacing(16)
        self.form_layout.addStretch()

        scroll.setWidget(container)
        return scroll

    def _build_footer(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("formFooter")
        frame.setFixedHeight(64)

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(24, 12, 24, 12)
        layout.setSpacing(12)

        self.cancel_btn = QPushButton(self._cancel_text)
        self.cancel_btn.setObjectName("secondaryButton")
        self.cancel_btn.setFixedHeight(40)
        self.cancel_btn.setMinimumWidth(100)
        layout.addWidget(self.cancel_btn)

        layout.addStretch()

        self.save_btn = QPushButton(self._save_text)
        self.save_btn.setObjectName("primaryButton")
        self.save_btn.setFixedHeight(40)
        self.save_btn.setMinimumWidth(120)
        layout.addWidget(self.save_btn)

        return frame

    def _connect_signals(self):
        self.save_btn.clicked.connect(self._on_save)
        self.cancel_btn.clicked.connect(self._on_cancel)

    # ─────────────────────────── Slots ───────────────────────────────

    def _on_save(self):
        data = self.collect_data()
        if data is not None:
            self.submitted.emit(data)
            self.accept()

    def _on_cancel(self):
        self.cancelled.emit()
        self.reject()

    # ─────────────────────────── Override اینها ───────────────────────

    def collect_data(self) -> dict | None:
        """زیرکلاس override می‌کنه"""
        return {}

    def populate(self, data: dict):
        """زیرکلاس override می‌کنه"""
        pass

    # ─────────────────────────── Public API ──────────────────────────

    def add_field(self, widget: QWidget):
        """فیلد جدید — قبل از stretch اضافه میشه"""
        count = self.form_layout.count()
        self.form_layout.insertWidget(count - 1, widget)

    def set_loading(self, loading: bool):
        self.save_btn.setEnabled(not loading)
        self.cancel_btn.setEnabled(not loading)
        self.save_btn.setText(
            "در حال ذخیره..." if loading else self._save_text
        )

    def set_title(self, title: str):
        self.form_title.setText(title)