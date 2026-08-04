"""
مدل Lookup — جدول جامع برای همه گزینه‌های سیستم
"""
from typing import Optional
from sqlalchemy import (
    String, Integer, Boolean, Text, JSON,
    ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin


class Lookup(Base, TimestampMixin):
    """
    جدول Lookup — نگهداری تمام گزینه‌های سیستم
    
    مثال:
      - انواع تأمین‌کننده
      - سطوح مشتری
      - دسته‌های هزینه
      - انواع عملیات ساخت
      - ...
    """
    __tablename__ = "lookups"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    # ═══ دسته‌بندی ═══
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="دسته: supplier_type, cost_category, ..."
    )

    # ═══ کد یکتا در دسته ═══
    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="کد یکتا در دسته: manufacturer, direct, ..."
    )

    # ═══ لیبل نمایشی ═══
    label_fa: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        comment="لیبل فارسی"
    )

    label_en: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
        comment="لیبل انگلیسی (اختیاری)"
    )

    # ═══ ساختار درختی (برای زیرشاخه‌ها) ═══
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("lookups.id", ondelete="CASCADE"),
        nullable=True,
        comment="والد (برای زیرشاخه‌ها)"
    )

    # ═══ ترتیب نمایش ═══
    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="ترتیب نمایش در لیست"
    )

    # ═══ محافظت از داده‌های اولیه سیستم ═══
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        server_default="false",
        comment="اگر True: کاربر نمی‌تواند حذف کند"
    )

    # ═══ وضعیت ═══
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        server_default="true",
        comment="فعال/غیرفعال"
    )

    # ═══ توضیحات ═══
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )

    # ═══ داده‌های اضافی (JSON) ═══
    extra_data: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        default=None,
        comment="داده‌های اضافی: رنگ، آیکون، تنظیمات..."
    )

    # ── Relationships ──
    parent: Mapped[Optional["Lookup"]] = relationship(
        "Lookup",
        remote_side=[id],
        backref="children",
        lazy="select"
    )

    # ── Constraints ──
    __table_args__ = (
        UniqueConstraint("category", "code", name="uq_lookup_category_code"),
        Index("ix_lookup_category_active", "category", "is_active"),
        Index("ix_lookup_parent", "parent_id"),
    )

    def __repr__(self) -> str:
        return f"<Lookup(id={self.id}, category={self.category}, code={self.code}, label={self.label_fa})>"