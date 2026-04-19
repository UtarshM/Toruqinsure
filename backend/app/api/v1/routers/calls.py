from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.schemas.call import CallInDB, CallCreate, CallUpdate
from app.crud import crud_call
from app.services import call_service
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[CallInDB], summary="List call logs")
async def list_calls(
    skip: int = 0,
    limit: int = 50,
    lead_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get call logs. Filter by lead_id to get all calls for a specific lead."""
    return await crud_call.get_calls(db, skip=skip, limit=limit, lead_id=lead_id, user_id=None)


@router.get("/my", response_model=List[CallInDB], summary="My call logs")
async def my_calls(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get only the current user's call logs."""
    return await crud_call.get_calls(db, skip=skip, limit=limit, user_id=current_user.id)


@router.post("/", response_model=CallInDB, summary="Log a call")
async def log_call(
    *,
    db: AsyncSession = Depends(get_db),
    call_in: CallCreate,
    current_user: User = Depends(get_current_user),
):
    """
    Log a completed/missed call.
    Called from the mobile app's 'Log Call' form immediately after calling a lead.
    """
    return await call_service.log_new_call(db=db, call_in=call_in, current_user=current_user)


@router.get("/{call_id}", response_model=CallInDB)
async def get_call(
    call_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    call = await crud_call.get_call(db, call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    return call


@router.put("/{call_id}", response_model=CallInDB, summary="Update call notes/outcome")
async def update_call(
    *,
    db: AsyncSession = Depends(get_db),
    call_id: UUID,
    call_in: CallUpdate,
    current_user: User = Depends(get_current_user),
):
    call = await crud_call.get_call(db, call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    updated = await crud_call.update_call(db=db, db_obj=call, obj_in=call_in)
    await db.commit()
    return updated
