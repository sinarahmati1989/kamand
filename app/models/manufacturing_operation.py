"""
Kamand - Manufacturing Operation Model
مدل عملیات ساخت
"""

from decimal import Decimal
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Numeric
)

from app.database.base import Base
from app.models.mixins import TimestampMixin
from app.enums.operation_enums import OperationStatus


class ManufacturingOperation(Base, TimestampMixin):
    """مدل عملیات ساخت"""

    __tablename__ = "manufacturing_operations"

    id = Column(Integer, primary_key=True, autoincrement=True)

    code = Column(
        String(20), unique=True, nullable=False, index=True,
        comment="کد عملیات - مثل OP-0001"
    )

    name = Column(
        String(150), nullable=False, index=True,
        comment="نام عملیات"
    )

    operation_type = Column(
        String(50), nullable=False, index=True,
        comment="کد Lookup نوع عملیات"
    )

    description = Column(Text, nullable=True, comment="توضیحات")

    # ویژگی‌ها
    is_outsourced = Column(
        Boolean, nullable=False, default=False, server_default="false",
        comment="برون‌سپاری می‌شود؟"
    )
    requires_qc = Column(
        Boolean, nullable=False, default=False, server_default="false",
        comment="نیاز به کنترل کیفیت دارد؟"
    )
    requires_machine = Column(
        Boolean, nullable=False, default=True, server_default="true",
        comment="نیاز به ماشین دارد؟ (اگر خیر، عملیات دستی است)"
    )
    is_bottleneck = Column(
        Boolean, nullable=False, default=False, server_default="false",
        comment="گلوگاه تولید است؟"
    )

    # زمان‌ها
    setup_time = Column(
        Numeric(10, 2), nullable=True,
        comment="زمان راه‌اندازی"
    )
    setup_time_unit = Column(
        String(50), nullable=False, default="minute", server_default="minute",
        comment="کد Lookup واحد زمان راه‌اندازی"
    )
    cycle_time = Column(
        Numeric(10, 2), nullable=True,
        comment="زمان تولید یک قطعه"
    )
    cycle_time_unit = Column(
        String(50), nullable=False, default="minute", server_default="minute",
        comment="کد Lookup واحد زمان تولید"
    )

    # ظرفیت
    capacity_per_hour = Column(
        Numeric(10, 2), nullable=True,
        comment="ظرفیت تولید در ساعت"
    )
    default_operator_count = Column(
        Integer, nullable=False, default=1, server_default="1",
        comment="تعداد اپراتور پیش‌فرض"
    )
    efficiency_percent = Column(
        Numeric(5, 2), nullable=True,
        comment="راندمان (%)"
    )
    oee_target = Column(
        Numeric(5, 2), nullable=True,
        comment="هدف OEE (%)"
    )

    # هزینه
    hourly_rate = Column(
        Numeric(18, 2), nullable=True,
        comment="نرخ ساعتی"
    )
    currency = Column(
        String(50), nullable=False, default="irr", server_default="irr",
        comment="کد Lookup ارز"
    )

    # مهارت
    skill_level = Column(
        String(50), nullable=True,
        comment="کد Lookup سطح مهارت"
    )
    required_skills_description = Column(
        Text, nullable=True,
        comment="توضیح مهارت‌های لازم"
    )

    # یادداشت‌ها
    required_tools = Column(Text, nullable=True, comment="ابزار لازم")
    safety_notes = Column(Text, nullable=True, comment="نکات ایمنی")
    notes = Column(Text, nullable=True, comment="یادداشت‌ها")

    # وضعیت
    status = Column(
        String(20), nullable=False,
        default=OperationStatus.ACTIVE.value,
        server_default="active",
        index=True,
        comment="وضعیت"
    )

    def __repr__(self):
        return f"<ManufacturingOperation(id={self.id}, code='{self.code}', name='{self.name}')>"