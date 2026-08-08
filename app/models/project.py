"""
Kamand - Project Models
مدیریت پروژه‌های سفارش مشتری
Project ← ProjectDevice ← ProjectCost
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
from app.models.mixins import TimestampMixin


class Project(Base, TimestampMixin):
    """پروژه — سفارش مشتری"""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)

    project_no = Column(
        String(30), unique=True, nullable=False, index=True,
        comment="شماره پروژه — PRJ-0001",
    )
    name = Column(String(200), nullable=False, index=True)
    contract_no = Column(String(50), nullable=True)

    # ─── مشتری ───
    customer_id = Column(
        Integer,
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )

    # ─── وضعیت ───
    status = Column(
        String(20), nullable=False,
        default="draft", server_default="draft", index=True,
    )
    priority = Column(
        String(20), nullable=True, default="normal",
    )

    # ─── تاریخ‌ها ───
    start_date           = Column(Date, nullable=True)
    delivery_date        = Column(Date, nullable=True)
    actual_delivery_date = Column(Date, nullable=True)

    # ─── مالی ───
    contract_value = Column(Numeric(18, 2), nullable=True)
    currency       = Column(String(10), nullable=True, default="IRR")

    # ─── توضیحات ───
    description = Column(Text, nullable=True)
    notes       = Column(Text, nullable=True)

    # ─── کاربران ───
    created_by_id   = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    confirmed_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    confirmed_at    = Column(DateTime(timezone=True), nullable=True)
    is_active       = Column(Boolean, nullable=False, default=True, server_default="true")

    # ─── Relationships ───
    customer = relationship("Customer", foreign_keys=[customer_id], lazy="select")
    created_by  = relationship("User", foreign_keys=[created_by_id],  lazy="select")
    confirmed_by = relationship("User", foreign_keys=[confirmed_by_id], lazy="select")
    project_devices = relationship(
        "ProjectDevice",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="select",
        order_by="ProjectDevice.id",
    )
    project_costs = relationship(
        "ProjectCost",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="select",
    )

    # ─── Properties ───
    @property
    def total_devices(self) -> int:
        return sum(d.quantity for d in (self.project_devices or []))

    @property
    def estimated_cost(self) -> float:
        return sum(
            float(d.estimated_total_cost or 0)
            for d in (self.project_devices or [])
        )

    @property
    def estimated_sale_total(self) -> float:
        """جمع قیمت فروش همه دستگاه‌ها"""
        return sum(
            float(d.unit_price or 0) * d.quantity
            for d in (self.project_devices or [])
        )

    @property
    def status_label(self) -> str:
        return {
            "draft":         "پیش‌نویس",
            "confirmed":     "تأیید شده",
            "in_production": "در تولید",
            "delivered":     "تحویل داده شده",
            "cancelled":     "لغو شده",
        }.get(self.status, self.status)

    @property
    def priority_label(self) -> str:
        return {
            "low": "پایین", "normal": "عادی",
            "high": "بالا", "urgent": "فوری",
        }.get(self.priority, self.priority or "عادی")

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, no='{self.project_no}', status='{self.status}')>"


class ProjectDevice(Base, TimestampMixin):
    """دستگاه‌های یک پروژه"""

    __tablename__ = "project_devices"

    id = Column(Integer, primary_key=True, autoincrement=True)

    project_id = Column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    device_template_id = Column(
        Integer, ForeignKey("device_templates.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )

    # ─── تعداد و قیمت فروش نهایی ───
    quantity   = Column(Integer, nullable=False, default=1)
    unit_price = Column(
        Numeric(18, 2), nullable=True,
        comment="قیمت فروش نهایی واحد — تعیین شده توسط کاربر",
    )

    # ─── مراجع مهندسی ───
    bom_header_id     = Column(Integer, ForeignKey("bom_headers.id",     ondelete="SET NULL"), nullable=True)
    routing_header_id = Column(Integer, ForeignKey("routing_headers.id", ondelete="SET NULL"), nullable=True)

    # ─── Snapshot هزینه‌یابی (سطح ۱+۲+۳) ───
    material_unit_cost      = Column(Numeric(18, 2), nullable=True, comment="هزینه مواد واحد — از BOM")
    labor_unit_cost         = Column(Numeric(18, 2), nullable=True, comment="هزینه کار واحد — از Routing")
    direct_unit_cost        = Column(Numeric(18, 2), nullable=True, comment="هزینه مستقیم = مواد + کار")
    overhead_percent        = Column(Numeric(5,  2), nullable=True, comment="درصد سربار — snapshot از SystemSettings")
    overhead_unit_cost      = Column(Numeric(18, 2), nullable=True, comment="هزینه سربار واحد")
    estimated_unit_cost     = Column(Numeric(18, 2), nullable=True, comment="هزینه تمام‌شده واحد = مستقیم + سربار")
    markup_percent          = Column(Numeric(5,  2), nullable=True, comment="درصد markup — snapshot از SystemSettings")
    suggested_sale_unit_price = Column(Numeric(18, 2), nullable=True, comment="قیمت پیشنهادی فروش واحد")

    # ─── Audit هزینه‌یابی ───
    bom_revision_no     = Column(Integer, nullable=True, comment="شماره revision BOM در زمان محاسبه")
    routing_revision_no = Column(Integer, nullable=True, comment="شماره revision Routing در زمان محاسبه")
    cost_version        = Column(Integer, nullable=False, default=0, server_default="0")
    cost_calculated_at  = Column(DateTime(timezone=True), nullable=True)
    cost_is_locked      = Column(
        Boolean, nullable=False, default=False, server_default="false",
        comment="قفل بعد از in_production — محاسبه مجدد ممنوع",
    )

    # ─── وضعیت تولید ───
    production_status = Column(String(20), nullable=True, default="pending")
    notes             = Column(Text, nullable=True)

    # ─── Relationships ───
    project = relationship("Project", back_populates="project_devices")
    device_template = relationship(
        "DeviceTemplate", foreign_keys=[device_template_id], lazy="joined"
    )
    bom_header     = relationship("BOMHeader",     foreign_keys=[bom_header_id],     lazy="select")
    routing_header = relationship("RoutingHeader", foreign_keys=[routing_header_id], lazy="select")

    # ─── Properties ───
    @property
    def estimated_total_cost(self) -> float:
        """هزینه تمام‌شده کل این ردیف"""
        if self.estimated_unit_cost:
            return float(self.estimated_unit_cost) * self.quantity
        return 0.0

    @property
    def sale_total(self) -> float:
        """جمع فروش این ردیف"""
        if self.unit_price:
            return float(self.unit_price) * self.quantity
        return 0.0

    @property
    def expected_profit(self) -> float:
        """سود مورد انتظار این ردیف"""
        return self.sale_total - self.estimated_total_cost

    @property
    def cost_is_complete(self) -> bool:
        """آیا هزینه‌یابی کامل شده؟"""
        return self.estimated_unit_cost is not None

    @property
    def production_status_label(self) -> str:
        return {
            "pending":     "در انتظار",
            "in_progress": "در حال تولید",
            "completed":   "تکمیل شده",
            "on_hold":     "معلق",
        }.get(self.production_status, self.production_status or "در انتظار")

    def __repr__(self) -> str:
        return (
            f"<ProjectDevice(id={self.id}, "
            f"project_id={self.project_id}, "
            f"template_id={self.device_template_id}, "
            f"qty={self.quantity})>"
        )


class ProjectCost(Base, TimestampMixin):
    """هزینه‌های واقعی یک پروژه"""

    __tablename__ = "project_costs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    project_id = Column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    cost_type_id = Column(
        Integer, ForeignKey("cost_types.id", ondelete="RESTRICT"),
        nullable=False,
    )
    amount      = Column(Numeric(18, 2), nullable=False, default=0)
    description = Column(Text, nullable=True)
    cost_date   = Column(Date, nullable=True)

    recorded_by_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # ─── Relationships ───
    project     = relationship("Project",   back_populates="project_costs")
    cost_type   = relationship("CostType",  foreign_keys=[cost_type_id],   lazy="joined")
    recorded_by = relationship("User",      foreign_keys=[recorded_by_id], lazy="select")

    def __repr__(self) -> str:
        return f"<ProjectCost(id={self.id}, project_id={self.project_id}, amount={self.amount})>"