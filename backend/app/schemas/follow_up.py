from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class FollowUpBase(BaseModel):
    lead_id: UUID
    assigned_to: Optional[UUID] = None
    lead_name: Optional[str] = None
    type: str = "call"
    scheduled_at: datetime
    notes: Optional[str] = None
    status: str = "pending"


class FollowUpCreate(FollowUpBase):
    pass


class FollowUpUpdate(BaseModel):
    assigned_to: Optional[UUID] = None
    scheduled_at: Optional[datetime] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    is_overdue: Optional[bool] = None
    completed_at: Optional[datetime] = None


class FollowUpInDB(FollowUpBase):
    id: UUID
    is_overdue: bool
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
