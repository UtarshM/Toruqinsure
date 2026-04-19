import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.core.database import Base


class Claim(Base):
    """
    Insurance claim lifecycle management.
    Linked to a policy and optionally to a lead.
    """
    __tablename__ = 'claims'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_id = Column(UUID(as_uuid=True), ForeignKey('policies.id', ondelete='SET NULL'), nullable=True)
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id', ondelete='SET NULL'), nullable=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    # Denormalized display fields
    customer_name = Column(String(255), nullable=False)
    policy_number = Column(String(100), nullable=True)
    vehicle_number = Column(String(50), nullable=True)

    claim_type = Column(String(50), nullable=True)          # accident | theft | natural_disaster | fire | other
    claim_amount = Column(Numeric(12, 2), nullable=True)
    approved_amount = Column(Numeric(12, 2), nullable=True)

    status = Column(String(50), default='filed')
    # filed | under_review | approved | rejected | settled | withdrawn

    incident_date = Column(DateTime(timezone=True), nullable=True)
    filed_date = Column(DateTime(timezone=True), server_default=func.now())
    settled_date = Column(DateTime(timezone=True), nullable=True)

    description = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    documents = Column(JSONB, nullable=True)                # list of doc refs

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('ix_claims_policy_id', 'policy_id'),
        Index('ix_claims_lead_id', 'lead_id'),
        Index('ix_claims_status', 'status'),
        Index('ix_claims_assigned_to', 'assigned_to'),
        Index('ix_claims_filed_date', 'filed_date'),
    )
