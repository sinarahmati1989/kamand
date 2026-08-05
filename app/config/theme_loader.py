"""
Theme Loader
بارگذاری فایل‌های QSS و اعمال به QApplication
"""
from pathlib import Path
from PySide6.QtWidgets import QApplication
from app.config.settings import BASE_DIR


QSS_DIR = BASE_DIR / "app" / "resources" / "qss"


def load_qss_file(filename: str) -> str:
    """خواندن یک فایل QSS"""
    path = QSS_DIR / filename
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def load_all_qss() -> str:
    """بارگذاری همه فایل‌های QSS"""
    qss_files = [
        "fonts.qss",
        "base.qss",
        "buttons.qss",
        "inputs.qss",
        "dialogs.qss",
        "scrollbar.qss",
        "main.qss",
        "master_data.qss",
        "sidebar.qss",
    ]
    combined = ""
    for filename in qss_files:
        content = load_qss_file(filename)
        if content:
            combined += f"\n/* === {filename} === */\n"
            combined += content
    return combined


def apply_theme(app: QApplication) -> None:
    """اعمال تم به برنامه"""
    qss = load_all_qss()
    app.setStyleSheet(qss)


class ThemeLoader:
    """Wrapper کلاس"""

    @staticmethod
    def load(app: QApplication) -> None:
        apply_theme(app)