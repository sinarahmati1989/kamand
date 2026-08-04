"""
Repository — Lookup
"""
from typing import List, Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.lookup import Lookup


class LookupRepository:
    """عملیات دیتابیس Lookup"""

    def __init__(self, session: Session):
        self._session = session

    # ══════════════════════════════════════════════════════════════
    # Read
    # ══════════════════════════════════════════════════════════════

    def get_by_id(self, lookup_id: int) -> Optional[Lookup]:
        return self._session.query(Lookup).filter(Lookup.id == lookup_id).first()

    def get_by_category_code(self, category: str, code: str) -> Optional[Lookup]:
        return self._session.query(Lookup).filter(
            Lookup.category == category,
            Lookup.code == code
        ).first()

    def get_by_category(
        self,
        category: str,
        active_only: bool = True,
        parent_id: Optional[int] = None,
        include_children: bool = False
    ) -> List[Lookup]:
        """
        همه آیتم‌های یک دسته
        
        Args:
            category: نام دسته
            active_only: فقط فعال‌ها
            parent_id: فقط فرزندان این والد
            include_children: فرزندان رو هم برگردون
        """
        q = self._session.query(Lookup).filter(Lookup.category == category)

        if active_only:
            q = q.filter(Lookup.is_active.is_(True))

        if parent_id is not None:
            q = q.filter(Lookup.parent_id == parent_id)
        elif not include_children:
            # فقط سطح اول (بدون parent)
            q = q.filter(Lookup.parent_id.is_(None))

        return q.order_by(Lookup.sort_order, Lookup.label_fa).all()

    def get_children(
        self,
        parent_id: int,
        active_only: bool = True
    ) -> List[Lookup]:
        """فرزندان یک آیتم"""
        q = self._session.query(Lookup).filter(Lookup.parent_id == parent_id)

        if active_only:
            q = q.filter(Lookup.is_active.is_(True))

        return q.order_by(Lookup.sort_order, Lookup.label_fa).all()

    def search(self, category: str, keyword: str) -> List[Lookup]:
        """جستجو در یک دسته"""
        kw = f"%{keyword}%"
        return (
            self._session.query(Lookup)
            .filter(Lookup.category == category)
            .filter(or_(
                Lookup.code.ilike(kw),
                Lookup.label_fa.ilike(kw),
                Lookup.label_en.ilike(kw),
            ))
            .order_by(Lookup.sort_order, Lookup.label_fa)
            .all()
        )

    def get_all_categories(self) -> List[str]:
        """لیست همه دسته‌های موجود"""
        results = (
            self._session.query(Lookup.category)
            .distinct()
            .order_by(Lookup.category)
            .all()
        )
        return [r[0] for r in results]

    def count_by_category(self, category: str) -> int:
        """تعداد آیتم‌های یک دسته"""
        return self._session.query(Lookup).filter(
            Lookup.category == category
        ).count()

    # ══════════════════════════════════════════════════════════════
    # Write
    # ══════════════════════════════════════════════════════════════

    def add(self, lookup: Lookup) -> Lookup:
        self._session.add(lookup)
        self._session.flush()
        self._session.refresh(lookup)
        return lookup

    def delete(self, lookup: Lookup) -> None:
        self._session.delete(lookup)
        self._session.flush()