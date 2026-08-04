"""
Repository مشتریان — فقط CRUD، بدون Business Logic
"""
from sqlalchemy.orm import Session

from app.repositories.base_repository import BaseRepository
from app.models.customer import Customer
from app.enums.customer_enums import CustomerStatus


class CustomerRepository(BaseRepository[Customer]):
    """عملیات دیتابیس برای مشتریان"""

    def __init__(self, session: Session):
        super().__init__(session, Customer)

    def find_by_name(self, name: str) -> Customer | None:
        """جست‌وجوی دقیق بر اساس نام"""
        return (
            self._session.query(Customer)
            .filter(Customer.name == name)
            .first()
        )

    def search(self, keyword: str) -> list[Customer]:
        """جست‌وجو در نام، تلفن و ایمیل"""
        kw = f"%{keyword}%"
        return (
            self._session.query(Customer)
            .filter(
                Customer.name.ilike(kw)
                | Customer.phone.ilike(kw)
                | Customer.mobile.ilike(kw)
                | Customer.email.ilike(kw)
                | Customer.contact_name.ilike(kw)
            )
            .order_by(Customer.name)
            .all()
        )

    def get_all_ordered(self) -> list[Customer]:
        """همه مشتریان مرتب بر اساس نام"""
        return (
            self._session.query(Customer)
            .order_by(Customer.name)
            .all()
        )

    def get_active(self) -> list[Customer]:
        """فقط مشتریان فعال — برای Dropdown"""
        return (
            self._session.query(Customer)
            .filter(Customer.status == CustomerStatus.ACTIVE.value)
            .order_by(Customer.name)
            .all()
        )