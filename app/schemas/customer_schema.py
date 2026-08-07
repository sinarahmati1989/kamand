"""
Kamand - Customer Schemas (DTOs)
گسترش‌یافته با فیلدهای مالی، تماس و همکاری
"""
import re
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, field_validator

from app.enums.customer_enums import CustomerStatus


class CustomerCreateDTO(BaseModel):
    """DTO ایجاد مشتری جدید"""

    # ─── پایه ───
    code: str | None = None  # خودکار
    name: str
    trade_name: str | None = None
    customer_type: str = "legal"
    tier: str | None = "b"
    national_id: str | None = None
    cooperation_start: date | None = None
    notes: str | None = None

    # ─── تماس ───
    contact_name: str | None = None
    contact_position: str | None = None
    contact_mobile: str | None = None
    phone: str | None = None
    mobile: str | None = None
    email: str | None = None
    website: str | None = None
    province: str | None = None
    city: str | None = None
    address: str | None = None
    postal_code: str | None = None

    # ─── مالی ───
    payment_terms: str | None = None
    currency: str | None = "irr"
    credit_days: int | None = None
    credit_limit: Decimal | None = None
    description: str | None = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("نام مشتری نمی‌تواند خالی باشد")
        return v

    @field_validator("customer_type")
    @classmethod
    def validate_customer_type(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            raise ValueError("انتخاب نوع مشتری الزامی است")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str | None) -> str | None:
        if v and v.strip():
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, v.strip()):
                raise ValueError("فرمت ایمیل صحیح نیست")
            return v.strip()
        return None

    @field_validator(
        "phone", "mobile", "contact_mobile", "postal_code",
        "national_id", "trade_name", "contact_name", "contact_position",
        "website", "province", "city", "code",
        mode="before"
    )
    @classmethod
    def clean_string(cls, v) -> str | None:
        if v and str(v).strip():
            return str(v).strip()
        return None


class CustomerUpdateDTO(BaseModel):
    """DTO ویرایش مشتری"""

    name: str | None = None
    trade_name: str | None = None
    customer_type: str | None = None
    tier: str | None = None
    status: str | None = None
    national_id: str | None = None
    cooperation_start: date | None = None
    notes: str | None = None

    contact_name: str | None = None
    contact_position: str | None = None
    contact_mobile: str | None = None
    phone: str | None = None
    mobile: str | None = None
    email: str | None = None
    website: str | None = None
    province: str | None = None
    city: str | None = None
    address: str | None = None
    postal_code: str | None = None

    payment_terms: str | None = None
    currency: str | None = None
    credit_days: int | None = None
    credit_limit: Decimal | None = None
    description: str | None = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("نام مشتری نمی‌تواند خالی باشد")
        return v

    @field_validator("customer_type", "status")
    @classmethod
    def validate_optional_code(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("مقدار این فیلد نمی‌تواند خالی باشد")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str | None) -> str | None:
        if v and v.strip():
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, v.strip()):
                raise ValueError("فرمت ایمیل صحیح نیست")
            return v.strip()
        return None


class CustomerReadDTO(BaseModel):
    """DTO خواندن مشتری"""

    id: int
    code: str | None
    name: str
    trade_name: str | None
    customer_type: str
    tier: str | None
    status: str = CustomerStatus.ACTIVE.value
    national_id: str | None
    cooperation_start: date | None
    notes: str | None

    contact_name: str | None
    contact_position: str | None
    contact_mobile: str | None
    phone: str | None
    mobile: str | None
    email: str | None
    website: str | None
    province: str | None
    city: str | None
    address: str | None
    postal_code: str | None

    payment_terms: str | None
    currency: str | None
    credit_days: int | None
    credit_limit: Decimal | None
    description: str | None

    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}