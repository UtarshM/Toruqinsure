from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List, Optional
import datetime

from app.models.insurance import Policy
from app.schemas.policy import PolicyCreate, PolicyUpdate

async def get_policy(db: AsyncSession, policy_id: UUID) -> Optional[Policy]:
    result = await db.execute(select(Policy).filter(Policy.id == policy_id))
    return result.scalar_one_or_none()

async def get_policies(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Policy]:
    result = await db.execute(select(Policy).offset(skip).limit(limit))
    return list(result.scalars().all())

async def create_policy(db: AsyncSession, policy_in: PolicyCreate) -> Policy:
    # Convert dates to datetime objects with timezone for PostgreSQL TIMESTAMPTZ compatibility
    start_dt = datetime.datetime.combine(policy_in.start_date, datetime.time.min, tzinfo=datetime.timezone.utc)
    end_dt = datetime.datetime.combine(policy_in.end_date, datetime.time.min, tzinfo=datetime.timezone.utc)
    
    db_obj = Policy(
        lead_id=policy_in.lead_id,
        policy_number=policy_in.policy_number,
        provider=policy_in.provider,
        type=policy_in.type,
        premium_amount=policy_in.premium_amount,
        status=policy_in.status,
        start_date=start_dt,
        end_date=end_dt
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_policy(db: AsyncSession, db_obj: Policy, obj_in: PolicyUpdate) -> Policy:
    update_data = obj_in.model_dump(exclude_unset=True)
    
    # Handle date to datetime conversions for updates if dates are provided
    for field, value in update_data.items():
        if field in ['start_date', 'end_date'] and value is not None:
            dt = datetime.datetime.combine(value, datetime.time.min, tzinfo=datetime.timezone.utc)
            setattr(db_obj, field, dt)
        else:
            setattr(db_obj, field, value)
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
