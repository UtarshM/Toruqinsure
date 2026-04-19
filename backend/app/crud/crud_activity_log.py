from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List, Optional

from app.models.insurance import ActivityLog
from app.schemas.activity_log import ActivityLogCreate

async def get_activity_log(db: AsyncSession, log_id: UUID) -> Optional[ActivityLog]:
    result = await db.execute(select(ActivityLog).filter(ActivityLog.id == log_id))
    return result.scalar_one_or_none()

async def get_activity_logs(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ActivityLog]:
    result = await db.execute(select(ActivityLog).offset(skip).limit(limit))
    return list(result.scalars().all())

async def create_activity_log(db: AsyncSession, obj_in: ActivityLogCreate) -> ActivityLog:
    db_obj = ActivityLog(
        user_id=obj_in.user_id,
        action=obj_in.action,
        entity_type=obj_in.entity_type,
        entity_id=obj_in.entity_id,
        metadata_=obj_in.metadata_
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
