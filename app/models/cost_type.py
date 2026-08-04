"""
Kamand - Cost Type Model
مدل نوع هزینه
"""

from sqlalchemy import (
    Column, Integer, String, Text, Boolean,
    Numeric, ForeignKey
)
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin
from app.enums.cost_enums import CostStatus


class CostType(Base, TimestampMixin):
    """مدل نوع هزینه"""

    __tablename__ = "cost_types"

    id = Column(Integer, primary_key=True, autoincrement=True)

    code = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        comment="کد نوع هزینه - مثل COST-0001"
    )

    name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="نام نوع هزینه"
    )

    category = Column(
        String(50),
        nullable=False,
        default="direct",
        index=True,
        comment="کد Lookup دسته‌بندی هزینه"
    )

    cost_behavior = Column(
        String(50),
        nullable=False,
        default="variable",
        comment="کد Lookup رفتار هزینه"
    )

    unit = Column(
        String(50),
        nullable=False,
        default="rial",
        comment="کد Lookup واحد هزینه"
    )

    default_amount = Column(
        Numeric(18, 2),
        nullable=True,
        default=None,
        comment="مبلغ پیش‌فرض"
    )

    allocation_method = Column(
        String(50),
        nullable=False,
        default="direct",
        comment="کد Lookup روش تخصیص هزینه"
    )

    account_code = Column(
        String(30),
        nullable=True,
        default=None,
        comment="کد حسابداری"
    )

    taxable = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        comment="مشمول مالیات"
    )

    parent_id = Column(
        Integer,
        ForeignKey("cost_types.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
        comment="نوع هزینه والد"
    )

    description = Column(
        Text,
        nullable=True,
        default=None,
        comment="توضیحات"
    )

    status = Column(
        String(20),
        nullable=False,
        default=CostStatus.ACTIVE.value,
        server_default="active",
        index=True,
        comment="وضعیت"
    )

    parent = relationship(
        "CostType",
        remote_side=[id],
        backref="children",
        lazy="select"
    )

    def __repr__(self):
        return f"<CostType(id={self.id}, code='{self.code}', name='{self.name}')>"