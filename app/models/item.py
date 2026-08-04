"""
Kamand - Item Model
کتابخانه اقلام/قطعات/مواد/اسمبلی
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import (
    Boolean, Column, Integer,
    Numeric, String, Text,
)
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.enums.engineering_enums import ItemStatus
from app.models.mixins import TimestampMixin


class Item(Base, TimestampMixin):
    """
    کتابخانه اقلام — همه چیز اینجاست:
    قطعه خریدنی، ماده اولیه، مصرفی، اسمبلی و ...
    Assembly = Item(item_type='assembly')
    """

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, autoincrement=True)

    code = Column(
        String(30), unique=True, nullable=False, index=True,
        comment="کد قلم - ITM-0001",
    )

    name = Column(
        String(200), nullable=False, index=True,
        comment="نام قلم",
    )

    # نوع — Lookup
    item_type = Column(
        String(50), nullable=False, default="purchased_part",
        comment="کد Lookup نوع قلم",
    )

    # واحد — Lookup
    uom = Column(
        String(20), nullable=False, default="pcs",
        comment="کد Lookup واحد",
    )

    # اطلاعات مهندسی
    specification = Column(Text, nullable=True, comment="مشخصات فنی")
    drawing_no = Column(
        String(100), nullable=True, comment="شماره نقشه",
    )
    part_no = Column(
        String(100), nullable=True, comment="شماره قطعه داخلی",
    )

    # سازنده — Lookup
    manufacturer = Column(
        String(50), nullable=True,
        comment="کد Lookup سازنده",
    )
    manufacturer_part_no = Column(
        String(100), nullable=True,
        comment="شماره قطعه سازنده",
    )

    # مشخصات فیزیکی — Lookup
    weight = Column(
        Numeric(10, 4), nullable=True,
        comment="وزن (کیلوگرم)",
    )
    material_grade = Column(
        String(50), nullable=True,
        comment="کد Lookup گرید متریال",
    )
    surface_treatment = Column(
        String(50), nullable=True,
        comment="کد Lookup نوع پوشش",
    )

    # هزینه استاندارد — برای محاسبه BOM Cost
    standard_cost = Column(
        Numeric(18, 2), nullable=True,
        comment="هزینه استاندارد واحد",
    )
    currency = Column(
        String(10), nullable=True, default="irr",
        comment="کد Lookup ارز",
    )

    # توضیحات
    notes = Column(Text, nullable=True, comment="یادداشت‌ها")

    # وضعیت
    status = Column(
        String(20), nullable=False,
        default=ItemStatus.ACTIVE.value,
        server_default="active",
        index=True,
        comment="وضعیت",
    )

    is_active = Column(
        Boolean, nullable=False,
        default=True, server_default="true",
    )

    # ── Relationships ──────────────────────────────────────────────
    bom_lines = relationship(
        "BOMLine",
        foreign_keys="BOMLine.item_id",
        back_populates="item",
        lazy="select",
    )

    def __repr__(self) -> str:
        return (
            f"<Item("
            f"id={self.id}, "
            f"code='{self.code}', "
            f"name='{self.name}', "
            f"type='{self.item_type}')>"
        )