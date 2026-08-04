"""migrate_customers_to_lookup

Revision ID: 399b9a953533
Revises: d519c3ab823b
Create Date: 2026-08-04 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '399b9a953533'
down_revision: Union[str, None] = 'd519c3ab823b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # حذف default های enum قبل از تغییر type
    op.execute("ALTER TABLE customers ALTER COLUMN customer_type DROP DEFAULT")
    op.execute("ALTER TABLE customers ALTER COLUMN status DROP DEFAULT")

    # تبدیل customer_type از enum فارسی به varchar با کد لاتین
    op.execute("""
        ALTER TABLE customers
        ALTER COLUMN customer_type TYPE VARCHAR(50)
        USING (
            CASE customer_type::text
                WHEN 'حقیقی' THEN 'real'
                WHEN 'حقوقی' THEN 'legal'
                ELSE 'legal'
            END
        )
    """)

    # تبدیل status از enum فارسی به varchar با کد لاتین
    op.execute("""
        ALTER TABLE customers
        ALTER COLUMN status TYPE VARCHAR(20)
        USING (
            CASE status::text
                WHEN 'فعال' THEN 'active'
                WHEN 'غیرفعال' THEN 'inactive'
                ELSE 'active'
            END
        )
    """)

    # بازگرداندن default های string
    op.execute("ALTER TABLE customers ALTER COLUMN customer_type SET DEFAULT 'legal'")
    op.execute("ALTER TABLE customers ALTER COLUMN status SET DEFAULT 'active'")

    # حذف enum type های قدیمی
    op.execute("DROP TYPE IF EXISTS customer_type_enum")
    op.execute("DROP TYPE IF EXISTS customer_status_enum")


def downgrade() -> None:
    # حذف default های string
    op.execute("ALTER TABLE customers ALTER COLUMN customer_type DROP DEFAULT")
    op.execute("ALTER TABLE customers ALTER COLUMN status DROP DEFAULT")

    # ساخت دوباره enum type ها
    op.execute("CREATE TYPE customer_type_enum AS ENUM ('حقیقی', 'حقوقی')")
    op.execute("CREATE TYPE customer_status_enum AS ENUM ('فعال', 'غیرفعال')")

    # تبدیل varchar به enum
    op.execute("""
        ALTER TABLE customers
        ALTER COLUMN customer_type TYPE customer_type_enum
        USING (
            CASE customer_type
                WHEN 'real' THEN 'حقیقی'::customer_type_enum
                WHEN 'legal' THEN 'حقوقی'::customer_type_enum
                ELSE 'حقوقی'::customer_type_enum
            END
        )
    """)

    op.execute("""
        ALTER TABLE customers
        ALTER COLUMN status TYPE customer_status_enum
        USING (
            CASE status
                WHEN 'active' THEN 'فعال'::customer_status_enum
                WHEN 'inactive' THEN 'غیرفعال'::customer_status_enum
                ELSE 'فعال'::customer_status_enum
            END
        )
    """)

    # بازگرداندن default های enum
    op.execute("ALTER TABLE customers ALTER COLUMN customer_type SET DEFAULT 'حقوقی'::customer_type_enum")
    op.execute("ALTER TABLE customers ALTER COLUMN status SET DEFAULT 'فعال'::customer_status_enum")