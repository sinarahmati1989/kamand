"""
Kamand - SystemSettings Model
تنظیمات سیستم به صورت key-value
"""
from __future__ import annotations

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import Session

from app.database.base import Base
from app.models.mixins import TimestampMixin


class SystemSetting(Base, TimestampMixin):
    """تنظیمات سیستم — key/value store"""

    __tablename__ = "system_settings"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    key         = Column(String(100), unique=True, nullable=False, index=True)
    value       = Column(Text, nullable=True)
    description = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<SystemSetting(key='{self.key}', value='{self.value}')>"