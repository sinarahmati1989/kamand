"""
AuroraTable — جدول استاندارد Aurora Glass
"""
from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMenu
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
import logging

logger = logging.getLogger(__name__)


class AuroraTable(QTableWidget):
    """
    جدول استاندارد با استایل Aurora Glass

    ویژگی‌ها:
    • RTL
    • انتخاب ردیف کامل
    • Context Menu (ویرایش / حذف)
    • Double-click → edit
    • Alternating row colors
    """

    row_double_clicked = Signal(int)
    edit_requested = Signal(int)
    delete_requested = Signal(int)

    def __init__(
        self,
        columns: list[dict],
        parent=None,
    ):
        """
        columns: [
            {"key": "username", "label": "نام کاربری", "width": 140},
            {"key": "full_name", "label": "نام کامل"},   # بدون width → stretch
        ]
        """
        super().__init__(parent)
        self._columns = columns
        self._row_id_map: dict[int, int] = {}

        self._setup_table()

    # ─────────────────────────── Setup ───────────────────────────────

    def _setup_table(self):
        self.setColumnCount(len(self._columns))
        self.setHorizontalHeaderLabels(
            [col["label"] for col in self._columns]
        )

        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.setShowGrid(False)
        self.verticalHeader().setVisible(False)
        self.setObjectName("auroraTable")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        # هدر
        header = self.horizontalHeader()
        header.setDefaultAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        header.setHighlightSections(False)
        header.setStretchLastSection(True)

        # سایز ستون‌ها
        for i, col in enumerate(self._columns):
            if "width" in col:
                header.resizeSection(i, col["width"])
            else:
                header.setSectionResizeMode(
                    i, QHeaderView.ResizeMode.Stretch
                )

        self.verticalHeader().setDefaultSectionSize(48)

        # Context Menu
        self.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.doubleClicked.connect(self._on_double_click)

    # ─────────────────────────── Data ─────────────────────────────────

    def load_data(self, rows: list[dict]):
        """
        rows: [{"id": 1, "username": "ali", ...}]
        کلید "id" برای ردیابی استفاده میشه
        """
        self.setRowCount(0)
        self._row_id_map.clear()

        for row_idx, row_data in enumerate(rows):
            self.insertRow(row_idx)
            record_id = row_data.get("id", row_idx)
            self._row_id_map[row_idx] = record_id

            for col_idx, col in enumerate(self._columns):
                value = row_data.get(col["key"], "")
                text = str(value) if value is not None else "—"
                item = QTableWidgetItem(text)
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignRight
                    | Qt.AlignmentFlag.AlignVCenter
                )
                self.setItem(row_idx, col_idx, item)

        self._apply_row_colors()

    def _apply_row_colors(self):
        for row in range(self.rowCount()):
            color = (
                QColor(255, 255, 255, 20)
                if row % 2 == 0
                else QColor(99, 102, 241, 8)
            )
            for col in range(self.columnCount()):
                item = self.item(row, col)
                if item:
                    item.setBackground(color)

    def clear_data(self):
        self.setRowCount(0)
        self._row_id_map.clear()

    # ─────────────────────────── Context Menu ─────────────────────────

    def _show_context_menu(self, pos):
        row = self.rowAt(pos.y())
        if row < 0:
            return

        self.selectRow(row)
        record_id = self._row_id_map.get(row)
        if record_id is None:
            return

        menu = QMenu(self)
        menu.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        edit_action = menu.addAction("✏️  ویرایش")
        menu.addSeparator()
        delete_action = menu.addAction("🗑️  حذف / غیرفعال")

        action = menu.exec(self.mapToGlobal(pos))

        if action == edit_action:
            self.edit_requested.emit(record_id)
        elif action == delete_action:
            self.delete_requested.emit(record_id)

    def _on_double_click(self, index):
        row = index.row()
        record_id = self._row_id_map.get(row)
        if record_id is not None:
            self.row_double_clicked.emit(record_id)
            self.edit_requested.emit(record_id)

    # ─────────────────────────── Helpers ──────────────────────────────

    def get_selected_id(self) -> int | None:
        row = self.currentRow()
        if row < 0:
            return None
        return self._row_id_map.get(row)

    def get_row_count(self) -> int:
        return self.rowCount()