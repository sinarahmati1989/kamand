"""
دسته‌بندی‌های Lookup — اسم category ها
"""
from enum import Enum


class LookupCategory(str, Enum):
    """دسته‌های Lookup که سیستم می‌شناسد"""

    # ─── تأمین‌کنندگان ───
    SUPPLIER_TYPE           = "supplier_type"
    SUPPLIER_SUBCATEGORY    = "supplier_subcategory"
    SUPPLIER_SPECIALIZATION = "supplier_specialization"
    SUPPLIER_TIER           = "supplier_tier"
    PAYMENT_TERMS           = "payment_terms"

    # ─── عمومی مالی ───
    CURRENCY                = "currency"

    # ─── هزینه‌ها ───
    COST_CATEGORY           = "cost_category"
    COST_BEHAVIOR           = "cost_behavior"
    COST_UNIT               = "cost_unit"
    ALLOCATION_METHOD       = "allocation_method"

    # ─── مشتریان ───
    CUSTOMER_TYPE           = "customer_type"

    # ─── عملیات ساخت ───
    OPERATION_TYPE          = "operation_type"
    SKILL_LEVEL             = "skill_level"
    TIME_UNIT               = "time_unit"

    # ─── دپارتمان / مرکز کار / ماشین ───
    DEPARTMENT_TYPE         = "department_type"
    WORK_CENTER_TYPE        = "work_center_type"
    MACHINE_TYPE            = "machine_type"

    # ─── مهندسی دستگاه ───
    DEVICE_TEMPLATE_TYPE    = "device_template_type"
    ITEM_TYPE               = "item_type"
    UOM                     = "uom"

    # ─── مشخصات فنی اقلام ───  🆕
    MATERIAL_GRADE          = "material_grade"
    SURFACE_TREATMENT       = "surface_treatment"
    ITEM_MANUFACTURER       = "item_manufacturer"

    # ─── پروژه ───
    PROJECT_TYPE            = "project_type"

    @classmethod
    def to_persian(cls, value: str) -> str:
        """اسم فارسی دسته"""
        mapping = {
            cls.SUPPLIER_TYPE.value:           "نوع تأمین‌کننده",
            cls.SUPPLIER_SUBCATEGORY.value:    "زیرشاخه تأمین‌کننده",
            cls.SUPPLIER_SPECIALIZATION.value: "جزئیات تخصصی تأمین‌کننده",
            cls.SUPPLIER_TIER.value:           "سطح تأمین‌کننده",
            cls.PAYMENT_TERMS.value:           "شرایط پرداخت",
            cls.CURRENCY.value:                "ارز",
            cls.COST_CATEGORY.value:           "دسته هزینه",
            cls.COST_BEHAVIOR.value:           "رفتار هزینه",
            cls.COST_UNIT.value:               "واحد هزینه",
            cls.ALLOCATION_METHOD.value:       "روش تخصیص هزینه",
            cls.CUSTOMER_TYPE.value:           "نوع مشتری",
            cls.OPERATION_TYPE.value:          "نوع عملیات ساخت",
            cls.SKILL_LEVEL.value:             "سطح مهارت",
            cls.TIME_UNIT.value:               "واحد زمان",
            cls.DEPARTMENT_TYPE.value:         "نوع دپارتمان",
            cls.WORK_CENTER_TYPE.value:        "نوع مرکز کار",
            cls.MACHINE_TYPE.value:            "نوع ماشین",
            cls.DEVICE_TEMPLATE_TYPE.value:    "نوع دستگاه",
            cls.ITEM_TYPE.value:               "نوع قلم",
            cls.UOM.value:                     "واحد اندازه‌گیری",
            cls.MATERIAL_GRADE.value:          "گرید متریال",
            cls.SURFACE_TREATMENT.value:       "نوع پوشش/آبکاری",
            cls.ITEM_MANUFACTURER.value:       "سازنده قطعه",
            cls.PROJECT_TYPE.value:            "نوع پروژه",
        }
        return mapping.get(value, value)

    @classmethod
    def all_categories(cls) -> dict[str, str]:
        return {cat.value: cls.to_persian(cat.value) for cat in cls}