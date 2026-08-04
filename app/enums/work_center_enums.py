"""
Kamand - Work Center Enums
"""
from enum import Enum


class WorkCenterStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

    @property
    def label(self) -> str:
        return {
            "active": "فعال",
            "inactive": "غیرفعال",
        }[self.value]