"""
Kamand - Project Detail Dialog
جزئیات پروژه با 2 Tab مدرن + مدیریت وضعیت + دستگاه‌ها
"""
import logging
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QWidget,
    QGroupBox, QScrollArea, QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from app.services.project_service import ProjectService
from app.database.session import get_session
from app.ui.base.base_table import AuroraTable
from app.ui.base.confirm_dialog import ConfirmDialog
from app.ui.widgets.toast import Toast
from app.ui.projects.project_device_dialog import ProjectDeviceDialog

logger = logging.getLogger(__name__)


STATUS_TRANSITIONS = {
    "draft":         [("✔️  تأیید پروژه",    "confirm",          "neonButton")],
    "confirmed":     [("🏭  شروع تولید",     "start_production", "neonButton")],
    "in_production": [("📦  تحویل پروژه",    "deliver",          "neonButton")],
    "delivered":     [],
    "cancelled":     [],
}

STATUS_LABELS = {
    "draft":         "پیش‌نویس",
    "confirmed":     "تأیید شده",
    "in_production": "در تولید",
    "delivered":     "تحویل داده شده",
    "cancelled":     "لغو شده",
}

PRIORITY_LABELS = {
    "low":    "پایین",
    "normal": "عادی",
    "high":   "بالا",
    "urgent": "فوری",
}

STATUS_COLORS = {
    "draft":         "#64748B",
    "confirmed":     "#3B82F6",
    "in_production": "#F59E0B",
    "delivered":     "#10B981",
    "cancelled":     "#EF4444",
}

DEVICE_COLUMNS = [
    {"key": "id",            "label": "شناسه",          "width": 60},
    {"key": "device_code",   "label": "کد دستگاه",      "width": 120},
    {"key": "device_name",   "label": "نام دستگاه",     "width": 200},
    {"key": "quantity",      "label": "تعداد",           "width": 70},
    {"key": "estimated",     "label": "هزینه تمام‌شده", "width": 150},
    {"key": "unit_price",    "label": "قیمت فروش",      "width": 150},
    {"key": "total_sale",    "label": "جمع فروش",        "width": 150},
    {"key": "costed",        "label": "هزینه‌یابی",     "width": 90},
    {"key": "prod_status",   "label": "وضعیت تولید"},
]


