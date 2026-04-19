from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime, date
from uuid import UUID

class PolicyBase(BaseModel):
    policy_number: str
    provider: str
    type: str # 'Health', 'Life', 'Auto'
    premium_amount: float
    status: Optional[str] = "Active"
    start_date: date
    end_date: date

class PolicyCreate(PolicyBase):
    lead_id: UUID

class PolicyUpdate(BaseModel):
    policy_number: Optional[str] = None
    provider: Optional[str] = None
    type: Optional[str] = None
    premium_amount: Optional[float] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    lead_id: Optional[UUID] = None

class PolicyInDB(PolicyBase):
    id: UUID
    lead_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
