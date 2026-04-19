from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class RTOWorkBase(BaseModel):
    lead_id: Optional[UUID] = None
    assigned_to: Optional[UUID] = None
    customer_name: str
    vehicle_number: Optional[str] = None
    work_type: str
    status: str = "pending"
    rto_office: Optional[str] = None
    fees: Optional[Decimal] = None
    due_date: Optional[datetime] = None


class RTOWorkCreate(RTOWorkBase):
    pass


class RTOWorkUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[UUID] = None
    fees: Optional[Decimal] = None
    due_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    notes: Optional[str] = None


class RTOWorkInDB(RTOWorkBase):
    id: UUID
    completion_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class FitnessWorkBase(BaseModel):
    lead_id: Optional[UUID] = None
    assigned_to: Optional[UUID] = None
    customer_name: str
    vehicle_number: str
    vehicle_type: Optional[str] = None
    status: str = "pending"
    test_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    fees: Optional[Decimal] = None


class FitnessWorkCreate(FitnessWorkBase):
    pass


class FitnessWorkUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[UUID] = None
    test_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    fees: Optional[Decimal] = None
    notes: Optional[str] = None


class FitnessWorkInDB(FitnessWorkBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
