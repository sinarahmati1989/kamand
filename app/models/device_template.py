"""
Kamand - DeviceTemplate Model
مدل قالب/تعریف مهندسی دستگاه
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey,
    Integer, Numeric, String, Text,
)
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.enums.engineering_enums import DeviceTemplateStatus
from app.models.mixins import TimestampMixin


class DeviceTemplate(Base, TimestampMixin):
    """قالب مهندسی دستگاه — بانک دانش فنی شرکت"""

    __tablename__ = "device_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)

    code = Column(
        String(30), unique=True, nullable=False, index=True,
        comment="کد دستگاه - DVT-0001",
    )

    name = Column(
        String(200), nullable=False, index=True,
        comment="نام دستگاه",
    )

    # نوع دستگاه — Lookup
    template_type = Column(
        String(50), nullable=True,
        comment="کد Lookup نوع دستگاه",
    )

    revision_no = Column(
        Integer, nullable=False, default=1,
        comment="شماره Revision",
    )

    status = Column(
        String(20), nullable=False,
        default=DeviceTemplateStatus.DRAFT.value,
        server_default="draft",
        index=True,
        comment="وضعیت",
    )

    description    = Column(Text, nullable=True, comment="توضیحات")
    technical_notes = Column(Text, nullable=True, comment="نکات مهندسی")

    # واحد اندازه‌گیری اصلی — Lookup
    default_uom = Column(
        String(20), nullable=True, default="pcs",
        comment="کد Lookup واحد",
    )

    estimated_weight = Column(
        Numeric(10, 3), nullable=True,
        comment="وزن تقریبی (کیلوگرم)",
    )

    estimated_cycle_time = Column(
        Integer, nullable=True,
        comment="زمان ساخت استاندارد (دقیقه)",
    )

    is_active = Column(
        Boolean, nullable=False,
        default=True, server_default="true",
    )

    approved_by_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    approved_at = Column(DateTime(timezone=True), nullable=True)

    created_by_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── Relationships ──────────────────────────────────────────────
    approved_by = relationship(
        "User",
        foreign_keys=[approved_by_id],
        lazy="select",
    )
    created_by = relationship(
        "User",
        foreign_keys=[created_by_id],
        lazy="select",
    )
    bom_headers = relationship(
        "BOMHeader",
        back_populates="device_template",
        lazy="select",
        cascade="all, delete-orphan",
    )
    # routing_headers بعداً اضافه میشه وقتی مدل ساخته شد

    def __repr__(self) -> str:
        return (
            f"<DeviceTemplate("
            f"id={self.id}, "
            f"code='{self.code}', "
            f"name='{self.name}', "
            f"rev={self.revision_no})>"
        )