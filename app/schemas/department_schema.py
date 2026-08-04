"""
Kamand - Department Schemas
اسکیماهای اعتبارسنجی دپارتمان
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from app.enums.department_enums import DepartmentStatus


class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    department_type: Optional[str] = Field(None, max_length=50)
    manager_name: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=150)
    phone: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("نام دپارتمان باید حداقل ۲ کاراکتر باشد")
        return v

    @field_validator("department_type", "manager_name", "location", "phone")
    @classmethod
    def clean_optional(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if v == "":
                return None
        return v


class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    department_type: Optional[str] = Field(None, max_length=50)
    manager_name: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=150)
    phone: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = None
    status: Optional[str] = Field(None, max_length=20)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) < 2:
                raise ValueError("نام دپارتمان باید حداقل ۲ کاراکتر باشد")
        return v


class DepartmentRead(BaseModel):
    id: int
    code: str
    name: str
    department_type: Optional[str] = None
    manager_name: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    status: str = DepartmentStatus.ACTIVE.value
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}