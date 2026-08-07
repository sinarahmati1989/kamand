"""
Kamand - Routing Models
RoutingHeader + RoutingOperation
هم‌الگوی BOM
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import (
    Boolean, Column, Date, DateTime,
    ForeignKey, Integer, Numeric,
    String, Text, UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin


class RoutingHeader(Base, TimestampMixin):
    """سرخط Routing — مسیر ساخت یک دستگاه"""

    __tablename__ = "routing_headers"

    id = Column(Integer, primary_key=True, autoincrement=True)

    device_template_id = Column(
        Integer,
        ForeignKey("device_templates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="تعریف دستگاه",
    )

    revision_no = Column(
        Integer, nullable=False, default=1,
        comment="شماره Revision",
    )

    status = Column(
        String(20), nullable=False,
        default="draft",
        server_default="draft",
        comment="وضعیت: draft / approved / obsolete",
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
            name="uq_routing_template_revision",
        ),
    )

    # ── Relationships ──────────────────────────────────────────────
    device_template = relationship(
        "DeviceTemplate",
        back_populates="routing_headers",
    )
    routing_operations = relationship(
        "RoutingOperation",
        back_populates="routing_header",
        cascade="all, delete-orphan",
        order_by="RoutingOperation.step_no",
        lazy="select",
    )
    approved_by = relationship(
        "User",
        foreign_keys=[approved_by_id],
        lazy="select",
    )

    @property
    def routing_code(self) -> str:
        if self.device_template:
            return f"ROU-{self.device_template.code}-R{self.revision_no}"
        return f"ROU-???-R{self.revision_no}"

    @property
    def total_setup_time(self) -> float:
        """جمع زمان آماده‌سازی (دقیقه)"""
        return sum(
            float(op.setup_time_min or 0)
            for op in (self.routing_operations or [])
        )

    @property
    def total_cycle_time(self) -> float:
        """جمع زمان سیکل (دقیقه)"""
        return sum(
            float(op.cycle_time_min or 0)
            for op in (self.routing_operations or [])
        )

    @property
    def total_time(self) -> float:
        """جمع کل زمان ساخت (دقیقه)"""
        return self.total_setup_time + self.total_cycle_time

    def __repr__(self) -> str:
        return (
            f"<RoutingHeader("
            f"id={self.id}, "
            f"template_id={self.device_template_id}, "
            f"rev={self.revision_no}, "
            f"status='{self.status}')>"
        )


class RoutingOperation(Base, TimestampMixin):
    """یک عملیات در مسیر ساخت"""

    __tablename__ = "routing_operations"

    id = Column(Integer, primary_key=True, autoincrement=True)

    routing_header_id = Column(
        Integer,
        ForeignKey("routing_headers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    step_no = Column(
        Integer, nullable=False, default=10,
        comment="شماره مرحله (10, 20, 30, ...)",
    )

    # ── عملیات ─────────────────────────────────────────────────────
    operation_id = Column(
        Integer,
        ForeignKey("manufacturing_operations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="نوع عملیات",
    )

    # ── محل انجام ──────────────────────────────────────────────────
    department_id = Column(
        Integer,
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
        comment="دپارتمان",
    )

    work_center_id = Column(
        Integer,
        ForeignKey("work_centers.id", ondelete="SET NULL"),
        nullable=True,
        comment="مرکز کار",
    )

    machine_id = Column(
        Integer,
        ForeignKey("machines.id", ondelete="SET NULL"),
        nullable=True,
        comment="ماشین",
    )

    # ── زمان‌بندی ───────────────────────────────────────────────────
    setup_time_min = Column(
        Numeric(10, 2), nullable=True, default=0,
        comment="زمان آماده‌سازی (دقیقه)",
    )

    cycle_time_min = Column(
        Numeric(10, 2), nullable=True, default=0,
        comment="زمان سیکل (دقیقه)",
    )

    labor_count = Column(
        Integer, nullable=True, default=1,
        comment="تعداد نیروی کار",
    )

    # ── هزینه ──────────────────────────────────────────────────────
    hourly_rate = Column(
        Numeric(18, 2), nullable=True,
        comment="نرخ ساعتی ماشین/نیروی کار (ریال)",
    )

    # ── سایر ────────────────────────────────────────────────────────
    is_outsourced = Column(
        Boolean, nullable=False,
        default=False, server_default="false",
        comment="برون‌سپاری",
    )

    notes = Column(Text, nullable=True)

    # ── Relationships ──────────────────────────────────────────────
    routing_header = relationship(
        "RoutingHeader",
        back_populates="routing_operations",
    )
    operation = relationship(
        "ManufacturingOperation",
        foreign_keys=[operation_id],
        lazy="joined",
    )
    department = relationship(
        "Department",
        foreign_keys=[department_id],
        lazy="select",
    )
    work_center = relationship(
        "WorkCenter",
        foreign_keys=[work_center_id],
        lazy="select",
    )
    machine = relationship(
        "Machine",
        foreign_keys=[machine_id],
        lazy="select",
    )

    @property
    def estimated_cost(self) -> float:
        """هزینه تخمینی این عملیات (ریال)"""
        if not self.hourly_rate:
            return 0.0
        total_min = float(self.setup_time_min or 0) + float(self.cycle_time_min or 0)
        return (total_min / 60.0) * float(self.hourly_rate)

    def __repr__(self) -> str:
        return (
            f"<RoutingOperation("
            f"id={self.id}, "
            f"header={self.routing_header_id}, "
            f"step={self.step_no})>"
        )