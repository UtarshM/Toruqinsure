from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class CustomerBase(BaseModel):
    lead_id: Optional[UUID] = None
    name: str
    email: Optional[str] = None
    phone: str
    address: Optional[str] = None
    kyc_status: str = "pending"
    metadata: Optional[Any] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    kyc_status: Optional[str] = None


class CustomerInDB(CustomerBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class VisitBase(BaseModel):
    customer_id: Optional[UUID] = None
    lead_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    purpose: str
    scheduled_at: datetime
    status: str = "scheduled"
    location: Optional[str] = None
    notes: Optional[str] = None


class VisitCreate(VisitBase):
    pass


class VisitUpdate(BaseModel):
    status: Optional[str] = None
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None
    check_in_lat: Optional[Decimal] = None
    check_in_lng: Optional[Decimal] = None


class VisitInDB(VisitBase):
    id: UUID
    completed_at: Optional[datetime] = None
    check_in_lat: Optional[Decimal] = None
    check_in_lng: Optional[Decimal] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