class ProjectDetailDialog(QDialog):
    """جزئیات پروژه"""

    def __init__(self, project_id: int, parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self._project = None
        self._customer_name = ""
        self._devices_snapshot: list[dict] = []

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowTitle("جزئیات پروژه")
        self.setMinimumSize(980, 700)
        self.resize(1040, 740)

        self._setup_ui()
        self._load_project()

    # ─────────────────── Setup ───────────────────

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # هدر + وضعیت
        header_row = QHBoxLayout()
        header_row.setSpacing(10)

        self.title_label = QLabel("جزئیات پروژه")
        self.title_label.setObjectName("pageTitle")
        header_row.addWidget(self.title_label)
        header_row.addStretch()

        self.status_chip = QLabel("—")
        self.status_chip.setObjectName("statusChip")
        self.status_chip.setFixedHeight(30)
        self.status_chip.setMinimumWidth(120)
        self.status_chip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_row.addWidget(self.status_chip)

        layout.addLayout(header_row)

        # نوار workflow
        self.workflow_bar = QFrame()
        self.workflow_bar.setObjectName("workflowFrame")
        self.workflow_layout = QHBoxLayout(self.workflow_bar)
        self.workflow_layout.setContentsMargins(12, 8, 12, 8)
        self.workflow_layout.setSpacing(8)
        layout.addWidget(self.workflow_bar)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setObjectName("customerTabs")
        self.tabs.addTab(self._build_info_tab(),    "📋  اطلاعات پروژه")
        self.tabs.addTab(self._build_devices_tab(), "🖥️  دستگاه‌ها")
        self.tabs.addTab(self._build_cost_tab(),    "📊  خلاصه هزینه‌یابی")
        layout.addWidget(self.tabs, 1)

        # دکمه بستن
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        close_btn = QPushButton("بستن")
        close_btn.setObjectName("secondaryButton")
        close_btn.setFixedSize(110, 40)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    # ─────────────────── Tab 1: اطلاعات ───────────────────

    def _build_info_tab(self) -> QScrollArea:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        self.info_labels: dict[str, QLabel] = {}

        # شناسه پروژه
        grp1 = QGroupBox("🔖  شناسه پروژه")
        grp1.setObjectName("formGroup")
        v1 = QVBoxLayout(grp1)
        v1.setContentsMargins(14, 20, 14, 14)
        v1.setSpacing(8)
        for key, lbl in [
            ("project_no",  "شماره پروژه"),
            ("name",        "نام پروژه"),
            ("customer",    "مشتری"),
            ("contract_no", "شماره قرارداد"),
            ("priority",    "اولویت"),
        ]:
            v1.addLayout(self._make_info_row(key, lbl))
        layout.addWidget(grp1)

        # تاریخ‌ها
        grp2 = QGroupBox("📅  تاریخ‌ها")
        grp2.setObjectName("formGroup")
        v2 = QVBoxLayout(grp2)
        v2.setContentsMargins(14, 20, 14, 14)
        v2.setSpacing(8)
        for key, lbl in [
            ("start_date",           "تاریخ شروع"),
            ("delivery_date",        "تاریخ تحویل برنامه‌ریزی‌شده"),
            ("actual_delivery_date", "تاریخ تحویل واقعی"),
        ]:
            v2.addLayout(self._make_info_row(key, lbl))
        layout.addWidget(grp2)

        # مالی
        grp3 = QGroupBox("💰  اطلاعات مالی")
        grp3.setObjectName("formGroup")
        v3 = QVBoxLayout(grp3)
        v3.setContentsMargins(14, 20, 14, 14)
        v3.setSpacing(8)
        v3.addLayout(self._make_info_row("contract_value",    "ارزش قرارداد"))
        v3.addLayout(self._make_info_row("estimated_total",   "جمع هزینه تمام‌شده"))
        v3.addLayout(self._make_info_row("sale_total",        "جمع قیمت فروش دستگاه‌ها"))
        v3.addLayout(self._make_info_row("expected_profit",   "سود مورد انتظار"))
        layout.addWidget(grp3)

        # توضیحات
        grp4 = QGroupBox("📝  توضیحات")
        grp4.setObjectName("formGroup")
        v4 = QVBoxLayout(grp4)
        v4.setContentsMargins(14, 20, 14, 14)
        v4.setSpacing(8)
        self.info_labels["description"] = QLabel("—")
        self.info_labels["description"].setWordWrap(True)
        self.info_labels["description"].setStyleSheet(
            "color: #1E293B; padding: 8px; background: #F8FAFC; "
            "border-radius: 6px; min-height: 40px;"
        )
        v4.addWidget(self.info_labels["description"])
        layout.addWidget(grp4)

        layout.addStretch(1)
        return self._wrap_scroll(content)

    def _make_info_row(self, key: str, label_text: str) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)

        lbl = QLabel(f"{label_text}:")
        lbl.setObjectName("fieldLabel")
        lbl.setFixedWidth(220)
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        f = QFont()
        f.setBold(True)
        lbl.setFont(f)

        val = QLabel("—")
        val.setObjectName("infoValue")
        val.setStyleSheet(
            "color: #1E293B; font-size: 13px; padding: 6px 10px; "
            "background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 6px;"
        )
        val.setWordWrap(True)
        self.info_labels[key] = val

        row.addWidget(lbl)
        row.addWidget(val, 1)
        return row

    # ─────────────────── Tab 2: دستگاه‌ها ───────────────────

    def _build_devices_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # هدر تب
        header = QHBoxLayout()
        title = QLabel("دستگاه‌های پروژه")
        title.setObjectName("pageTitle")
        f = QFont()
        f.setPointSize(14)
        f.setBold(True)
        title.setFont(f)
        header.addWidget(title)
        header.addStretch()

        self.btn_add_device = QPushButton("➕  افزودن دستگاه")
        self.btn_add_device.setObjectName("neonButton")
        self.btn_add_device.setFixedWidth(180)
        self.btn_add_device.setFixedHeight(38)
        self.btn_add_device.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_device.clicked.connect(self._on_add_device)
        header.addWidget(self.btn_add_device)
        layout.addLayout(header)

        # جدول
        self.devices_table = AuroraTable(DEVICE_COLUMNS, parent=self)
        self.devices_table.edit_requested.connect(self._on_edit_device)
        self.devices_table.delete_requested.connect(self._on_delete_device)
        layout.addWidget(self.devices_table, 1)

        # خلاصه پایین
        self.summary_frame = QFrame()
        self.summary_frame.setObjectName("summaryFrame")
        self.summary_frame.setStyleSheet("""
            QFrame#summaryFrame {
                background-color: #EEF2FF;
                border: 1px solid rgba(99, 102, 241, 0.3);
                border-radius: 8px;
            }
        """)
        sl = QHBoxLayout(self.summary_frame)
        sl.setContentsMargins(16, 12, 16, 12)
        sl.setSpacing(20)

        self.total_devices_label = QLabel("تعداد کل: 0")
        self.total_devices_label.setStyleSheet(
            "color: #6366F1; font-weight: bold; font-size: 13px;"
        )
        self.total_estimated_label = QLabel("هزینه تمام‌شده: —")
        self.total_estimated_label.setStyleSheet(
            "color: #3B82F6; font-weight: bold; font-size: 13px;"
        )
        self.total_sale_label = QLabel("جمع فروش: —")
        self.total_sale_label.setStyleSheet(
            "color: #10B981; font-weight: bold; font-size: 13px;"
        )

        sl.addWidget(self.total_devices_label)
        sl.addStretch()
        sl.addWidget(self.total_estimated_label)
        sl.addWidget(self.total_sale_label)
        layout.addWidget(self.summary_frame)

        # دکمه‌های عملیات
        actions = QHBoxLayout()
        edit_dev_btn = QPushButton("✏️  ویرایش دستگاه")
        edit_dev_btn.setObjectName("secondaryButton")
        edit_dev_btn.setFixedWidth(160)
        edit_dev_btn.clicked.connect(self._on_edit_device_selected)

        del_dev_btn = QPushButton("🗑️  حذف دستگاه")
        del_dev_btn.setObjectName("warningButton")
        del_dev_btn.setFixedWidth(140)
        del_dev_btn.clicked.connect(self._on_delete_device_selected)

        actions.addStretch()
        actions.addWidget(edit_dev_btn)
        actions.addWidget(del_dev_btn)
        layout.addLayout(actions)

        return widget

    # ─────────────────── Tab 3: خلاصه هزینه‌یابی ───────────────────

    def _build_cost_tab(self) -> QScrollArea:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        self._cost_summary_labels: dict[str, QLabel] = {}

        # ─── هزینه‌های مستقیم ───
        grp1 = QGroupBox("🔩  هزینه‌های مستقیم")
        grp1.setObjectName("formGroup")
        v1 = QVBoxLayout(grp1)
        v1.setContentsMargins(14, 20, 14, 14)
        v1.setSpacing(8)
        for key, lbl in [
            ("total_material", "جمع هزینه مواد (BOM)"),
            ("total_labor",    "جمع هزینه کار (Routing)"),
            ("total_direct",   "جمع هزینه مستقیم"),
        ]:
            v1.addLayout(self._make_cost_row(key, lbl))
        layout.addWidget(grp1)

        # ─── سربار ───
        grp2 = QGroupBox("🏭  سربار و هزینه تمام‌شده")
        grp2.setObjectName("formGroup")
        v2 = QVBoxLayout(grp2)
        v2.setContentsMargins(14, 20, 14, 14)
        v2.setSpacing(8)
        for key, lbl in [
            ("total_overhead",   "جمع سربار عمومی"),
            ("total_estimated",  "جمع هزینه تمام‌شده"),
        ]:
            v2.addLayout(self._make_cost_row(key, lbl))
        layout.addWidget(grp2)

        # ─── فروش و سود ───
        grp3 = QGroupBox("💰  فروش و سود")
        grp3.setObjectName("formGroup")
        v3 = QVBoxLayout(grp3)
        v3.setContentsMargins(14, 20, 14, 14)
        v3.setSpacing(8)
        for key, lbl in [
            ("total_suggested",  "جمع قیمت پیشنهادی سیستم"),
            ("total_sale",       "جمع قیمت فروش نهایی"),
            ("total_profit",     "سود مورد انتظار"),
            ("profit_margin",    "حاشیه سود (٪)"),
        ]:
            v3.addLayout(self._make_cost_row(key, lbl))
        layout.addWidget(grp3)

        # ─── وضعیت هزینه‌یابی ───
        grp4 = QGroupBox("📋  وضعیت هزینه‌یابی")
        grp4.setObjectName("formGroup")
        v4 = QVBoxLayout(grp4)
        v4.setContentsMargins(14, 20, 14, 14)
        v4.setSpacing(8)

        self.cost_status_label = QLabel("—")
        self.cost_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cost_status_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; padding: 12px; "
            "border-radius: 8px; background: #F8FAFC;"
        )
        v4.addWidget(self.cost_status_label)
        layout.addWidget(grp4)

        layout.addStretch(1)
        return self._wrap_scroll(content)

    def _make_cost_row(self, key: str, label_text: str) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)

        lbl = QLabel(f"{label_text}:")
        lbl.setObjectName("fieldLabel")
        lbl.setFixedWidth(260)
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        f = QFont()
        f.setBold(True)
        lbl.setFont(f)

        val = QLabel("—")
        val.setObjectName("infoValue")
        val.setStyleSheet(
            "color: #1E293B; font-size: 13px; padding: 6px 10px; "
            "background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 6px;"
        )
        self._cost_summary_labels[key] = val

        row.addWidget(lbl)
        row.addWidget(val, 1)
        return row

    # ─────────────────── Helpers ───────────────────

    def _wrap_scroll(self, content: QWidget) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(content)
        return scroll

    def _format_money(self, value, currency: str = "irr") -> str:
        if not value:
            return "—"
        v = float(value)
        if currency == "usd":
            return f"{v:,.2f} دلار"
        if currency == "eur":
            return f"{v:,.2f} یورو"
        if v >= 1_000_000_000:
            return f"{v / 1_000_000_000:,.2f} میلیارد ریال"
        if v >= 1_000_000:
            return f"{v / 1_000_000:,.2f} میلیون ریال"
        if v >= 1_000:
            return f"{v / 1_000:,.0f} هزار ریال"
        return f"{v:,.0f} ریال"

    def _format_date(self, d) -> str:
        if not d:
            return "—"
        try:
            import jdatetime
            jd = jdatetime.date.fromgregorian(date=d)
            return jd.strftime("%Y/%m/%d")
        except Exception:
            return str(d)

    # ─────────────────── Load ───────────────────

    def _load_project(self):
        try:
            with get_session() as session:
                svc = ProjectService(session)
                self._project = svc.get_by_id(self.project_id)

                if not self._project:
                    Toast.error(self, "پروژه یافت نشد")
                    self.reject()
                    return

                p = self._project

                # ✅ کپی همه داده‌ها قبل از بستن session
                self._customer_name = p.customer.name if p.customer else "—"

                self._devices_snapshot = []
                for d in (p.project_devices or []):
                    self._devices_snapshot.append({
                        "id":                    d.id,
                        "device_template_id":    d.device_template_id,
                        "device_code":           d.device_template.code if d.device_template else "—",
                        "device_name":           d.device_template.name if d.device_template else "—",
                        "quantity":              d.quantity,
                        "unit_price":            float(d.unit_price)            if d.unit_price            else 0.0,
                        "bom_header_id":         d.bom_header_id,
                        "routing_header_id":     d.routing_header_id,
                        "production_status":     d.production_status or "pending",
                        "notes":                 d.notes,
                        # ─── فیلدهای هزینه‌یابی ───
                        "material_unit_cost":        float(d.material_unit_cost)        if d.material_unit_cost        else None,
                        "labor_unit_cost":           float(d.labor_unit_cost)           if d.labor_unit_cost           else None,
                        "direct_unit_cost":          float(d.direct_unit_cost)          if d.direct_unit_cost          else None,
                        "overhead_percent":          float(d.overhead_percent)          if d.overhead_percent          else None,
                        "overhead_unit_cost":        float(d.overhead_unit_cost)        if d.overhead_unit_cost        else None,
                        "estimated_unit_cost":       float(d.estimated_unit_cost)       if d.estimated_unit_cost       else None,
                        "markup_percent":            float(d.markup_percent)            if d.markup_percent            else None,
                        "suggested_sale_unit_price": float(d.suggested_sale_unit_price) if d.suggested_sale_unit_price else None,
                        "bom_revision_no":           d.bom_revision_no,
                        "routing_revision_no":       d.routing_revision_no,
                        "cost_version":              d.cost_version or 0,
                        "cost_calculated_at":        str(d.cost_calculated_at) if d.cost_calculated_at else None,
                        "cost_is_locked":            d.cost_is_locked or False,
                    })

            self._update_header()
            self._update_workflow()
            self._update_info()
            self._update_devices()
            self._update_cost_tab()

        except Exception as e:
            logger.error(f"خطا در بارگذاری پروژه: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _update_header(self):
        p = self._project
        self.title_label.setText(f"{p.project_no} — {p.name}")

        color = STATUS_COLORS.get(p.status, "#64748B")
        label = STATUS_LABELS.get(p.status, p.status)
        self.status_chip.setText(label)
        self.status_chip.setStyleSheet(f"""
            QLabel#statusChip {{
                background-color: {color};
                color: white;
                border-radius: 15px;
                padding: 4px 16px;
                font-weight: bold;
                font-size: 12px;
            }}
        """)

    def _update_workflow(self):
        while self.workflow_layout.count():
            item = self.workflow_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        p = self._project

        info = QLabel(
            f"مدیریت وضعیت — وضعیت فعلی: {STATUS_LABELS.get(p.status, p.status)}"
        )
        info.setStyleSheet("color: #64748B; font-size: 12px;")
        self.workflow_layout.addWidget(info)
        self.workflow_layout.addStretch()

        for label, action, obj_name in STATUS_TRANSITIONS.get(p.status, []):
            btn = QPushButton(label)
            btn.setObjectName(obj_name)
            btn.setFixedWidth(160)
            btn.setFixedHeight(36)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, a=action: self._on_workflow_action(a))
            self.workflow_layout.addWidget(btn)

        if p.status not in ("delivered", "cancelled"):
            cancel_btn = QPushButton("🚫  لغو پروژه")
            cancel_btn.setObjectName("warningButton")
            cancel_btn.setFixedWidth(140)
            cancel_btn.setFixedHeight(36)
            cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            cancel_btn.clicked.connect(lambda: self._on_workflow_action("cancel"))
            self.workflow_layout.addWidget(cancel_btn)

    def _update_info(self):
        p = self._project

        # محاسبه اعداد مالی از snapshot
        estimated_total = sum(
            (d.get("estimated_unit_cost") or 0) * d["quantity"]
            for d in self._devices_snapshot
        )
        sale_total = sum(
            d["unit_price"] * d["quantity"]
            for d in self._devices_snapshot
        )
        expected_profit = sale_total - estimated_total

        self.info_labels["project_no"].setText(p.project_no or "—")
        self.info_labels["name"].setText(p.name or "—")
        self.info_labels["customer"].setText(self._customer_name)
        self.info_labels["contract_no"].setText(p.contract_no or "—")
        self.info_labels["priority"].setText(
            PRIORITY_LABELS.get(p.priority, p.priority or "—")
        )
        self.info_labels["start_date"].setText(self._format_date(p.start_date))
        self.info_labels["delivery_date"].setText(self._format_date(p.delivery_date))
        self.info_labels["actual_delivery_date"].setText(
            self._format_date(p.actual_delivery_date)
        )
        self.info_labels["contract_value"].setText(
            self._format_money(p.contract_value, p.currency or "irr")
        )
        self.info_labels["estimated_total"].setText(
            self._format_money(estimated_total)
        )
        self.info_labels["sale_total"].setText(
            self._format_money(sale_total)
        )
        self.info_labels["expected_profit"].setText(
            self._format_money(expected_profit)
        )
        self.info_labels["description"].setText(p.description or "—")

    def _update_devices(self):
        prod_status_labels = {
            "pending":     "⏳ در انتظار",
            "in_progress": "🔧 در حال تولید",
            "completed":   "✅ تکمیل شده",
            "on_hold":     "⏸ معلق",
        }

        rows = []
        total_qty       = 0
        total_estimated = 0.0
        total_sale      = 0.0

        for d in self._devices_snapshot:
            qty          = d["quantity"]
            est_unit     = d.get("estimated_unit_cost") or 0
            sale_unit    = d["unit_price"]
            est_total    = est_unit * qty
            sale_total_v = sale_unit * qty

            total_qty       += qty
            total_estimated += est_total
            total_sale      += sale_total_v

            # آیکون هزینه‌یابی
            if d.get("estimated_unit_cost"):
                costed = f"✅ v{d.get('cost_version', 1)}"
            else:
                costed = "⚠️ ناقص"

            rows.append({
                "id":          d["id"],
                "device_code": d["device_code"],
                "device_name": d["device_name"],
                "quantity":    qty,
                "estimated":   self._format_money(est_unit) if est_unit else "⚠️ —",
                "unit_price":  self._format_money(sale_unit),
                "total_sale":  self._format_money(sale_total_v),
                "costed":      costed,
                "prod_status": prod_status_labels.get(
                    d["production_status"], d["production_status"]
                ),
            })

        self.devices_table.load_data(rows)

        self.total_devices_label.setText(
            f"📦 {total_qty} دستگاه ({len(self._devices_snapshot)} نوع)"
        )
        self.total_estimated_label.setText(
            f"🔵 هزینه: {self._format_money(total_estimated)}"
        )
        self.total_sale_label.setText(
            f"🟢 فروش: {self._format_money(total_sale)}"
        )

        can_edit = self._project.status in ("draft", "confirmed")
        self.btn_add_device.setEnabled(can_edit)

    def _update_cost_tab(self):
        """آپدیت تب خلاصه هزینه‌یابی"""
        from app.services.cost_calculation_service import CostCalculationService

        # محاسبه از snapshot
        total_material  = 0.0
        total_labor     = 0.0
        total_direct    = 0.0
        total_overhead  = 0.0
        total_estimated = 0.0
        total_suggested = 0.0
        total_sale      = 0.0
        incomplete      = 0

        for d in self._devices_snapshot:
            qty = d["quantity"]
            if d.get("estimated_unit_cost"):
                total_material  += (d.get("material_unit_cost")        or 0) * qty
                total_labor     += (d.get("labor_unit_cost")           or 0) * qty
                total_direct    += (d.get("direct_unit_cost")          or 0) * qty
                total_overhead  += (d.get("overhead_unit_cost")        or 0) * qty
                total_estimated += (d.get("estimated_unit_cost")       or 0) * qty
                total_suggested += (d.get("suggested_sale_unit_price") or 0) * qty
            else:
                incomplete += 1
            total_sale += d["unit_price"] * qty

        total_profit   = total_sale - total_estimated
        profit_margin  = (
            (total_profit / total_sale * 100) if total_sale > 0 else 0
        )

        # آپدیت label‌ها
        self._cost_summary_labels["total_material"].setText(
            self._format_money(total_material)
        )
        self._cost_summary_labels["total_labor"].setText(
            self._format_money(total_labor)
        )
        self._cost_summary_labels["total_direct"].setText(
            self._format_money(total_direct)
        )
        self._cost_summary_labels["total_overhead"].setText(
            self._format_money(total_overhead)
        )
        self._cost_summary_labels["total_estimated"].setText(
            self._format_money(total_estimated)
        )
        self._cost_summary_labels["total_suggested"].setText(
            self._format_money(total_suggested)
        )
        self._cost_summary_labels["total_sale"].setText(
            self._format_money(total_sale)
        )
        self._cost_summary_labels["total_profit"].setText(
            self._format_money(total_profit)
        )
        self._cost_summary_labels["profit_margin"].setText(
            f"{profit_margin:.1f}٪"
        )

        # وضعیت
        total_devices = len(self._devices_snapshot)
        costed        = total_devices - incomplete

        if incomplete == 0 and total_devices > 0:
            self.cost_status_label.setText(
                f"✅ همه {total_devices} دستگاه هزینه‌یابی شده‌اند"
            )
            self.cost_status_label.setStyleSheet(
                "font-size: 14px; font-weight: bold; padding: 12px; "
                "border-radius: 8px; background: #D1FAE5; color: #065F46;"
            )
        elif total_devices == 0:
            self.cost_status_label.setText("⚠️ هیچ دستگاهی در پروژه نیست")
            self.cost_status_label.setStyleSheet(
                "font-size: 14px; font-weight: bold; padding: 12px; "
                "border-radius: 8px; background: #FEF3C7; color: #92400E;"
            )
        else:
            self.cost_status_label.setText(
                f"⚠️ {costed} از {total_devices} دستگاه هزینه‌یابی شده — "
                f"{incomplete} دستگاه ناقص"
            )
            self.cost_status_label.setStyleSheet(
                "font-size: 14px; font-weight: bold; padding: 12px; "
                "border-radius: 8px; background: #FEF3C7; color: #92400E;"
            )

    # ─────────────────── Actions ───────────────────

    def _on_workflow_action(self, action: str):
        action_labels = {
            "confirm":          "تأیید",
            "start_production": "شروع تولید",
            "deliver":          "تحویل",
            "cancel":           "لغو",
        }

        dlg = ConfirmDialog(
            parent=self,
            title="تأیید عملیات",
            message=f"آیا از «{action_labels.get(action, action)}» این پروژه اطمینان دارید؟",
            confirm_text="بله، انجام بده",
            cancel_text="انصراف",
            dangerous=(action == "cancel"),
        )
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            with get_session() as session:
                svc   = ProjectService(session)
                fresh = svc.get_by_id(self.project_id)

                if action == "confirm":
                    svc.confirm(fresh)
                elif action == "start_production":
                    # قفل هزینه‌یابی همه دستگاه‌ها
                    svc.start_production(fresh)
                    for device in fresh.project_devices:
                        device.cost_is_locked = True
                elif action == "deliver":
                    svc.deliver(fresh)
                elif action == "cancel":
                    svc.cancel(fresh)

            Toast.success(self, "عملیات با موفقیت انجام شد")
            self._load_project()

        except ValueError as e:
            Toast.warning(self, str(e))
        except Exception as e:
            logger.error(f"خطا: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _on_add_device(self):
        dlg = ProjectDeviceDialog(project_id=self.project_id, parent=self)
        if dlg.exec():
            self._load_project()
            Toast.success(self, "دستگاه اضافه شد")

    def _on_edit_device(self, device_id: int):
        snap = next(
            (d for d in self._devices_snapshot if d["id"] == device_id),
            None
        )
        if snap is None:
            Toast.error(self, "دستگاه یافت نشد")
            return

        dlg = ProjectDeviceDialog(
            project_id=self.project_id,
            device_snapshot=snap,
            parent=self,
        )
        if dlg.exec():
            self._load_project()
            Toast.success(self, "دستگاه ویرایش شد")

    def _on_edit_device_selected(self):
        did = self.devices_table.get_selected_id()
        if did is None:
            Toast.warning(self, "یک دستگاه انتخاب کنید")
            return
        self._on_edit_device(did)

    def _on_delete_device(self, device_id: int):
        dlg = ConfirmDialog(
            parent=self,
            title="تأیید حذف دستگاه",
            message="این دستگاه از پروژه حذف شود؟",
            confirm_text="بله، حذف کن",
            cancel_text="انصراف",
            dangerous=True,
        )
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            with get_session() as session:
                svc    = ProjectService(session)
                device = svc.device_repo.get_by_id(device_id)
                if device:
                    svc.remove_device(device)
            self._load_project()
            Toast.success(self, "دستگاه حذف شد")
        except Exception as e:
            logger.error(f"خطا: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _on_delete_device_selected(self):
        did = self.devices_table.get_selected_id()
        if did is None:
            Toast.warning(self, "یک دستگاه انتخاب کنید")
            return
        self._on_delete_device(did)