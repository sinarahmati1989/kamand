"""
Kamand - Routing Page
صفحه ویرایشگر مسیر ساخت — هم‌الگوی BOM Page
"""
import logging

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QDialog,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from app.ui.widgets.workflow_bar import WorkflowBar
from app.ui.widgets.toast import Toast
from app.ui.base.confirm_dialog import ConfirmDialog
from app.services.routing_service import RoutingService
from app.services.device_template_service import DeviceTemplateService
from app.enums.engineering_enums import RoutingStatus
from app.database.session import get_session

logger = logging.getLogger(__name__)

ENGINEERING_STEPS = [
    ("device_templates", "تعریف دستگاه"),
    ("items",            "اقلام"),
    ("bom",              "BOM"),
    ("routing",          "مسیر ساخت"),
]

OP_COLUMNS = [
    {"key": "step_no",     "label": "مرحله",           "width": 70},
    {"key": "op_code",     "label": "کد عملیات",       "width": 100},
    {"key": "op_name",     "label": "نام عملیات",      "width": 200},
    {"key": "department",  "label": "دپارتمان",         "width": 120},
    {"key": "work_center", "label": "مرکز کار",        "width": 120},
    {"key": "machine",     "label": "ماشین",            "width": 120},
    {"key": "setup_time",  "label": "آماده‌سازی (دق)", "width": 100},
    {"key": "cycle_time",  "label": "سیکل (دق)",       "width": 90},
    {"key": "labor",       "label": "نیروی کار",       "width": 80},
    {"key": "est_cost",    "label": "هزینه تخمینی",    "width": 140},
    {"key": "outsourced",  "label": "برون‌سپاری",      "width": 85},
    {"key": "notes",       "label": "یادداشت",          "width": 150},
]


