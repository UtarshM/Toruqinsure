from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class CallBase(BaseModel):
    lead_id: Optional[UUID] = None
    lead_name: Optional[str] = None
    phone_number: Optional[str] = None
    duration: Optional[str] = None
    status: Optional[str] = "completed"
    outcome: Optional[str] = "interested"
    notes: Optional[str] = None
    follow_up_date: Optional[datetime] = None


class CallCreate(CallBase):
    pass


class CallUpdate(BaseModel):
    status: Optional[str] = None
    outcome: Optional[str] = None
    notes: Optional[str] = None
    follow_up_date: Optional[datetime] = None


class CallInDB(CallBase):
    id: UUID
    user_id: Optional[UUID] = None
    created_at: datetime

    model_config = {"from_attributes": True}
