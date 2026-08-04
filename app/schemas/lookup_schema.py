"""
Schema های Lookup
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict


class LookupBase(BaseModel):
    """فیلدهای مشترک"""
    category:    str = Field(..., min_length=2, max_length=50)
    code:        str = Field(..., min_length=1, max_length=50)
    label_fa:    str = Field(..., min_length=1, max_length=150)
    label_en:    Optional[str] = Field(None, max_length=150)
    parent_id:   Optional[int] = None
    sort_order:  int = Field(default=0, ge=0)
    is_active:   bool = True
    description: Optional[str] = None
    extra_data:  Optional[dict] = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        v = v.strip().lower()
        # کد فقط باید حروف انگلیسی، عدد، _ و - داشته باشه
        import re
        if not re.match(r"^[a-z0-9_\-]+$", v):
            raise ValueError("کد فقط می‌تواند شامل حروف انگلیسی کوچک، عدد، _ و - باشد")
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("label_fa")
    @classmethod
    def validate_label(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("لیبل نمی‌تواند خالی باشد")
        return v


class LookupCreate(LookupBase):
    """ساخت Lookup جدید — is_system همیشه False برای کاربر"""
    pass


class LookupUpdate(BaseModel):
    """ویرایش — همه فیلدها اختیاری"""
    label_fa:    Optional[str] = Field(None, min_length=1, max_length=150)
    label_en:    Optional[str] = Field(None, max_length=150)
    parent_id:   Optional[int] = None
    sort_order:  Optional[int] = Field(None, ge=0)
    is_active:   Optional[bool] = None
    description: Optional[str] = None
    extra_data:  Optional[dict] = None

    @field_validator("label_fa")
    @classmethod
    def validate_label(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("لیبل نمی‌تواند خالی باشد")
        return v


class LookupRead(LookupBase):
    """خواندن Lookup"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_system: bool
    created_at: datetime
    updated_at: Optional[datetime] = None