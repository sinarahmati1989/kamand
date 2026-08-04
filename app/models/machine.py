"""
Kamand - Machine Model
مدل ماشین‌آلات
"""
from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, Date
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin
from app.enums.machine_enums import MachineStatus


class Machine(Base, TimestampMixin):
    """مدل ماشین‌آلات"""

    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, autoincrement=True)

    code = Column(
        String(20), unique=True, nullable=False, index=True,
        comment="کد ماشین - مثل MCH-001"
    )

    name = Column(
        String(150), nullable=False, index=True,
        comment="نام ماشین"
    )

    machine_type = Column(
        String(50), nullable=True,
        comment="کد Lookup نوع ماشین"
    )

    brand = Column(
        String(100), nullable=True,
        comment="برند/سازنده"
    )

    model = Column(
        String(100), nullable=True,
        comment="مدل"
    )

    serial_number = Column(
        String(100), nullable=True,
        comment="شماره سریال"
    )

    manufacture_year = Column(
        Integer, nullable=True,
        comment="سال ساخت (میلادی)"
    )

    # موقعیت
    department_id = Column(
        Integer, ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True, index=True,
        comment="دپارتمان"
    )

    work_center_id = Column(
        Integer, ForeignKey("work_centers.id", ondelete="SET NULL"),
        nullable=True, index=True,
        comment="مرکز کار"
    )

    location = Column(
        String(150), nullable=True,
        comment="موقعیت دقیق در کارگاه"
    )

    # ظرفیت و نرخ
    capacity_per_hour = Column(
        Numeric(10, 2), nullable=True,
        comment="ظرفیت تولید در ساعت"
    )

    hourly_rate = Column(
        Numeric(18, 2), nullable=True,
        comment="نرخ ساعتی استفاده"
    )

    currency = Column(
        String(50), nullable=False, default="irr", server_default="irr",
        comment="کد Lookup ارز"
    )

    # نگهداری
    last_maintenance_date = Column(
        Date, nullable=True,
        comment="تاریخ آخرین سرویس"
    )

    next_maintenance_date = Column(
        Date, nullable=True,
        comment="تاریخ سرویس بعدی"
    )

    maintenance_interval_days = Column(
        Integer, nullable=True,
        comment="فاصله سرویس‌دهی (روز)"
    )

    # یادداشت‌ها
    technical_notes = Column(Text, nullable=True, comment="مشخصات فنی")
    notes = Column(Text, nullable=True, comment="یادداشت‌ها")

    status = Column(
        String(20), nullable=False,
        default=MachineStatus.ACTIVE.value,
        server_default="active",
        index=True,
        comment="وضعیت"
    )

    # Relationships
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

    def __repr__(self):
        return f"<Machine(id={self.id}, code='{self.code}', name='{self.name}')>"