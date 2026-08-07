"""add routing tables

Revision ID: f1a2b3c4d5e6
Revises: da0813c04d3e
Create Date: 2026-08-05 21:30:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'f1a2b3c4d5e6'
down_revision = 'da0813c04d3e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── routing_headers ────────────────────────────────────────────
    op.create_table(
        'routing_headers',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('device_template_id', sa.Integer(),
                  sa.ForeignKey('device_templates.id', ondelete='CASCADE'),
                  nullable=False),
        sa.Column('revision_no', sa.Integer(), nullable=False, default=1),
        sa.Column('status', sa.String(20), nullable=False,
                  server_default='draft'),
        sa.Column('effective_from', sa.Date(), nullable=True),
        sa.Column('effective_to',   sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('approved_by_id', sa.Integer(),
                  sa.ForeignKey('users.id', ondelete='SET NULL'),
                  nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('device_template_id', 'revision_no',
                            name='uq_routing_template_revision'),
    )
    op.create_index(
        'ix_routing_headers_device_template_id',
        'routing_headers', ['device_template_id']
    )

    # ── routing_operations ─────────────────────────────────────────
    op.create_table(
        'routing_operations',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('routing_header_id', sa.Integer(),
                  sa.ForeignKey('routing_headers.id', ondelete='CASCADE'),
                  nullable=False),
        sa.Column('step_no', sa.Integer(), nullable=False, default=10),
        sa.Column('operation_id', sa.Integer(),
                  sa.ForeignKey('manufacturing_operations.id',
                                ondelete='RESTRICT'),
                  nullable=False),
        sa.Column('department_id', sa.Integer(),
                  sa.ForeignKey('departments.id', ondelete='SET NULL'),
                  nullable=True),
        sa.Column('work_center_id', sa.Integer(),
                  sa.ForeignKey('work_centers.id', ondelete='SET NULL'),
                  nullable=True),
        sa.Column('machine_id', sa.Integer(),
                  sa.ForeignKey('machines.id', ondelete='SET NULL'),
                  nullable=True),
        sa.Column('setup_time_min', sa.Numeric(10, 2),
                  nullable=True, default=0),
        sa.Column('cycle_time_min', sa.Numeric(10, 2),
                  nullable=True, default=0),
        sa.Column('labor_count', sa.Integer(), nullable=True, default=1),
        sa.Column('hourly_rate', sa.Numeric(18, 2), nullable=True),
        sa.Column('is_outsourced', sa.Boolean(), nullable=False,
                  server_default='false'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(
        'ix_routing_operations_routing_header_id',
        'routing_operations', ['routing_header_id']
    )
    op.create_index(
        'ix_routing_operations_operation_id',
        'routing_operations', ['operation_id']
    )


def downgrade() -> None:
    op.drop_index('ix_routing_operations_operation_id',
                  table_name='routing_operations')
    op.drop_index('ix_routing_operations_routing_header_id',
                  table_name='routing_operations')
    op.drop_table('routing_operations')

    op.drop_index('ix_routing_headers_device_template_id',
                  table_name='routing_headers')
    op.drop_table('routing_headers')