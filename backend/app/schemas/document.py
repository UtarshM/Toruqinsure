from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID

class DocumentBase(BaseModel):
    entity_type: str
    entity_id: UUID
    file_name: str
    file_path: str
    uploaded_by: Optional[UUID] = None

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    file_name: Optional[str] = None
    # We generally don't update file_path directly; we'd re-upload.

class DocumentInDB(DocumentBase):
    id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
