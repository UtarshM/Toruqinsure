from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List, Optional

from app.models.crm import Customer, Visit
from app.schemas.crm import CustomerCreate, VisitCreate, VisitUpdate


async def create_customer(db: AsyncSession, obj_in: CustomerCreate) -> Customer:
    customer = Customer(**obj_in.model_dump())
    db.add(customer)
    await db.flush()
    return customer


async def get_customers(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
) -> List[Customer]:
    stmt = select(Customer).order_by(Customer.created_at.desc())
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_visit(db: AsyncSession, obj_in: VisitCreate) -> Visit:
    visit = Visit(**obj_in.model_dump())
    db.add(visit)
    await db.flush()
    return visit


async def get_visits(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    user_id: Optional[UUID] = None,
) -> List[Visit]:
    stmt = select(Visit).order_by(Visit.scheduled_at.asc())
    if user_id:
        stmt = stmt.where(Visit.user_id == user_id)
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())
