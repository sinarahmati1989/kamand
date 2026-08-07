"""تست SmartSpinBox"""
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QDoubleSpinBox, QLabel,
)
from app.ui.widgets.smart_spinbox import SmartDoubleSpinBox


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test SpinBox")
        self.resize(400, 300)

        w = QWidget()
        self.setCentralWidget(w)
        layout = QVBoxLayout(w)

        layout.addWidget(QLabel("1) QDoubleSpinBox معمولی:"))
        sp1 = QDoubleSpinBox()
        sp1.setRange(0, 99999)
        sp1.setMinimumHeight(40)
        layout.addWidget(sp1)

        layout.addWidget(QLabel("2) SmartDoubleSpinBox (جدید):"))
        sp2 = SmartDoubleSpinBox()
        sp2.setRange(0, 99999)
        sp2.setMinimumHeight(40)
        layout.addWidget(sp2)

        layout.addWidget(QLabel("3) SmartDoubleSpinBox با suffix:"))
        sp3 = SmartDoubleSpinBox()
        sp3.setRange(0, 99999)
        sp3.setSuffix(" kg")
        sp3.setMinimumHeight(40)
        layout.addWidget(sp3)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = TestWindow()
    win.show()
    sys.exit(app.exec())