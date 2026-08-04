"""migrate_cost_types_to_lookup

Revision ID: d519c3ab823b
Revises: 5a87964fd42b
Create Date: 2026-08-04 10:10:27.094531

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd519c3ab823b'
down_revision: Union[str, None] = '5a87964fd42b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # حذف default های enum قبل از تغییر type
    op.execute("ALTER TABLE cost_types ALTER COLUMN category DROP DEFAULT")
    op.execute("ALTER TABLE cost_types ALTER COLUMN cost_behavior DROP DEFAULT")
    op.execute("ALTER TABLE cost_types ALTER COLUMN unit DROP DEFAULT")
    op.execute("ALTER TABLE cost_types ALTER COLUMN allocation_method DROP DEFAULT")
    op.execute("ALTER TABLE cost_types ALTER COLUMN status DROP DEFAULT")

    # تبدیل enum -> varchar
    op.execute("""
        ALTER TABLE cost_types
        ALTER COLUMN category TYPE VARCHAR(50)
        USING category::text
    """)
    op.execute("""
        ALTER TABLE cost_types
        ALTER COLUMN cost_behavior TYPE VARCHAR(50)
        USING cost_behavior::text
    """)
    op.execute("""
        ALTER TABLE cost_types
        ALTER COLUMN unit TYPE VARCHAR(50)
        USING unit::text
    """)
    op.execute("""
        ALTER TABLE cost_types
        ALTER COLUMN allocation_method TYPE VARCHAR(50)
        USING allocation_method::text
    """)
    op.execute("""
        ALTER TABLE cost_types
        ALTER COLUMN status TYPE VARCHAR(20)
        USING status::text
    """)

    # بازگرداندن default ها به صورت string
    op.execute("ALTER TABLE cost_types ALTER COLUMN category SET DEFAULT 'direct'")
    op.execute("ALTER TABLE cost_types ALTER COLUMN cost_behavior SET DEFAULT 'variable'")
    op.execute("ALTER TABLE cost_types ALTER COLUMN unit SET DEFAULT 'rial'")
    op.execute("ALTER TABLE cost_types ALTER COLUMN allocation_method SET DEFAULT 'direct'")
    op.execute("ALTER TABLE cost_types ALTER COLUMN status SET DEFAULT 'active'")

    # حذف type های enum قدیمی PostgreSQL
    op.execute("DROP TYPE IF EXISTS costcategory")
    op.execute("DROP TYPE IF EXISTS costbehavior")
    op.execute("DROP TYPE IF EXISTS costunit")
    op.execute("DROP TYPE IF EXISTS allocationmethod")
    op.execute("DROP TYPE IF EXISTS coststatus")


def downgrade() -> None:
    # حذف default های string قبل از برگشت
    op.execute("ALTER TABLE cost_types ALTER COLUMN category DROP DEFAULT")
    op.execute("ALTER TABLE cost_types ALTER COLUMN cost_behavior DROP DEFAULT")
    op.execute("ALTER TABLE cost_types ALTER COLUMN unit DROP DEFAULT")
    op.execute("ALTER TABLE cost_types ALTER COLUMN allocation_method DROP DEFAULT")
    op.execute("ALTER TABLE cost_types ALTER COLUMN status DROP DEFAULT")

    # ساخت دوباره enum type ها
    op.execute("""
        CREATE TYPE costcategory AS ENUM (
            'direct', 'indirect', 'fixed', 'variable'
        )
    """)
    op.execute("""
        CREATE TYPE costbehavior AS ENUM (
            'fixed', 'variable', 'semi_variable', 'step'
        )
    """)
    op.execute("""
        CREATE TYPE costunit AS ENUM (
            'rial', 'dollar', 'euro', 'percent', 'hour', 'unit'
        )
    """)
    op.execute("""
        CREATE TYPE allocationmethod AS ENUM (
            'direct', 'machine_hour', 'labor_hour', 'production_qty', 'area', 'manual'
        )
    """)
    op.execute("""
        CREATE TYPE coststatus AS ENUM (
            'active', 'inactive', 'archived'
        )
    """)

    # تبدیل varchar -> enum
    op.execute("""
        ALTER TABLE cost_types
        ALTER COLUMN category TYPE costcategory
        USING category::costcategory
    """)
    op.execute("""
        ALTER TABLE cost_types
        ALTER COLUMN cost_behavior TYPE costbehavior
        USING cost_behavior::costbehavior
    """)
    op.execute("""
        ALTER TABLE cost_types
        ALTER COLUMN unit TYPE costunit
        USING unit::costunit
    """)
    op.execute("""
        ALTER TABLE cost_types
        ALTER COLUMN allocation_method TYPE allocationmethod
        USING allocation_method::allocationmethod
    """)
    op.execute("""
        ALTER TABLE cost_types
        ALTER COLUMN status TYPE coststatus
        USING status::coststatus
    """)

    # بازگرداندن default های enum
    op.execute("ALTER TABLE cost_types ALTER COLUMN category SET DEFAULT 'direct'::costcategory")
    op.execute("ALTER TABLE cost_types ALTER COLUMN cost_behavior SET DEFAULT 'variable'::costbehavior")
    op.execute("ALTER TABLE cost_types ALTER COLUMN unit SET DEFAULT 'rial'::costunit")
    op.execute("ALTER TABLE cost_types ALTER COLUMN allocation_method SET DEFAULT 'direct'::allocationmethod")
    op.execute("ALTER TABLE cost_types ALTER COLUMN status SET DEFAULT 'active'::coststatus")