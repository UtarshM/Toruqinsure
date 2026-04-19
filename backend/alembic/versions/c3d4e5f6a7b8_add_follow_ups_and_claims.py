"""add_follow_ups_and_claims

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-04-19 11:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Follow Ups table
    op.create_table(
        'follow_ups',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('lead_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('leads.id', ondelete='CASCADE'), nullable=False),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('lead_name', sa.String(255), nullable=True),
        sa.Column('type', sa.String(50), nullable=True, server_default='call'),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), nullable=True, server_default='pending'),
        sa.Column('is_overdue', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.create_index('ix_follow_ups_lead_id', 'follow_ups', ['lead_id'])
    op.create_index('ix_follow_ups_assigned_to', 'follow_ups', ['assigned_to'])
    op.create_index('ix_follow_ups_status', 'follow_ups', ['status'])
    op.create_index('ix_follow_ups_scheduled_at', 'follow_ups', ['scheduled_at'])

    # Claims table
    op.create_table(
        'claims',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('policy_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('policies.id', ondelete='SET NULL'), nullable=True),
        sa.Column('lead_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('leads.id', ondelete='SET NULL'), nullable=True),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('customer_name', sa.String(255), nullable=False),
        sa.Column('policy_number', sa.String(100), nullable=True),
        sa.Column('vehicle_number', sa.String(50), nullable=True),
        sa.Column('claim_type', sa.String(50), nullable=True),
        sa.Column('claim_amount', sa.Numeric(12, 2), nullable=True),
        sa.Column('approved_amount', sa.Numeric(12, 2), nullable=True),
        sa.Column('status', sa.String(50), nullable=True, server_default='filed'),
        sa.Column('incident_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('filed_date', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('settled_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('documents', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.create_index('ix_claims_policy_id', 'claims', ['policy_id'])
    op.create_index('ix_claims_lead_id', 'claims', ['lead_id'])
    op.create_index('ix_claims_status', 'claims', ['status'])
    op.create_index('ix_claims_assigned_to', 'claims', ['assigned_to'])
    op.create_index('ix_claims_filed_date', 'claims', ['filed_date'])


def downgrade() -> None:
    op.drop_table('claims')
    op.drop_table('follow_ups')
