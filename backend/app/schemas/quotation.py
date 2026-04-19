from pydantic import BaseModel, ConfigDict
from typing import Optional, Any, Dict
from datetime import datetime
from uuid import UUID
from decimal import Decimal

class QuotationBase(BaseModel):
    lead_id: Optional[UUID] = None
    created_by: Optional[UUID] = None
    amount: Decimal
    status: Optional[str] = "Draft"
    details: Optional[Dict[str, Any]] = None

class QuotationCreate(QuotationBase):
    pass

class QuotationUpdate(BaseModel):
    amount: Optional[Decimal] = None
    status: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class QuotationInDB(QuotationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
