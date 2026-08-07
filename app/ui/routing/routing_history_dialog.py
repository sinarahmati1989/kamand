"""
Kamand - Routing History Dialog
پنجره تاریخچه Routing های یک دستگاه
"""
import logging
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QAbstractItemView, QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from app.services.routing_service import RoutingService
from app.services.device_template_service import DeviceTemplateService
from app.enums.engineering_enums import RoutingStatus
from app.database.session import get_session
from app.ui.widgets.toast import Toast

logger = logging.getLogger(__name__)

COLUMNS = [
    {"key": "revision",   "label": "Revision",       "width": 100},
    {"key": "status",     "label": "وضعیت",          "width": 120},
    {"key": "ops_count",  "label": "تعداد عملیات",   "width": 110},
    {"key": "total_time", "label": "زمان کل (دقیقه)", "width": 140},
    {"key": "total_cost", "label": "هزینه تخمینی",   "width": 180},
    {"key": "created_at", "label": "تاریخ ایجاد",    "width": 160},
    {"key": "notes",      "label": "یادداشت",         "width": 200},
]


class RoutingHistoryDialog(QDialog):
    """پنجره تاریخچه Routing های یک دستگاه"""

    def __init__(self, device_template_id: int, parent=None):
        super().__init__(parent)
        self.device_template_id = device_template_id
        self._selected_id: Optional[int] = None
        self._data: list[dict] = []

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowTitle("تاریخچه Routing ها")
        self.setMinimumSize(960, 500)
        self.setModal(True)

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        self._title = QLabel("تاریخچه Routing ها")
        self._title.setStyleSheet(
            "font-size: 16px; font-weight: 700; color: #1E293B;"
        )
        layout.addWidget(self._title)

        # اطلاعات دستگاه
        self._info = QFrame()
        self._info.setStyleSheet("""
            QFrame {
                background: rgba(99,102,241,0.06);
                border: 1px solid rgba(99,102,241,0.18);
                border-radius: 8px;
            }
            QLabel { background: transparent; padding: 4px 10px; }
        """)
        info_lay = QHBoxLayout(self._info)
        info_lay.setContentsMargins(12, 8, 12, 8)
        self._device_lbl = QLabel("")
        self._device_lbl.setStyleSheet(
            "font-size: 13px; font-weight: 700; color: #4F46E5;"
        )
        info_lay.addWidget(self._device_lbl)
        info_lay.addStretch()
        layout.addWidget(self._info)

        # جدول
        self._table = QTableWidget()
        self._table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._table.setColumnCount(len(COLUMNS))
        self._table.setHorizontalHeaderLabels([c["label"] for c in COLUMNS])
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.verticalHeader().setDefaultSectionSize(40)
        self._table.doubleClicked.connect(self._on_open)

        hdr = self._table.horizontalHeader()
        hdr.setStretchLastSection(True)
        for i, col in enumerate(COLUMNS):
            self._table.setColumnWidth(i, col["width"])

        self._table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 1px solid rgba(99,102,241,0.15);
                border-radius: 10px;
                font-size: 13px;
            }
            QTableWidget::item { padding: 8px 10px; }
            QTableWidget::item:selected {
                background: rgba(99,102,241,0.18);
                color: #1E293B;
            }
            QHeaderView::section {
                background: rgba(99,102,241,0.09);
                color: #374151;
                font-weight: 700;
                padding: 10px;
                border: none;
                border-bottom: 1px solid rgba(99,102,241,0.2);
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

        open_btn = QPushButton("باز کردن Routing انتخابی")
        open_btn.setObjectName("neonButton")
        open_btn.setFixedHeight(38)
        open_btn.setMinimumWidth(200)
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
                    self._device_lbl.setText(f"دستگاه: {tmpl.code} — {tmpl.name}")

                svc = RoutingService(session)
                headers = svc.get_headers_by_template(self.device_template_id)

                data = []
                for h in headers:
                    times = svc.calculate_total_time(h.id)
                    cost  = svc.calculate_total_cost(h.id)
                    ops   = svc.get_operations(h.id)

                    data.append({
                        "id":         h.id,
                        "revision":   f"Rev.{h.revision_no:02d}",
                        "status":     RoutingStatus(h.status).label if h.status else "—",
                        "status_clr": RoutingStatus(h.status).color if h.status else "#64748B",
                        "ops_count":  str(len(ops)),
                        "total_time": f"{times['total_min']:.1f}",
                        "total_cost": f"{cost:,.0f} ریال" if cost else "—",
                        "created_at": h.created_at.strftime("%Y-%m-%d %H:%M") if h.created_at else "—",
                        "notes":      h.notes or "—",
                    })

            self._data = data
            self._table.setRowCount(0)
            for row_data in data:
                r = self._table.rowCount()
                self._table.insertRow(r)
                for ci, col in enumerate(COLUMNS):
                    val = row_data.get(col["key"], "")
                    cell = QTableWidgetItem(str(val))
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if col["key"] == "status":
                        cell.setForeground(QColor(row_data["status_clr"]))
                        f = cell.font()
                        f.setBold(True)
                        cell.setFont(f)
                    self._table.setItem(r, ci, cell)

        except Exception as e:
            logger.error(f"خطا: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _on_open(self):
        row = self._table.currentRow()
        if row < 0 or row >= len(self._data):
            Toast.warning(self, "یک Routing را انتخاب کنید")
            return
        self._selected_id = self._data[row]["id"]
        self.accept()

    def get_selected_id(self) -> Optional[int]:
        return self._selected_id