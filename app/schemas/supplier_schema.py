"""
Pydantic Schema های تأمین‌کننده
"""
from datetime import date
from decimal import Decimal
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict

from app.enums.supplier_enums import (
    SupplierTier, SupplierStatus, PaymentTerms, Currency
)


class SupplierBase(BaseModel):
    """فیلدهای مشترک"""

    # ── پایه ──
    name:       str = Field(..., min_length=2, max_length=200)
    trade_name: Optional[str] = Field(None, max_length=200)

    # Level 1
    supplier_types: List[str] = Field(default_factory=list)

    # Level 2 (parent-child)
    # {"raw_material": ["فلزات", "پلاستیک"]}
    subcategories: Dict[str, List[str]] = Field(default_factory=dict)

    # 🆕 Level 3 (parent-child)
    # {"raw_material_فلزات": ["استیل 304", "آهن ST37"]}
    specializations: Dict[str, List[str]] = Field(default_factory=dict)

    # توضیحات تخصصی
    specialty_description: Optional[str] = None

    tier:   str = Field(default=SupplierTier.B.value)
    status: str = Field(default=SupplierStatus.ACTIVE.value)

    cooperation_start: Optional[date] = None

    # ── تماس ──
    contact_name:     Optional[str] = Field(None, max_length=150)
    contact_position: Optional[str] = Field(None, max_length=100)
    mobile:           Optional[str] = Field(None, max_length=20)
    phone:            Optional[str] = Field(None, max_length=20)
    email:            Optional[str] = Field(None, max_length=150)
    website:          Optional[str] = Field(None, max_length=200)
    province:         Optional[str] = Field(None, max_length=50)
    city:             Optional[str] = Field(None, max_length=50)
    office_address:   Optional[str] = None
    factory_address:  Optional[str] = None

    # ── مالی ──
    national_id:    Optional[str]     = Field(None, max_length=20)
    account_number: Optional[str]     = Field(None, max_length=50)
    bank_name:      Optional[str]     = Field(None, max_length=100)
    payment_terms:  Optional[str]     = None
    credit_days:    Optional[int]     = Field(None, ge=0)
    credit_limit:   Optional[Decimal] = Field(None, ge=0)
    currency:       str               = Field(default=Currency.IRR.value)

    has_active_contract: bool           = False
    contract_start:      Optional[date] = None
    contract_end:        Optional[date] = None

    description: Optional[str] = None


class SupplierCreate(SupplierBase):
    """ساخت تأمین‌کننده جدید (کد خودکار)"""
    pass


class SupplierUpdate(BaseModel):
    """ویرایش — همه فیلدها اختیاری"""

    name:       Optional[str] = Field(None, min_length=2, max_length=200)
    trade_name: Optional[str] = Field(None, max_length=200)

    supplier_types:        Optional[List[str]]            = None
    subcategories:         Optional[Dict[str, List[str]]] = None
    specializations:       Optional[Dict[str, List[str]]] = None  # 🆕
    specialty_description: Optional[str]                  = None

    tier:   Optional[str] = None
    status: Optional[str] = None

    cooperation_start: Optional[date] = None

    contact_name:     Optional[str] = None
    contact_position: Optional[str] = None
    mobile:           Optional[str] = None
    phone:            Optional[str] = None
    email:            Optional[str] = None
    website:          Optional[str] = None
    province:         Optional[str] = None
    city:             Optional[str] = None
    office_address:   Optional[str] = None
    factory_address:  Optional[str] = None

    national_id:    Optional[str]     = None
    account_number: Optional[str]     = None
    bank_name:      Optional[str]     = None
    payment_terms:  Optional[str]     = None
    credit_days:    Optional[int]     = None
    credit_limit:   Optional[Decimal] = None
    currency:       Optional[str]     = None

    has_active_contract: Optional[bool] = None
    contract_start:      Optional[date] = None
    contract_end:        Optional[date] = None

    description: Optional[str] = None


class SupplierRead(SupplierBase):
    """خواندن تأمین‌کننده"""
    model_config = ConfigDict(from_attributes=True)

    id:   int
    code: str