"""
SearchableDeviceCombo — انتخاب دستگاه با جستجو
مناسب برای صفحات دستگاه در پایگاه داده
"""
import logging
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLineEdit, QPushButton, QDialog,
    QListWidget, QListWidgetItem, QLabel,
)
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QGuiApplication

from app.database.session import get_session
from app.services.device_template_service import DeviceTemplateService

logger = logging.getLogger(__name__)


class DeviceSearchPopup(QDialog):
    """Popup جستجوی دستگاه"""

    device_selected = Signal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.Popup |
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setFixedSize(420, 340)

        # ✅ اول داده بارگذاری میشه (داخل session)
        self._all_devices = []
        self._load_devices()

        # بعد UI ساخته میشه
        self._setup_ui()
        self._apply_style()

        # بعد داده نمایش داده میشه
        self._populate(self._all_devices)

    def _load_devices(self):
        """بارگذاری داده‌ها — کپی مستقیم (نه ORM object)"""
        try:
            with get_session() as session:
                svc = DeviceTemplateService(session)
                templates = svc.search(keyword="")
                # ✅ کپی tuple — session بسته میشه بعد
                self._all_devices = [
                    (t.id, t.code or "", t.name or "", t.template_type or "")
                    for t in templates
                ]
            logger.info(f"✅ {len(self._all_devices)} دستگاه بارگذاری شد")
        except Exception as e:
            logger.error(f"خطا در بارگذاری دستگاه‌ها: {e}", exc_info=True)
            self._all_devices = []

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QWidget()
        card.setObjectName("searchCard")
        outer.addWidget(card)

        v = QVBoxLayout(card)
        v.setContentsMargins(10, 10, 10, 10)
        v.setSpacing(8)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("🔍 جستجو: نام یا کد دستگاه...")
        self.search_input.setFixedHeight(34)
        self.search_input.textChanged.connect(self._filter)
        v.addWidget(self.search_input)

        self.list_widget = QListWidget()
        self.list_widget.setObjectName("deviceList")
        self.list_widget.itemDoubleClicked.connect(self._on_item_selected)
        self.list_widget.itemClicked.connect(self._on_item_selected)
        v.addWidget(self.list_widget, 1)

        self.info_label = QLabel("در حال بارگذاری...")
        self.info_label.setObjectName("infoLabel")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(self.info_label)

    def _apply_style(self):
        self.setStyleSheet("""
            QWidget#searchCard {
                background-color: #FFFFFF;
                border: 1px solid rgba(99, 102, 241, 0.3);
                border-radius: 10px;
            }
            QLineEdit#searchInput {
                background-color: #F8FAFC;
                color: #1E293B;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                padding: 6px 10px;
                font-family: "Vazirmatn", sans-serif;
                font-size: 13px;
            }
            QLineEdit#searchInput:focus {
                border-color: #6366F1;
                background-color: white;
            }
            QListWidget#deviceList {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                padding: 4px;
                font-family: "Vazirmatn", sans-serif;
                font-size: 13px;
                outline: none;
            }
            QListWidget#deviceList::item {
                padding: 8px 10px;
                border-radius: 4px;
                color: #1E293B;
            }
            QListWidget#deviceList::item:hover {
                background-color: rgba(99, 102, 241, 0.1);
                color: #6366F1;
            }
            QListWidget#deviceList::item:selected {
                background-color: #6366F1;
                color: white;
            }
            QLabel#infoLabel {
                color: #94A3B8;
                font-size: 11px;
                font-family: "Vazirmatn", sans-serif;
            }
        """)

    def _populate(self, devices: list):
        self.list_widget.clear()
        if not devices:
            self.info_label.setText("هیچ دستگاهی یافت نشد")
            return

        for did, code, name, dtype in devices:
            display = f"{code} — {name}" if code else name
            if dtype:
                display += f"  [{dtype}]"
            item = QListWidgetItem(display)
            item.setData(
                Qt.ItemDataRole.UserRole,
                (did, f"{code} — {name}" if code else name)
            )
            self.list_widget.addItem(item)

        self.info_label.setText(f"{len(devices)} دستگاه")

    def _filter(self, text: str):
        text = text.strip().lower()
        if not text:
            self._populate(self._all_devices)
            return
        filtered = [
            d for d in self._all_devices
            if text in d[1].lower()
            or text in d[2].lower()
            or text in d[3].lower()
        ]
        self._populate(filtered)

    def _on_item_selected(self, item: QListWidgetItem):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            did, display = data
            self.device_selected.emit(did, display)
        self.accept()

    def showEvent(self, event):
        super().showEvent(event)
        self.search_input.setFocus()
        self.search_input.clear()
        self._populate(self._all_devices)


