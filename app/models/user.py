"""
User Model
جدول کاربران سیستم
"""

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.mixins import IDMixin, TimestampMixin
from app.enums.roles import UserRole


class User(Base, IDMixin, TimestampMixin):
    """مدل کاربران"""
    
    __tablename__ = "users"
    
    # نام کاربری (یونیک)
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    
    # نام کامل
    full_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    
    # ایمیل
    email: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    
    # هش پسورد (bcrypt)
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    
    # نقش
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=UserRole.OPERATOR.value,
    )
    
    # وضعیت فعال
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"