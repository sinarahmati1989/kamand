"""
Kamand - BOM Page
صفحه BOM Editor — قلب مهندسی
"""
import logging
from decimal import Decimal

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
from app.services.bom_service import BOMService
from app.services.device_template_service import DeviceTemplateService
from app.services.lookup_service import LookupService
from app.enums.engineering_enums import BOMStatus
from app.enums.lookup_categories import LookupCategory
from app.database.session import get_session

logger = logging.getLogger(__name__)

ENGINEERING_STEPS = [
    ("device_templates", "تعریف دستگاه"),
    ("items",            "اقلام"),
    ("bom",              "BOM"),
    ("routing",          "مسیر ساخت"),
]

LINE_COLUMNS = [
    {"key": "sort_order",  "label": "ردیف",         "width": 60},
    {"key": "item_code",   "label": "کد قلم",        "width": 110},
    {"key": "item_name",   "label": "نام قلم",       "width": 220},
    {"key": "item_type",   "label": "نوع",           "width": 110},
    {"key": "quantity",    "label": "مقدار",         "width": 90},
    {"key": "uom",         "label": "واحد",          "width": 75},
    {"key": "scrap_pct",   "label": "ضایعات %",      "width": 90},
    {"key": "is_optional", "label": "اختیاری",       "width": 80},
    {"key": "line_cost",   "label": "هزینه تخمینی",  "width": 140},
    {"key": "notes",       "label": "یادداشت",       "width": 160},
]


