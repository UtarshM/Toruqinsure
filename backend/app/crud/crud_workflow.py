from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List, Optional

from app.models.workflow import RTOWork, FitnessWork
from app.schemas.workflow import RTOWorkCreate, RTOWorkUpdate, FitnessWorkCreate, FitnessWorkUpdate


async def create_rto_work(db: AsyncSession, obj_in: RTOWorkCreate) -> RTOWork:
    rto = RTOWork(**obj_in.model_dump())
    db.add(rto)
    await db.flush()
    return rto


async def get_rto_works(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
) -> List[RTOWork]:
    stmt = select(RTOWork).order_by(RTOWork.created_at.desc())
    if status:
        stmt = stmt.where(RTOWork.status == status)
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_fitness_work(db: AsyncSession, obj_in: FitnessWorkCreate) -> FitnessWork:
    fitness = FitnessWork(**obj_in.model_dump())
    db.add(fitness)
    await db.flush()
    return fitness


async def get_fitness_works(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
) -> List[FitnessWork]:
    stmt = select(FitnessWork).order_by(FitnessWork.created_at.desc())
    if status:
        stmt = stmt.where(FitnessWork.status == status)
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())
