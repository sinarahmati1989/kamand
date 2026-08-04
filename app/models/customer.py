"""
مدل مشتری
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import IDMixin, TimestampMixin
from app.enums.customer_enums import CustomerStatus

if TYPE_CHECKING:
    from app.models.device import Device


class Customer(Base, IDMixin, TimestampMixin):
    """جدول مشتریان"""

    __tablename__ = "customers"

    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="نام شرکت"
    )
    trade_name: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="نام تجاری"
    )
    customer_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="legal",
        server_default="legal",
        index=True,
        comment="کد Lookup نوع مشتری (real/legal)"
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=CustomerStatus.ACTIVE.value,
        server_default="active",
        index=True,
        comment="وضعیت مشتری"
    )
    contact_name: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="نام شخص رابط"
    )
    contact_title: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="سمت رابط"
    )
    contact_mobile: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="موبایل رابط"
    )
    phone: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="تلفن ثابت"
    )
    mobile: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="موبایل"
    )
    email: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="ایمیل"
    )
    address: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="آدرس کامل"
    )
    postal_code: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="کدپستی"
    )
    national_id: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="شناسه ملی"
    )
    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="توضیحات"
    )
