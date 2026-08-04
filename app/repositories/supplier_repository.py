"""
Repository تأمین‌کننده
"""
from typing import Optional, List
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from app.repositories.base_repository import BaseRepository
from app.models.supplier import Supplier


class SupplierRepository(BaseRepository[Supplier]):
    """Repository برای عملیات دیتابیس تأمین‌کنندگان"""

    def __init__(self, session: Session):
        super().__init__(session, Supplier)

    def get_all(self) -> List[Supplier]:
        """همه تأمین‌کنندگان"""
        return self._session.query(Supplier).order_by(Supplier.name).all()

    def get_by_code(self, code: str) -> Optional[Supplier]:
        """پیدا کردن با کد"""
        return self._session.query(Supplier).filter(
            Supplier.code == code
        ).first()

    def find_by_name(self, name: str) -> Optional[Supplier]:
        """پیدا کردن با نام (case-insensitive)"""
        return (
            self._session.query(Supplier)
            .filter(func.lower(Supplier.name) == name.lower())
            .first()
        )

    def search(self, keyword: str) -> List[Supplier]:
        """جستجو در نام، نام تجاری، تلفن، ایمیل، کد"""
        kw = f"%{keyword}%"
        return (
            self._session.query(Supplier)
            .filter(or_(
                Supplier.name.ilike(kw),
                Supplier.trade_name.ilike(kw),
                Supplier.mobile.ilike(kw),
                Supplier.phone.ilike(kw),
                Supplier.email.ilike(kw),
                Supplier.code.ilike(kw),
            ))
            .order_by(Supplier.name)
            .all()
        )

    def get_max_code_number(self) -> int:
        """بزرگ‌ترین شماره کد تولید‌شده"""
        suppliers = self._session.query(Supplier.code).all()
        max_num = 0
        for (code,) in suppliers:
            if code and code.startswith("SUP-"):
                try:
                    num = int(code.split("-")[1])
                    if num > max_num:
                        max_num = num
                except (ValueError, IndexError):
                    continue
        return max_num