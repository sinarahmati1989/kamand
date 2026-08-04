"""
Kamand - Department Enums
"""
from enum import Enum


class DepartmentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

    @property
    def label(self) -> str:
        return {
            "active": "فعال",
            "inactive": "غیرفعال",
        }[self.value]