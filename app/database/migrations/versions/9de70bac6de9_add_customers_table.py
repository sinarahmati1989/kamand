"""add_customers_table

Revision ID: 9de70bac6de9
Revises: 012e1e521593
Create Date: 2026-08-03 19:44:02.130578

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9de70bac6de9'
down_revision: Union[str, None] = '012e1e521593'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('customers',
        sa.Column('name', sa.String(length=100), nullable=False, comment='نام شرکت'),
        sa.Column('trade_name', sa.String(length=100), nullable=True, comment='نام تجاری'),
        sa.Column('customer_type', sa.Enum('REAL', 'LEGAL', name='customer_type_enum'), nullable=False, comment='نوع مشتری'),
        sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', name='customer_status_enum'), nullable=False, comment='وضعیت'),
        sa.Column('contact_name', sa.String(length=100), nullable=True, comment='نام شخص رابط'),
        sa.Column('contact_title', sa.String(length=50), nullable=True, comment='سمت رابط'),
        sa.Column('contact_mobile', sa.String(length=20), nullable=True, comment='موبایل رابط'),
        sa.Column('phone', sa.String(length=20), nullable=True, comment='تلفن ثابت'),
        sa.Column('mobile', sa.String(length=20), nullable=True, comment='موبایل'),
        sa.Column('email', sa.String(length=100), nullable=True, comment='ایمیل'),
        sa.Column('address', sa.Text(), nullable=True, comment='آدرس کامل'),
        sa.Column('postal_code', sa.String(length=20), nullable=True, comment='کدپستی'),
        sa.Column('national_id', sa.String(length=20), nullable=True, comment='شناسه ملی'),
        sa.Column('notes', sa.Text(), nullable=True, comment='توضیحات'),
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('customers')