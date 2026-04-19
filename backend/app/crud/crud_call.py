from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List, Optional

from app.models.call import Call
from app.schemas.call import CallCreate, CallUpdate


async def create_call(db: AsyncSession, obj_in: CallCreate, user_id: UUID) -> Call:
    call = Call(**obj_in.model_dump(), user_id=user_id)
    db.add(call)
    await db.flush()
    return call


async def get_call(db: AsyncSession, call_id: UUID) -> Optional[Call]:
    result = await db.execute(select(Call).where(Call.id == call_id))
    return result.scalar_one_or_none()


async def get_calls(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    lead_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None,
) -> List[Call]:
    stmt = select(Call).order_by(Call.created_at.desc())
    if lead_id:
        stmt = stmt.where(Call.lead_id == lead_id)
    if user_id:
        stmt = stmt.where(Call.user_id == user_id)
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_call(db: AsyncSession, db_obj: Call, obj_in: CallUpdate) -> Call:
    for field, value in obj_in.model_dump(exclude_unset=True).items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    await db.flush()
    return db_obj
