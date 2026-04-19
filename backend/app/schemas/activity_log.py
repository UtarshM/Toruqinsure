from pydantic import BaseModel, ConfigDict
from typing import Optional, Any, Dict
from datetime import datetime
from uuid import UUID

class ActivityLogBase(BaseModel):
    user_id: Optional[UUID] = None
    action: str
    entity_type: str
    entity_id: UUID
    metadata_: Optional[Dict[str, Any]] = None

class ActivityLogCreate(ActivityLogBase):
    pass

class ActivityLogInDB(ActivityLogBase):
    id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
