"""
Kamand - BOM Service
منطق کسب‌وکار BOM
"""
from typing import Optional
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.bom import BOMHeader, BOMLine
from app.repositories.bom_repository import BOMHeaderRepository, BOMLineRepository
from app.enums.engineering_enums import BOMStatus
import logging

logger = logging.getLogger(__name__)


class BOMService:

    def __init__(self, session: Session):
        self.session = session
        self.header_repo = BOMHeaderRepository(session)
        self.line_repo = BOMLineRepository(session)

    # ── BOMHeader ──────────────────────────────────────────────────

    def get_header_by_id(self, header_id: int) -> Optional[BOMHeader]:
        return self.header_repo.get_by_id(header_id)

    def get_headers_by_template(self, device_template_id: int) -> list[BOMHeader]:
        return self.header_repo.get_by_template(device_template_id)

    def get_with_lines(self, bom_header_id: int) -> Optional[BOMHeader]:
        return self.header_repo.get_with_lines(bom_header_id)

    def create_header(
        self,
        device_template_id: int,
        revision_no: Optional[int] = None,
        notes: str = "",
    ) -> BOMHeader:
        if revision_no is None:
            revision_no = self.header_repo.get_next_revision(device_template_id)

        if self.header_repo.exists_revision(device_template_id, revision_no):
            raise ValueError(
                f"Revision {revision_no} برای این تعریف دستگاه قبلاً ثبت شده است"
            )

        header = BOMHeader(
            device_template_id=device_template_id,
            revision_no=revision_no,
            status=BOMStatus.DRAFT.value,
            notes=notes,
        )
        return self.header_repo.create(header)

    def update_header(
        self,
        header_id: int,
        notes: str = "",
        status: Optional[str] = None,
    ) -> BOMHeader:
        header = self.header_repo.get_by_id(header_id)
        if not header:
            raise ValueError("BOM یافت نشد")
        header.notes = notes
        if status:
            header.status = status
        return self.header_repo.update(header)

    def delete_header(self, header_id: int) -> None:
        header = self.header_repo.get_by_id(header_id)
        if not header:
            raise ValueError("BOM یافت نشد")
        if header.status == BOMStatus.APPROVED.value:
            raise ValueError("BOM تأیید شده را نمی‌توان حذف کرد")
        self.header_repo.delete(header)

    def change_header_status(self, header_id: int, new_status: str) -> BOMHeader:
        header = self.header_repo.get_by_id(header_id)
        if not header:
            raise ValueError("BOM یافت نشد")
        header.status = new_status
        return self.header_repo.update(header)

    # ── BOMLine ────────────────────────────────────────────────────

    def get_lines(self, bom_header_id: int) -> list[BOMLine]:
        return self.line_repo.get_by_header(bom_header_id)

    def get_line_by_id(self, line_id: int) -> Optional[BOMLine]:
        return self.line_repo.get_by_id(line_id)

    def add_line(
        self,
        bom_header_id: int,
        item_id: int,
        quantity: Decimal,
        uom: Optional[str] = None,
        scrap_percent: Decimal = Decimal("0"),
        is_optional: bool = False,
        notes: str = "",
    ) -> BOMLine:
        header = self.header_repo.get_by_id(bom_header_id)
        if not header:
            raise ValueError("BOM یافت نشد")
        if header.status == BOMStatus.APPROVED.value:
            raise ValueError("BOM تأیید شده را نمی‌توان ویرایش کرد")

        max_order = self.line_repo.get_max_sort_order(bom_header_id)

        line = BOMLine(
            bom_header_id=bom_header_id,
            item_id=item_id,
            quantity=quantity,
            uom=uom,
            scrap_percent=scrap_percent,
            sort_order=max_order + 10,
            is_optional=is_optional,
            notes=notes,
        )
        return self.line_repo.create(line)

    def update_line(
        self,
        line_id: int,
        quantity: Decimal,
        uom: Optional[str] = None,
        scrap_percent: Decimal = Decimal("0"),
        is_optional: bool = False,
        notes: str = "",
    ) -> BOMLine:
        line = self.line_repo.get_by_id(line_id)
        if not line:
            raise ValueError("خط BOM یافت نشد")

        header = self.header_repo.get_by_id(line.bom_header_id)
        if header and header.status == BOMStatus.APPROVED.value:
            raise ValueError("BOM تأیید شده را نمی‌توان ویرایش کرد")

        line.quantity = quantity
        if uom:
            line.uom = uom
        line.scrap_percent = scrap_percent
        line.is_optional = is_optional
        line.notes = notes
        return self.line_repo.update(line)

    def delete_line(self, line_id: int) -> None:
        line = self.line_repo.get_by_id(line_id)
        if not line:
            raise ValueError("خط BOM یافت نشد")

        header = self.header_repo.get_by_id(line.bom_header_id)
        if header and header.status == BOMStatus.APPROVED.value:
            raise ValueError("BOM تأیید شده را نمی‌توان ویرایش کرد")

        self.line_repo.delete(line)

    # ── محاسبات ────────────────────────────────────────────────────

    def calculate_bom_cost(self, bom_header_id: int) -> Decimal:
        lines = self.line_repo.get_by_header(bom_header_id)
        total = Decimal("0")
        for line in lines:
            if line.item and line.item.standard_cost:
                qty = Decimal(str(line.quantity))
                cost = Decimal(str(line.item.standard_cost))
                scrap = Decimal(str(line.scrap_percent or 0)) / 100
                total += qty * cost * (1 + scrap)
        return total