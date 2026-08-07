"""
WorkflowBar — نوار مراحل Workflow
نمایش مراحل به‌صورت زنجیر با وضعیت فعال/غیرفعال
"""
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QPushButton, QLabel,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class WorkflowBar(QFrame):
    """
    نوار مراحل Workflow

    استفاده:
        bar = WorkflowBar([
            ("device_templates", "تعریف دستگاه"),
            ("items",            "اقلام"),
            ("bom",              "BOM"),
            ("routing",          "مسیر ساخت"),
        ])
        bar.step_clicked.connect(self._on_step)
        bar.set_active("items")
    """

    step_clicked = Signal(str)  # key مرحله کلیک‌شده

    def __init__(
        self,
        steps: list[tuple[str, str]],
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("workflowBar")
        self.setFixedHeight(56)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self._steps: dict[str, QPushButton] = {}
        self._setup_ui(steps)
        self._apply_style()

    def _setup_ui(self, steps: list[tuple[str, str]]):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(0)

        for i, (key, label) in enumerate(steps, 1):
            # دکمه مرحله
            btn = QPushButton(f"  {i}  {label}  ")
            btn.setObjectName("workflowStep")
            btn.setFixedHeight(38)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

            font = QFont()
            font.setPointSize(10)
            font.setBold(True)
            btn.setFont(font)

            btn.clicked.connect(
                lambda checked=False, k=key: self.step_clicked.emit(k)
            )
            self._steps[key] = btn
            layout.addWidget(btn)

            # پیکان بین مراحل
            if i < len(steps):
                arrow = QLabel("  ←  ")
                arrow.setObjectName("workflowArrow")
                arrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
                f = QFont()
                f.setPointSize(12)
                arrow.setFont(f)
                layout.addWidget(arrow)

        layout.addStretch()

    def _apply_style(self):
        self.setStyleSheet("""
            QFrame#workflowBar {
                background: rgba(255, 255, 255, 0.7);
                border: 1px solid rgba(99, 102, 241, 0.15);
                border-radius: 12px;
            }

            QPushButton#workflowStep {
                background: rgba(99, 102, 241, 0.08);
                color: #64748B;
                border: 1px solid rgba(99, 102, 241, 0.2);
                border-radius: 8px;
                font-family: "Segoe UI", "B Nazanin", sans-serif;
                font-size: 13px;
                font-weight: bold;
                padding: 0 12px;
                min-width: 120px;
            }
            QPushButton#workflowStep:hover {
                background: rgba(99, 102, 241, 0.15);
                color: #6366F1;
                border-color: rgba(99, 102, 241, 0.4);
            }

            QPushButton#workflowStepActive {
                background: #6366F1;
                color: white;
                border: 1px solid #4F46E5;
                border-radius: 8px;
                font-family: "Segoe UI", "B Nazanin", sans-serif;
                font-size: 13px;
                font-weight: bold;
                padding: 0 12px;
                min-width: 120px;
            }
            QPushButton#workflowStepActive:hover {
                background: #4F46E5;
            }

            QPushButton#workflowStepDone {
                background: rgba(16, 185, 129, 0.1);
                color: #10B981;
                border: 1px solid rgba(16, 185, 129, 0.3);
                border-radius: 8px;
                font-family: "Segoe UI", "B Nazanin", sans-serif;
                font-size: 13px;
                font-weight: bold;
                padding: 0 12px;
                min-width: 120px;
            }

            QLabel#workflowArrow {
                color: #94A3B8;
                background: transparent;
                font-size: 14px;
            }
        """)

    def set_active(self, key: str):
        """فعال کردن یک مرحله"""
        for k, btn in self._steps.items():
            if k == key:
                btn.setObjectName("workflowStepActive")
            else:
                btn.setObjectName("workflowStep")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def set_done(self, keys: list[str]):
        """علامت‌گذاری مراحل تکمیل‌شده"""
        for k, btn in self._steps.items():
            if k in keys:
                btn.setObjectName("workflowStepDone")
                btn.style().unpolish(btn)
                btn.style().polish(btn)