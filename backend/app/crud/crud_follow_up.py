from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List, Optional
from datetime import datetime

from app.models.follow_up import FollowUp
from app.schemas.follow_up import FollowUpCreate, FollowUpUpdate


async def create_follow_up(db: AsyncSession, obj_in: FollowUpCreate) -> FollowUp:
    follow_up = FollowUp(**obj_in.model_dump())
    db.add(follow_up)
    await db.flush()
    return follow_up


async def get_follow_up(db: AsyncSession, follow_up_id: UUID) -> Optional[FollowUp]:
    result = await db.execute(select(FollowUp).where(FollowUp.id == follow_up_id))
    return result.scalar_one_or_none()


async def get_follow_ups(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    lead_id: Optional[UUID] = None,
    assigned_to: Optional[UUID] = None,
    status: Optional[str] = None,
) -> List[FollowUp]:
    stmt = select(FollowUp).order_by(FollowUp.scheduled_at.asc())
    if lead_id:
        stmt = stmt.where(FollowUp.lead_id == lead_id)
    if assigned_to:
        stmt = stmt.where(FollowUp.assigned_to == assigned_to)
    if status:
        stmt = stmt.where(FollowUp.status == status)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_follow_up(db: AsyncSession, db_obj: FollowUp, obj_in: FollowUpUpdate) -> FollowUp:
    for field, value in obj_in.model_dump(exclude_unset=True).items():
        setattr(db_obj, field, value)
    
    if obj_in.status == 'completed' and not db_obj.completed_at:
        db_obj.completed_at = datetime.now()
        
    db.add(db_obj)
    await db.flush()
    return db_obj
