from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class TransactionBase(BaseModel):
    user_id: Optional[UUID] = None
    lead_id: Optional[UUID] = None
    policy_id: Optional[UUID] = None
    type: str
    category: Optional[str] = None
    amount: Decimal
    status: str = "completed"
    payment_method: Optional[str] = None
    reference_number: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Any] = None
    date: Optional[datetime] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionInDB(TransactionBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class LoanBase(BaseModel):
    lead_id: Optional[UUID] = None
    assigned_to: Optional[UUID] = None
    customer_name: str
    loan_type: Optional[str] = None
    amount: Decimal
    tenure_months: Optional[int] = None
    interest_rate: Optional[Decimal] = None
    status: str = "applied"
    bank_name: Optional[str] = None
    notes: Optional[str] = None


class LoanCreate(LoanBase):
    pass


class LoanUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[UUID] = None
    amount: Optional[Decimal] = None
    bank_name: Optional[str] = None
    disbursement_date: Optional[datetime] = None
    notes: Optional[str] = None


class LoanInDB(LoanBase):
    id: UUID
    disbursement_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