class RoutingPage(QWidget):
    """صفحه مسیر ساخت"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._current_template_id: int | None = None
        self._current_header_id:   int | None = None
        self._ops_data: list[dict] = []
        self._setup_ui()
        self._load_templates()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        # WorkflowBar
        wf = WorkflowBar(ENGINEERING_STEPS)
        wf.set_active("routing")
        wf.step_clicked.connect(self._on_workflow_step)
        layout.addWidget(wf)

        # عنوان
        title = QLabel("ویرایشگر مسیر ساخت (Routing)")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        layout.addLayout(self._build_selector_row())
        layout.addWidget(self._build_header_info())

        section_title = QLabel("عملیات مسیر ساخت")
        section_title.setStyleSheet("""
            font-size: 14px; font-weight: 700; color: #374151;
            padding: 4px 0;
            border-bottom: 2px solid rgba(99,102,241,0.2);
        """)
        layout.addWidget(section_title)

        layout.addLayout(self._build_op_actions())
        layout.addWidget(self._build_table(), stretch=1)
        layout.addLayout(self._build_bottom_row())

    def _build_selector_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)

        lbl1 = QLabel("تعریف دستگاه:")
        lbl1.setFixedWidth(110)
        lbl1.setStyleSheet("font-weight: 700; color: #374151; font-size: 13px;")

        self._template_combo = QComboBox()
        self._template_combo.setFixedHeight(40)
        self._template_combo.setMinimumWidth(320)
        self._template_combo.currentIndexChanged.connect(self._on_template_changed)

        lbl2 = QLabel("Routing:")
        lbl2.setFixedWidth(60)
        lbl2.setStyleSheet("font-weight: 700; color: #374151; font-size: 13px;")

        self._routing_combo = QComboBox()
        self._routing_combo.setFixedHeight(40)
        self._routing_combo.setMinimumWidth(220)
        self._routing_combo.currentIndexChanged.connect(self._on_routing_changed)

        history_btn = QPushButton("📋 تاریخچه")
        history_btn.setObjectName("secondaryButton")
        history_btn.setFixedHeight(40)
        history_btn.setMinimumWidth(110)
        history_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        history_btn.clicked.connect(self._on_show_history)

        new_btn = QPushButton("+ Routing جدید")
        new_btn.setObjectName("primaryButton")
        new_btn.setFixedHeight(40)
        new_btn.setMinimumWidth(140)
        new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_btn.clicked.connect(self._on_new_routing)

        row.addWidget(lbl1)
        row.addWidget(self._template_combo)
        row.addSpacing(16)
        row.addWidget(lbl2)
        row.addWidget(self._routing_combo)
        row.addWidget(history_btn)
        row.addWidget(new_btn)
        row.addStretch()
        return row

    def _build_header_info(self) -> QFrame:
        self._header_frame = QFrame()
        self._header_frame.setObjectName("bomInfoFrame")
        self._header_frame.setFixedHeight(56)
        self._header_frame.setStyleSheet("""
            QFrame#bomInfoFrame {
                background: rgba(99,102,241,0.06);
                border: 1px solid rgba(99,102,241,0.18);
                border-radius: 10px;
            }
            QLabel { background: transparent; }
        """)

        row = QHBoxLayout(self._header_frame)
        row.setContentsMargins(18, 8, 18, 8)
        row.setSpacing(24)

        self._lbl_code   = QLabel("هیچ Routing انتخاب نشده")
        self._lbl_code.setStyleSheet("font-weight: 700; color: #1E293B; font-size: 13px;")

        self._lbl_status = QLabel("")
        self._lbl_status.setStyleSheet("font-size: 13px;")

        self._lbl_count  = QLabel("")
        self._lbl_count.setStyleSheet("color: #64748B; font-size: 13px; font-weight: 600;")

        self._lbl_time   = QLabel("")
        self._lbl_time.setStyleSheet("font-weight: 700; color: #6366F1; font-size: 13px;")

        self._status_btn = QPushButton("تغییر وضعیت")
        self._status_btn.setObjectName("warningButton")
        self._status_btn.setFixedHeight(34)
        self._status_btn.setFixedWidth(130)
        self._status_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._status_btn.clicked.connect(self._on_toggle_status)
        self._status_btn.setVisible(False)

        row.addWidget(self._lbl_code)
        row.addWidget(self._lbl_status)
        row.addWidget(self._lbl_count)
        row.addStretch()
        row.addWidget(self._lbl_time)
        row.addWidget(self._status_btn)
        return self._header_frame

    def _build_op_actions(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)

        self._add_btn = QPushButton("+ افزودن عملیات")
        self._add_btn.setObjectName("primaryButton")
        self._add_btn.setFixedHeight(38)
        self._add_btn.setFixedWidth(160)
        self._add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._add_btn.clicked.connect(self._on_add_op)

        self._edit_btn = QPushButton("ویرایش عملیات")
        self._edit_btn.setObjectName("secondaryButton")
        self._edit_btn.setFixedHeight(38)
        self._edit_btn.setFixedWidth(130)
        self._edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._edit_btn.clicked.connect(self._on_edit_op)

        self._del_btn = QPushButton("حذف عملیات")
        self._del_btn.setObjectName("warningButton")
        self._del_btn.setFixedHeight(38)
        self._del_btn.setFixedWidth(120)
        self._del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._del_btn.clicked.connect(self._on_delete_op)

        row.addWidget(self._add_btn)
        row.addWidget(self._edit_btn)
        row.addWidget(self._del_btn)
        row.addStretch()
        return row

    def _build_table(self) -> QTableWidget:
        self._table = QTableWidget()
        self._table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._table.setColumnCount(len(OP_COLUMNS))
        self._table.setHorizontalHeaderLabels([c["label"] for c in OP_COLUMNS])
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.verticalHeader().setDefaultSectionSize(38)
        self._table.doubleClicked.connect(self._on_edit_op)

        hdr = self._table.horizontalHeader()
        hdr.setStretchLastSection(True)
        for i, col in enumerate(OP_COLUMNS):
            self._table.setColumnWidth(i, col["width"])

        self._table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 1px solid rgba(99,102,241,0.15);
                border-radius: 10px;
                gridline-color: rgba(99,102,241,0.08);
                font-size: 13px;
            }
            QTableWidget::item { padding: 8px 10px; }
            QTableWidget::item:selected {
                background: rgba(99,102,241,0.15);
                color: #1E293B;
            }
            QHeaderView::section {
                background: rgba(99,102,241,0.09);
                color: #374151;
                font-weight: 700;
                padding: 10px 8px;
                border: none;
                border-bottom: 1px solid rgba(99,102,241,0.2);
            }
            QTableWidget::item:alternate {
                background: rgba(248,250,252,0.9);
            }
        """)
        return self._table

    def _build_bottom_row(self) -> QHBoxLayout:
        row = QHBoxLayout()

        self._del_routing_btn = QPushButton("حذف کل Routing")
        self._del_routing_btn.setObjectName("dangerButton")
        self._del_routing_btn.setFixedHeight(38)
        self._del_routing_btn.setFixedWidth(150)
        self._del_routing_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._del_routing_btn.clicked.connect(self._on_delete_routing)

        self._total_label = QLabel("")
        self._total_label.setStyleSheet("""
            font-size: 15px; font-weight: 700; color: #6366F1;
            padding: 8px 16px;
            background: rgba(99,102,241,0.08);
            border-radius: 8px;
        """)

        row.addWidget(self._del_routing_btn)
        row.addStretch()
        row.addWidget(self._total_label)
        return row

    # ── Data ───────────────────────────────────────────────────────

    def _load_templates(self):
        try:
            with get_session() as session:
                svc = DeviceTemplateService(session)
                templates = svc.search("", None, None)

            self._template_combo.blockSignals(True)
            self._template_combo.clear()
            self._template_combo.addItem("— دستگاه را انتخاب کنید —", None)
            for t in templates:
                self._template_combo.addItem(f"{t.code}  —  {t.name}", t.id)
            self._template_combo.blockSignals(False)

        except Exception as e:
            Toast.error(self, f"خطا: {e}")

    def _load_routing_list(self, template_id: int):
        try:
            with get_session() as session:
                svc = RoutingService(session)
                headers = svc.get_headers_by_template(template_id)

            self._routing_combo.blockSignals(True)
            self._routing_combo.clear()
            self._routing_combo.addItem("— Routing انتخاب کنید —", None)
            for h in headers:
                lbl = RoutingStatus(h.status).label if h.status else ""
                self._routing_combo.addItem(
                    f"Rev.{h.revision_no:02d}  —  {lbl}", h.id
                )
            self._routing_combo.blockSignals(False)

            if len(headers) == 1:
                self._routing_combo.setCurrentIndex(1)

        except Exception as e:
            logger.error(f"خطا: {e}")

    def _load_routing_ops(self, header_id: int):
        try:
            with get_session() as session:
                svc    = RoutingService(session)
                header = svc.get_with_operations(header_id)
                times  = svc.calculate_total_time(header_id)
                cost   = svc.calculate_total_cost(header_id)

            if not header:
                return

            self._lbl_code.setText(header.routing_code)

            st = RoutingStatus(header.status) if header.status else None
            if st:
                self._lbl_status.setText(f"وضعیت: {st.label}")
                self._lbl_status.setStyleSheet(
                    f"font-size:13px; font-weight:700; color:{st.color};"
                )

            ops = header.routing_operations or []
            self._lbl_count.setText(f"تعداد عملیات: {len(ops)}")

            total_min = times["total_min"]
            if total_min >= 60:
                time_str = f"{total_min/60:.1f} ساعت ({total_min:.0f} دق)"
            else:
                time_str = f"{total_min:.0f} دقیقه"
            self._lbl_time.setText(f"زمان کل: {time_str}")

            cost_str = f"{cost:,.0f} ریال" if cost else "—"
            self._total_label.setText(f"هزینه تخمینی کل: {cost_str}")

            self._status_btn.setVisible(True)

            self._ops_data = []
            self._table.setRowCount(0)

            for op in ops:
                mfg_op = op.operation
                est = op.estimated_cost

                row_data = {
                    "id":          op.id,
                    "step_no":     str(op.step_no),
                    "op_code":     mfg_op.code     if mfg_op else "—",
                    "op_name":     mfg_op.name     if mfg_op else "—",
                    "department":  op.department.name  if op.department  else "—",
                    "work_center": op.work_center.name if op.work_center else "—",
                    "machine":     op.machine.name     if op.machine     else "—",
                    "setup_time":  f"{float(op.setup_time_min or 0):.1f}",
                    "cycle_time":  f"{float(op.cycle_time_min or 0):.1f}",
                    "labor":       str(op.labor_count or 1),
                    "est_cost":    f"{est:,.0f}" if est else "—",
                    "outsourced":  "بله" if op.is_outsourced else "خیر",
                    "notes":       op.notes or "—",
                }
                self._ops_data.append(row_data)

                r = self._table.rowCount()
                self._table.insertRow(r)

                for ci, col in enumerate(OP_COLUMNS):
                    val  = row_data.get(col["key"], "")
                    cell = QTableWidgetItem(str(val))
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                    if col["key"] == "est_cost" and est:
                        cell.setForeground(QColor("#6366F1"))
                    if col["key"] == "outsourced" and op.is_outsourced:
                        cell.setForeground(QColor("#F59E0B"))

                    self._table.setItem(r, ci, cell)

        except Exception as e:
            logger.error(f"خطا در بارگذاری عملیات Routing: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _clear_display(self):
        self._ops_data = []
        self._table.setRowCount(0)
        self._current_header_id = None
        self._lbl_code.setText("هیچ Routing انتخاب نشده")
        self._lbl_status.setText("")
        self._lbl_count.setText("")
        self._lbl_time.setText("")
        self._status_btn.setVisible(False)
        self._total_label.setText("")

    # ── Events ─────────────────────────────────────────────────────

    def _on_workflow_step(self, key: str):
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, "_navigate_to"):
                parent._navigate_to(key)
                return
            parent = parent.parent()

    def _on_template_changed(self, _idx: int):
        tid = self._template_combo.currentData()
        self._current_template_id = tid
        self._routing_combo.blockSignals(True)
        self._routing_combo.clear()
        self._routing_combo.addItem("— Routing انتخاب کنید —", None)
        self._routing_combo.blockSignals(False)
        self._clear_display()
        if tid:
            self._load_routing_list(tid)

    def _on_routing_changed(self, _idx: int):
        hid = self._routing_combo.currentData()
        self._current_header_id = hid
        self._table.setRowCount(0)
        self._ops_data = []
        if hid:
            self._load_routing_ops(hid)
        else:
            self._clear_display()

    def _on_new_routing(self):
        if not self._current_template_id:
            Toast.warning(self, "ابتدا یک دستگاه انتخاب کنید")
            return
        try:
            with get_session() as session:
                svc    = RoutingService(session)
                header = svc.create_header(self._current_template_id)
                new_id = header.id
                rev    = header.revision_no

            Toast.success(self, f"Routing Rev.{rev:02d} ساخته شد")
            self._load_routing_list(self._current_template_id)

            for i in range(self._routing_combo.count()):
                if self._routing_combo.itemData(i) == new_id:
                    self._routing_combo.setCurrentIndex(i)
                    break

        except ValueError as e:
            Toast.warning(self, str(e))
        except Exception as e:
            Toast.error(self, f"خطا: {e}")

    def _on_show_history(self):
        if not self._current_template_id:
            Toast.warning(self, "ابتدا یک دستگاه انتخاب کنید")
            return
        from app.ui.routing.routing_history_dialog import RoutingHistoryDialog
        dlg = RoutingHistoryDialog(self._current_template_id, parent=self)
        if dlg.exec():
            selected = dlg.get_selected_id()
            if selected:
                for i in range(self._routing_combo.count()):
                    if self._routing_combo.itemData(i) == selected:
                        self._routing_combo.setCurrentIndex(i)
                        return
                self._load_routing_list(self._current_template_id)
                for i in range(self._routing_combo.count()):
                    if self._routing_combo.itemData(i) == selected:
                        self._routing_combo.setCurrentIndex(i)
                        break

    def _on_add_op(self):
        if not self._current_header_id:
            Toast.warning(self, "ابتدا یک Routing انتخاب کنید")
            return
        from app.ui.routing.routing_operation_dialog import RoutingOperationDialog
        dlg = RoutingOperationDialog(
            routing_header_id=self._current_header_id,
            parent=self,
        )
        if dlg.exec():
            self._load_routing_ops(self._current_header_id)
            Toast.success(self, "عملیات با موفقیت افزوده شد")

    def _on_edit_op(self):
        row = self._table.currentRow()
        if row < 0 or row >= len(self._ops_data):
            Toast.warning(self, "یک عملیات را انتخاب کنید")
            return
        op_id = self._ops_data[row]["id"]
        from app.ui.routing.routing_operation_dialog import RoutingOperationDialog
        dlg = RoutingOperationDialog(
            routing_header_id=self._current_header_id,
            op_id=op_id,
            parent=self,
        )
        if dlg.exec():
            self._load_routing_ops(self._current_header_id)
            Toast.success(self, "عملیات ویرایش شد")

    def _on_delete_op(self):
        row = self._table.currentRow()
        if row < 0 or row >= len(self._ops_data):
            Toast.warning(self, "یک عملیات را انتخاب کنید")
            return
        op_id   = self._ops_data[row]["id"]
        op_name = self._ops_data[row]["op_name"]

        dlg = ConfirmDialog(
            parent=self,
            title="تأیید حذف",
            message=f"عملیات «{op_name}» از Routing حذف شود؟",
            confirm_text="بله، حذف کن",
            cancel_text="انصراف",
            dangerous=True,
        )
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            with get_session() as session:
                svc = RoutingService(session)
                svc.delete_operation(op_id)
            self._load_routing_ops(self._current_header_id)
            Toast.success(self, "عملیات حذف شد")
        except ValueError as e:
            Toast.warning(self, str(e))
        except Exception as e:
            Toast.error(self, f"خطا: {e}")

    def _on_toggle_status(self):
        if not self._current_header_id:
            return
        try:
            with get_session() as session:
                svc    = RoutingService(session)
                header = svc.get_header_by_id(self._current_header_id)
            if not header:
                return

            cycle = {
                RoutingStatus.DRAFT.value:    RoutingStatus.APPROVED.value,
                RoutingStatus.APPROVED.value: RoutingStatus.OBSOLETE.value,
                RoutingStatus.OBSOLETE.value: RoutingStatus.DRAFT.value,
            }
            new_st = cycle.get(header.status, RoutingStatus.DRAFT.value)

            with get_session() as session:
                svc = RoutingService(session)
                svc.change_header_status(self._current_header_id, new_st)

            Toast.info(
                self,
                f"وضعیت Routing به «{RoutingStatus(new_st).label}» تغییر کرد"
            )
            self._load_routing_ops(self._current_header_id)
            if self._current_template_id:
                cur_id = self._current_header_id
                self._load_routing_list(self._current_template_id)
                for i in range(self._routing_combo.count()):
                    if self._routing_combo.itemData(i) == cur_id:
                        self._routing_combo.blockSignals(True)
                        self._routing_combo.setCurrentIndex(i)
                        self._routing_combo.blockSignals(False)
                        break

        except Exception as e:
            Toast.error(self, f"خطا: {e}")

    def _on_delete_routing(self):
        if not self._current_header_id:
            Toast.warning(self, "ابتدا یک Routing انتخاب کنید")
            return
        dlg = ConfirmDialog(
            parent=self,
            title="تأیید حذف Routing",
            message="این Routing و همه عملیات آن حذف شود؟",
            confirm_text="بله، حذف کن",
            cancel_text="انصراف",
            dangerous=True,
        )
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            with get_session() as session:
                svc = RoutingService(session)
                svc.delete_header(self._current_header_id)
            Toast.success(self, "Routing حذف شد")
            tid = self._current_template_id
            self._clear_display()
            if tid:
                self._load_routing_list(tid)
        except ValueError as e:
            Toast.warning(self, str(e))
        except Exception as e:
            Toast.error(self, f"خطا: {e}")

    def refresh(self):
        cur_template = self._current_template_id
        cur_header   = self._current_header_id
        self._load_templates()
        if cur_template:
            idx = self._template_combo.findData(cur_template)
            if idx >= 0:
                self._template_combo.setCurrentIndex(idx)
                if cur_header:
                    idx2 = self._routing_combo.findData(cur_header)
                    if idx2 >= 0:
                        self._routing_combo.setCurrentIndex(idx2)