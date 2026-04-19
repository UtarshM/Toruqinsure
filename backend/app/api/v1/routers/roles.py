from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_user, require_permissions
from app.schemas.user import RoleInDB, RoleCreate, RoleUpdate
from app.crud import crud_role

router = APIRouter()

@router.get("/", response_model=List[RoleInDB], dependencies=[Depends(require_permissions(["read_roles"]))])
async def read_roles(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    roles = await crud_role.get_roles(db, skip=skip, limit=limit)
    return roles

@router.post("/", response_model=RoleInDB, dependencies=[Depends(require_permissions(["create_role"]))])
async def create_role(
    *,
    db: AsyncSession = Depends(get_db),
    role_in: RoleCreate
):
    return await crud_role.create_role(db=db, obj_in=role_in)

@router.put("/{role_id}", response_model=RoleInDB, dependencies=[Depends(require_permissions(["update_role"]))])
async def update_role(
    *,
    db: AsyncSession = Depends(get_db),
    role_id: UUID,
    role_in: RoleUpdate
):
    db_role = await crud_role.get_role(db, role_id=role_id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    return await crud_role.update_role(db=db, db_obj=db_role, obj_in=role_in)
