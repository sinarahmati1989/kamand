"""
Kamand - Manufacturing Operation Enumerations
انواع شمارشی مربوط به عملیات ساخت
"""

from enum import Enum


class OperationStatus(str, Enum):
    """وضعیت عملیات"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

    @property
    def label(self) -> str:
        labels = {
            "active": "فعال",
            "inactive": "غیرفعال",
            "archived": "بایگانی",
        }
        return labels[self.value]