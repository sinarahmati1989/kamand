"""
Permissions
دسترسی‌های سیستم
"""

from enum import Enum
from app.enums.roles import UserRole


class Permission(str, Enum):
    """دسترسی‌های ریز سیستم"""
    
    # User Management
    USER_VIEW = "user.view"
    USER_CREATE = "user.create"
    USER_UPDATE = "user.update"
    USER_DELETE = "user.delete"
    
    # Device Management (بعداً)
    DEVICE_VIEW = "device.view"
    DEVICE_CREATE = "device.create"
    DEVICE_UPDATE = "device.update"
    DEVICE_DELETE = "device.delete"
    
    # Project Management (بعداً)
    PROJECT_VIEW = "project.view"
    PROJECT_CREATE = "project.create"
    PROJECT_UPDATE = "project.update"
    PROJECT_DELETE = "project.delete"
    PROJECT_APPROVE = "project.approve"
    
    # Reports
    REPORT_VIEW = "report.view"
    REPORT_EXPORT = "report.export"
    
    # Audit
    AUDIT_VIEW = "audit.view"


# ══════════════════════════════════
# نقشه دسترسی‌ها بر اساس نقش
# ══════════════════════════════════
ROLE_PERMISSIONS: dict[str, set[Permission]] = {
    
    # ✅ Admin — همه‌چی
    UserRole.ADMIN.value: set(Permission),
    
    # ✅ Manager — همه به جز حذف کاربر
    UserRole.MANAGER.value: {
        Permission.USER_VIEW,
        Permission.USER_CREATE,
        Permission.USER_UPDATE,
        Permission.DEVICE_VIEW,
        Permission.DEVICE_CREATE,
        Permission.DEVICE_UPDATE,
        Permission.PROJECT_VIEW,
        Permission.PROJECT_CREATE,
        Permission.PROJECT_UPDATE,
        Permission.PROJECT_APPROVE,
        Permission.REPORT_VIEW,
        Permission.REPORT_EXPORT,
        Permission.AUDIT_VIEW,
    },
    
    # ✅ Operator — ورود داده
    UserRole.OPERATOR.value: {
        Permission.DEVICE_VIEW,
        Permission.DEVICE_CREATE,
        Permission.DEVICE_UPDATE,
        Permission.PROJECT_VIEW,
        Permission.PROJECT_CREATE,
        Permission.PROJECT_UPDATE,
        Permission.REPORT_VIEW,
    },
    
    # ✅ Viewer — فقط مشاهده
    UserRole.VIEWER.value: {
        Permission.DEVICE_VIEW,
        Permission.PROJECT_VIEW,
        Permission.REPORT_VIEW,
    },
}


def has_permission(role: str, permission: Permission) -> bool:
    """چک دسترسی یه نقش به یه permission"""
    return permission in ROLE_PERMISSIONS.get(role, set())