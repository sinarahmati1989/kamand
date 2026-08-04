"""
Model تأمین‌کننده — با پشتیبانی ۳ سطح دسته‌بندی
"""
from datetime import date
from typing import Optional
from sqlalchemy import String, Text, Date, Boolean, Integer, JSON, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal

from app.database.base import Base
from app.models.mixins import TimestampMixin
from app.enums.supplier_enums import (
    SupplierTier, SupplierStatus, PaymentTerms, Currency
)


class Supplier(Base, TimestampMixin):
    """مدل تأمین‌کننده"""
    __tablename__ = "suppliers"

    # ══ شناسه و کد ══
    id:   Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)

    # ══ اطلاعات پایه ══
    name:       Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    trade_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # ── چند نوع تأمین‌کننده (Level 1) ──
    # مثال: ["raw_material", "parts", "services"]
    supplier_types: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    # ── زیرشاخه‌های تخصصی (Level 2) — parent-child ──
    # مثال: {"raw_material": ["فلزات", "پلاستیک"], "parts": ["الکترونیکی"]}
    subcategories: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # ── 🆕 جزئیات تخصصی (Level 3) — parent-child ──
    # مثال: {"raw_material_فلزات": ["استیل 304", "آهن ST37"]}
    specializations: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # ── توضیحات تخصصی (متن آزاد) ──
    specialty_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    tier:   Mapped[str] = mapped_column(String(2),  default=SupplierTier.B.value,       nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=SupplierStatus.ACTIVE.value, nullable=False, index=True)

    cooperation_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # ══ اطلاعات تماس ══
    contact_name:     Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    contact_position: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    mobile:           Mapped[Optional[str]] = mapped_column(String(20),  nullable=True)
    phone:            Mapped[Optional[str]] = mapped_column(String(20),  nullable=True)
    email:            Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    website:          Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    province:         Mapped[Optional[str]] = mapped_column(String(50),  nullable=True)
    city:             Mapped[Optional[str]] = mapped_column(String(50),  nullable=True)
    office_address:   Mapped[Optional[str]] = mapped_column(Text,        nullable=True)
    factory_address:  Mapped[Optional[str]] = mapped_column(Text,        nullable=True)

    # ══ اطلاعات مالی ══
    national_id:    Mapped[Optional[str]]     = mapped_column(String(20),   nullable=True)
    account_number: Mapped[Optional[str]]     = mapped_column(String(50),   nullable=True)
    bank_name:      Mapped[Optional[str]]     = mapped_column(String(100),  nullable=True)
    payment_terms:  Mapped[Optional[str]]     = mapped_column(String(20),   nullable=True)
    credit_days:    Mapped[Optional[int]]     = mapped_column(Integer,      nullable=True)
    credit_limit:   Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2), nullable=True)
    currency:       Mapped[str]               = mapped_column(String(3), default=Currency.IRR.value, nullable=False)

    has_active_contract: Mapped[bool]           = mapped_column(Boolean, default=False, nullable=False)
    contract_start:      Mapped[Optional[date]] = mapped_column(Date,    nullable=True)
    contract_end:        Mapped[Optional[date]] = mapped_column(Date,    nullable=True)

    # ══ سایر ══
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Supplier(id={self.id}, code={self.code}, name={self.name})>"