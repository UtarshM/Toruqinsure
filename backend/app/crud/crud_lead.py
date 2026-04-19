from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List, Optional

from app.models.insurance import Lead
from app.schemas.lead import LeadCreate, LeadUpdate

async def get_lead(db: AsyncSession, lead_id: UUID) -> Optional[Lead]:
    result = await db.execute(select(Lead).filter(Lead.id == lead_id))
    return result.scalar_one_or_none()

async def get_leads(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Lead]:
    result = await db.execute(select(Lead).offset(skip).limit(limit))
    return list(result.scalars().all())

async def create_lead(db: AsyncSession, lead_in: LeadCreate, user_id: UUID) -> Lead:
    db_obj = Lead(
        client_name=lead_in.client_name,
        client_email=lead_in.client_email,
        client_phone=lead_in.client_phone,
        status=lead_in.status,
        assigned_to=user_id
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_lead(db: AsyncSession, db_obj: Lead, obj_in: LeadUpdate) -> Lead:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
