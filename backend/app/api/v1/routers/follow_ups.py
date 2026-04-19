from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.schemas.follow_up import FollowUpInDB, FollowUpCreate, FollowUpUpdate
from app.crud import crud_follow_up
from app.models.user import User
from app.services.activity_log_service import log_action

router = APIRouter()


@router.get("/", response_model=List[FollowUpInDB])
async def list_follow_ups(
    skip: int = 0,
    limit: int = 50,
    lead_id: Optional[UUID] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await crud_follow_up.get_follow_ups(db, skip=skip, limit=limit, lead_id=lead_id, status=status)


@router.post("/", response_model=FollowUpInDB)
async def create_follow_up(
    *,
    db: AsyncSession = Depends(get_db),
    obj_in: FollowUpCreate,
    current_user: User = Depends(get_current_user),
):
    follow_up = await crud_follow_up.create_follow_up(db, obj_in=obj_in)
    await log_action(
        db, user=current_user,
        action="created_follow_up",
        entity_type="follow_up",
        entity_id=follow_up.id,
        meta={"lead_name": follow_up.lead_name, "scheduled_at": str(follow_up.scheduled_at)}
    )
    await db.commit()
    return follow_up


@router.get("/{follow_up_id}", response_model=FollowUpInDB)
async def get_follow_up(
    follow_up_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    follow_up = await crud_follow_up.get_follow_up(db, follow_up_id)
    if not follow_up:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    return follow_up


@router.put("/{follow_up_id}", response_model=FollowUpInDB)
async def update_follow_up(
    *,
    db: AsyncSession = Depends(get_db),
    follow_up_id: UUID,
    obj_in: FollowUpUpdate,
    current_user: User = Depends(get_current_user),
):
    follow_up = await crud_follow_up.get_follow_up(db, follow_up_id)
    if not follow_up:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    
    updated = await crud_follow_up.update_follow_up(db, db_obj=follow_up, obj_in=obj_in)
    await log_action(
        db, user=current_user,
        action="updated_follow_up",
        entity_type="follow_up",
        entity_id=updated.id,
        meta={"status": updated.status}
    )
    await db.commit()
    return updated
