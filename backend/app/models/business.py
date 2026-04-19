import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.core.database import Base


class Transaction(Base):
    """
    Finance ledger tracking income, expenses, and commissions.
    """
    __tablename__ = 'transactions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id', ondelete='SET NULL'), nullable=True)
    policy_id = Column(UUID(as_uuid=True), ForeignKey('policies.id', ondelete='SET NULL'), nullable=True)

    type = Column(String(50), nullable=False)          # income | expense | commission | refund
    category = Column(String(100), nullable=True)      # renewal | new_policy | service_fee | etc.
    amount = Column(Numeric(12, 2), nullable=False)
    status = Column(String(50), default='completed')    # pending | completed | failed | cancelled

    payment_method = Column(String(50), nullable=True)  # cash | bank_transfer | upi | card
    reference_number = Column(String(100), nullable=True)
    
    description = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)

    date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_transactions_type', 'type'),
        Index('ix_transactions_status', 'status'),
        Index('ix_transactions_user_id', 'user_id'),
        Index('ix_transactions_date', 'date'),
    )


class Loan(Base):
    """
    Loan application management for customers.
    """
    __tablename__ = 'loans'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id', ondelete='SET NULL'), nullable=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    customer_name = Column(String(255), nullable=False)
    loan_type = Column(String(100), nullable=True)      # car_loan | personal_loan | business_loan
    amount = Column(Numeric(12, 2), nullable=False)
    tenure_months = Column(Numeric(5, 0), nullable=True)
    interest_rate = Column(Numeric(5, 2), nullable=True)

    status = Column(String(50), default='applied')     # applied | under_review | approved | disbursed | rejected | closed
    
    bank_name = Column(String(100), nullable=True)
    disbursement_date = Column(DateTime(timezone=True), nullable=True)
    
    notes = Column(Text, nullable=True)
    documents = Column(JSONB, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('ix_loans_status', 'status'),
        Index('ix_loans_assigned_to', 'assigned_to'),
        Index('ix_loans_customer_name', 'customer_name'),
    )
