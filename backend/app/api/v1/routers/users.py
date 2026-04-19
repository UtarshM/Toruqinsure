from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_user, require_permissions
from app.schemas.user import UserInDB, UserCreate, UserUpdate
from app.crud import crud_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[UserInDB], dependencies=[Depends(require_permissions(["read_users"]))])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    users = await crud_user.get_users(db, skip=skip, limit=limit)
    return users

@router.post("/", response_model=UserInDB, dependencies=[Depends(require_permissions(["create_user"]))])
async def create_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate
):
    # Usually created via Supabase webhook, but this allows admin creation
    db_user = await crud_user.get_user(db, user_id=user_in.id)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return await crud_user.create_user(db=db, obj_in=user_in)

@router.put("/{user_id}", response_model=UserInDB, dependencies=[Depends(require_permissions(["update_user"]))])
async def update_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_id: UUID,
    user_in: UserUpdate
):
    db_user = await crud_user.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return await crud_user.update_user(db=db, db_obj=db_user, obj_in=user_in)
