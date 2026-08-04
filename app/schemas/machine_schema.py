"""
Kamand - Machine Schemas
اسکیماهای اعتبارسنجی ماشین‌آلات
"""
from typing import Optional
from decimal import Decimal
from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator
from app.enums.machine_enums import MachineStatus


class MachineCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    machine_type: Optional[str] = Field(None, max_length=50)
    brand: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    manufacture_year: Optional[int] = Field(None, ge=1900, le=2100)
    department_id: Optional[int] = None
    work_center_id: Optional[int] = None
    location: Optional[str] = Field(None, max_length=150)
    capacity_per_hour: Optional[Decimal] = None
    hourly_rate: Optional[Decimal] = None
    currency: str = Field(default="irr", max_length=50)
    last_maintenance_date: Optional[date] = None
    next_maintenance_date: Optional[date] = None
    maintenance_interval_days: Optional[int] = Field(None, ge=1)
    technical_notes: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("نام ماشین باید حداقل ۲ کاراکتر باشد")
        return v

    @field_validator("capacity_per_hour", "hourly_rate")
    @classmethod
    def validate_positive(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < 0:
            raise ValueError("مقدار نمی‌تواند منفی باشد")
        return v

    @field_validator(
        "brand", "model", "serial_number", "location",
        "technical_notes", "notes"
    )
    @classmethod
    def clean_optional(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if v == "":
                return None
        return v


class MachineUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    machine_type: Optional[str] = Field(None, max_length=50)
    brand: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    manufacture_year: Optional[int] = Field(None, ge=1900, le=2100)
    department_id: Optional[int] = None
    work_center_id: Optional[int] = None
    location: Optional[str] = Field(None, max_length=150)
    capacity_per_hour: Optional[Decimal] = None
    hourly_rate: Optional[Decimal] = None
    currency: Optional[str] = Field(None, max_length=50)
    last_maintenance_date: Optional[date] = None
    next_maintenance_date: Optional[date] = None
    maintenance_interval_days: Optional[int] = Field(None, ge=1)
    technical_notes: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = Field(None, max_length=20)


class MachineRead(BaseModel):
    id: int
    code: str
    name: str
    machine_type: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    manufacture_year: Optional[int] = None
    department_id: Optional[int] = None
    work_center_id: Optional[int] = None
    location: Optional[str] = None
    capacity_per_hour: Optional[Decimal] = None
    hourly_rate: Optional[Decimal] = None
    currency: str = "irr"
    last_maintenance_date: Optional[date] = None
    next_maintenance_date: Optional[date] = None
    maintenance_interval_days: Optional[int] = None
    technical_notes: Optional[str] = None
    notes: Optional[str] = None
    status: str = MachineStatus.ACTIVE.value
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}