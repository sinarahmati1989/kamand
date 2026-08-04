"""
Audit Service
ثبت لاگ فعالیت‌های حساس
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


audit_logger = logging.getLogger("audit")


class AuditService:
    """سرویس ثبت لاگ فعالیت‌ها"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def log(
        self,
        action: str,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """ثبت یک لاگ"""
        
        log = AuditLog(
            user_id=user_id,
            username=username,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=ip_address,
        )
        
        self.session.add(log)
        self.session.flush()
        
        # لاگ در فایل audit.log
        audit_logger.info(
            f"[{action}] user={username or 'N/A'} "
            f"entity={entity_type}:{entity_id} details={details}"
        )
        
        return log
    
    def log_login_success(self, user_id: int, username: str) -> None:
        self.log(
            action="LOGIN_SUCCESS",
            user_id=user_id,
            username=username,
            details="ورود موفق",
        )
    
    def log_login_failed(self, username: str, reason: str) -> None:
        self.log(
            action="LOGIN_FAILED",
            username=username,
            details=f"ورود ناموفق: {reason}",
        )
    
    def log_logout(self, user_id: int, username: str) -> None:
        self.log(
            action="LOGOUT",
            user_id=user_id,
            username=username,
            details="خروج",
        )