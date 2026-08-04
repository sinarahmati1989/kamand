"""
Base Dialog
پایه‌ی همه دیالوگ‌ها
"""

from PySide6.QtWidgets import QDialog
from PySide6.QtCore import Qt


class BaseDialog(QDialog):
    """پایه دیالوگ‌های Aurora"""
    
    def __init__(self, parent=None, title: str = ""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
    
    def center_on_screen(self):
        """وسط صفحه"""
        screen = self.screen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)