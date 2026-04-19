from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.schemas.claim import ClaimInDB, ClaimCreate, ClaimUpdate
from app.crud import crud_claim
from app.models.user import User
from app.services.activity_log_service import log_action

router = APIRouter()


@router.get("/", response_model=List[ClaimInDB])
async def list_claims(
    skip: int = 0,
    limit: int = 50,
    policy_id: Optional[UUID] = None,
    lead_id: Optional[UUID] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await crud_claim.get_claims(db, skip=skip, limit=limit, policy_id=policy_id, lead_id=lead_id, status=status)


@router.post("/", response_model=ClaimInDB)
async def create_claim(
    *,
    db: AsyncSession = Depends(get_db),
    obj_in: ClaimCreate,
    current_user: User = Depends(get_current_user),
):
    claim = await crud_claim.create_claim(db, obj_in=obj_in)
    await log_action(
        db, user=current_user,
        action="created_claim",
        entity_type="claim",
        entity_id=claim.id,
        meta={"customer_name": claim.customer_name, "policy_number": claim.policy_number}
    )
    await db.commit()
    return claim


@router.get("/{claim_id}", response_model=ClaimInDB)
async def get_claim(
    claim_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    claim = await crud_claim.get_claim(db, claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim


@router.put("/{claim_id}", response_model=ClaimInDB)
async def update_claim(
    *,
    db: AsyncSession = Depends(get_db),
    claim_id: UUID,
    obj_in: ClaimUpdate,
    current_user: User = Depends(get_current_user),
):
    claim = await crud_claim.get_claim(db, claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    updated = await crud_claim.update_claim(db, db_obj=claim, obj_in=obj_in)
    await log_action(
        db, user=current_user,
        action="updated_claim",
        entity_type="claim",
        entity_id=updated.id,
        meta={"status": updated.status}
    )
    await db.commit()
    return updated
