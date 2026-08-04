"""
Kamand - Engineering Enums
Enumهای ماژول مهندسی دستگاه
"""
from enum import Enum


class DeviceTemplateStatus(str, Enum):
    """وضعیت قالب دستگاه"""
    DRAFT        = "draft"         # پیش‌نویس
    UNDER_REVIEW = "under_review"  # در حال بررسی
    APPROVED     = "approved"      # تأیید شده
    OBSOLETE     = "obsolete"      # منسوخ

    @property
    def label(self) -> str:
        return {
            "draft":        "پیش‌نویس",
            "under_review": "در حال بررسی",
            "approved":     "تأیید شده",
            "obsolete":     "منسوخ",
        }.get(self.value, self.value)

    @property
    def color(self) -> str:
        return {
            "draft":        "#64748B",
            "under_review": "#F59E0B",
            "approved":     "#10B981",
            "obsolete":     "#EF4444",
        }.get(self.value, "#64748B")


class ItemStatus(str, Enum):
    """وضعیت قلم"""
    DRAFT    = "draft"    # پیش‌نویس
    ACTIVE   = "active"   # فعال
    OBSOLETE = "obsolete" # منسوخ

    @property
    def label(self) -> str:
        return {
            "draft":    "پیش‌نویس",
            "active":   "فعال",
            "obsolete": "منسوخ",
        }.get(self.value, self.value)

    @property
    def color(self) -> str:
        return {
            "draft":    "#64748B",
            "active":   "#10B981",
            "obsolete": "#EF4444",
        }.get(self.value, "#64748B")


class BOMStatus(str, Enum):
    """وضعیت BOM"""
    DRAFT    = "draft"    # پیش‌نویس
    APPROVED = "approved" # تأیید شده
    OBSOLETE = "obsolete" # منسوخ

    @property
    def label(self) -> str:
        return {
            "draft":    "پیش‌نویس",
            "approved": "تأیید شده",
            "obsolete": "منسوخ",
        }.get(self.value, self.value)

    @property
    def color(self) -> str:
        return {
            "draft":    "#64748B",
            "approved": "#10B981",
            "obsolete": "#EF4444",
        }.get(self.value, "#64748B")


class RoutingStatus(str, Enum):
    """وضعیت مسیر ساخت"""
    DRAFT    = "draft"
    APPROVED = "approved"
    OBSOLETE = "obsolete"

    @property
    def label(self) -> str:
        return {
            "draft":    "پیش‌نویس",
            "approved": "تأیید شده",
            "obsolete": "منسوخ",
        }.get(self.value, self.value)

    @property
    def color(self) -> str:
        return {
            "draft":    "#64748B",
            "approved": "#10B981",
            "obsolete": "#EF4444",
        }.get(self.value, "#64748B")