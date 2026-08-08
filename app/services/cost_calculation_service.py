"""
Kamand - Cost Calculation Service
هزینه‌یابی ۳ سطحی دستگاه

سطح ۱: مواد (BOM) + کار (Routing) = هزینه مستقیم
سطح ۲: + سربار عمومی (درصدی)
سطح ۳: + markup → قیمت پیشنهادی فروش
"""
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from sqlalchemy.orm import Session

from app.services.bom_service import BOMService
from app.services.routing_service import RoutingService
from app.services.system_settings_service import SystemSettingsService
from app.models.project import ProjectDevice

logger = logging.getLogger(__name__)

TWO_PLACES = Decimal("0.01")


@dataclass
class CostBreakdown:
    """نتیجه هزینه‌یابی یک دستگاه"""

    # سطح ۱ — مستقیم
    material_unit_cost: Decimal = Decimal("0")
    labor_unit_cost:    Decimal = Decimal("0")
    direct_unit_cost:   Decimal = Decimal("0")

    # سطح ۲ — سربار
    overhead_percent:   Decimal = Decimal("0")
    overhead_unit_cost: Decimal = Decimal("0")

    # هزینه تمام‌شده
    estimated_unit_cost: Decimal = Decimal("0")

    # سطح ۳ — فروش
    markup_percent:            Decimal = Decimal("0")
    suggested_sale_unit_price: Decimal = Decimal("0")

    # اطلاعات مرجع
    bom_revision_no:     Optional[int] = None
    routing_revision_no: Optional[int] = None

    # وضعیت
    has_bom:     bool = False
    has_routing: bool = False
    warnings:    list[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []

    @property
    def is_complete(self) -> bool:
        """آیا هزینه‌یابی کامل است؟"""
        return self.estimated_unit_cost > 0

    def as_dict(self) -> dict:
        return {
            "material_unit_cost":      float(self.material_unit_cost),
            "labor_unit_cost":         float(self.labor_unit_cost),
            "direct_unit_cost":        float(self.direct_unit_cost),
            "overhead_percent":        float(self.overhead_percent),
            "overhead_unit_cost":      float(self.overhead_unit_cost),
            "estimated_unit_cost":     float(self.estimated_unit_cost),
            "markup_percent":          float(self.markup_percent),
            "suggested_sale_unit_price": float(self.suggested_sale_unit_price),
            "bom_revision_no":         self.bom_revision_no,
            "routing_revision_no":     self.routing_revision_no,
        }

    def format_summary(self) -> str:
        """متن خلاصه برای نمایش"""
        lines = [
            f"مواد:              {self.material_unit_cost:>15,.0f} ریال",
            f"کار/ماشین:         {self.labor_unit_cost:>15,.0f} ریال",
            f"─────────────────────────────────",
            f"هزینه مستقیم:      {self.direct_unit_cost:>15,.0f} ریال",
            f"سربار ({self.overhead_percent}٪):   {self.overhead_unit_cost:>15,.0f} ریال",
            f"─────────────────────────────────",
            f"هزینه تمام‌شده:    {self.estimated_unit_cost:>15,.0f} ریال",
            f"سود markup ({self.markup_percent}٪): "
            f"{self.suggested_sale_unit_price - self.estimated_unit_cost:>10,.0f} ریال",
            f"─────────────────────────────────",
            f"قیمت پیشنهادی:     {self.suggested_sale_unit_price:>15,.0f} ریال",
        ]
        return "\n".join(lines)


class CostCalculationService:
    """
    سرویس مرکزی هزینه‌یابی

    Usage:
        svc = CostCalculationService(session)
        breakdown = svc.calculate(bom_header_id=5, routing_header_id=3)
        svc.apply_to_device(project_device, breakdown)
    """

    def __init__(self, session: Session):
        self._session = session
        self._bom_svc     = BOMService(session)
        self._routing_svc = RoutingService(session)
        self._settings    = SystemSettingsService(session)

    def calculate(
        self,
        bom_header_id:     Optional[int] = None,
        routing_header_id: Optional[int] = None,
        overhead_percent:  Optional[Decimal] = None,
        markup_percent:    Optional[Decimal] = None,
    ) -> CostBreakdown:
        """
        محاسبه هزینه‌یابی کامل یک دستگاه

        Args:
            bom_header_id:     شناسه BOM (اختیاری)
            routing_header_id: شناسه Routing (اختیاری)
            overhead_percent:  درصد سربار (اگر None → از SystemSettings)
            markup_percent:    درصد markup (اگر None → از SystemSettings)

        Returns:
            CostBreakdown با تمام اطلاعات
        """
        bd = CostBreakdown()

        # ─── دریافت نرخ‌ها از SystemSettings ───
        if overhead_percent is None:
            overhead_percent = self._settings.get_overhead_percent()
        if markup_percent is None:
            markup_percent = self._settings.get_markup_percent()

        bd.overhead_percent = overhead_percent.quantize(TWO_PLACES)
        bd.markup_percent   = markup_percent.quantize(TWO_PLACES)

        # ─── سطح ۱-الف: هزینه مواد از BOM ───
        if bom_header_id:
            try:
                bom = self._bom_svc.get_header_by_id(bom_header_id)
                if bom:
                    bd.has_bom          = True
                    bd.bom_revision_no  = bom.revision_no
                    bd.material_unit_cost = self._bom_svc.calculate_bom_cost(
                        bom_header_id
                    ).quantize(TWO_PLACES)
                else:
                    bd.warnings.append("BOM انتخاب‌شده یافت نشد")
            except Exception as e:
                logger.error(f"خطا در محاسبه هزینه BOM: {e}")
                bd.warnings.append(f"خطا در BOM: {e}")
        else:
            bd.warnings.append("BOM انتخاب نشده — هزینه مواد صفر است")

        # ─── سطح ۱-ب: هزینه کار از Routing ───
        if routing_header_id:
            try:
                routing = self._routing_svc.get_header_by_id(routing_header_id)
                if routing:
                    bd.has_routing          = True
                    bd.routing_revision_no  = routing.revision_no
                    bd.labor_unit_cost = self._routing_svc.calculate_total_cost(
                        routing_header_id
                    ).quantize(TWO_PLACES)
                else:
                    bd.warnings.append("Routing انتخاب‌شده یافت نشد")
            except Exception as e:
                logger.error(f"خطا در محاسبه هزینه Routing: {e}")
                bd.warnings.append(f"خطا در Routing: {e}")
        else:
            bd.warnings.append("Routing انتخاب نشده — هزینه کار صفر است")

        # ─── هزینه مستقیم ───
        bd.direct_unit_cost = (
            bd.material_unit_cost + bd.labor_unit_cost
        ).quantize(TWO_PLACES)

        # ─── سطح ۲: سربار ───
        bd.overhead_unit_cost = (
            bd.direct_unit_cost * bd.overhead_percent / Decimal("100")
        ).quantize(TWO_PLACES)

        # ─── هزینه تمام‌شده ───
        bd.estimated_unit_cost = (
            bd.direct_unit_cost + bd.overhead_unit_cost
        ).quantize(TWO_PLACES)

        # ─── سطح ۳: markup → قیمت پیشنهادی ───
        markup_amount = (
            bd.estimated_unit_cost * bd.markup_percent / Decimal("100")
        ).quantize(TWO_PLACES)

        bd.suggested_sale_unit_price = (
            bd.estimated_unit_cost + markup_amount
        ).quantize(TWO_PLACES)

        logger.info(
            f"✅ هزینه‌یابی: مواد={bd.material_unit_cost:,} "
            f"کار={bd.labor_unit_cost:,} "
            f"تمام‌شده={bd.estimated_unit_cost:,} "
            f"پیشنهادی={bd.suggested_sale_unit_price:,}"
        )

        return bd

    def apply_to_device(
        self,
        device: ProjectDevice,
        breakdown: CostBreakdown,
        lock: bool = False,
    ) -> ProjectDevice:
        """
        اعمال نتیجه هزینه‌یابی روی ProjectDevice

        Args:
            device:    شیء ProjectDevice
            breakdown: نتیجه calculate()
            lock:      اگر True → cost_is_locked = True
        """
        if device.cost_is_locked:
            raise ValueError(
                "هزینه‌یابی این دستگاه قفل شده است "
                "(پروژه در مرحله تولید یا بالاتر است)"
            )

        device.material_unit_cost        = breakdown.material_unit_cost
        device.labor_unit_cost           = breakdown.labor_unit_cost
        device.direct_unit_cost          = breakdown.direct_unit_cost
        device.overhead_percent          = breakdown.overhead_percent
        device.overhead_unit_cost        = breakdown.overhead_unit_cost
        device.estimated_unit_cost       = breakdown.estimated_unit_cost
        device.markup_percent            = breakdown.markup_percent
        device.suggested_sale_unit_price = breakdown.suggested_sale_unit_price
        device.bom_revision_no           = breakdown.bom_revision_no
        device.routing_revision_no       = breakdown.routing_revision_no

        # اگر unit_price هنوز تنظیم نشده، قیمت پیشنهادی را پیش‌فرض بگذار
        if not device.unit_price:
            device.unit_price = breakdown.suggested_sale_unit_price

        # نسخه و تاریخ
        device.cost_version       = (device.cost_version or 0) + 1
        device.cost_calculated_at = datetime.now(timezone.utc)
        device.cost_is_locked     = lock

        logger.info(
            f"✅ هزینه‌یابی اعمال شد روی ProjectDevice #{device.id} "
            f"(version={device.cost_version})"
        )
        return device

    def lock_device_cost(self, device: ProjectDevice) -> ProjectDevice:
        """قفل کردن هزینه‌یابی بعد از in_production"""
        device.cost_is_locked = True
        return device

    def get_project_summary(self, devices: list[ProjectDevice]) -> dict:
        """
        خلاصه هزینه‌یابی کل پروژه

        Returns:
            dict با جمع‌های کل
        """
        total_material   = Decimal("0")
        total_labor      = Decimal("0")
        total_direct     = Decimal("0")
        total_overhead   = Decimal("0")
        total_estimated  = Decimal("0")
        total_suggested  = Decimal("0")
        total_sale       = Decimal("0")
        incomplete_count = 0

        for d in devices:
            qty = Decimal(str(d.quantity))

            if d.material_unit_cost:
                total_material  += Decimal(str(d.material_unit_cost))  * qty
            if d.labor_unit_cost:
                total_labor     += Decimal(str(d.labor_unit_cost))      * qty
            if d.direct_unit_cost:
                total_direct    += Decimal(str(d.direct_unit_cost))     * qty
            if d.overhead_unit_cost:
                total_overhead  += Decimal(str(d.overhead_unit_cost))   * qty
            if d.estimated_unit_cost:
                total_estimated += Decimal(str(d.estimated_unit_cost))  * qty
            else:
                incomplete_count += 1
            if d.suggested_sale_unit_price:
                total_suggested += Decimal(str(d.suggested_sale_unit_price)) * qty
            if d.unit_price:
                total_sale      += Decimal(str(d.unit_price)) * qty

        total_profit   = total_sale - total_estimated
        profit_margin  = (
            (total_profit / total_sale * 100).quantize(TWO_PLACES)
            if total_sale > 0 else Decimal("0")
        )

        return {
            "total_material":    float(total_material),
            "total_labor":       float(total_labor),
            "total_direct":      float(total_direct),
            "total_overhead":    float(total_overhead),
            "total_estimated":   float(total_estimated),
            "total_suggested":   float(total_suggested),
            "total_sale":        float(total_sale),
            "total_profit":      float(total_profit),
            "profit_margin_pct": float(profit_margin),
            "incomplete_count":  incomplete_count,
            "is_fully_costed":   incomplete_count == 0,
        }