"""
Kamand - Item Schemas
"""
from typing import Optional
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from app.enums.engineering_enums import ItemStatus


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    code: Optional[str] = Field(None, max_length=30)
    item_type: str = Field(default="purchased_part", max_length=50)
    uom: str = Field(default="pcs", max_length=20)
    specification: Optional[str] = None
    drawing_no: Optional[str] = Field(None, max_length=100)
    part_no: Optional[str] = Field(None, max_length=100)
    manufacturer: Optional[str] = Field(None, max_length=50)
    manufacturer_part_no: Optional[str] = Field(None, max_length=100)
    weight: Optional[float] = Field(None, ge=0)
    material_grade: Optional[str] = Field(None, max_length=50)
    surface_treatment: Optional[str] = Field(None, max_length=50)
    standard_cost: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(default="irr", max_length=10)
    notes: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("نام قلم باید حداقل ۲ کاراکتر باشد")
        return v

    @field_validator("code")
    @classmethod
    def clean_code(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if v == "":
                return None
        return v


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    code: Optional[str] = Field(None, max_length=30)
    item_type: Optional[str] = Field(None, max_length=50)
    uom: Optional[str] = Field(None, max_length=20)
    specification: Optional[str] = None
    drawing_no: Optional[str] = Field(None, max_length=100)
    part_no: Optional[str] = Field(None, max_length=100)
    manufacturer: Optional[str] = Field(None, max_length=50)
    manufacturer_part_no: Optional[str] = Field(None, max_length=100)
    weight: Optional[float] = Field(None, ge=0)
    material_grade: Optional[str] = Field(None, max_length=50)
    surface_treatment: Optional[str] = Field(None, max_length=50)
    standard_cost: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=10)
    notes: Optional[str] = None
    status: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None


class ItemRead(BaseModel):
    id: int
    code: str
    name: str
    item_type: str = "purchased_part"
    uom: str = "pcs"
    specification: Optional[str] = None
    drawing_no: Optional[str] = None
    part_no: Optional[str] = None
    manufacturer: Optional[str] = None
    manufacturer_part_no: Optional[str] = None
    weight: Optional[float] = None
    material_grade: Optional[str] = None
    surface_treatment: Optional[str] = None
    standard_cost: Optional[Decimal] = None
    currency: Optional[str] = None
    notes: Optional[str] = None
    status: str = ItemStatus.ACTIVE.value
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}