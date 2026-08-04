"""add_cost_types_table

Revision ID: 60450842d0e5
Revises: 83ae18da1a58
Create Date: 2026-08-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

# revision identifiers
revision = '60450842d0e5'
down_revision = '83ae18da1a58'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── ساخت Enum Type ها با raw SQL ──
    op.execute(
        "CREATE TYPE costcategory AS ENUM "
        "('direct', 'indirect', 'fixed', 'variable')"
    )
    op.execute(
        "CREATE TYPE costbehavior AS ENUM "
        "('fixed', 'variable', 'semi_variable', 'step')"
    )
    op.execute(
        "CREATE TYPE costunit AS ENUM "
        "('rial', 'dollar', 'euro', 'percent', 'hour', 'unit')"
    )
    op.execute(
        "CREATE TYPE allocationmethod AS ENUM "
        "('direct', 'machine_hour', 'labor_hour', "
        "'production_qty', 'area', 'manual')"
    )
    op.execute(
        "CREATE TYPE coststatus AS ENUM "
        "('active', 'inactive', 'archived')"
    )

    # ── ساخت جدول با raw SQL کامل ──
    op.execute("""
        CREATE TABLE cost_types (
            id          SERIAL PRIMARY KEY,
            code        VARCHAR(20)  NOT NULL,
            name        VARCHAR(100) NOT NULL,
            category    costcategory NOT NULL,
            cost_behavior costbehavior NOT NULL,
            unit        costunit     NOT NULL,
            default_amount NUMERIC(18, 2),
            allocation_method allocationmethod NOT NULL,
            account_code VARCHAR(30),
            taxable     BOOLEAN      NOT NULL DEFAULT false,
            parent_id   INTEGER REFERENCES cost_types(id) ON DELETE SET NULL,
            description TEXT,
            status      coststatus   NOT NULL DEFAULT 'active',
            created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
            updated_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
        )
    """)

    op.execute(
        "CREATE UNIQUE INDEX ix_cost_types_code ON cost_types (code)"
    )
    op.execute(
        "CREATE INDEX ix_cost_types_name ON cost_types (name)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS cost_types CASCADE")
    op.execute("DROP TYPE IF EXISTS coststatus")
    op.execute("DROP TYPE IF EXISTS allocationmethod")
    op.execute("DROP TYPE IF EXISTS costunit")
    op.execute("DROP TYPE IF EXISTS costbehavior")
    op.execute("DROP TYPE IF EXISTS costcategory")