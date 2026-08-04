"""
Kamand - Work Center Schemas
اسکیماهای اعتبارسنجی مرکز کار
"""
from typing import Optional
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from app.enums.work_center_enums import WorkCenterStatus


class WorkCenterCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    department_id: Optional[int] = None
    work_center_type: Optional[str] = Field(None, max_length=50)
    capacity_per_hour: Optional[Decimal] = None
    capacity_unit: Optional[str] = Field(None, max_length=50)
    shift_count: int = Field(default=1, ge=1, le=10)
    location: Optional[str] = Field(None, max_length=150)
    notes: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("نام مرکز کار باید حداقل ۲ کاراکتر باشد")
        return v

    @field_validator("capacity_per_hour")
    @classmethod
    def validate_capacity(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < 0:
            raise ValueError("ظرفیت نمی‌تواند منفی باشد")
        return v


class WorkCenterUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    department_id: Optional[int] = None
    work_center_type: Optional[str] = Field(None, max_length=50)
    capacity_per_hour: Optional[Decimal] = None
    capacity_unit: Optional[str] = Field(None, max_length=50)
    shift_count: Optional[int] = Field(None, ge=1, le=10)
    location: Optional[str] = Field(None, max_length=150)
    notes: Optional[str] = None
    status: Optional[str] = Field(None, max_length=20)


class WorkCenterRead(BaseModel):
    id: int
    code: str
    name: str
    department_id: Optional[int] = None
    work_center_type: Optional[str] = None
    capacity_per_hour: Optional[Decimal] = None
    capacity_unit: Optional[str] = None
    shift_count: int = 1
    location: Optional[str] = None
    notes: Optional[str] = None
    status: str = WorkCenterStatus.ACTIVE.value
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}