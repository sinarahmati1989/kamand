"""
Kamand - BOM Models
BOMHeader + BOMLine
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean, Column, Date, DateTime,
    ForeignKey, Integer, Numeric,
    String, Text, UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.enums.engineering_enums import BOMStatus
from app.models.mixins import TimestampMixin


class BOMHeader(Base, TimestampMixin):
    """سرنسخه BOM"""

    __tablename__ = "bom_headers"

    id = Column(Integer, primary_key=True, autoincrement=True)

    device_template_id = Column(
        Integer,
        ForeignKey("device_templates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="قالب دستگاه",
    )

    revision_no = Column(
        Integer, nullable=False, default=1,
        comment="شماره Revision",
    )

    status = Column(
        String(20), nullable=False,
        default=BOMStatus.DRAFT.value,
        server_default="draft",
        comment="وضعیت",
    )

    effective_from = Column(Date, nullable=True, comment="شروع اعتبار")
    effective_to   = Column(Date, nullable=True, comment="پایان اعتبار")

    notes = Column(Text, nullable=True)

    approved_by_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    approved_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "device_template_id", "revision_no",
            name="uq_bom_template_revision",
        ),
    )

    # ── Relationships ──────────────────────────────────────────────
    device_template = relationship(
        "DeviceTemplate",
        back_populates="bom_headers",
    )
    bom_lines = relationship(
        "BOMLine",
        back_populates="bom_header",
        cascade="all, delete-orphan",
        order_by="BOMLine.sort_order",
        lazy="select",
    )
    approved_by = relationship(
        "User",
        foreign_keys=[approved_by_id],
        lazy="select",
    )

    @property
    def bom_code(self) -> str:
        if self.device_template:
            return f"BOM-{self.device_template.code}-R{self.revision_no}"
        return f"BOM-???-R{self.revision_no}"

    def __repr__(self) -> str:
        return (
            f"<BOMHeader("
            f"id={self.id}, "
            f"template_id={self.device_template_id}, "
            f"rev={self.revision_no}, "
            f"status='{self.status}')>"
        )


class BOMLine(Base, TimestampMixin):
    """خط BOM"""

    __tablename__ = "bom_lines"

    id = Column(Integer, primary_key=True, autoincrement=True)

    bom_header_id = Column(
        Integer,
        ForeignKey("bom_headers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    item_id = Column(
        Integer,
        ForeignKey("items.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    quantity = Column(
        Numeric(18, 6), nullable=False, default=1,
        comment="مقدار",
    )

    uom = Column(
        String(20), nullable=True,
        comment="واحد (اگه با آیتم فرق داشته باشه)",
    )

    scrap_percent = Column(
        Numeric(5, 2), nullable=True, default=0,
        comment="درصد ضایعات",
    )

    operation_id = Column(
        Integer,
        ForeignKey("manufacturing_operations.id", ondelete="SET NULL"),
        nullable=True,
        comment="عملیات مصرف",
    )

    sort_order = Column(
        Integer, nullable=False, default=0,
        comment="ترتیب نمایش",
    )

    is_optional = Column(
        Boolean, nullable=False,
        default=False, server_default="false",
        comment="قطعه اختیاری",
    )

    notes = Column(Text, nullable=True)

    # ── Relationships ──────────────────────────────────────────────
    bom_header = relationship(
        "BOMHeader",
        back_populates="bom_lines",
    )
    item = relationship(
        "Item",
        foreign_keys=[item_id],
        back_populates="bom_lines",
        lazy="joined",
    )
    operation = relationship(
        "ManufacturingOperation",
        foreign_keys=[operation_id],
        lazy="select",
    )

    def __repr__(self) -> str:
        return (
            f"<BOMLine("
            f"id={self.id}, "
            f"bom={self.bom_header_id}, "
            f"item={self.item_id}, "
            f"qty={self.quantity})>"
        )