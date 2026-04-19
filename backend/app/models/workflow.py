import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.core.database import Base


class RTOWork(Base):
    """
    RTO related workflow tracking (Transfer, Hypothecation, etc.)
    """
    __tablename__ = 'rto_work'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id', ondelete='SET NULL'), nullable=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    customer_name = Column(String(255), nullable=False)
    vehicle_number = Column(String(50), nullable=True)
    work_type = Column(String(100), nullable=False)    # transfer | hp_addition | hp_deletion | address_change
    
    status = Column(String(50), default='pending')      # pending | in_progress | completed | rejected
    rto_office = Column(String(100), nullable=True)
    
    fees = Column(Numeric(12, 2), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    completion_date = Column(DateTime(timezone=True), nullable=True)
    
    notes = Column(Text, nullable=True)
    documents = Column(JSONB, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('ix_rto_work_status', 'status'),
        Index('ix_rto_work_vehicle_number', 'vehicle_number'),
    )


class FitnessWork(Base):
    """
    Vehicle fitness certificate management.
    """
    __tablename__ = 'fitness_work'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id', ondelete='SET NULL'), nullable=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    customer_name = Column(String(255), nullable=False)
    vehicle_number = Column(String(50), nullable=False)
    vehicle_type = Column(String(100), nullable=True)
    
    status = Column(String(50), default='pending')      # pending | scheduled | passed | failed
    test_date = Column(DateTime(timezone=True), nullable=True)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    
    fees = Column(Numeric(12, 2), nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('ix_fitness_work_status', 'status'),
        Index('ix_fitness_work_vehicle_number', 'vehicle_number'),
        Index('ix_fitness_work_test_date', 'test_date'),
    )
