"""
Kamand - Cost Type Enumerations
انواع شمارشی مربوط به هزینه‌ها
"""

from enum import Enum


class CostCategory(str, Enum):
    """دسته‌بندی هزینه"""
    DIRECT = "direct"
    INDIRECT = "indirect"
    FIXED = "fixed"
    VARIABLE = "variable"

    @property
    def label(self) -> str:
        labels = {
            "direct": "مستقیم",
            "indirect": "غیرمستقیم",
            "fixed": "ثابت",
            "variable": "متغیر",
        }
        return labels[self.value]


class CostBehavior(str, Enum):
    """رفتار هزینه"""
    FIXED = "fixed"
    VARIABLE = "variable"
    SEMI_VARIABLE = "semi_variable"
    STEP = "step"

    @property
    def label(self) -> str:
        labels = {
            "fixed": "ثابت",
            "variable": "متغیر",
            "semi_variable": "نیمه‌متغیر",
            "step": "پلکانی",
        }
        return labels[self.value]


class CostUnit(str, Enum):
    """واحد هزینه"""
    RIAL = "rial"
    DOLLAR = "dollar"
    EURO = "euro"
    PERCENT = "percent"
    HOUR = "hour"
    UNIT = "unit"

    @property
    def label(self) -> str:
        labels = {
            "rial": "ریال",
            "dollar": "دلار",
            "euro": "یورو",
            "percent": "درصد",
            "hour": "ساعت",
            "unit": "عدد",
        }
        return labels[self.value]


class AllocationMethod(str, Enum):
    """روش تخصیص هزینه"""
    DIRECT = "direct"
    MACHINE_HOUR = "machine_hour"
    LABOR_HOUR = "labor_hour"
    PRODUCTION_QTY = "production_qty"
    AREA = "area"
    MANUAL = "manual"

    @property
    def label(self) -> str:
        labels = {
            "direct": "مستقیم",
            "machine_hour": "ساعت ماشین",
            "labor_hour": "ساعت نیروی کار",
            "production_qty": "تعداد تولید",
            "area": "متراژ",
            "manual": "دستی",
        }
        return labels[self.value]


class CostStatus(str, Enum):
    """وضعیت هزینه"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

    @property
    def label(self) -> str:
        labels = {
            "active": "فعال",
            "inactive": "غیرفعال",
            "archived": "بایگانی",
        }
        return labels[self.value]