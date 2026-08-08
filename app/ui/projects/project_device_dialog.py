"""
Kamand - Project Device Dialog
افزودن/ویرایش دستگاه در پروژه
با هزینه‌یابی ۳ سطحی خودکار
"""
import logging
from decimal import Decimal
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QTextEdit,
    QPushButton, QWidget, QGroupBox,
    QScrollArea, QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from app.database.session import get_session
from app.services.project_service import ProjectService
from app.services.cost_calculation_service import CostCalculationService
from app.services.system_settings_service import SystemSettingsService
from app.ui.widgets.toast import Toast
from app.ui.widgets.money_widget import MoneyWidget
from app.ui.widgets.smart_spinbox import SmartSpinBox
from app.ui.widgets.searchable_device_combo import SearchableDeviceCombo

logger = logging.getLogger(__name__)


PRODUCTION_STATUS = [
    ("pending",     "⏳ در انتظار"),
    ("in_progress", "🔧 در حال تولید"),
    ("completed",   "✅ تکمیل شده"),
    ("on_hold",     "⏸ معلق"),
]


class ProjectDeviceDialog(QDialog):
    """فرم افزودن/ویرایش دستگاه پروژه با هزینه‌یابی ۳ سطحی"""

    def __init__(
        self,
        project_id: int,
        device_snapshot: Optional[dict] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.project_id  = project_id
        self._snapshot   = device_snapshot
        self.is_edit     = device_snapshot is not None
        self.device_id   = device_snapshot["id"] if device_snapshot else None

        # نگهداری آخرین breakdown محاسبه‌شده
        self._last_breakdown = None

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowTitle(
            "ویرایش دستگاه" if self.is_edit else "افزودن دستگاه به پروژه"
        )
        self.setMinimumSize(720, 780)
        self.resize(760, 820)

        self._setup_ui()

        if self.is_edit:
            self._fill_form()

    # ─────────────────── Setup ───────────────────

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title_text = (
            "✏️ ویرایش دستگاه پروژه" if self.is_edit
            else "➕ افزودن دستگاه به پروژه"
        )
        title = QLabel(title_text)
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # محتوا داخل scroll
        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(16)

        cl.addWidget(self._build_device_group())
        cl.addWidget(self._build_reference_group())
        cl.addWidget(self._build_cost_breakdown_group())
        cl.addWidget(self._build_pricing_group())
        cl.addWidget(self._build_notes_group())
        cl.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        # دکمه‌ها
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        save_btn = QPushButton("💾  ذخیره")
        save_btn.setObjectName("neonButton")
        save_btn.setFixedSize(140, 42)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._on_save)

        cancel_btn = QPushButton("انصراف")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.setFixedSize(110, 42)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)

        btn_row.addStretch(1)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    # ─────────────────── Groups ───────────────────

    def _build_device_group(self) -> QGroupBox:
        grp = QGroupBox("🖥️  انتخاب دستگاه")
        grp.setObjectName("formGroup")
        v = QVBoxLayout(grp)
        v.setContentsMargins(14, 20, 14, 14)
        v.setSpacing(12)

        # ردیف دستگاه + تعداد
        row = QHBoxLayout()
        row.setSpacing(12)

        self.device_combo = SearchableDeviceCombo()
        self.device_combo.device_changed.connect(self._on_device_changed)
        row.addWidget(self._make_field("دستگاه", self.device_combo, required=True), 2)

        self.qty_spin = SmartSpinBox()
        self.qty_spin.setRange(1, 9999)
        self.qty_spin.setValue(1)
        self.qty_spin.setMinimumHeight(36)
        row.addWidget(self._make_field("تعداد", self.qty_spin, required=True), 1)

        v.addLayout(row)

        # وضعیت تولید (فقط ویرایش)
        if self.is_edit:
            self.prod_status_combo = QComboBox()
            self.prod_status_combo.setMinimumHeight(36)
            for code, label in PRODUCTION_STATUS:
                self.prod_status_combo.addItem(label, code)
            v.addWidget(self._make_field("وضعیت تولید", self.prod_status_combo))
        else:
            self.prod_status_combo = None

        return grp

    def _build_reference_group(self) -> QGroupBox:
        grp = QGroupBox("📐  مراجع مهندسی (BOM / Routing)")
        grp.setObjectName("formGroup")
        v = QVBoxLayout(grp)
        v.setContentsMargins(14, 20, 14, 14)
        v.setSpacing(12)

        row = QHBoxLayout()
        row.setSpacing(12)

        self.bom_combo = QComboBox()
        self.bom_combo.setMinimumHeight(36)
        self.bom_combo.addItem("— بدون BOM —", None)
        self.bom_combo.currentIndexChanged.connect(self._on_reference_changed)
        row.addWidget(self._make_field("BOM مرجع", self.bom_combo), 1)

        self.routing_combo = QComboBox()
        self.routing_combo.setMinimumHeight(36)
        self.routing_combo.addItem("— بدون Routing —", None)
        self.routing_combo.currentIndexChanged.connect(self._on_reference_changed)
        row.addWidget(self._make_field("Routing مرجع", self.routing_combo), 1)

        v.addLayout(row)

        # دکمه محاسبه
        calc_row = QHBoxLayout()
        calc_row.addStretch()

        self.calc_btn = QPushButton("🧮  محاسبه هزینه")
        self.calc_btn.setObjectName("secondaryButton")
        self.calc_btn.setFixedHeight(36)
        self.calc_btn.setFixedWidth(160)
        self.calc_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.calc_btn.clicked.connect(self._on_calculate)
        calc_row.addWidget(self.calc_btn)

        v.addLayout(calc_row)

        hint = QLabel("💡 پس از انتخاب BOM و Routing، روی «محاسبه هزینه» کلیک کنید")
        hint.setStyleSheet("color: #64748B; font-size: 11px; padding: 4px 0;")
        hint.setWordWrap(True)
        v.addWidget(hint)

        return grp

    def _build_cost_breakdown_group(self) -> QGroupBox:
        """نمایش breakdown هزینه‌یابی"""
        grp = QGroupBox("📊  جزئیات هزینه‌یابی (خودکار)")
        grp.setObjectName("formGroup")
        v = QVBoxLayout(grp)
        v.setContentsMargins(14, 20, 14, 14)
        v.setSpacing(8)

        # Frame داخلی برای breakdown
        self.breakdown_frame = QFrame()
        self.breakdown_frame.setObjectName("breakdownFrame")
        self.breakdown_frame.setStyleSheet("""
            QFrame#breakdownFrame {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 4px;
            }
        """)
        fl = QVBoxLayout(self.breakdown_frame)
        fl.setContentsMargins(12, 10, 12, 10)
        fl.setSpacing(6)

        # ردیف‌های breakdown
        self._cost_labels = {}
        rows_def = [
            ("material",  "🔩 هزینه مواد (BOM):",       "#1E293B"),
            ("labor",     "⚙️ هزینه کار (Routing):",     "#1E293B"),
            ("sep1",      None,                           None),
            ("direct",    "📌 هزینه مستقیم:",             "#3B82F6"),
            ("overhead",  "🏭 سربار عمومی:",              "#1E293B"),
            ("sep2",      None,                           None),
            ("estimated", "💼 هزینه تمام‌شده واحد:",     "#6366F1"),
            ("profit",    "📈 سود (markup):",             "#10B981"),
            ("sep3",      None,                           None),
            ("suggested", "💡 قیمت پیشنهادی فروش:",      "#F59E0B"),
        ]

        for key, label_text, color in rows_def:
            if label_text is None:
                # خط جداکننده
                sep = QFrame()
                sep.setFrameShape(QFrame.Shape.HLine)
                sep.setStyleSheet("color: #E2E8F0;")
                fl.addWidget(sep)
                continue

            row_w = QHBoxLayout()
            row_w.setSpacing(8)

            lbl = QLabel(label_text)
            lbl.setStyleSheet(
                f"color: #64748B; font-size: 12px; font-family: Vazirmatn;"
            )
            lbl.setFixedWidth(200)
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            val = QLabel("—")
            val.setStyleSheet(
                f"color: {color}; font-size: 13px; "
                f"font-weight: bold; font-family: Vazirmatn;"
            )
            val.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            self._cost_labels[key] = val

            row_w.addWidget(lbl)
            row_w.addWidget(val, 1)
            fl.addLayout(row_w)

        v.addWidget(self.breakdown_frame)

        # وضعیت محاسبه
        self.calc_status_label = QLabel("⚠️ هنوز محاسبه نشده")
        self.calc_status_label.setStyleSheet(
            "color: #F59E0B; font-size: 11px; padding: 4px 0;"
        )
        self.calc_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(self.calc_status_label)

        # هشدارها
        self.warnings_label = QLabel("")
        self.warnings_label.setStyleSheet(
            "color: #EF4444; font-size: 11px; padding: 4px 0;"
        )
        self.warnings_label.setWordWrap(True)
        self.warnings_label.hide()
        v.addWidget(self.warnings_label)

        return grp

    def _build_pricing_group(self) -> QGroupBox:
        grp = QGroupBox("💰  قیمت فروش نهایی")
        grp.setObjectName("formGroup")
        v = QVBoxLayout(grp)
        v.setContentsMargins(14, 20, 14, 14)
        v.setSpacing(12)

        hint = QLabel(
            "💡 قیمت پیشنهادی سیستم را می‌توانید اینجا تغییر دهید. "
            "این مبلغ به عنوان قیمت فروش نهایی ذخیره می‌شود."
        )
        hint.setStyleSheet("color: #64748B; font-size: 11px; padding: 4px 0;")
        hint.setWordWrap(True)
        v.addWidget(hint)

        self.unit_price_widget = MoneyWidget()
        v.addWidget(self._make_field("قیمت فروش واحد (نهایی)", self.unit_price_widget))

        # دکمه کپی از پیشنهادی
        copy_row = QHBoxLayout()
        copy_row.addStretch()
        self.copy_suggested_btn = QPushButton("📋  کپی از قیمت پیشنهادی")
        self.copy_suggested_btn.setObjectName("secondaryButton")
        self.copy_suggested_btn.setFixedHeight(32)
        self.copy_suggested_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_suggested_btn.clicked.connect(self._copy_suggested_price)
        self.copy_suggested_btn.setEnabled(False)
        copy_row.addWidget(self.copy_suggested_btn)
        v.addLayout(copy_row)

        return grp

    def _build_notes_group(self) -> QGroupBox:
        grp = QGroupBox("📝  یادداشت")
        grp.setObjectName("formGroup")
        v = QVBoxLayout(grp)
        v.setContentsMargins(14, 20, 14, 14)
        v.setSpacing(12)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("یادداشت اختیاری...")
        self.notes_input.setMinimumHeight(60)
        self.notes_input.setMaximumHeight(90)
        f = QFont("Vazirmatn", 10)
        self.notes_input.setFont(f)
        self.notes_input.document().setDefaultFont(f)
        v.addWidget(self.notes_input)

        return grp

    # ─────────────────── Helpers ───────────────────

    def _make_field(
        self, label_text: str, widget: QWidget, required: bool = False
    ) -> QWidget:
        wrapper = QWidget()
        v = QVBoxLayout(wrapper)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(6)

        lbl = QLabel(f"{label_text} *" if required else label_text)
        lbl.setObjectName("fieldLabel")
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        if required:
            lbl.setStyleSheet(
                "QLabel#fieldLabel { color: #6366F1; font-weight: 600; }"
            )
        v.addWidget(lbl)
        v.addWidget(widget)
        return wrapper

    def _fmt_money(self, value) -> str:
        """فرمت عدد به ریال"""
        if not value:
            return "—"
        v = float(value)
        if v >= 1_000_000_000:
            return f"{v / 1_000_000_000:,.2f} میلیارد ریال"
        if v >= 1_000_000:
            return f"{v / 1_000_000:,.2f} میلیون ریال"
        if v >= 1_000:
            return f"{v / 1_000:,.0f} هزار ریال"
        return f"{v:,.0f} ریال"

    def _update_breakdown_ui(self, bd) -> None:
        """آپدیت نمایش breakdown در UI"""
        if not bd:
            for lbl in self._cost_labels.values():
                lbl.setText("—")
            self.calc_status_label.setText("⚠️ هنوز محاسبه نشده")
            self.calc_status_label.setStyleSheet(
                "color: #F59E0B; font-size: 11px; padding: 4px 0;"
            )
            self.copy_suggested_btn.setEnabled(False)
            return

        profit = bd.suggested_sale_unit_price - bd.estimated_unit_cost

        self._cost_labels["material"].setText(
            self._fmt_money(bd.material_unit_cost)
        )
        self._cost_labels["labor"].setText(
            self._fmt_money(bd.labor_unit_cost)
        )
        self._cost_labels["direct"].setText(
            self._fmt_money(bd.direct_unit_cost)
        )
        self._cost_labels["overhead"].setText(
            f"{self._fmt_money(bd.overhead_unit_cost)}  ({bd.overhead_percent}٪)"
        )
        self._cost_labels["estimated"].setText(
            self._fmt_money(bd.estimated_unit_cost)
        )
        self._cost_labels["profit"].setText(
            f"{self._fmt_money(profit)}  ({bd.markup_percent}٪)"
        )
        self._cost_labels["suggested"].setText(
            self._fmt_money(bd.suggested_sale_unit_price)
        )

        if bd.is_complete:
            self.calc_status_label.setText("✅ هزینه‌یابی با موفقیت انجام شد")
            self.calc_status_label.setStyleSheet(
                "color: #10B981; font-size: 11px; padding: 4px 0;"
            )
        else:
            self.calc_status_label.setText("⚠️ هزینه‌یابی ناقص — BOM یا Routing ندارد")
            self.calc_status_label.setStyleSheet(
                "color: #F59E0B; font-size: 11px; padding: 4px 0;"
            )

        # هشدارها
        if bd.warnings:
            self.warnings_label.setText("⚠️ " + " | ".join(bd.warnings))
            self.warnings_label.show()
        else:
            self.warnings_label.hide()

        self.copy_suggested_btn.setEnabled(
            bd.suggested_sale_unit_price > 0
        )

    # ─────────────────── Data ───────────────────

    def _on_device_changed(self, device_id: int):
        """بعد از انتخاب دستگاه — BOM و Routing بارگذاری شوند"""
        self.bom_combo.clear()
        self.bom_combo.addItem("— بدون BOM —", None)
        self.routing_combo.clear()
        self.routing_combo.addItem("— بدون Routing —", None)

        # ریست breakdown
        self._last_breakdown = None
        self._update_breakdown_ui(None)

        if not device_id:
            return

        try:
            from app.services.bom_service import BOMService
            from app.services.routing_service import RoutingService

            with get_session() as session:
                bom_svc     = BOMService(session)
                routing_svc = RoutingService(session)

                boms     = bom_svc.get_headers_by_template(device_id)
                routings = routing_svc.get_headers_by_template(device_id)

                # ✅ کپی قبل از بستن session
                bom_data     = [(b.id, b.revision_no, b.status) for b in boms]
                routing_data = [(r.id, r.revision_no, r.status) for r in routings]

            for bid, rev, status in bom_data:
                self.bom_combo.addItem(f"Rev.{rev}  [{status}]", bid)

            for rid, rev, status in routing_data:
                self.routing_combo.addItem(f"Rev.{rid}  [{status}]", rid)

            # اگر فقط یکی هست، خودکار انتخاب کن
            if len(bom_data) == 1:
                self.bom_combo.setCurrentIndex(1)
            if len(routing_data) == 1:
                self.routing_combo.setCurrentIndex(1)

        except Exception as e:
            logger.error(f"خطا در بارگذاری BOM/Routing: {e}")
            Toast.warning(self, f"خطا در بارگذاری مراجع: {e}")

    def _on_reference_changed(self, _index: int):
        """با تغییر BOM یا Routing، breakdown را ریست کن"""
        self._last_breakdown = None
        self._update_breakdown_ui(None)
        self.calc_status_label.setText("💡 BOM یا Routing تغییر کرد — مجدد محاسبه کنید")
        self.calc_status_label.setStyleSheet(
            "color: #6366F1; font-size: 11px; padding: 4px 0;"
        )

    def _on_calculate(self):
        """محاسبه هزینه از BOM + Routing"""
        bom_id     = self.bom_combo.currentData()
        routing_id = self.routing_combo.currentData()

        if not bom_id and not routing_id:
            Toast.warning(self, "حداقل یک BOM یا Routing انتخاب کنید")
            return

        try:
            with get_session() as session:
                svc = CostCalculationService(session)
                bd  = svc.calculate(
                    bom_header_id=bom_id,
                    routing_header_id=routing_id,
                )

            self._last_breakdown = bd
            self._update_breakdown_ui(bd)

            # اگر unit_price خالی است، قیمت پیشنهادی را پیش‌فرض بگذار
            current_amount, _ = self.unit_price_widget.get_amount_and_currency()
            if not current_amount or current_amount == 0:
                self._copy_suggested_price()

            Toast.success(self, "✅ هزینه‌یابی با موفقیت انجام شد")

        except Exception as e:
            logger.error(f"خطا در هزینه‌یابی: {e}", exc_info=True)
            Toast.error(self, f"خطا در محاسبه: {e}")

    def _copy_suggested_price(self):
        """کپی قیمت پیشنهادی به قیمت فروش"""
        if not self._last_breakdown:
            return
        suggested = float(self._last_breakdown.suggested_sale_unit_price)
        if suggested > 0:
            self.unit_price_widget.set_amount_and_currency(suggested, "irr")

    def _fill_form(self):
        """پر کردن فرم از snapshot — نه ORM"""
        d = self._snapshot
        if not d:
            return

        # دستگاه — غیرقابل تغییر
        self.device_combo.set_device_id(d["device_template_id"])
        self.device_combo.setEnabled(False)

        # بارگذاری BOM/Routing
        self._on_device_changed(d["device_template_id"])

        # تعداد
        self.qty_spin.setValue(d.get("quantity", 1))

        # BOM
        bom_id = d.get("bom_header_id")
        if bom_id:
            idx = self.bom_combo.findData(bom_id)
            if idx >= 0:
                self.bom_combo.setCurrentIndex(idx)

        # Routing
        routing_id = d.get("routing_header_id")
        if routing_id:
            idx = self.routing_combo.findData(routing_id)
            if idx >= 0:
                self.routing_combo.setCurrentIndex(idx)

        # قیمت فروش نهایی
        price = d.get("unit_price", 0)
        if price:
            self.unit_price_widget.set_amount_and_currency(float(price), "irr")

        # وضعیت تولید
        if self.prod_status_combo:
            status = d.get("production_status", "pending")
            idx = self.prod_status_combo.findData(status)
            if idx >= 0:
                self.prod_status_combo.setCurrentIndex(idx)

        # یادداشت
        notes = d.get("notes") or ""
        if notes:
            self.notes_input.setPlainText(notes)

        # نمایش snapshot هزینه‌یابی قبلی (اگر وجود داشت)
        if d.get("estimated_unit_cost"):
            self._show_existing_cost_snapshot(d)

        # قفل هزینه
        if d.get("cost_is_locked"):
            self.calc_btn.setEnabled(False)
            self.calc_btn.setToolTip("هزینه‌یابی قفل شده (پروژه در تولید است)")
            self.calc_status_label.setText("🔒 هزینه‌یابی قفل شده است")
            self.calc_status_label.setStyleSheet(
                "color: #64748B; font-size: 11px; padding: 4px 0;"
            )

    def _show_existing_cost_snapshot(self, d: dict):
        """نمایش snapshot هزینه‌یابی ذخیره‌شده قبلی"""
        from app.services.cost_calculation_service import CostBreakdown

        bd = CostBreakdown(
            material_unit_cost      = Decimal(str(d.get("material_unit_cost")  or 0)),
            labor_unit_cost         = Decimal(str(d.get("labor_unit_cost")      or 0)),
            direct_unit_cost        = Decimal(str(d.get("direct_unit_cost")     or 0)),
            overhead_percent        = Decimal(str(d.get("overhead_percent")     or 0)),
            overhead_unit_cost      = Decimal(str(d.get("overhead_unit_cost")   or 0)),
            estimated_unit_cost     = Decimal(str(d.get("estimated_unit_cost")  or 0)),
            markup_percent          = Decimal(str(d.get("markup_percent")       or 0)),
            suggested_sale_unit_price = Decimal(str(d.get("suggested_sale_unit_price") or 0)),
            bom_revision_no         = d.get("bom_revision_no"),
            routing_revision_no     = d.get("routing_revision_no"),
        )
        self._last_breakdown = bd
        self._update_breakdown_ui(bd)

        version = d.get("cost_version", 0)
        calc_at = d.get("cost_calculated_at")
        info_text = f"📋 نسخه {version} هزینه‌یابی"
        if calc_at:
            info_text += f" — {calc_at}"
        self.calc_status_label.setText(info_text)
        self.calc_status_label.setStyleSheet(
            "color: #6366F1; font-size: 11px; padding: 4px 0;"
        )

    def _on_save(self):
        device_id = self.device_combo.get_device_id()
        if not device_id:
            Toast.warning(self, "انتخاب دستگاه الزامی است")
            return

        bom_id     = self.bom_combo.currentData()
        routing_id = self.routing_combo.currentData()
        amount, _  = self.unit_price_widget.get_amount_and_currency()

        data = {
            "device_template_id": device_id,
            "quantity":           self.qty_spin.value(),
            "unit_price":         amount,
            "bom_header_id":      bom_id,
            "routing_header_id":  routing_id,
            "notes":              self.notes_input.toPlainText().strip() or None,
        }

        if self.prod_status_combo:
            data["production_status"] = self.prod_status_combo.currentData()

        # ─── اعمال breakdown هزینه‌یابی ───
        if self._last_breakdown:
            bd = self._last_breakdown
            data.update(bd.as_dict())

        try:
            with get_session() as session:
                svc = ProjectService(session)

                if self.is_edit:
                    device = svc.device_repo.get_by_id(self.device_id)
                    if not device:
                        Toast.error(self, "دستگاه یافت نشد")
                        return
                    if device.cost_is_locked:
                        # حتی در ویرایش، cost fields را آپدیت نکن
                        data.pop("material_unit_cost",      None)
                        data.pop("labor_unit_cost",         None)
                        data.pop("direct_unit_cost",        None)
                        data.pop("overhead_percent",        None)
                        data.pop("overhead_unit_cost",      None)
                        data.pop("estimated_unit_cost",     None)
                        data.pop("markup_percent",          None)
                        data.pop("suggested_sale_unit_price", None)
                        data.pop("bom_revision_no",         None)
                        data.pop("routing_revision_no",     None)
                    svc.update_device(device, data)
                else:
                    svc.add_device(self.project_id, data)

            self.accept()

        except Exception as e:
            logger.error(f"خطا در ذخیره دستگاه: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")