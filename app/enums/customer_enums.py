"""
Kamand - Customer Enumerations
انواع شمارشی مربوط به مشتریان
"""

from enum import Enum


class CustomerStatus(str, Enum):
    """وضعیت مشتری"""
    ACTIVE = "active"
    INACTIVE = "inactive"

    @property
    def label(self) -> str:
        labels = {
            "active": "فعال",
            "inactive": "غیرفعال",
        }
        return labels[self.value]