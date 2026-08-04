"""
WorkflowBar — نوار مراحل بالای صفحه ماژول‌ها
مثال: دستگاه → اقلام → اسمبلی → BOM → بازگشایی
"""
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QPushButton, QLabel
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class WorkflowStep(QPushButton):
    """یک مرحله در Workflow"""

    def __init__(self, index: int, label: str, step_key: str, parent=None):
        super().__init__(parent)
        self.step_key = step_key
        self.index = index
        self.setText(f"  {index}   {label}  ")
        self.setObjectName("workflowStep")
        self.setFixedHeight(38)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.setFont(font)

    def set_active(self, active: bool):
        self.setObjectName("workflowStepActive" if active else "workflowStep")
        self.style().unpolish(self)
        self.style().polish(self)


class WorkflowArrow(QLabel):
    """پیکان بین مراحل"""

    def __init__(self, parent=None):
        super().__init__("◀", parent)
        self.setObjectName("workflowArrow")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(12)
        self.setFont(font)


class WorkflowBar(QFrame):
    """
    نوار مراحل کار
    مثال: [1 دستگاه] → [2 اقلام] → [3 اسمبلی] → ...
    """

    step_clicked = Signal(str)  # step_key

    def __init__(self, steps: list[tuple[str, str]], parent=None):
        """
        steps: [("device", "دستگاه"), ("items", "اقلام"), ...]
        """
        super().__init__(parent)
        self.setObjectName("workflowBar")
        self.setFixedHeight(60)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self._steps: dict[str, WorkflowStep] = {}
        self._setup_ui(steps)

    def _setup_ui(self, steps):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(6)

        for i, (key, label) in enumerate(steps, 1):
            step = WorkflowStep(i, label, key)
            step.clicked.connect(lambda checked=False, k=key: self.step_clicked.emit(k))
            self._steps[key] = step
            layout.addWidget(step)

            if i < len(steps):
                layout.addWidget(WorkflowArrow())

        layout.addStretch()

    def set_active(self, step_key: str):
        for key, step in self._steps.items():
            step.set_active(key == step_key)