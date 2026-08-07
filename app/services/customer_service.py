"""
Kamand - Customer Service
Business Logic + Auto-code generation
"""
import logging
import re

from sqlalchemy.orm import Session

from app.repositories.customer_repository import CustomerRepository
from app.models.customer import Customer
from app.schemas.customer_schema import (
    CustomerCreateDTO,
    CustomerUpdateDTO,
    CustomerReadDTO,
)
from app.enums.customer_enums import CustomerStatus
from app.core.exceptions import NotFoundError, DuplicateError

logger = logging.getLogger(__name__)


CODE_PREFIX = "CUS"
CODE_PATTERN = re.compile(rf"^{CODE_PREFIX}-(\d+)$")


class CustomerService:
    """سرویس مدیریت مشتریان"""

    def __init__(self, session: Session):
        self._repo = CustomerRepository(session)

    # ─── Private ───

    def _to_dto(self, customer: Customer) -> CustomerReadDTO:
        return CustomerReadDTO.model_validate(customer)

    def _find_or_raise(self, customer_id: int) -> Customer:
        customer = self._repo.get_by_id(customer_id)
        if not customer:
            raise NotFoundError(
                f"مشتری با شناسه {customer_id} یافت نشد"
            )
        return customer

    def _normalize_status(self, value) -> str:
        if isinstance(value, CustomerStatus):
            value = value.value
        valid_values = {st.value for st in CustomerStatus}
        if value not in valid_values:
            raise ValueError("وضعیت انتخاب‌شده معتبر نیست")
        return value

    def _generate_next_code(self) -> str:
        """تولید خودکار کد — CUS-0001, CUS-0002, ..."""
        last_code = self._repo.get_last_code()
        if not last_code:
            return f"{CODE_PREFIX}-0001"

        match = CODE_PATTERN.match(last_code)
        if not match:
            return f"{CODE_PREFIX}-0001"

        next_num = int(match.group(1)) + 1
        return f"{CODE_PREFIX}-{next_num:04d}"

    # ─── Read ───

    def get_all(self) -> list[CustomerReadDTO]:
        return [self._to_dto(c) for c in self._repo.get_all_ordered()]

    def get_active(self) -> list[CustomerReadDTO]:
        return [self._to_dto(c) for c in self._repo.get_active()]

    def get_by_id(self, customer_id: int) -> CustomerReadDTO:
        return self._to_dto(self._find_or_raise(customer_id))

    def search(self, keyword: str) -> list[CustomerReadDTO]:
        if not keyword or not keyword.strip():
            return self.get_all()
        return [
            self._to_dto(c) for c in self._repo.search(keyword.strip())
        ]

    # ─── Write ───

    def create(self, dto: CustomerCreateDTO) -> CustomerReadDTO:
        """ایجاد مشتری جدید — با Auto-code"""
        # نام تکراری؟
        if self._repo.find_by_name(dto.name):
            raise DuplicateError(
                f"مشتری با نام «{dto.name}» قبلاً ثبت شده است"
            )

        # کد
        code = dto.code
        if code:
            # کاربر دستی وارد کرده
            if self._repo.find_by_code(code):
                raise DuplicateError(
                    f"کد «{code}» قبلاً استفاده شده است"
                )
        else:
            code = self._generate_next_code()

        customer = Customer(
            code=code,
            name=dto.name,
            trade_name=dto.trade_name,
            customer_type=dto.customer_type,
            tier=dto.tier or "b",
            status=CustomerStatus.ACTIVE.value,
            national_id=dto.national_id,
            cooperation_start=dto.cooperation_start,
            notes=dto.notes,
            contact_name=dto.contact_name,
            contact_position=dto.contact_position,
            contact_mobile=dto.contact_mobile,
            phone=dto.phone,
            mobile=dto.mobile,
            email=dto.email,
            website=dto.website,
            province=dto.province,
            city=dto.city,
            address=dto.address,
            postal_code=dto.postal_code,
            payment_terms=dto.payment_terms,
            currency=dto.currency or "irr",
            credit_days=dto.credit_days,
            credit_limit=dto.credit_limit,
            description=dto.description,
        )
        created = self._repo.create(customer)
        logger.info(
            f"مشتری جدید: {created.code} - {created.name} "
            f"(ID={created.id})"
        )
        return self._to_dto(created)

    def update(
        self, customer_id: int, dto: CustomerUpdateDTO
    ) -> CustomerReadDTO:
        """ویرایش مشتری"""
        customer = self._find_or_raise(customer_id)

        if dto.name and dto.name != customer.name:
            existing = self._repo.find_by_name(dto.name)
            if existing and existing.id != customer_id:
                raise DuplicateError(
                    f"مشتری با نام «{dto.name}» قبلاً ثبت شده است"
                )

        update_data = dto.model_dump(exclude_none=True)

        if "status" in update_data:
            update_data["status"] = self._normalize_status(
                update_data["status"]
            )

        for field, value in update_data.items():
            setattr(customer, field, value)

        updated = self._repo.update(customer)
        logger.info(
            f"مشتری ویرایش شد: {updated.name} (ID={customer_id})"
        )
        return self._to_dto(updated)

    def change_status(
        self, customer_id: int, new_status
    ) -> CustomerReadDTO:
        """تغییر وضعیت مشتری"""
        customer = self._find_or_raise(customer_id)
        normalized = self._normalize_status(new_status)
        customer.status = normalized
        updated = self._repo.update(customer)
        logger.info(
            f"وضعیت مشتری {updated.name} → {normalized}"
        )
        return self._to_dto(updated)

    # ─── Stats ───

    def get_stats(self) -> dict:
        """آمار مشتریان"""
        all_customers = self._repo.get_all_ordered()
        active_count = sum(
            1 for c in all_customers
            if c.status == CustomerStatus.ACTIVE.value
        )
        return {
            "total": len(all_customers),
            "active": active_count,
            "inactive": len(all_customers) - active_count,
        }