from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List, Optional

from app.models.user import Permission
from app.schemas.user import PermissionCreate, PermissionUpdate

async def get_permission(db: AsyncSession, permission_id: UUID) -> Optional[Permission]:
    result = await db.execute(select(Permission).filter(Permission.id == permission_id))
    return result.scalar_one_or_none()

async def get_permissions(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Permission]:
    result = await db.execute(select(Permission).offset(skip).limit(limit))
    return list(result.scalars().all())

async def create_permission(db: AsyncSession, obj_in: PermissionCreate) -> Permission:
    db_obj = Permission(
        name=obj_in.name,
        description=obj_in.description
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_permission(db: AsyncSession, db_obj: Permission, obj_in: PermissionUpdate) -> Permission:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
