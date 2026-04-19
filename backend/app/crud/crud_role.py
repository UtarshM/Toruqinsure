from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import List, Optional

from app.models.user import Role
from app.schemas.user import RoleCreate, RoleUpdate

async def get_role(db: AsyncSession, role_id: UUID) -> Optional[Role]:
    stmt = select(Role).options(selectinload(Role.permissions)).filter(Role.id == role_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_roles(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Role]:
    stmt = select(Role).options(selectinload(Role.permissions)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def create_role(db: AsyncSession, obj_in: RoleCreate) -> Role:
    db_obj = Role(
        name=obj_in.name,
        description=obj_in.description
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_role(db: AsyncSession, db_obj: Role, obj_in: RoleUpdate) -> Role:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
