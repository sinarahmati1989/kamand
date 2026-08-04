"""Test - MainWindow بدون login"""
import sys
import os

os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from app.config.logging_config import setup_logging
from app.config.theme_loader import apply_theme
from app.core.access_control import AccessControl, CurrentUser
from app.enums.roles import UserRole
from app.ui.main_window import MainWindow

setup_logging()


def main():
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    apply_theme(app)

    AccessControl.set_current_user(CurrentUser(
        id=1,
        username="admin",
        full_name="مدیر تست",
        role=UserRole.ADMIN,
        is_active=True,
    ))

    window = MainWindow()
    print(f">>> BEFORE:  {window.width()} x {window.height()}")
    window.setMinimumSize(800, 600)      # ← اضافه کن
    window.resize(1920, 1080)             # ← اضافه کن
    window.showMaximized()
    print(f">>> AFTER:   {window.width()} x {window.height()}")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()