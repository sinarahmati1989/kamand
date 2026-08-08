"""
SearchableCustomerCombo — انتخاب مشتری با جستجو
مناسب برای هزاران مشتری
"""
import logging
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLineEdit, QPushButton, QDialog,
    QListWidget, QListWidgetItem, QLabel,
    QFrame,
)
from PySide6.QtCore import Qt, Signal, QPoint

from app.database.session import get_session
from app.services.customer_service import CustomerService

logger = logging.getLogger(__name__)


class CustomerSearchPopup(QDialog):
    """Popup جستجو در لیست مشتریان"""

    customer_selected = Signal(int, str)  # id, display_name

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.Popup |
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setFixedSize(380, 320)

        self._all_customers = []
        self._setup_ui()
        self._apply_style()
        self._load_customers()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QWidget()
        card.setObjectName("searchCard")
        outer.addWidget(card)

        v = QVBoxLayout(card)
        v.setContentsMargins(10, 10, 10, 10)
        v.setSpacing(8)

        # فیلد جستجو
        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText(
            "🔍 جستجو نام، کد، نام تجاری..."
        )
        self.search_input.setFixedHeight(34)
        self.search_input.textChanged.connect(self._filter)
        v.addWidget(self.search_input)

        # لیست
        self.list_widget = QListWidget()
        self.list_widget.setObjectName("customerList")
        self.list_widget.itemDoubleClicked.connect(self._on_item_selected)
        self.list_widget.itemClicked.connect(self._on_item_selected)
        v.addWidget(self.list_widget, 1)

        # پیام تعداد
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
            QListWidget#customerList {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                padding: 4px;
                font-family: "Vazirmatn", sans-serif;
                font-size: 13px;
                outline: none;
            }
            QListWidget#customerList::item {
                padding: 8px 10px;
                border-radius: 4px;
                color: #1E293B;
            }
            QListWidget#customerList::item:hover {
                background-color: rgba(99, 102, 241, 0.1);
                color: #6366F1;
            }
            QListWidget#customerList::item:selected {
                background-color: #6366F1;
                color: white;
            }
            QLabel#infoLabel {
                color: #94A3B8;
                font-size: 11px;
                font-family: "Vazirmatn", sans-serif;
            }
        """)

    def _load_customers(self):
        try:
            with get_session() as session:
                svc = CustomerService(session)
                customers = svc.get_all()
                self._all_customers = [
                    (c.id, c.code or "", c.name or "", c.trade_name or "")
                    for c in customers
                ]
            self._populate(self._all_customers)
        except Exception as e:
            logger.error(f"خطا در بارگذاری مشتریان: {e}", exc_info=True)
            self.info_label.setText(f"خطا: {e}")

    def _populate(self, customers):
        self.list_widget.clear()
        for cid, code, name, trade in customers:
            display = f"{code} — {name}" if code else name
            if trade:
                display += f"  ({trade})"
            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, (cid, f"{code} — {name}" if code else name))
            self.list_widget.addItem(item)

        self.info_label.setText(f"{len(customers)} مشتری")

    def _filter(self, text: str):
        text = text.strip().lower()
        if not text:
            self._populate(self._all_customers)
            return

        filtered = [
            c for c in self._all_customers
            if text in c[1].lower()
            or text in c[2].lower()
            or text in c[3].lower()
        ]
        self._populate(filtered)

    def _on_item_selected(self, item: QListWidgetItem):
        cid, display = item.data(Qt.ItemDataRole.UserRole)
        self.customer_selected.emit(cid, display)
        self.accept()

    def showEvent(self, event):
        super().showEvent(event)
        self.search_input.setFocus()


class SearchableCustomerCombo(QWidget):
    """
    Widget انتخاب مشتری با جستجو

    Usage:
        combo = SearchableCustomerCombo()
        combo.set_customer_id(5)
        cid = combo.get_customer_id()
    """

    customer_changed = Signal(int)  # customer_id or None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._customer_id: Optional[int] = None
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # نمایشگر (readonly)
        self.display = QLineEdit()
        self.display.setObjectName("scDisplay")
        self.display.setReadOnly(True)
        self.display.setPlaceholderText("— انتخاب مشتری —")
        self.display.setCursor(Qt.CursorShape.PointingHandCursor)
        self.display.mousePressEvent = lambda e: self._open_popup()

        # دکمه جستجو
        self.pick_btn = QPushButton("🔍")
        self.pick_btn.setObjectName("scBtn")
        self.pick_btn.setFixedSize(36, 36)
        self.pick_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pick_btn.setToolTip("جستجو و انتخاب مشتری")
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
        """)

    def _open_popup(self):
        popup = CustomerSearchPopup(self)
        popup.customer_selected.connect(self._on_customer_selected)

        # موقعیت popup: زیر ویجت
        pos = self.mapToGlobal(QPoint(0, self.height() + 2))

        # اگر پایین صفحه هست، بالا نمایش بده
        from PySide6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen().availableGeometry()
        popup_h = 320
        if pos.y() + popup_h > screen.bottom():
            pos = self.mapToGlobal(QPoint(0, -popup_h - 2))

        popup.move(pos)
        popup.exec()

    def _on_customer_selected(self, customer_id: int, display: str):
        self._customer_id = customer_id
        self.display.setText(display)
        self.customer_changed.emit(customer_id)

    # ═══ Public API ═══

    def get_customer_id(self) -> Optional[int]:
        return self._customer_id

    def set_customer_id(self, customer_id: Optional[int]):
        if customer_id is None:
            self._customer_id = None
            self.display.setText("")
            return

        try:
            with get_session() as session:
                svc = CustomerService(session)
                c = svc.get_by_id(customer_id)
                if c:
                    self._customer_id = c.id
                    display = f"{c.code} — {c.name}" if c.code else c.name
                    self.display.setText(display)
        except Exception as e:
            logger.error(f"خطا: {e}")

    def clear(self):
        self._customer_id = None
        self.display.setText("")