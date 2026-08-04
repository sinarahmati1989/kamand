"""
UserService — Business Logic مدیریت کاربران
"""
from sqlalchemy.orm import Session
import logging

from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password
from app.core.exceptions import (
    UserNotFoundError,
    DuplicateUsernameError,
    ValidationError,
)
from app.schemas.user_schema import (
    UserCreateDTO,
    UserUpdateDTO,
    UserReadDTO,
    ChangePasswordDTO,
)
from app.validators.user_validator import UserValidator
from app.models.user import User

logger = logging.getLogger(__name__)


class UserService:

    def __init__(self, session: Session):
        self._session = session
        self._repo = UserRepository(session)

    # ─────────────────────────── Read ────────────────────────────────

    def get_all_users(self) -> list[UserReadDTO]:
        users = self._repo.get_all()
        return [self._to_dto(u) for u in users]

    def get_user_by_id(self, user_id: int) -> UserReadDTO:
        user = self._repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"کاربر با شناسه {user_id} یافت نشد")
        return self._to_dto(user)

    # ─────────────────────────── Create ──────────────────────────────

    def create_user(self, dto: UserCreateDTO) -> UserReadDTO:
        if self._repo.get_by_username(dto.username):
            raise DuplicateUsernameError(
                f"نام کاربری «{dto.username}» قبلاً ثبت شده است"
            )

        UserValidator.validate_username(dto.username)
        UserValidator.validate_password(dto.password)
        if dto.email:
            UserValidator.validate_email(dto.email)

        user = User(
            username=dto.username,
            full_name=dto.full_name,
            email=dto.email,
            password_hash=hash_password(dto.password),
            role=dto.role,
            is_active=True,
        )
        created = self._repo.create(user)
        logger.info(f"کاربر جدید ساخته شد: {dto.username}")
        return self._to_dto(created)

    # ─────────────────────────── Update ──────────────────────────────

    def update_user(self, user_id: int, dto: UserUpdateDTO) -> UserReadDTO:
        user = self._repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"کاربر با شناسه {user_id} یافت نشد")

        if dto.full_name is not None:
            user.full_name = dto.full_name
        if dto.email is not None:
            UserValidator.validate_email(dto.email)
            user.email = dto.email
        if dto.role is not None:
            user.role = dto.role
        if dto.is_active is not None:
            user.is_active = dto.is_active

        updated = self._repo.update(user)
        logger.info(f"کاربر {user_id} ویرایش شد")
        return self._to_dto(updated)

    # ─────────────────────────── Deactivate ──────────────────────────

    def deactivate_user(self, user_id: int) -> UserReadDTO:
        user = self._repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"کاربر با شناسه {user_id} یافت نشد")

        user.is_active = False
        updated = self._repo.update(user)
        logger.info(f"کاربر {user_id} غیرفعال شد")
        return self._to_dto(updated)

    # ─────────────────────────── Password ────────────────────────────

    def change_password(self, user_id: int, dto: ChangePasswordDTO):
        user = self._repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"کاربر با شناسه {user_id} یافت نشد")

        if not verify_password(dto.old_password, user.password_hash):
            raise ValidationError("رمز عبور فعلی اشتباه است")

        UserValidator.validate_password(dto.new_password)
        user.password_hash = hash_password(dto.new_password)
        self._repo.update(user)
        logger.info(f"رمز عبور کاربر {user_id} تغییر کرد")

    # ─────────────────────────── Mapper ──────────────────────────────

    @staticmethod
    def _to_dto(user: User) -> UserReadDTO:
        """تبدیل Model به DTO با استفاده از from_attributes"""
        return UserReadDTO.model_validate(user)