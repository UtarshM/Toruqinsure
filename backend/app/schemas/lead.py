from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID

class LeadBase(BaseModel):
    client_name: str
    client_email: Optional[EmailStr] = None
    client_phone: Optional[str] = None
    status: Optional[str] = "New"

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    client_name: Optional[str] = None
    client_email: Optional[EmailStr] = None
    client_phone: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[UUID] = None

class LeadInDB(LeadBase):
    id: UUID
    assigned_to: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
