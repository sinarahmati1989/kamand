"""
Audit Log Model
جدول لاگ فعالیت‌های حساس
"""

from sqlalchemy import String, Integer, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime

from app.database.base import Base
from app.models.mixins import IDMixin


class AuditLog(Base, IDMixin):
    """مدل لاگ فعالیت‌ها"""
    
    __tablename__ = "audit_logs"
    
    # کاربر مربوطه (nullable چون login failed ممکنه user نداشته باشه)
    user_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )
    
    # نام کاربر (برای وقتی user_id null هست)
    username: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    
    # نوع عملیات (LOGIN, LOGOUT, CREATE, UPDATE, DELETE, ...)
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    
    # موجودیت (User, Project, Device, ...)
    entity_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    
    # آی‌دی موجودیت
    entity_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    
    # جزئیات اضافی
    details: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    
    # IP کاربر
    ip_address: Mapped[str | None] = mapped_column(
        String(45),   # IPv6 هم جا میشه
        nullable=True,
    )
    
    # زمان
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    
    def __repr__(self) -> str:
        return f"<AuditLog(user='{self.username}', action='{self.action}')>"