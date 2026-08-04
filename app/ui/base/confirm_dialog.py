"""
دیالوگ تأیید — هماهنگ با Aurora Glass Light Theme
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSizePolicy, QWidget, QFrame
)
from PySide6.QtCore import Qt
import logging

logger = logging.getLogger(__name__)


class ConfirmDialog(QDialog):
    """
    دیالوگ تأیید فارسی — هماهنگ با تم Aurora
    
    Usage:
        dlg = ConfirmDialog(
            parent=self,
            title="تأیید غیرفعال‌سازی",
            message="مشتری «رحمتی» غیرفعال شود؟",
            confirm_text="بله، غیرفعال کن",
            cancel_text="انصراف",
            dangerous=True
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            ...
    """

    def __init__(
        self,
        parent=None,
        title: str = "تأیید",
        message: str = "آیا مطمئن هستید؟",
        confirm_text: str = "بله",
        cancel_text: str = "انصراف",
        dangerous: bool = False
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(460, 220)

        # LTR روی خود دیالوگ — چیدمان دستی می‌کنیم
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        # Frameless مطابق تم Aurora
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._build_ui(title, message, confirm_text, cancel_text, dangerous)
        self._apply_style(dangerous)

    # ══════════════════════════════════════════════════════════════════

    def _build_ui(self, title, message, confirm_text, cancel_text, dangerous):

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        # ─── کارت اصلی ───
        self._card = QWidget()
        self._card.setObjectName("confirmCard")
        self._card.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        outer.addWidget(self._card)

        root = QVBoxLayout(self._card)
        root.setContentsMargins(28, 24, 28, 22)
        root.setSpacing(0)

        # ═══ عنوان (راست‌چین) ═══
        title_lbl = QLabel(title)
        title_lbl.setObjectName("confirmTitle")
        title_lbl.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        title_lbl.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        root.addWidget(title_lbl)

        root.addSpacing(10)

        # ═══ خط جداکننده ═══
        sep = QFrame()
        sep.setObjectName("confirmSep")
        sep.setFrameShape(QFrame.Shape.HLine)
        root.addWidget(sep)

        root.addSpacing(18)

        # ═══ متن پیام (راست‌چین) ═══
        msg_lbl = QLabel(message)
        msg_lbl.setObjectName("confirmMessage")
        msg_lbl.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        msg_lbl.setWordWrap(True)
        msg_lbl.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        root.addWidget(msg_lbl)

        root.addStretch(1)

        # ═══ دکمه‌ها ═══
        # LTR: [stretch] [انصراف] [تأیید]
        # نمایش: خالی سمت چپ ← انصراف ← تأیید (راست)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.setContentsMargins(0, 0, 0, 0)

        cancel_btn = QPushButton(cancel_text)
        cancel_btn.setObjectName("confirmCancelBtn")
        cancel_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setDefault(True)
        cancel_btn.clicked.connect(self.reject)

        confirm_btn = QPushButton(confirm_text)
        confirm_btn.setObjectName(
            "confirmDangerBtn" if dangerous else "confirmPrimaryBtn"
        )
        confirm_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.clicked.connect(self.accept)

        btn_row.addStretch(1)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(confirm_btn)

        root.addLayout(btn_row)

    # ══════════════════════════════════════════════════════════════════

    def _apply_style(self, dangerous: bool):

        # رنگ‌های تم Aurora
        primary       = "#6366F1"   # بنفش Indigo (رنگ اصلی پروژه)
        primary_hover = "#4F46E5"
        danger        = "#EF4444"
        danger_hover  = "#DC2626"

        confirm_bg    = danger if dangerous else primary
        confirm_hover = danger_hover if dangerous else primary_hover

        self.setStyleSheet(f"""

            /* ── کارت اصلی ─── */
            QWidget#confirmCard {{
                background-color: rgba(255, 255, 255, 0.98);
                border: 1px solid rgba(99, 102, 241, 0.3);
                border-radius: 20px;
            }}

            /* ── عنوان ─── */
            QLabel#confirmTitle {{
                font-family: "Segoe UI", "B Nazanin", sans-serif;
                font-size: 16px;
                font-weight: bold;
                color: #6366F1;
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }}

            /* ── خط جداکننده ─── */
            QFrame#confirmSep {{
                background-color: rgba(99, 102, 241, 0.15);
                border: none;
                min-height: 1px;
                max-height: 1px;
            }}

            /* ── متن پیام ─── */
            QLabel#confirmMessage {{
                font-family: "Segoe UI", "B Nazanin", sans-serif;
                font-size: 14px;
                color: #1E293B;
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }}

            /* ── دکمه تأیید (اصلی/خطر) ─── */
            QPushButton#confirmPrimaryBtn,
            QPushButton#confirmDangerBtn {{
                background-color: {confirm_bg};
                color: white;
                border: none;
                border-radius: 8px;
                font-family: "Segoe UI", "B Nazanin", sans-serif;
                font-size: 14px;
                font-weight: bold;
                min-width: 140px;
                max-width: 140px;
                min-height: 40px;
                max-height: 40px;
                padding: 0px;
            }}
            QPushButton#confirmPrimaryBtn:hover,
            QPushButton#confirmDangerBtn:hover {{
                background-color: {confirm_hover};
            }}

            /* ── دکمه انصراف ─── */
            QPushButton#confirmCancelBtn {{
                background-color: rgba(241, 245, 249, 0.9);
                color: #64748B;
                border: 1px solid rgba(148, 163, 184, 0.4);
                border-radius: 8px;
                font-family: "Segoe UI", "B Nazanin", sans-serif;
                font-size: 14px;
                font-weight: 600;
                min-width: 100px;
                max-width: 100px;
                min-height: 40px;
                max-height: 40px;
                padding: 0px;
            }}
            QPushButton#confirmCancelBtn:hover {{
                background-color: rgba(226, 232, 240, 1);
                color: #1E293B;
                border-color: rgba(100, 116, 139, 0.6);
            }}

        """)

    # ══════════════════════════════════════════════════════════════════
    # درگ کردن (چون frameless)
    # ══════════════════════════════════════════════════════════════════

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, "_drag_pos"):
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()