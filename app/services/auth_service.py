"""
Auth Service
منطق لاگین/لاگ‌اوت
"""

import logging
from app.database.session import get_session, SessionLocal
from app.repositories.user_repository import UserRepository
from app.services.audit_service import AuditService
from app.core.security import verify_password
from app.core.exceptions import AuthenticationError
from app.core.access_control import AccessControl, CurrentUser
from app.validators.user_validator import UserValidator
from app.schemas.user_schema import UserLoginDTO, UserReadDTO


logger = logging.getLogger(__name__)


def _write_audit(action_fn):
    """اجرای audit log در session جداگانه — بدون تأثیر rollback"""
    session = SessionLocal()
    try:
        audit = AuditService(session)
        action_fn(audit)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Audit log failed: {e}")
    finally:
        session.close()


class AuthService:
    """سرویس احراز هویت"""
    
    def login(self, dto: UserLoginDTO) -> UserReadDTO:
        """
        ورود کاربر
        
        Raises:
            ValidationError: اگه ورودی نامعتبر
            AuthenticationError: اگه کاربر/پسورد اشتباه
        """
        # 1. Validation
        UserValidator.validate_username(dto.username)
        UserValidator.validate_password(dto.password)
        
        # 2. جستجو در DB
        with get_session() as session:
            repo = UserRepository(session)
            user = repo.get_by_username(dto.username.strip())
            
            # کاربر پیدا نشد
            if not user:
                _write_audit(lambda a: a.log_login_failed(dto.username, "کاربر یافت نشد"))
                logger.warning(f"Login failed — user not found: {dto.username}")
                raise AuthenticationError("نام کاربری یا پسورد اشتباه است")
            
            # کاربر غیرفعال
            if not user.is_active:
                _write_audit(lambda a: a.log_login_failed(dto.username, "کاربر غیرفعال"))
                logger.warning(f"Login failed — inactive user: {dto.username}")
                raise AuthenticationError("این کاربر غیرفعال است")
            
            # چک پسورد
            if not verify_password(dto.password, user.password_hash):
                _write_audit(lambda a: a.log_login_failed(dto.username, "پسورد اشتباه"))
                logger.warning(f"Login failed — wrong password: {dto.username}")
                raise AuthenticationError("نام کاربری یا پسورد اشتباه است")
            
            # ✅ موفق
            uid, uname = user.id, user.username
            dto_out = UserReadDTO.model_validate(user)
            
            # ست کردن session
            AccessControl.set_current_user(CurrentUser(
                id=user.id,
                username=user.username,
                full_name=user.full_name,
                role=user.role,
                is_active=user.is_active,
            ))
        
        # audit در session جدا
        _write_audit(lambda a: a.log_login_success(uid, uname))
        logger.info(f"Login SUCCESS: {uname}")
        return dto_out
    
    def logout(self) -> None:
        """خروج کاربر"""
        current = AccessControl.get_current_user()
        if not current:
            return
        
        _write_audit(lambda a: a.log_logout(current.id, current.username))
        logger.info(f"Logout: {current.username}")
        AccessControl.clear()