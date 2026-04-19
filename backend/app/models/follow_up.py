import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base


class FollowUp(Base):
    """
    Scheduled follow-up tasks linked to leads.
    Created from the post-call form or manually from lead detail.
    """
    __tablename__ = 'follow_ups'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id', ondelete='CASCADE'), nullable=False)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    lead_name = Column(String(255), nullable=True)          # denormalized for display
    type = Column(String(50), default='call')               # call | meeting | email | whatsapp | visit
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    notes = Column(Text, nullable=True)
    status = Column(String(50), default='pending')          # pending | completed | cancelled | overdue
    is_overdue = Column(Boolean, default=False)

    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('ix_follow_ups_lead_id', 'lead_id'),
        Index('ix_follow_ups_assigned_to', 'assigned_to'),
        Index('ix_follow_ups_status', 'status'),
        Index('ix_follow_ups_scheduled_at', 'scheduled_at'),
    )
