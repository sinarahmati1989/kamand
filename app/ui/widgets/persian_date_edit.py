"""
PersianDateEdit — Widget انتخاب تاریخ شمسی
────────────────────────────────────────────
• نمایش: 1405/08/15
• Popup calendar شمسی با ماه‌ها و روزهای فارسی
• استایل هماهنگ با Aurora Glass Light
• ذخیره داخلی: datetime.date میلادی (استاندارد)
• کوچک و هوشمند (خودش موقعیت بهینه رو پیدا می‌کنه)
"""
from datetime import date
from typing import Optional
import logging
import jdatetime

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGridLayout,
    QLineEdit, QPushButton, QLabel, QDialog,
    QComboBox,
)
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QGuiApplication

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════
# ثابت‌ها
# ══════════════════════════════════════════════════════════

PERSIAN_MONTHS = [
    "فروردین", "اردیبهشت", "خرداد", "تیر",
    "مرداد",   "شهریور",   "مهر",   "آبان",
    "آذر",     "دی",       "بهمن",  "اسفند",
]

PERSIAN_WEEKDAYS = ["ش", "ی", "د", "س", "چ", "پ", "ج"]


# ══════════════════════════════════════════════════════════
# دیالوگ انتخاب تاریخ (Popup)
# ══════════════════════════════════════════════════════════

