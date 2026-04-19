from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List, Optional

from app.models.business import Loan
from app.schemas.business import LoanCreate, LoanUpdate


async def create_loan(db: AsyncSession, obj_in: LoanCreate) -> Loan:
    loan = Loan(**obj_in.model_dump())
    db.add(loan)
    await db.flush()
    return loan


async def get_loans(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
) -> List[Loan]:
    stmt = select(Loan).order_by(Loan.created_at.desc())
    if status:
        stmt = stmt.where(Loan.status == status)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_loan(db: AsyncSession, db_obj: Loan, obj_in: LoanUpdate) -> Loan:
    for field, value in obj_in.model_dump(exclude_unset=True).items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    await db.flush()
    return db_obj
