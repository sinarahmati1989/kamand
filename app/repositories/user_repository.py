"""
User Repository
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):

    def __init__(self, session: Session):
        super().__init__(session, User)

    def get_by_username(self, username: str) -> Optional[User]:
        """جستجو با username"""
        stmt = select(User).where(User.username == username)
        return self._session.execute(stmt).scalar_one_or_none()

    def username_exists(self, username: str) -> bool:
        """آیا username قبلاً گرفته شده؟"""
        return self.get_by_username(username) is not None

    def get_active_users(self) -> list[User]:
        """کاربران فعال"""
        stmt = select(User).where(User.is_active == True)
        return list(self._session.execute(stmt).scalars().all())