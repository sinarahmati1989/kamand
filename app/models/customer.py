"""
Kamand - Customer Model
مدل مشتری با فیلدهای گسترش‌یافته
"""
from __future__ import annotations
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, Date, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.mixins import IDMixin, TimestampMixin
from app.enums.customer_enums import CustomerStatus


class Customer(Base, IDMixin, TimestampMixin):
    """جدول مشتریان"""

    __tablename__ = "customers"

    # ─── شناسه ───
    code: Mapped[str | None] = mapped_column(
        String(30), unique=True, nullable=True, index=True,
        comment="کد مشتری - CUS-0001"
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="نام شرکت"
    )
    trade_name: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="نام تجاری"
    )
    customer_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="legal",
        server_default="legal", index=True,
        comment="کد Lookup نوع مشتری (real/legal)"
    )
    tier: Mapped[str | None] = mapped_column(
        String(20), nullable=True, default="b",
        server_default="b",
        comment="کد Lookup سطح مشتری (a/b/c)"
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False,
        default=CustomerStatus.ACTIVE.value,
        server_default="active", index=True,
        comment="وضعیت مشتری"
    )
    national_id: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="شناسه ملی/کد اقتصادی"
    )
    cooperation_start: Mapped[date | None] = mapped_column(
        Date, nullable=True, comment="تاریخ شروع همکاری"
    )
    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="یادداشت‌ها"
    )

    # ─── اطلاعات تماس ───
    contact_name: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="نام شخص رابط"
    )
    contact_position: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="سمت رابط"
    )
    contact_mobile: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="موبایل رابط"
    )
    phone: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="تلفن ثابت"
    )
    mobile: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="موبایل شرکت"
    )
    email: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="ایمیل"
    )
    website: Mapped[str | None] = mapped_column(
        String(200), nullable=True, comment="وب‌سایت"
    )
    province: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="استان"
    )
    city: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="شهر"
    )
    address: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="آدرس کامل"
    )
    postal_code: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="کدپستی"
    )

    # ─── اطلاعات مالی ───
    payment_terms: Mapped[str | None] = mapped_column(
        String(50), nullable=True,
        comment="کد Lookup شرایط پرداخت"
    )
    currency: Mapped[str | None] = mapped_column(
        String(10), nullable=True, default="irr",
        server_default="irr",
        comment="کد Lookup ارز معاملات"
    )
    credit_days: Mapped[int | None] = mapped_column(
        Integer, nullable=True,
        comment="مدت تسویه (روز)"
    )
    credit_limit: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2), nullable=True,
        comment="سقف اعتبار مشتری (به ریال)"
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="توضیحات مالی"
    )

    def __repr__(self) -> str:
        return (
            f"<Customer("
            f"id={self.id}, "
            f"code='{self.code}', "
            f"name='{self.name}')>"
        )