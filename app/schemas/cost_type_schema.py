"""
Kamand - Cost Type Schemas
اسکیماهای اعتبارسنجی نوع هزینه
"""

from typing import Optional
from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.enums.cost_enums import CostStatus


class CostTypeCreate(BaseModel):
    """اسکیما ایجاد نوع هزینه"""

    name: str = Field(..., min_length=2, max_length=100)
    category: str = Field(..., min_length=1, max_length=50)
    cost_behavior: str = Field(..., min_length=1, max_length=50)
    unit: str = Field(..., min_length=1, max_length=50)
    default_amount: Optional[Decimal] = None
    allocation_method: str = Field(..., min_length=1, max_length=50)
    account_code: Optional[str] = Field(None, max_length=30)
    taxable: bool = False
    parent_id: Optional[int] = None
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("نام نوع هزینه باید حداقل ۲ کاراکتر باشد")
        return v

    @field_validator("category", "cost_behavior", "unit", "allocation_method")
    @classmethod
    def validate_lookup_code(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("انتخاب این فیلد الزامی است")
        return v

    @field_validator("default_amount")
    @classmethod
    def validate_amount(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < 0:
            raise ValueError("مبلغ پیش‌فرض نمی‌تواند منفی باشد")
        return v

    @field_validator("account_code")
    @classmethod
    def validate_account_code(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if v == "":
                return None
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if v == "":
                return None
        return v


class CostTypeUpdate(BaseModel):
    """اسکیما ویرایش نوع هزینه"""

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    cost_behavior: Optional[str] = Field(None, min_length=1, max_length=50)
    unit: Optional[str] = Field(None, min_length=1, max_length=50)
    default_amount: Optional[Decimal] = None
    allocation_method: Optional[str] = Field(None, min_length=1, max_length=50)
    account_code: Optional[str] = Field(None, max_length=30)
    taxable: Optional[bool] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None
    status: Optional[str] = Field(None, max_length=20)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) < 2:
                raise ValueError("نام نوع هزینه باید حداقل ۲ کاراکتر باشد")
        return v

    @field_validator("category", "cost_behavior", "unit", "allocation_method", "status")
    @classmethod
    def validate_optional_lookup_code(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("مقدار این فیلد نمی‌تواند خالی باشد")
        return v

    @field_validator("default_amount")
    @classmethod
    def validate_amount(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < 0:
            raise ValueError("مبلغ پیش‌فرض نمی‌تواند منفی باشد")
        return v

    @field_validator("account_code")
    @classmethod
    def validate_account_code(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if v == "":
                return None
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if v == "":
                return None
        return v


class CostTypeRead(BaseModel):
    """اسکیما خواندن نوع هزینه"""

    id: int
    code: str
    name: str
    category: str
    cost_behavior: str
    unit: str
    default_amount: Optional[Decimal] = None
    allocation_method: str
    account_code: Optional[str] = None
    taxable: bool
    parent_id: Optional[int] = None
    description: Optional[str] = None
    status: str = CostStatus.ACTIVE.value
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}