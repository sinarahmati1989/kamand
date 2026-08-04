"""
Access Control
مدیریت دسترسی کاربر فعلی
"""

import logging
from typing import Optional
from dataclasses import dataclass

from app.enums.permissions import Permission, has_permission


logger = logging.getLogger(__name__)


@dataclass
class CurrentUser:
    """اطلاعات کاربر فعلی (session)"""
    id: int
    username: str
    full_name: str
    role: str
    is_active: bool
    
    def can(self, permission: Permission) -> bool:
        """آیا این کاربر دسترسی داره؟"""
        return has_permission(self.role, permission)
    
    def is_admin(self) -> bool:
        return self.role == "admin"


class AccessControl:
    """مدیریت Session کاربر فعلی (Singleton)"""
    
    _current_user: Optional[CurrentUser] = None
    
    @classmethod
    def set_current_user(cls, user: CurrentUser) -> None:
        cls._current_user = user
        logger.info(f"Current user set: {user.username} ({user.role})")
    
    @classmethod
    def get_current_user(cls) -> Optional[CurrentUser]:
        return cls._current_user
    
    @classmethod
    def clear(cls) -> None:
        if cls._current_user:
            logger.info(f"Current user cleared: {cls._current_user.username}")
        cls._current_user = None
    
    @classmethod
    def is_logged_in(cls) -> bool:
        return cls._current_user is not None
    
    @classmethod
    def can(cls, permission: Permission) -> bool:
        """چک سریع دسترسی"""
        if not cls._current_user:
            return False
        return cls._current_user.can(permission)