class SearchableDeviceCombo(QWidget):
    """
    Widget انتخاب دستگاه با جستجو

    Usage:
        combo = SearchableDeviceCombo()
        combo.set_device_id(5)
        did = combo.get_device_id()
    """

    device_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._device_id: Optional[int] = None
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.display = QLineEdit()
        self.display.setObjectName("scDisplay")
        self.display.setReadOnly(True)
        self.display.setPlaceholderText("— انتخاب دستگاه —")
        self.display.setCursor(Qt.CursorShape.PointingHandCursor)
        self.display.mousePressEvent = lambda e: self._open_popup()

        self.pick_btn = QPushButton("🔍")
        self.pick_btn.setObjectName("scBtn")
        self.pick_btn.setFixedSize(36, 36)
        self.pick_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pick_btn.setToolTip("جستجو و انتخاب دستگاه")
        self.pick_btn.clicked.connect(self._open_popup)

        layout.addWidget(self.display, 1)
        layout.addWidget(self.pick_btn)
        self.setFixedHeight(36)

    def _apply_style(self):
        self.setStyleSheet("""
            QLineEdit#scDisplay {
                background-color: white;
                color: #1E293B;
                border: 1px solid #E2E8F0;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                padding: 6px 10px;
                font-family: "Vazirmatn", sans-serif;
                font-size: 13px;
            }
            QLineEdit#scDisplay:focus {
                border-color: #6366F1;
            }
            QPushButton#scBtn {
                background-color: #6366F1;
                color: white;
                border: none;
                border-top-left-radius: 8px;
                border-bottom-left-radius: 8px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
                font-size: 14px;
            }
            QPushButton#scBtn:hover {
                background-color: #4F46E5;
            }
            QPushButton#scBtn:disabled {
                background-color: #CBD5E1;
            }
        """)

    def _open_popup(self):
        if not self.isEnabled():
            return

        popup = DeviceSearchPopup(self)
        popup.device_selected.connect(self._on_device_selected)

        popup_h = 340
        popup_w = 420

        pos_below = self.mapToGlobal(QPoint(0, self.height() + 4))
        pos_above = self.mapToGlobal(QPoint(0, -popup_h - 4))
        screen = QGuiApplication.primaryScreen().availableGeometry()

        if pos_below.y() + popup_h > screen.bottom():
            pos = pos_above
            if pos.y() < screen.top():
                pos.setY(screen.top() + 10)
        else:
            pos = pos_below

        if pos.x() + popup_w > screen.right():
            pos.setX(screen.right() - popup_w - 10)
        if pos.x() < screen.left():
            pos.setX(screen.left() + 10)

        popup.move(pos)
        popup.exec()

    def _on_device_selected(self, device_id: int, display: str):
        self._device_id = device_id
        self.display.setText(display)
        self.device_changed.emit(device_id)

    # ─── Public API ───

    def get_device_id(self) -> Optional[int]:
        return self._device_id

    def set_device_id(self, device_id: Optional[int]):
        if device_id is None:
            self._device_id = None
            self.display.setText("")
            return
        try:
            with get_session() as session:
                svc = DeviceTemplateService(session)
                t = svc.get_by_id(device_id)
                if t:
                    self._device_id = t.id
                    display = f"{t.code} — {t.name}" if t.code else t.name
                    self.display.setText(display)
        except Exception as e:
            logger.error(f"خطا در set_device_id: {e}")

    def clear(self):
        self._device_id = None
        self.display.setText("")

    def setEnabled(self, enabled: bool):
        super().setEnabled(enabled)
        self.display.setEnabled(enabled)
        self.pick_btn.setEnabled(enabled)