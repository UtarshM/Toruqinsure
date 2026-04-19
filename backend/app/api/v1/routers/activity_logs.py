from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_user, require_permissions
from app.schemas.activity_log import ActivityLogInDB, ActivityLogCreate
from app.crud import crud_activity_log
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[ActivityLogInDB], dependencies=[Depends(require_permissions(["read_activity_logs"]))])
async def read_activity_logs(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    activity_logs = await crud_activity_log.get_activity_logs(db, skip=skip, limit=limit)
    return activity_logs

@router.post("/", response_model=ActivityLogInDB, dependencies=[Depends(require_permissions(["create_activity_log"]))])
async def create_activity_log(
    *,
    db: AsyncSession = Depends(get_db),
    activity_log_in: ActivityLogCreate,
    current_user: User = Depends(get_current_user)
):
    activity_log_in.user_id = current_user.id
    return await crud_activity_log.create_activity_log(db=db, obj_in=activity_log_in)
