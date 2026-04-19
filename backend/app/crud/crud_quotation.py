from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List, Optional

from app.models.insurance import Quotation
from app.schemas.quotation import QuotationCreate, QuotationUpdate

async def get_quotation(db: AsyncSession, quotation_id: UUID) -> Optional[Quotation]:
    result = await db.execute(select(Quotation).filter(Quotation.id == quotation_id))
    return result.scalar_one_or_none()

async def get_quotations(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Quotation]:
    result = await db.execute(select(Quotation).offset(skip).limit(limit))
    return list(result.scalars().all())

async def create_quotation(db: AsyncSession, obj_in: QuotationCreate) -> Quotation:
    db_obj = Quotation(
        lead_id=obj_in.lead_id,
        created_by=obj_in.created_by,
        amount=obj_in.amount,
        status=obj_in.status,
        details=obj_in.details
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_quotation(db: AsyncSession, db_obj: Quotation, obj_in: QuotationUpdate) -> Quotation:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
