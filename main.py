"""
نقطه ورود — کمند (Kamand)
"""
import sys
import os

# DPI Awareness
os.environ["QT_ENABLE_HIGHDPI_SCALING"]   = "1"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer

from app.config.logging_config import setup_logging
from app.config.theme_loader import apply_theme
from app.ui.auth.login_window import LoginWindow
from app.ui.main_window import MainWindow
from app.constants import BRAND_NAME

import logging

setup_logging()
logger = logging.getLogger(__name__)


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    app.setApplicationName(BRAND_NAME)

    apply_theme(app)

    from app.config.display import Display
    sw, sh = Display.screen_size()
    logger.info(
        f"صفحه: {sw}x{sh}  |  دسته: {Display.category()}  |  scale: {Display.scale_factor()}"
    )

    login = LoginWindow()

    # نگهداری MainWindow در متغیر بیرونی که garbage نشه
    state = {"window": None}

    def on_login_success(user):
        # کاملاً login رو ببند
        login.hide()

        # ساخت MainWindow بدون parent
        window = MainWindow()
        state["window"] = window

        # سایز صریح
        screen = app.primaryScreen().availableGeometry()
        window.setGeometry(screen)

        # نمایش maximized
        window.showMaximized()
        window.raise_()
        window.activateWindow()

        def on_logout():
            window.close()
            state["window"] = None
            login.reset_form()
            login.show()
            login.raise_()
            login.activateWindow()

        window.logout_requested.connect(on_logout)
        logger.info("MainWindow باز شد")

    login.login_success.connect(on_login_success)
    login.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()