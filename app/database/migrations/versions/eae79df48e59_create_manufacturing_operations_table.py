"""create_manufacturing_operations_table

Revision ID: eae79df48e59
Revises: 399b9a953533
Create Date: 2026-08-04 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eae79df48e59'
down_revision: Union[str, None] = '399b9a953533'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'manufacturing_operations',

        # شناسه و کد
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('code', sa.String(20), nullable=False),
        sa.Column('name', sa.String(150), nullable=False),

        # نوع و توضیحات
        sa.Column('operation_type', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),

        # ویژگی‌ها (bool)
        sa.Column('is_outsourced', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('requires_qc', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('requires_machine', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_bottleneck', sa.Boolean(), nullable=False, server_default='false'),

        # زمان‌ها
        sa.Column('setup_time', sa.Numeric(10, 2), nullable=True),
        sa.Column('setup_time_unit', sa.String(50), nullable=False, server_default='minute'),
        sa.Column('cycle_time', sa.Numeric(10, 2), nullable=True),
        sa.Column('cycle_time_unit', sa.String(50), nullable=False, server_default='minute'),

        # ظرفیت
        sa.Column('capacity_per_hour', sa.Numeric(10, 2), nullable=True),
        sa.Column('default_operator_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('efficiency_percent', sa.Numeric(5, 2), nullable=True),
        sa.Column('oee_target', sa.Numeric(5, 2), nullable=True),

        # هزینه
        sa.Column('hourly_rate', sa.Numeric(18, 2), nullable=True),
        sa.Column('currency', sa.String(50), nullable=False, server_default='irr'),

        # مهارت
        sa.Column('skill_level', sa.String(50), nullable=True),
        sa.Column('required_skills_description', sa.Text(), nullable=True),

        # یادداشت‌ها
        sa.Column('required_tools', sa.Text(), nullable=True),
        sa.Column('safety_notes', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),

        # وضعیت
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ایندکس‌ها
    op.create_index('ix_mfg_ops_code', 'manufacturing_operations', ['code'], unique=True)
    op.create_index('ix_mfg_ops_name', 'manufacturing_operations', ['name'])
    op.create_index('ix_mfg_ops_operation_type', 'manufacturing_operations', ['operation_type'])
    op.create_index('ix_mfg_ops_status', 'manufacturing_operations', ['status'])


def downgrade() -> None:
    op.drop_index('ix_mfg_ops_status', table_name='manufacturing_operations')
    op.drop_index('ix_mfg_ops_operation_type', table_name='manufacturing_operations')
    op.drop_index('ix_mfg_ops_name', table_name='manufacturing_operations')
    op.drop_index('ix_mfg_ops_code', table_name='manufacturing_operations')
    op.drop_table('manufacturing_operations')