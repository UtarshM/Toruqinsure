import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.core.database import Base


class Customer(Base):
    """
    Permanent customer profiles (converted from leads).
    """
    __tablename__ = 'customers'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id', ondelete='SET NULL'), nullable=True)
    
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=False)
    address = Column(Text, nullable=True)
    
    kyc_status = Column(String(50), default='pending') # pending | verified | rejected
    metadata_ = Column("metadata", JSONB, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('ix_customers_phone', 'phone'),
        Index('ix_customers_name', 'name'),
    )


class Visit(Base):
    """
    Field visits tracking for CRM executives or Sales.
    """
    __tablename__ = 'visits'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id', ondelete='CASCADE'), nullable=True)
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id', ondelete='CASCADE'), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    purpose = Column(String(255), nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    status = Column(String(50), default='scheduled')    # scheduled | completed | cancelled | missed
    location = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Check-in/out coordinates for field tracking
    check_in_lat = Column(Numeric(10, 7), nullable=True)
    check_in_lng = Column(Numeric(10, 7), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_visits_user_id', 'user_id'),
        Index('ix_visits_status', 'status'),
        Index('ix_visits_scheduled_at', 'scheduled_at'),
    )
