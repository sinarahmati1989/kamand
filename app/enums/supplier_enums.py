"""
Enum های تأمین‌کنندگان
"""
from enum import Enum


class SupplierType(str, Enum):
    """انواع تأمین‌کننده (چند انتخابی)"""
    RAW_MATERIAL = "raw_material"        # مواد اولیه
    PARTS        = "parts"               # قطعات
    SERVICES     = "services"            # خدمات
    CONTRACTOR   = "contractor"          # پیمانکار
    PACKAGING    = "packaging"           # بسته‌بندی
    TOOLS        = "tools"               # ابزار و تجهیزات

    @classmethod
    def to_persian(cls, value: str) -> str:
        mapping = {
            cls.RAW_MATERIAL.value: "مواد اولیه",
            cls.PARTS.value:        "قطعات",
            cls.SERVICES.value:     "خدمات",
            cls.CONTRACTOR.value:   "پیمانکار",
            cls.PACKAGING.value:    "بسته‌بندی",
            cls.TOOLS.value:        "ابزار و تجهیزات",
        }
        return mapping.get(value, value)

    @classmethod
    def all_persian(cls) -> dict:
        """برای ساخت CheckBox ها"""
        return {member.value: cls.to_persian(member.value) for member in cls}


class SupplierTier(str, Enum):
    """سطح تأمین‌کننده"""
    A = "A"   # استراتژیک
    B = "B"
    C = "C"

    @classmethod
    def to_persian(cls, value: str) -> str:
        mapping = {
            cls.A.value: "A - استراتژیک",
            cls.B.value: "B - معمولی",
            cls.C.value: "C - جایگزین",
        }
        return mapping.get(value, value)


class SupplierStatus(str, Enum):
    """وضعیت تأمین‌کننده"""
    ACTIVE       = "active"        # فعال
    INACTIVE     = "inactive"      # غیرفعال
    UNDER_REVIEW = "under_review"  # در ارزیابی
    BLOCKED      = "blocked"       # مسدود

    @classmethod
    def to_persian(cls, value: str) -> str:
        mapping = {
            cls.ACTIVE.value:       "فعال",
            cls.INACTIVE.value:     "غیرفعال",
            cls.UNDER_REVIEW.value: "در ارزیابی",
            cls.BLOCKED.value:      "مسدود",
        }
        return mapping.get(value, value)


class PaymentTerms(str, Enum):
    """شرایط پرداخت"""
    CASH        = "cash"          # نقدی
    CHECK       = "check"         # چک
    CREDIT      = "credit"        # اعتباری
    INSTALLMENT = "installment"   # مدت‌دار

    @classmethod
    def to_persian(cls, value: str) -> str:
        mapping = {
            cls.CASH.value:        "نقدی",
            cls.CHECK.value:       "چک",
            cls.CREDIT.value:      "اعتباری",
            cls.INSTALLMENT.value: "مدت‌دار",
        }
        return mapping.get(value, value)


class Currency(str, Enum):
    """ارز معامله"""
    IRR = "IRR"   # ریال
    USD = "USD"   # دلار
    EUR = "EUR"   # یورو

    @classmethod
    def to_persian(cls, value: str) -> str:
        mapping = {
            cls.IRR.value: "ریال",
            cls.USD.value: "دلار",
            cls.EUR.value: "یورو",
        }
        return mapping.get(value, value)