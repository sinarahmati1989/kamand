"""
Kamand - DeviceTemplate Schemas
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from app.enums.engineering_enums import DeviceTemplateStatus


class DeviceTemplateCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    code: Optional[str] = Field(None, max_length=30)
    template_type: Optional[str] = Field(None, max_length=50)
    revision_no: int = Field(default=1, ge=1)
    description: Optional[str] = None
    technical_notes: Optional[str] = None
    default_uom: Optional[str] = Field(default="pcs", max_length=20)
    estimated_weight: Optional[float] = Field(default=None, ge=0)
    estimated_cycle_time: Optional[int] = Field(default=None, ge=0)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("نام دستگاه باید حداقل ۲ کاراکتر باشد")
        return v

    @field_validator("code")
    @classmethod
    def clean_code(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if v == "":
                return None
        return v


class DeviceTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    template_type: Optional[str] = Field(None, max_length=50)
    revision_no: Optional[int] = Field(None, ge=1)
    status: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    technical_notes: Optional[str] = None
    default_uom: Optional[str] = Field(None, max_length=20)
    estimated_weight: Optional[float] = Field(None, ge=0)
    estimated_cycle_time: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    approved_by_id: Optional[int] = None


class DeviceTemplateRead(BaseModel):
    id: int
    code: str
    name: str
    template_type: Optional[str] = None
    revision_no: int = 1
    status: str = DeviceTemplateStatus.DRAFT.value
    description: Optional[str] = None
    technical_notes: Optional[str] = None
    default_uom: Optional[str] = None
    estimated_weight: Optional[float] = None
    estimated_cycle_time: Optional[int] = None
    is_active: bool = True
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_by_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}