class BOMPage(QWidget):
    """صفحه BOM Editor"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._current_template_id: int | None = None
        self._current_header_id: int | None = None
        self._lines_data: list[dict] = []
        self._setup_ui()
        self._load_templates()

    # ── Setup ──────────────────────────────────────────────────────

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        # WorkflowBar
        wf = WorkflowBar(ENGINEERING_STEPS)
        wf.set_active("bom")
        wf.step_clicked.connect(self._on_workflow_step)
        layout.addWidget(wf)

        # عنوان
        title = QLabel("ویرایشگر BOM — ساختار قطعات")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # ردیف انتخاب
        layout.addLayout(self._build_selector_row())

        # نوار اطلاعات
        layout.addWidget(self._build_header_info())

        # ── بخش خطوط BOM (بدون GroupBox) ─────────────────────────
        # عنوان بخش
        section_title = QLabel("خطوط BOM")
        section_title.setStyleSheet("""
            font-size: 14px;
            font-weight: 700;
            color: #374151;
            padding: 4px 0;
            border-bottom: 2px solid rgba(99, 102, 241, 0.2);
        """)
        layout.addWidget(section_title)

        # دکمه‌های عملیات — بالای جدول
        layout.addLayout(self._build_line_actions())

        # جدول
        layout.addWidget(self._build_table(), stretch=1)

        # پایین
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
        self._template_combo.currentIndexChanged.connect(
            self._on_template_changed
        )

        lbl2 = QLabel("BOM:")
        lbl2.setFixedWidth(45)
        lbl2.setStyleSheet("font-weight: 700; color: #374151; font-size: 13px;")

        self._bom_combo = QComboBox()
        self._bom_combo.setFixedHeight(40)
        self._bom_combo.setMinimumWidth(220)
        self._bom_combo.currentIndexChanged.connect(self._on_bom_changed)

        # دکمه تاریخچه
        history_btn = QPushButton("📋 تاریخچه")
        history_btn.setObjectName("secondaryButton")
        history_btn.setFixedHeight(40)
        history_btn.setMinimumWidth(110)
        history_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        history_btn.clicked.connect(self._on_show_history)

        # دکمه BOM جدید
        new_bom_btn = QPushButton("+ BOM جدید")
        new_bom_btn.setObjectName("primaryButton")
        new_bom_btn.setFixedHeight(40)
        new_bom_btn.setMinimumWidth(130)
        new_bom_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_bom_btn.clicked.connect(self._on_new_bom)

        row.addWidget(lbl1)
        row.addWidget(self._template_combo)
        row.addSpacing(16)
        row.addWidget(lbl2)
        row.addWidget(self._bom_combo)
        row.addWidget(history_btn)
        row.addWidget(new_bom_btn)
        row.addStretch()
        return row

    def _build_header_info(self) -> QFrame:
        self._header_frame = QFrame()
        self._header_frame.setObjectName("bomInfoFrame")
        self._header_frame.setFixedHeight(56)
        self._header_frame.setStyleSheet("""
            QFrame#bomInfoFrame {
                background: rgba(99, 102, 241, 0.06);
                border: 1px solid rgba(99, 102, 241, 0.18);
                border-radius: 10px;
            }
            QLabel { background: transparent; }
        """)

        row = QHBoxLayout(self._header_frame)
        row.setContentsMargins(18, 8, 18, 8)
        row.setSpacing(24)

        self._lbl_code = QLabel("هیچ BOM انتخاب نشده")
        self._lbl_code.setStyleSheet(
            "font-weight: 700; color: #1E293B; font-size: 13px;"
        )

        self._lbl_status = QLabel("")
        self._lbl_status.setStyleSheet("font-size: 13px;")

        self._lbl_count = QLabel("")
        self._lbl_count.setStyleSheet(
            "color: #64748B; font-size: 13px; font-weight: 600;"
        )

        self._lbl_cost = QLabel("")
        self._lbl_cost.setStyleSheet(
            "font-weight: 700; color: #6366F1; font-size: 13px;"
        )

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
        row.addWidget(self._lbl_cost)
        row.addWidget(self._status_btn)
        return self._header_frame

    def _build_line_actions(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)

        self._add_line_btn = QPushButton("+ افزودن قلم")
        self._add_line_btn.setObjectName("primaryButton")
        self._add_line_btn.setFixedHeight(38)
        self._add_line_btn.setFixedWidth(140)
        self._add_line_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._add_line_btn.clicked.connect(self._on_add_line)

        self._edit_line_btn = QPushButton("ویرایش خط")
        self._edit_line_btn.setObjectName("secondaryButton")
        self._edit_line_btn.setFixedHeight(38)
        self._edit_line_btn.setFixedWidth(120)
        self._edit_line_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._edit_line_btn.clicked.connect(self._on_edit_line)

        self._del_line_btn = QPushButton("حذف خط")
        self._del_line_btn.setObjectName("warningButton")
        self._del_line_btn.setFixedHeight(38)
        self._del_line_btn.setFixedWidth(110)
        self._del_line_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._del_line_btn.clicked.connect(self._on_delete_line)

        row.addWidget(self._add_line_btn)
        row.addWidget(self._edit_line_btn)
        row.addWidget(self._del_line_btn)
        row.addStretch()
        return row

    def _build_table(self) -> QTableWidget:
        self._table = QTableWidget()
        self._table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._table.setColumnCount(len(LINE_COLUMNS))
        self._table.setHorizontalHeaderLabels(
            [c["label"] for c in LINE_COLUMNS]
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
        self._table.setMinimumHeight(320)
        self._table.doubleClicked.connect(self._on_edit_line)

        # تنظیم عرض ستون‌ها
        hdr = self._table.horizontalHeader()
        hdr.setStretchLastSection(True)

        for i, col in enumerate(LINE_COLUMNS):
            if "width" in col:
                self._table.setColumnWidth(i, col["width"])

        # ارتفاع ردیف‌ها
        self._table.verticalHeader().setDefaultSectionSize(38)

        self._table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 1px solid rgba(99, 102, 241, 0.15);
                border-radius: 10px;
                gridline-color: rgba(99, 102, 241, 0.08);
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px 10px;
            }
            QTableWidget::item:selected {
                background: rgba(99, 102, 241, 0.15);
                color: #1E293B;
            }
            QHeaderView::section {
                background: rgba(99, 102, 241, 0.09);
                color: #374151;
                font-weight: 700;
                padding: 10px 8px;
                border: none;
                border-bottom: 1px solid rgba(99, 102, 241, 0.2);
            }
            QTableWidget::item:alternate {
                background: rgba(248, 250, 252, 0.9);
            }
        """)

        return self._table

    def _build_bottom_row(self) -> QHBoxLayout:
        row = QHBoxLayout()

        self._del_bom_btn = QPushButton("حذف کل BOM")
        self._del_bom_btn.setObjectName("dangerButton")
        self._del_bom_btn.setFixedHeight(38)
        self._del_bom_btn.setFixedWidth(140)
        self._del_bom_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._del_bom_btn.clicked.connect(self._on_delete_bom)

        self._total_label = QLabel("")
        self._total_label.setStyleSheet("""
            font-size: 15px;
            font-weight: 700;
            color: #6366F1;
            padding: 8px 16px;
            background: rgba(99, 102, 241, 0.08);
            border-radius: 8px;
        """)

        row.addWidget(self._del_bom_btn)
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
            self._template_combo.addItem(
                "— دستگاه را انتخاب کنید —", None
            )
            for t in templates:
                self._template_combo.addItem(
                    f"{t.code}  —  {t.name}", t.id
                )
            self._template_combo.blockSignals(False)

        except Exception as e:
            logger.error(f"خطا در بارگذاری دستگاه‌ها: {e}")
            Toast.error(self, f"خطا: {e}")

    def _load_bom_list(self, template_id: int):
        try:
            with get_session() as session:
                svc = BOMService(session)
                headers = svc.get_headers_by_template(template_id)

            self._bom_combo.blockSignals(True)
            self._bom_combo.clear()
            self._bom_combo.addItem("— BOM انتخاب کنید —", None)
            for h in headers:
                lbl = BOMStatus(h.status).label if h.status else ""
                self._bom_combo.addItem(
                    f"Rev.{h.revision_no:02d}  —  {lbl}", h.id
                )
            self._bom_combo.blockSignals(False)

            if len(headers) == 1:
                self._bom_combo.setCurrentIndex(1)

        except Exception as e:
            logger.error(f"خطا در بارگذاری BOM: {e}")

    def _load_bom_lines(self, header_id: int):
        try:
            with get_session() as session:
                svc = BOMService(session)
                bom = svc.get_with_lines(header_id)
                lookup_svc = LookupService(session)
                type_map = lookup_svc.get_code_to_label_map(
                    LookupCategory.ITEM_TYPE.value
                )
                uom_map = lookup_svc.get_code_to_label_map(
                    LookupCategory.UOM.value
                )
                total_cost = svc.calculate_bom_cost(header_id)

            if not bom:
                return

            self._lbl_code.setText(bom.bom_code)
            st = BOMStatus(bom.status) if bom.status else None
            if st:
                self._lbl_status.setText(f"وضعیت: {st.label}")
                self._lbl_status.setStyleSheet(
                    f"font-size:13px; font-weight:700; color:{st.color};"
                )
            self._lbl_count.setText(f"تعداد خطوط: {len(bom.bom_lines)}")
            cost_str = f"{total_cost:,.0f}" if total_cost else "—"
            self._lbl_cost.setText(f"هزینه تخمینی: {cost_str} ریال")
            self._status_btn.setVisible(True)
            self._total_label.setText(f"جمع کل: {cost_str} ریال")

            self._lines_data = []
            self._table.setRowCount(0)

            for line in bom.bom_lines:
                item = line.item
                if not item:
                    continue

                line_cost = Decimal("0")
                if item.standard_cost and line.quantity:
                    qty = Decimal(str(line.quantity))
                    cost = Decimal(str(item.standard_cost))
                    scrap = Decimal(str(line.scrap_percent or 0)) / 100
                    line_cost = qty * cost * (1 + scrap)

                row_data = {
                    "id":          line.id,
                    "sort_order":  str(line.sort_order),
                    "item_code":   item.code,
                    "item_name":   item.name,
                    "item_type":   type_map.get(
                        item.item_type, item.item_type or "—"
                    ),
                    "quantity":    f"{float(line.quantity):g}",
                    "uom":         uom_map.get(line.uom, line.uom or "—"),
                    "scrap_pct":   f"{line.scrap_percent or 0}%",
                    "is_optional": "بله" if line.is_optional else "خیر",
                    "line_cost":   f"{line_cost:,.0f}" if line_cost else "—",
                    "notes":       line.notes or "—",
                }
                self._lines_data.append(row_data)

                r = self._table.rowCount()
                self._table.insertRow(r)

                for ci, col in enumerate(LINE_COLUMNS):
                    val = row_data.get(col["key"], "")
                    cell = QTableWidgetItem(str(val))
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                    if col["key"] == "line_cost" and line_cost > 0:
                        cell.setForeground(QColor("#6366F1"))
                    if col["key"] == "is_optional" and line.is_optional:
                        cell.setForeground(QColor("#F59E0B"))

                    self._table.setItem(r, ci, cell)

        except Exception as e:
            logger.error(f"خطا در بارگذاری خطوط BOM: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _clear_display(self):
        self._lines_data = []
        self._table.setRowCount(0)
        self._current_header_id = None
        self._lbl_code.setText("هیچ BOM انتخاب نشده")
        self._lbl_status.setText("")
        self._lbl_count.setText("")
        self._lbl_cost.setText("")
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
        self._bom_combo.blockSignals(True)
        self._bom_combo.clear()
        self._bom_combo.addItem("— BOM انتخاب کنید —", None)
        self._bom_combo.blockSignals(False)
        self._clear_display()
        if tid:
            self._load_bom_list(tid)

    def _on_bom_changed(self, _idx: int):
        hid = self._bom_combo.currentData()
        self._current_header_id = hid
        self._table.setRowCount(0)
        self._lines_data = []
        if hid:
            self._load_bom_lines(hid)
        else:
            self._clear_display()

    def _on_new_bom(self):
        if not self._current_template_id:
            Toast.warning(self, "ابتدا یک دستگاه انتخاب کنید")
            return
        try:
            with get_session() as session:
                svc = BOMService(session)
                header = svc.create_header(self._current_template_id)
                new_id = header.id
                rev = header.revision_no

            Toast.success(self, f"BOM Rev.{rev:02d} ساخته شد")
            self._load_bom_list(self._current_template_id)

            for i in range(self._bom_combo.count()):
                if self._bom_combo.itemData(i) == new_id:
                    self._bom_combo.setCurrentIndex(i)
                    break

        except ValueError as e:
            Toast.warning(self, str(e))
        except Exception as e:
            logger.error(f"خطا در ساخت BOM: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _on_show_history(self):
        """نمایش تاریخچه تمام BOM های یک دستگاه"""
        if not self._current_template_id:
            Toast.warning(self, "ابتدا یک دستگاه انتخاب کنید")
            return

        from app.ui.bom.bom_history_dialog import BOMHistoryDialog
        dlg = BOMHistoryDialog(
            device_template_id=self._current_template_id,
            parent=self,
        )
        if dlg.exec():
            selected = dlg.get_selected_id()
            if selected:
                # بارگذاری BOM انتخابی
                for i in range(self._bom_combo.count()):
                    if self._bom_combo.itemData(i) == selected:
                        self._bom_combo.setCurrentIndex(i)
                        return
                # اگر در combo نبود، لیست را refresh کن
                self._load_bom_list(self._current_template_id)
                for i in range(self._bom_combo.count()):
                    if self._bom_combo.itemData(i) == selected:
                        self._bom_combo.setCurrentIndex(i)
                        break

    def _on_add_line(self):
        if not self._current_header_id:
            Toast.warning(self, "ابتدا یک BOM انتخاب کنید")
            return
        from app.ui.bom.bom_line_dialog import BOMLineDialog
        dlg = BOMLineDialog(
            bom_header_id=self._current_header_id,
            parent=self,
        )
        if dlg.exec():
            self._load_bom_lines(self._current_header_id)
            Toast.success(self, "قلم با موفقیت اضافه شد")

    def _on_edit_line(self):
        row = self._table.currentRow()
        if row < 0 or row >= len(self._lines_data):
            Toast.warning(self, "یک خط را انتخاب کنید")
            return
        line_id = self._lines_data[row]["id"]
        from app.ui.bom.bom_line_dialog import BOMLineDialog
        dlg = BOMLineDialog(
            bom_header_id=self._current_header_id,
            line_id=line_id,
            parent=self,
        )
        if dlg.exec():
            self._load_bom_lines(self._current_header_id)
            Toast.success(self, "خط BOM ویرایش شد")

    def _on_delete_line(self):
        row = self._table.currentRow()
        if row < 0 or row >= len(self._lines_data):
            Toast.warning(self, "یک خط را انتخاب کنید")
            return
        line_id = self._lines_data[row]["id"]
        item_name = self._lines_data[row]["item_name"]

        dlg = ConfirmDialog(
            parent=self,
            title="تأیید حذف",
            message=f"قلم «{item_name}» از BOM حذف شود؟",
            confirm_text="بله، حذف کن",
            cancel_text="انصراف",
            dangerous=True,
        )
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            with get_session() as session:
                svc = BOMService(session)
                svc.delete_line(line_id)
            self._load_bom_lines(self._current_header_id)
            Toast.success(self, "خط BOM حذف شد")
        except ValueError as e:
            Toast.warning(self, str(e))
        except Exception as e:
            Toast.error(self, f"خطا: {e}")

    def _on_toggle_status(self):
        if not self._current_header_id:
            return
        try:
            with get_session() as session:
                svc = BOMService(session)
                header = svc.get_header_by_id(self._current_header_id)
            if not header:
                return

            cycle = {
                BOMStatus.DRAFT.value:    BOMStatus.APPROVED.value,
                BOMStatus.APPROVED.value: BOMStatus.OBSOLETE.value,
                BOMStatus.OBSOLETE.value: BOMStatus.DRAFT.value,
            }
            new_st = cycle.get(header.status, BOMStatus.DRAFT.value)

            with get_session() as session:
                svc = BOMService(session)
                svc.change_header_status(self._current_header_id, new_st)

            Toast.info(
                self,
                f"وضعیت BOM به «{BOMStatus(new_st).label}» تغییر کرد"
            )
            self._load_bom_lines(self._current_header_id)
            if self._current_template_id:
                cur_id = self._current_header_id
                self._load_bom_list(self._current_template_id)
                for i in range(self._bom_combo.count()):
                    if self._bom_combo.itemData(i) == cur_id:
                        self._bom_combo.blockSignals(True)
                        self._bom_combo.setCurrentIndex(i)
                        self._bom_combo.blockSignals(False)
                        break

        except Exception as e:
            Toast.error(self, f"خطا: {e}")

    def _on_delete_bom(self):
        if not self._current_header_id:
            Toast.warning(self, "ابتدا یک BOM انتخاب کنید")
            return
        dlg = ConfirmDialog(
            parent=self,
            title="تأیید حذف BOM",
            message="این BOM و همه خطوط آن حذف شود؟",
            confirm_text="بله، حذف کن",
            cancel_text="انصراف",
            dangerous=True,
        )
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            with get_session() as session:
                svc = BOMService(session)
                svc.delete_header(self._current_header_id)
            Toast.success(self, "BOM حذف شد")
            tid = self._current_template_id
            self._clear_display()
            if tid:
                self._load_bom_list(tid)
        except ValueError as e:
            Toast.warning(self, str(e))
        except Exception as e:
            Toast.error(self, f"خطا: {e}")

    def refresh(self):
        current_template_id = self._current_template_id
        current_header_id = self._current_header_id

        self._load_templates()

        if current_template_id:
            idx = self._template_combo.findData(current_template_id)
            if idx >= 0:
                self._template_combo.setCurrentIndex(idx)
                if current_header_id:
                    idx2 = self._bom_combo.findData(current_header_id)
                    if idx2 >= 0:
                        self._bom_combo.setCurrentIndex(idx2)