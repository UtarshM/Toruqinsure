import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Lead(Base):
    __tablename__ = 'leads'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    client_name = Column(String(255), nullable=False)
    client_email = Column(String(255), nullable=True)
    client_phone = Column(String(50), nullable=True)
    status = Column(String(50), default='New')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    policies = relationship("Policy", back_populates="lead")
    quotations = relationship("Quotation", back_populates="lead")

    __table_args__ = (
        Index('ix_leads_status', 'status'),
        Index('ix_leads_assigned_to', 'assigned_to'),
        Index('ix_leads_created_at', 'created_at'),
        Index('ix_leads_client_email', 'client_email'),
    )


class Quotation(Base):
    __tablename__ = 'quotations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id', ondelete='CASCADE'), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    amount = Column(Numeric(12, 2), nullable=False)
    status = Column(String(50), default='Draft')
    details = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    lead = relationship("Lead", back_populates="quotations")

    __table_args__ = (
        Index('ix_quotations_lead_id', 'lead_id'),
        Index('ix_quotations_status', 'status'),
        Index('ix_quotations_created_by', 'created_by'),
    )


class Policy(Base):
    __tablename__ = 'policies'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id', ondelete='SET NULL'), nullable=True)
    policy_number = Column(String(100), unique=True, nullable=False)
    provider = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    premium_amount = Column(Numeric(12, 2), nullable=False)
    status = Column(String(50), default='Active')
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    lead = relationship("Lead", back_populates="policies")

    __table_args__ = (
        Index('ix_policies_lead_id', 'lead_id'),
        Index('ix_policies_status', 'status'),
        Index('ix_policies_end_date', 'end_date'),
        Index('ix_policies_provider', 'provider'),
    )


class Document(Base):
    __tablename__ = 'documents'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(50), nullable=False)  # 'lead', 'policy', 'quotation', 'kyc'
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_documents_entity_type_id', 'entity_type', 'entity_id'),
        Index('ix_documents_uploaded_by', 'uploaded_by'),
    )


class ActivityLog(Base):
    __tablename__ = 'activity_logs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    metadata_ = Column("metadata", JSONB, nullable=True)  # avoiding reserved keyword
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_activity_logs_user_id', 'user_id'),
        Index('ix_activity_logs_entity', 'entity_type', 'entity_id'),
        Index('ix_activity_logs_created_at', 'created_at'),
        Index('ix_activity_logs_action', 'action'),
    )
