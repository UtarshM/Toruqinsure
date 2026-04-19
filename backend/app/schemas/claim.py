from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class ClaimBase(BaseModel):
    policy_id: Optional[UUID] = None
    lead_id: Optional[UUID] = None
    assigned_to: Optional[UUID] = None
    customer_name: str
    policy_number: Optional[str] = None
    vehicle_number: Optional[str] = None
    claim_type: Optional[str] = None
    claim_amount: Optional[Decimal] = None
    incident_date: Optional[datetime] = None
    description: Optional[str] = None


class ClaimCreate(ClaimBase):
    pass


class ClaimUpdate(BaseModel):
    assigned_to: Optional[UUID] = None
    claim_amount: Optional[Decimal] = None
    approved_amount: Optional[Decimal] = None
    status: Optional[str] = None
    settled_date: Optional[datetime] = None
    description: Optional[str] = None
    rejection_reason: Optional[str] = None
    documents: Optional[List[Any]] = None


class ClaimInDB(ClaimBase):
    id: UUID
    approved_amount: Optional[Decimal] = None
    status: str
    filed_date: datetime
    settled_date: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    documents: Optional[List[Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
