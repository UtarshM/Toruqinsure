"""add_calls_table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-04-19 11:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'calls',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('lead_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('leads.id', ondelete='SET NULL'), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('lead_name', sa.String(255), nullable=True),
        sa.Column('phone_number', sa.String(50), nullable=True),
        sa.Column('duration', sa.String(50), nullable=True),
        sa.Column('status', sa.String(50), nullable=True, server_default='completed'),
        sa.Column('outcome', sa.String(50), nullable=True, server_default='interested'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('follow_up_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.create_index('ix_calls_lead_id', 'calls', ['lead_id'])
    op.create_index('ix_calls_user_id', 'calls', ['user_id'])
    op.create_index('ix_calls_status', 'calls', ['status'])
    op.create_index('ix_calls_created_at', 'calls', ['created_at'])
    op.create_index('ix_calls_outcome', 'calls', ['outcome'])


def downgrade() -> None:
    op.drop_table('calls')
