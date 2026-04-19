import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Call(Base):
    """
    Logs every call made to/from a lead.
    Created from the mobile 'Log Call' form after the agent calls a prospect.
    """
    __tablename__ = 'calls'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id', ondelete='SET NULL'), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    # The name is stored directly so the log survives lead deletion
    lead_name = Column(String(255), nullable=True)
    phone_number = Column(String(50), nullable=True)

    duration = Column(String(50), nullable=True)      # e.g. "5 min", "2:30"
    status = Column(String(50), default='completed')   # completed | missed | no_answer
    outcome = Column(String(50), default='interested') # interested | callback | not_interested | etc.
    notes = Column(Text, nullable=True)

    # If a follow-up was scheduled from this call
    follow_up_date = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_calls_lead_id', 'lead_id'),
        Index('ix_calls_user_id', 'user_id'),
        Index('ix_calls_status', 'status'),
        Index('ix_calls_created_at', 'created_at'),
        Index('ix_calls_outcome', 'outcome'),
    )
