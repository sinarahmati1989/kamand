"""
User Roles
"""

from enum import Enum


class UserRole(str, Enum):
    """نقش‌های کاربری"""
    
    ADMIN = "admin"           # مدیر کل — همه‌ی دسترسی‌ها
    MANAGER = "manager"       # مدیر — تأیید و گزارش
    OPERATOR = "operator"     # اپراتور — ورود داده
    VIEWER = "viewer"         # ناظر — فقط مشاهده
    
    @classmethod
    def choices(cls):
        return [(role.value, role.name) for role in cls]