class PersianCalendarPopup(QDialog):
    """پنجره Popup تقویم شمسی — کوچک و کاربردی"""

    date_selected = Signal(object)  # jdatetime.date or None

    def __init__(self, current_jdate: jdatetime.date, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.Popup |
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self._current = current_jdate
        self._display_year = current_jdate.year
        self._display_month = current_jdate.month

        self._setup_ui()
        self._apply_style()
        self._render_days()

    # ─────────────────────────────────────────────

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self._card = QWidget()
        self._card.setObjectName("calCard")
        self._card.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        outer.addWidget(self._card)

        root = QVBoxLayout(self._card)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(6)

        # ── هدر: سال/ماه ──
        header = QHBoxLayout()
        header.setSpacing(4)

        self.prev_btn = QPushButton("‹")
        self.prev_btn.setObjectName("calNavBtn")
        self.prev_btn.setFixedSize(24, 24)
        self.prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_btn.clicked.connect(self._on_prev_month)

        self.month_combo = QComboBox()
        self.month_combo.setObjectName("calCombo")
        for m in PERSIAN_MONTHS:
            self.month_combo.addItem(m)
        self.month_combo.setCurrentIndex(self._display_month - 1)
        self.month_combo.currentIndexChanged.connect(self._on_month_changed)

        self.year_combo = QComboBox()
        self.year_combo.setObjectName("calCombo")
        current_year = jdatetime.date.today().year
        for y in range(current_year - 50, current_year + 20):
            self.year_combo.addItem(str(y), y)
        self.year_combo.setCurrentText(str(self._display_year))
        self.year_combo.currentIndexChanged.connect(self._on_year_changed)

        self.next_btn = QPushButton("›")
        self.next_btn.setObjectName("calNavBtn")
        self.next_btn.setFixedSize(24, 24)
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.clicked.connect(self._on_next_month)

        header.addWidget(self.prev_btn)
        header.addWidget(self.month_combo, 1)
        header.addWidget(self.year_combo, 1)
        header.addWidget(self.next_btn)
        root.addLayout(header)

        # ── نام روزهای هفته ──
        weekdays_row = QHBoxLayout()
        weekdays_row.setSpacing(2)
        for wd in PERSIAN_WEEKDAYS:
            lbl = QLabel(wd)
            lbl.setObjectName("calWeekday")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setFixedSize(26, 20)
            weekdays_row.addWidget(lbl)
        root.addLayout(weekdays_row)

        # ── گرید روزها ──
        self.days_grid = QGridLayout()
        self.days_grid.setSpacing(2)
        root.addLayout(self.days_grid)

        # ── دکمه امروز/پاک ──
        footer = QHBoxLayout()
        footer.setSpacing(6)

        self.today_btn = QPushButton("امروز")
        self.today_btn.setObjectName("calTodayBtn")
        self.today_btn.setFixedHeight(26)
        self.today_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.today_btn.clicked.connect(self._on_today)

        self.clear_btn = QPushButton("پاک")
        self.clear_btn.setObjectName("calClearBtn")
        self.clear_btn.setFixedHeight(26)
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.clicked.connect(self._on_clear)

        footer.addWidget(self.today_btn)
        footer.addWidget(self.clear_btn)
        root.addLayout(footer)

    # ─────────────────────────────────────────────

    def _apply_style(self):
        self.setStyleSheet("""
            QWidget#calCard {
                background-color: #FFFFFF;
                border: 1px solid rgba(99, 102, 241, 0.3);
                border-radius: 10px;
            }

            QPushButton#calNavBtn {
                background-color: rgba(99, 102, 241, 0.1);
                color: #6366F1;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton#calNavBtn:hover {
                background-color: rgba(99, 102, 241, 0.2);
            }

            QComboBox#calCombo {
                background-color: #F8FAFC;
                color: #1E293B;
                border: 1px solid #E2E8F0;
                border-radius: 5px;
                padding: 3px 6px;
                font-family: "Vazirmatn", sans-serif;
                font-size: 12px;
                font-weight: 600;
                min-height: 22px;
            }
            QComboBox#calCombo::drop-down {
                border: none;
                width: 18px;
            }
            QComboBox#calCombo QAbstractItemView {
                background-color: white;
                border: 1px solid #E2E8F0;
                selection-background-color: #6366F1;
                selection-color: white;
            }

            QLabel#calWeekday {
                background-color: #EDE9FE;
                color: #6366F1;
                border-radius: 3px;
                font-family: "Vazirmatn", sans-serif;
                font-size: 11px;
                font-weight: bold;
            }

            QPushButton#calDay {
                background-color: transparent;
                color: #1E293B;
                border: none;
                border-radius: 4px;
                font-family: "Vazirmatn", sans-serif;
                font-size: 11px;
                font-weight: 500;
                min-width: 26px;
                min-height: 22px;
                max-width: 26px;
                max-height: 22px;
            }
            QPushButton#calDay:hover {
                background-color: rgba(99, 102, 241, 0.15);
                color: #6366F1;
            }

            QPushButton#calDaySelected {
                background-color: #6366F1;
                color: white;
                border: none;
                border-radius: 4px;
                font-family: "Vazirmatn", sans-serif;
                font-size: 11px;
                font-weight: bold;
                min-width: 26px;
                min-height: 22px;
                max-width: 26px;
                max-height: 22px;
            }

            QPushButton#calDayToday {
                background-color: rgba(99, 102, 241, 0.1);
                color: #6366F1;
                border: 1px solid #6366F1;
                border-radius: 4px;
                font-family: "Vazirmatn", sans-serif;
                font-size: 11px;
                font-weight: bold;
                min-width: 26px;
                min-height: 22px;
                max-width: 26px;
                max-height: 22px;
            }
            QPushButton#calDayToday:hover {
                background-color: rgba(99, 102, 241, 0.25);
            }

            QPushButton#calTodayBtn {
                background-color: #6366F1;
                color: white;
                border: none;
                border-radius: 5px;
                font-family: "Vazirmatn", sans-serif;
                font-size: 11px;
                font-weight: bold;
                padding: 0 10px;
            }
            QPushButton#calTodayBtn:hover {
                background-color: #4F46E5;
            }

            QPushButton#calClearBtn {
                background-color: #F1F5F9;
                color: #64748B;
                border: 1px solid #CBD5E1;
                border-radius: 5px;
                font-family: "Vazirmatn", sans-serif;
                font-size: 11px;
                font-weight: 600;
                padding: 0 10px;
            }
            QPushButton#calClearBtn:hover {
                background-color: #E2E8F0;
            }
        """)

    # ─────────────────────────────────────────────

    def _clear_grid(self):
        while self.days_grid.count():
            item = self.days_grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _render_days(self):
        self._clear_grid()

        first_day = jdatetime.date(self._display_year, self._display_month, 1)
        first_weekday = first_day.weekday()

        if self._display_month <= 6:
            days_in_month = 31
        elif self._display_month <= 11:
            days_in_month = 30
        else:
            days_in_month = 30 if jdatetime.date(self._display_year, 1, 1).isleap() else 29

        today = jdatetime.date.today()

        row, col = 0, first_weekday

        for day in range(1, days_in_month + 1):
            btn = QPushButton(str(day))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

            is_selected = (
                day == self._current.day and
                self._display_month == self._current.month and
                self._display_year == self._current.year
            )
            is_today = (
                day == today.day and
                self._display_month == today.month and
                self._display_year == today.year
            )

            if is_selected:
                btn.setObjectName("calDaySelected")
            elif is_today:
                btn.setObjectName("calDayToday")
            else:
                btn.setObjectName("calDay")

            btn.clicked.connect(lambda checked=False, d=day: self._on_day_clicked(d))
            self.days_grid.addWidget(btn, row, col)

            col += 1
            if col > 6:
                col = 0
                row += 1

    # ─────────────────────────────────────────────
    # Handlers
    # ─────────────────────────────────────────────

    def _on_day_clicked(self, day: int):
        selected = jdatetime.date(self._display_year, self._display_month, day)
        self.date_selected.emit(selected)
        self.accept()

    def _on_prev_month(self):
        self._display_month -= 1
        if self._display_month < 1:
            self._display_month = 12
            self._display_year -= 1
        self._sync_combos()
        self._render_days()

    def _on_next_month(self):
        self._display_month += 1
        if self._display_month > 12:
            self._display_month = 1
            self._display_year += 1
        self._sync_combos()
        self._render_days()

    def _on_month_changed(self, index: int):
        self._display_month = index + 1
        self._render_days()

    def _on_year_changed(self, index: int):
        self._display_year = self.year_combo.itemData(index)
        self._render_days()

    def _on_today(self):
        today = jdatetime.date.today()
        self.date_selected.emit(today)
        self.accept()

    def _on_clear(self):
        self.date_selected.emit(None)
        self.accept()

    def _sync_combos(self):
        self.month_combo.blockSignals(True)
        self.year_combo.blockSignals(True)

        self.month_combo.setCurrentIndex(self._display_month - 1)
        idx = self.year_combo.findData(self._display_year)
        if idx >= 0:
            self.year_combo.setCurrentIndex(idx)

        self.month_combo.blockSignals(False)
        self.year_combo.blockSignals(False)


# ══════════════════════════════════════════════════════════
# Widget اصلی
# ══════════════════════════════════════════════════════════

class PersianDateEdit(QWidget):
    """
    ویجت انتخاب تاریخ شمسی

    Usage:
        de = PersianDateEdit()
        de.set_date(date(2024, 11, 5))
        gregorian = de.get_date()  # datetime.date یا None
    """

    date_changed = Signal(object)

    def __init__(self, parent=None, allow_empty: bool = True):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._allow_empty = allow_empty
        self._current: Optional[jdatetime.date] = None

        self._setup_ui()
        self._apply_style()

        if not allow_empty:
            self.set_today()

    # ─────────────────────────────────────────────

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.display = QLineEdit()
        self.display.setObjectName("pdeDisplay")
        self.display.setReadOnly(True)
        self.display.setPlaceholderText("انتخاب تاریخ...")
        self.display.setCursor(Qt.CursorShape.PointingHandCursor)
        self.display.mousePressEvent = lambda e: self._open_popup()

        self.pick_btn = QPushButton("📅")
        self.pick_btn.setObjectName("pdeBtn")
        self.pick_btn.setFixedSize(36, 36)
        self.pick_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pick_btn.clicked.connect(self._open_popup)

        layout.addWidget(self.display, 1)
        layout.addWidget(self.pick_btn)

        self.setFixedHeight(36)

    def _apply_style(self):
        self.setStyleSheet("""
            QLineEdit#pdeDisplay {
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
            QLineEdit#pdeDisplay:focus {
                border-color: #6366F1;
            }

            QPushButton#pdeBtn {
                background-color: #6366F1;
                color: white;
                border: none;
                border-top-left-radius: 8px;
                border-bottom-left-radius: 8px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
                font-size: 14px;
            }
            QPushButton#pdeBtn:hover {
                background-color: #4F46E5;
            }
        """)

    # ─────────────────────────────────────────────
    # Popup — با موقعیت هوشمند
    # ─────────────────────────────────────────────

    def _open_popup(self):
        try:
            current = self._current or jdatetime.date.today()
            popup = PersianCalendarPopup(current, self)
            popup.date_selected.connect(self._on_date_selected)

            # سایز واقعی popup را قبل از نمایش محاسبه کن
            popup.adjustSize()
            popup_size = popup.sizeHint()
            popup_h = popup_size.height() if popup_size.height() > 0 else 300
            popup_w = popup_size.width() if popup_size.width() > 0 else 240

            # موقعیت پیش‌فرض: زیر ویجت
            pos_below = self.mapToGlobal(QPoint(0, self.height() + 4))
            pos_above = self.mapToGlobal(QPoint(0, -popup_h - 4))

            screen = QGuiApplication.primaryScreen().availableGeometry()

            # اگر پایین جا نیست، بالای ویجت
            if pos_below.y() + popup_h > screen.bottom():
                pos = pos_above
                # اگر بالا هم جا نیست، بچسبان به پایین صفحه
                if pos.y() < screen.top():
                    pos.setY(screen.top() + 10)
            else:
                pos = pos_below

            # تنظیم افقی
            if pos.x() + popup_w > screen.right():
                pos.setX(screen.right() - popup_w - 10)
            if pos.x() < screen.left():
                pos.setX(screen.left() + 10)

            popup.move(pos)
            popup.exec()

        except Exception as e:
            logger.error(f"خطا در باز کردن تقویم: {e}", exc_info=True)

    def _on_date_selected(self, jdate: Optional[jdatetime.date]):
        if jdate is None:
            self._current = None
            self.display.setText("")
        else:
            self._current = jdate
            self._update_display()

        greg = self.get_date()
        self.date_changed.emit(greg)

    def _update_display(self):
        if self._current:
            text = f"{self._current.year:04d}/{self._current.month:02d}/{self._current.day:02d}"
            self.display.setText(text)

    # ─────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────

    def set_date(self, greg_date: Optional[date]):
        if greg_date is None:
            self._current = None
            self.display.setText("")
        else:
            self._current = jdatetime.date.fromgregorian(date=greg_date)
            self._update_display()

    def get_date(self) -> Optional[date]:
        if self._current is None:
            return None
        return self._current.togregorian()

    def set_today(self):
        self._current = jdatetime.date.today()
        self._update_display()

    def clear(self):
        self._current = None
        self.display.setText("")