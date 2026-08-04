"""
User DTOs (Pydantic Schemas)
بین Service ↔ UI فقط این‌ها میگذرن
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class UserLoginDTO(BaseModel):
    """ورودی لاگین"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=4, max_length=100)


class UserCreateDTO(BaseModel):
    """ساخت کاربر جدید"""
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=2, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    password: str = Field(..., min_length=4, max_length=100)
    role: str = Field(default="operator")
    is_active: bool = Field(default=True)


class UserUpdateDTO(BaseModel):
    """ویرایش کاربر"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserReadDTO(BaseModel):
    """خروجی کاربر (بدون پسورد)"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    full_name: str
    email: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ChangePasswordDTO(BaseModel):
    """تغییر پسورد"""
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=4, max_length=100)