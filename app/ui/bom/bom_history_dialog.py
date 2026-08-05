"""
Kamand - BOM History Dialog
پنجره نمایش تاریخچه تمام BOM های یک دستگاه
"""
import logging

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from app.services.bom_service import BOMService
from app.services.device_template_service import DeviceTemplateService
from app.enums.engineering_enums import BOMStatus
from app.database.session import get_session
from app.ui.widgets.toast import Toast

logger = logging.getLogger(__name__)

HISTORY_COLUMNS = [
    {"key": "revision",    "label": "Revision",     "width": 100},
    {"key": "status",      "label": "وضعیت",         "width": 120},
    {"key": "lines_count", "label": "تعداد خطوط",   "width": 110},
    {"key": "total_cost",  "label": "هزینه تخمینی", "width": 180},
    {"key": "created_at",  "label": "تاریخ ایجاد",  "width": 160},
    {"key": "notes",       "label": "یادداشت",      "width": 200},
]


class BOMHistoryDialog(QDialog):
    """پنجره تاریخچه BOM های یک دستگاه"""

    def __init__(self, device_template_id: int, parent=None):
        super().__init__(parent)
        self.device_template_id = device_template_id
        self._selected_id: int | None = None
        self._history_data: list[dict] = []

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowTitle("تاریخچه BOM ها")
        self.setMinimumSize(920, 500)
        self.setModal(True)

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # عنوان
        self._title_label = QLabel("تاریخچه BOM ها")
        self._title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
            color: #1E293B;
        """)
        layout.addWidget(self._title_label)

        # نوار اطلاعات دستگاه
        self._info_frame = QFrame()
        self._info_frame.setStyleSheet("""
            QFrame {
                background: rgba(99, 102, 241, 0.06);
                border: 1px solid rgba(99, 102, 241, 0.18);
                border-radius: 8px;
                padding: 4px;
            }
            QLabel { background: transparent; padding: 4px 10px; }
        """)
        info_layout = QHBoxLayout(self._info_frame)
        info_layout.setContentsMargins(12, 8, 12, 8)

        self._device_label = QLabel("")
        self._device_label.setStyleSheet(
            "font-size: 13px; font-weight: 700; color: #4F46E5;"
        )
        info_layout.addWidget(self._device_label)
        info_layout.addStretch()

        layout.addWidget(self._info_frame)

        # جدول
        self._table = QTableWidget()
        self._table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._table.setColumnCount(len(HISTORY_COLUMNS))
        self._table.setHorizontalHeaderLabels(
            [c["label"] for c in HISTORY_COLUMNS]
        )
        self._table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self._table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self._table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.verticalHeader().setDefaultSectionSize(40)
        self._table.doubleClicked.connect(self._on_open)

        hdr = self._table.horizontalHeader()
        hdr.setStretchLastSection(True)
        for i, col in enumerate(HISTORY_COLUMNS):
            if "width" in col:
                self._table.setColumnWidth(i, col["width"])

        self._table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 1px solid rgba(99, 102, 241, 0.15);
                border-radius: 10px;
                gridline-color: rgba(99, 102, 241, 0.08);
                font-size: 13px;
            }
            QTableWidget::item { padding: 8px 10px; }
            QTableWidget::item:selected {
                background: rgba(99, 102, 241, 0.18);
                color: #1E293B;
            }
            QHeaderView::section {
                background: rgba(99, 102, 241, 0.09);
                color: #374151;
                font-weight: 700;
                padding: 10px;
                border: none;
                border-bottom: 1px solid rgba(99, 102, 241, 0.2);
            }
            QTableWidget::item:alternate {
                background: rgba(248, 250, 252, 0.9);
            }
        """)

        layout.addWidget(self._table, stretch=1)

        # دکمه‌ها
        btn_row = QHBoxLayout()

        close_btn = QPushButton("بستن")
        close_btn.setObjectName("secondaryButton")
        close_btn.setFixedHeight(38)
        close_btn.setFixedWidth(100)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.reject)

        open_btn = QPushButton("باز کردن BOM انتخابی")
        open_btn.setObjectName("primaryButton")
        open_btn.setFixedHeight(38)
        open_btn.setMinimumWidth(180)
        open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_btn.clicked.connect(self._on_open)

        btn_row.addWidget(close_btn)
        btn_row.addStretch()
        btn_row.addWidget(open_btn)
        layout.addLayout(btn_row)

    def _load_data(self):
        try:
            with get_session() as session:
                tmpl_svc = DeviceTemplateService(session)
                tmpl = tmpl_svc.get_by_id(self.device_template_id)

                if tmpl:
                    self._device_label.setText(
                        f"دستگاه: {tmpl.code} — {tmpl.name}"
                    )

                bom_svc = BOMService(session)
                headers = bom_svc.get_headers_by_template(
                    self.device_template_id
                )

                # محاسبه هزینه‌ها
                data = []
                for h in headers:
                    total_cost = bom_svc.calculate_bom_cost(h.id)
                    # لود تعداد خطوط
                    bom_full = bom_svc.get_with_lines(h.id)
                    lines_count = len(bom_full.bom_lines) if bom_full else 0

                    data.append({
                        "id":          h.id,
                        "revision":    f"Rev.{h.revision_no:02d}",
                        "status":      BOMStatus(h.status).label if h.status else "—",
                        "status_color": BOMStatus(h.status).color if h.status else "#64748B",
                        "lines_count": str(lines_count),
                        "total_cost":  f"{total_cost:,.0f} ریال" if total_cost else "—",
                        "created_at":  h.created_at.strftime("%Y-%m-%d %H:%M") if h.created_at else "—",
                        "notes":       h.notes or "—",
                    })

            self._history_data = data
            self._fill_table(data)

        except Exception as e:
            logger.error(f"خطا در بارگذاری تاریخچه: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _fill_table(self, data: list[dict]):
        self._table.setRowCount(0)
        for row_data in data:
            r = self._table.rowCount()
            self._table.insertRow(r)

            for ci, col in enumerate(HISTORY_COLUMNS):
                val = row_data.get(col["key"], "")
                cell = QTableWidgetItem(str(val))
                cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                if col["key"] == "status":
                    cell.setForeground(QColor(row_data["status_color"]))
                    font = cell.font()
                    font.setBold(True)
                    cell.setFont(font)

                self._table.setItem(r, ci, cell)

    def _on_open(self):
        row = self._table.currentRow()
        if row < 0 or row >= len(self._history_data):
            Toast.warning(self, "یک BOM را انتخاب کنید")
            return
        self._selected_id = self._history_data[row]["id"]
        self.accept()

    def get_selected_id(self) -> int | None:
        return self._selected_id