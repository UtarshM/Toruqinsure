from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_user, require_permissions
from app.schemas.user import PermissionInDB, PermissionCreate, PermissionUpdate
from app.crud import crud_permission

router = APIRouter()

@router.get("/", response_model=List[PermissionInDB], dependencies=[Depends(require_permissions(["read_permissions"]))])
async def read_permissions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    permissions = await crud_permission.get_permissions(db, skip=skip, limit=limit)
    return permissions

@router.post("/", response_model=PermissionInDB, dependencies=[Depends(require_permissions(["create_permission"]))])
async def create_permission(
    *,
    db: AsyncSession = Depends(get_db),
    permission_in: PermissionCreate
):
    return await crud_permission.create_permission(db=db, obj_in=permission_in)

@router.put("/{permission_id}", response_model=PermissionInDB, dependencies=[Depends(require_permissions(["update_permission"]))])
async def update_permission(
    *,
    db: AsyncSession = Depends(get_db),
    permission_id: UUID,
    permission_in: PermissionUpdate
):
    db_permission = await crud_permission.get_permission(db, permission_id=permission_id)
    if not db_permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return await crud_permission.update_permission(db=db, db_obj=db_permission, obj_in=permission_in)
