from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List, Optional

from app.models.business import Transaction
from app.schemas.business import TransactionCreate


async def create_transaction(db: AsyncSession, obj_in: TransactionCreate) -> Transaction:
    transaction = Transaction(**obj_in.model_dump())
    db.add(transaction)
    await db.flush()
    return transaction


async def get_transactions(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    type: Optional[str] = None,
    user_id: Optional[UUID] = None,
) -> List[Transaction]:
    stmt = select(Transaction).order_by(Transaction.date.desc())
    if type:
        stmt = stmt.where(Transaction.type == type)
    if user_id:
        stmt = stmt.where(Transaction.user_id == user_id)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())
