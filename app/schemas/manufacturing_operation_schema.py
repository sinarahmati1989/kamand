"""
Kamand - Manufacturing Operation Schemas
اسکیماهای اعتبارسنجی عملیات ساخت
"""

from typing import Optional
from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.enums.operation_enums import OperationStatus


class ManufacturingOperationCreate(BaseModel):
    """اسکیما ایجاد عملیات ساخت"""

    # پایه
    name: str = Field(..., min_length=2, max_length=150)
    operation_type: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None

    # ویژگی‌ها
    is_outsourced: bool = False
    requires_qc: bool = False
    requires_machine: bool = True
    is_bottleneck: bool = False

    # زمان‌ها
    setup_time: Optional[Decimal] = None
    setup_time_unit: str = Field(default="minute", max_length=50)
    cycle_time: Optional[Decimal] = None
    cycle_time_unit: str = Field(default="minute", max_length=50)

    # ظرفیت
    capacity_per_hour: Optional[Decimal] = None
    default_operator_count: int = Field(default=1, ge=1)
    efficiency_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    oee_target: Optional[Decimal] = Field(None, ge=0, le=100)

    # هزینه
    hourly_rate: Optional[Decimal] = None
    currency: str = Field(default="irr", max_length=50)

    # مهارت
    skill_level: Optional[str] = Field(None, max_length=50)
    required_skills_description: Optional[str] = None

    # یادداشت‌ها
    required_tools: Optional[str] = None
    safety_notes: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("نام عملیات باید حداقل ۲ کاراکتر باشد")
        return v

    @field_validator("operation_type")
    @classmethod
    def validate_op_type(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            raise ValueError("انتخاب نوع عملیات الزامی است")
        return v

    @field_validator(
        "setup_time", "cycle_time", "capacity_per_hour", "hourly_rate"
    )
    @classmethod
    def validate_positive(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < 0:
            raise ValueError("مقدار نمی‌تواند منفی باشد")
        return v

    @field_validator(
        "description", "required_skills_description",
        "required_tools", "safety_notes", "notes", "skill_level"
    )
    @classmethod
    def clean_optional(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if v == "":
                return None
        return v


class ManufacturingOperationUpdate(BaseModel):
    """اسکیما ویرایش عملیات ساخت"""

    name: Optional[str] = Field(None, min_length=2, max_length=150)
    operation_type: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None

    is_outsourced: Optional[bool] = None
    requires_qc: Optional[bool] = None
    requires_machine: Optional[bool] = None
    is_bottleneck: Optional[bool] = None

    setup_time: Optional[Decimal] = None
    setup_time_unit: Optional[str] = Field(None, max_length=50)
    cycle_time: Optional[Decimal] = None
    cycle_time_unit: Optional[str] = Field(None, max_length=50)

    capacity_per_hour: Optional[Decimal] = None
    default_operator_count: Optional[int] = Field(None, ge=1)
    efficiency_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    oee_target: Optional[Decimal] = Field(None, ge=0, le=100)

    hourly_rate: Optional[Decimal] = None
    currency: Optional[str] = Field(None, max_length=50)

    skill_level: Optional[str] = Field(None, max_length=50)
    required_skills_description: Optional[str] = None

    required_tools: Optional[str] = None
    safety_notes: Optional[str] = None
    notes: Optional[str] = None

    status: Optional[str] = Field(None, max_length=20)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) < 2:
                raise ValueError("نام عملیات باید حداقل ۲ کاراکتر باشد")
        return v

    @field_validator("operation_type", "status")
    @classmethod
    def validate_optional_code(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("مقدار این فیلد نمی‌تواند خالی باشد")
        return v


class ManufacturingOperationRead(BaseModel):
    """اسکیما خواندن عملیات ساخت"""

    id: int
    code: str
    name: str
    operation_type: str
    description: Optional[str] = None

    is_outsourced: bool
    requires_qc: bool
    requires_machine: bool
    is_bottleneck: bool

    setup_time: Optional[Decimal] = None
    setup_time_unit: str
    cycle_time: Optional[Decimal] = None
    cycle_time_unit: str

    capacity_per_hour: Optional[Decimal] = None
    default_operator_count: int
    efficiency_percent: Optional[Decimal] = None
    oee_target: Optional[Decimal] = None

    hourly_rate: Optional[Decimal] = None
    currency: str

    skill_level: Optional[str] = None
    required_skills_description: Optional[str] = None

    required_tools: Optional[str] = None
    safety_notes: Optional[str] = None
    notes: Optional[str] = None

    status: str = OperationStatus.ACTIVE.value
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}