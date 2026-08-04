"""
Kamand - Machine Enums
"""
from enum import Enum


class MachineStatus(str, Enum):
    ACTIVE      = "active"
    INACTIVE    = "inactive"
    MAINTENANCE = "maintenance"
    BROKEN      = "broken"

    @property
    def label(self) -> str:
        return {
            "active":      "فعال",
            "inactive":    "غیرفعال",
            "maintenance": "در تعمیر",
            "broken":      "خراب",
        }[self.value]