"""
Kamand - Work Center Model
مدل مرکز کار
"""
from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin
from app.enums.work_center_enums import WorkCenterStatus


class WorkCenter(Base, TimestampMixin):
    """مدل مرکز کار"""

    __tablename__ = "work_centers"

    id = Column(Integer, primary_key=True, autoincrement=True)

    code = Column(
        String(20), unique=True, nullable=False, index=True,
        comment="کد مرکز کار - مثل WC-001"
    )

    name = Column(
        String(150), nullable=False, index=True,
        comment="نام مرکز کار"
    )

    department_id = Column(
        Integer, ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True, index=True,
        comment="دپارتمان مربوطه"
    )

    work_center_type = Column(
        String(50), nullable=True,
        comment="کد Lookup نوع مرکز کار"
    )

    capacity_per_hour = Column(
        Numeric(10, 2), nullable=True,
        comment="ظرفیت تولید در ساعت"
    )

    capacity_unit = Column(
        String(50), nullable=True, default="unit",
        comment="واحد ظرفیت (قطعه/کیلوگرم/...)"
    )

    shift_count = Column(
        Integer, nullable=False, default=1, server_default="1",
        comment="تعداد شیفت‌های کاری"
    )

    location = Column(
        String(150), nullable=True,
        comment="موقعیت در کارگاه"
    )

    notes = Column(Text, nullable=True, comment="یادداشت‌ها")

    status = Column(
        String(20), nullable=False,
        default=WorkCenterStatus.ACTIVE.value,
        server_default="active",
        index=True,
        comment="وضعیت"
    )

    # Relationship
    department = relationship(
        "Department",
        foreign_keys=[department_id],
        lazy="select",
    )

    def __repr__(self):
        return f"<WorkCenter(id={self.id}, code='{self.code}', name='{self.name}')>"