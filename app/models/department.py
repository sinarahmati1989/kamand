"""
Kamand - Department Model
مدل دپارتمان/بخش کارگاه
"""
from sqlalchemy import Column, Integer, String, Text

from app.database.base import Base
from app.models.mixins import TimestampMixin
from app.enums.department_enums import DepartmentStatus


class Department(Base, TimestampMixin):
    """مدل دپارتمان"""

    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, autoincrement=True)

    code = Column(
        String(20), unique=True, nullable=False, index=True,
        comment="کد دپارتمان - مثل DEP-001"
    )

    name = Column(
        String(150), nullable=False, index=True,
        comment="نام دپارتمان"
    )

    department_type = Column(
        String(50), nullable=True,
        comment="کد Lookup نوع دپارتمان"
    )

    manager_name = Column(
        String(100), nullable=True,
        comment="نام مسئول/مدیر دپارتمان"
    )

    location = Column(
        String(150), nullable=True,
        comment="محل/موقعیت دپارتمان در کارگاه"
    )

    phone = Column(
        String(20), nullable=True,
        comment="تلفن داخلی"
    )

    notes = Column(Text, nullable=True, comment="یادداشت‌ها")

    status = Column(
        String(20), nullable=False,
        default=DepartmentStatus.ACTIVE.value,
        server_default="active",
        index=True,
        comment="وضعیت"
    )

    def __repr__(self):
        return f"<Department(id={self.id}, code='{self.code}', name='{self.name}')>"