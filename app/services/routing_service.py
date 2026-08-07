"""
Kamand - Routing Service
منطق کسب‌وکار مسیر ساخت
"""
from typing import Optional
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.routing import RoutingHeader, RoutingOperation
from app.repositories.routing_repository import (
    RoutingHeaderRepository, RoutingOperationRepository
)
from app.enums.engineering_enums import RoutingStatus
import logging

logger = logging.getLogger(__name__)


class RoutingService:

    def __init__(self, session: Session):
        self.session = session
        self.header_repo = RoutingHeaderRepository(session)
        self.op_repo = RoutingOperationRepository(session)

    # ── RoutingHeader ──────────────────────────────────────────────

    def get_header_by_id(self, header_id: int) -> Optional[RoutingHeader]:
        return self.header_repo.get_by_id(header_id)

    def get_headers_by_template(self, device_template_id: int) -> list[RoutingHeader]:
        return self.header_repo.get_by_template(device_template_id)

    def get_with_operations(self, routing_header_id: int) -> Optional[RoutingHeader]:
        return self.header_repo.get_with_operations(routing_header_id)

    def create_header(
        self,
        device_template_id: int,
        revision_no: Optional[int] = None,
        notes: str = "",
    ) -> RoutingHeader:
        if revision_no is None:
            revision_no = self.header_repo.get_next_revision(device_template_id)

        if self.header_repo.exists_revision(device_template_id, revision_no):
            raise ValueError(
                f"Revision {revision_no} برای این تعریف دستگاه قبلاً ثبت شده است"
            )

        header = RoutingHeader(
            device_template_id=device_template_id,
            revision_no=revision_no,
            status=RoutingStatus.DRAFT.value,
            notes=notes,
        )
        return self.header_repo.create(header)

    def update_header(
        self,
        header_id: int,
        notes: str = "",
        status: Optional[str] = None,
    ) -> RoutingHeader:
        header = self.header_repo.get_by_id(header_id)
        if not header:
            raise ValueError("Routing یافت نشد")
        header.notes = notes
        if status:
            header.status = status
        return self.header_repo.update(header)

    def delete_header(self, header_id: int) -> None:
        header = self.header_repo.get_by_id(header_id)
        if not header:
            raise ValueError("Routing یافت نشد")
        if header.status == RoutingStatus.APPROVED.value:
            raise ValueError("Routing تأیید شده را نمی‌توان حذف کرد")
        self.header_repo.delete(header)

    def change_header_status(self, header_id: int, new_status: str) -> RoutingHeader:
        header = self.header_repo.get_by_id(header_id)
        if not header:
            raise ValueError("Routing یافت نشد")
        header.status = new_status
        return self.header_repo.update(header)

    # ── RoutingOperation ───────────────────────────────────────────

    def get_operations(self, routing_header_id: int) -> list[RoutingOperation]:
        return self.op_repo.get_by_header(routing_header_id)

    def get_operation_by_id(self, op_id: int) -> Optional[RoutingOperation]:
        return self.op_repo.get_by_id(op_id)

    def add_operation(
        self,
        routing_header_id: int,
        operation_id: int,
        department_id: Optional[int] = None,
        work_center_id: Optional[int] = None,
        machine_id: Optional[int] = None,
        setup_time_min: Decimal = Decimal("0"),
        cycle_time_min: Decimal = Decimal("0"),
        labor_count: int = 1,
        hourly_rate: Optional[Decimal] = None,
        is_outsourced: bool = False,
        notes: str = "",
    ) -> RoutingOperation:
        header = self.header_repo.get_by_id(routing_header_id)
        if not header:
            raise ValueError("Routing یافت نشد")
        if header.status == RoutingStatus.APPROVED.value:
            raise ValueError("Routing تأیید شده را نمی‌توان ویرایش کرد")

        max_step = self.op_repo.get_max_step_no(routing_header_id)

        op = RoutingOperation(
            routing_header_id=routing_header_id,
            step_no=max_step + 10,
            operation_id=operation_id,
            department_id=department_id,
            work_center_id=work_center_id,
            machine_id=machine_id,
            setup_time_min=setup_time_min,
            cycle_time_min=cycle_time_min,
            labor_count=labor_count,
            hourly_rate=hourly_rate,
            is_outsourced=is_outsourced,
            notes=notes,
        )
        return self.op_repo.create(op)

    def update_operation(
        self,
        op_id: int,
        operation_id: int,
        department_id: Optional[int] = None,
        work_center_id: Optional[int] = None,
        machine_id: Optional[int] = None,
        setup_time_min: Decimal = Decimal("0"),
        cycle_time_min: Decimal = Decimal("0"),
        labor_count: int = 1,
        hourly_rate: Optional[Decimal] = None,
        is_outsourced: bool = False,
        notes: str = "",
    ) -> RoutingOperation:
        op = self.op_repo.get_by_id(op_id)
        if not op:
            raise ValueError("عملیات یافت نشد")

        header = self.header_repo.get_by_id(op.routing_header_id)
        if header and header.status == RoutingStatus.APPROVED.value:
            raise ValueError("Routing تأیید شده را نمی‌توان ویرایش کرد")

        op.operation_id   = operation_id
        op.department_id  = department_id
        op.work_center_id = work_center_id
        op.machine_id     = machine_id
        op.setup_time_min = setup_time_min
        op.cycle_time_min = cycle_time_min
        op.labor_count    = labor_count
        op.hourly_rate    = hourly_rate
        op.is_outsourced  = is_outsourced
        op.notes          = notes
        return self.op_repo.update(op)

    def delete_operation(self, op_id: int) -> None:
        op = self.op_repo.get_by_id(op_id)
        if not op:
            raise ValueError("عملیات یافت نشد")
        header = self.header_repo.get_by_id(op.routing_header_id)
        if header and header.status == RoutingStatus.APPROVED.value:
            raise ValueError("Routing تأیید شده را نمی‌توان ویرایش کرد")
        self.op_repo.delete(op)

    # ── محاسبات ────────────────────────────────────────────────────

    def calculate_total_time(self, routing_header_id: int) -> dict:
        """محاسبه زمان‌های کل (دقیقه)"""
        ops = self.op_repo.get_by_header(routing_header_id)
        setup = sum(float(op.setup_time_min or 0) for op in ops)
        cycle = sum(float(op.cycle_time_min or 0) for op in ops)
        return {
            "setup_min":  setup,
            "cycle_min":  cycle,
            "total_min":  setup + cycle,
            "total_hour": (setup + cycle) / 60.0,
        }

    def calculate_total_cost(self, routing_header_id: int) -> Decimal:
        """محاسبه هزینه تخمینی کل ساخت (ریال)"""
        ops = self.op_repo.get_by_header(routing_header_id)
        total = Decimal("0")
        for op in ops:
            if op.hourly_rate:
                total_min = float(op.setup_time_min or 0) + float(op.cycle_time_min or 0)
                total += Decimal(str(total_min / 60.0)) * Decimal(str(op.hourly_rate))
        return total