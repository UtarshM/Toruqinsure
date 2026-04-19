from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_user, require_permissions
from app.schemas.lead import LeadInDB, LeadCreate, LeadUpdate
from app.crud import crud_lead
from app.services import lead_service
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[LeadInDB])
async def read_leads(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve leads.
    """
    leads = await crud_lead.get_leads(db, skip=skip, limit=limit)
    return leads

@router.post("/", response_model=LeadInDB, dependencies=[Depends(require_permissions(["create_lead"]))])
async def create_lead(
    *,
    db: AsyncSession = Depends(get_db),
    lead_in: LeadCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create new lead.
    Requires 'create_lead' permission.
    """
    return await lead_service.create_new_lead(db=db, lead_in=lead_in, current_user=current_user)

@router.put("/{lead_id}", response_model=LeadInDB, dependencies=[Depends(require_permissions(["update_lead"]))])
async def update_lead(
    *,
    db: AsyncSession = Depends(get_db),
    lead_id: UUID,
    lead_in: LeadUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing lead.
    Requires 'update_lead' permission.
    """
    return await lead_service.update_existing_lead(db=db, lead_id=lead_id, obj_in=lead_in, current_user=current_user)
