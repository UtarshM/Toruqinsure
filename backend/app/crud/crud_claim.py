from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List, Optional

from app.models.claim import Claim
from app.schemas.claim import ClaimCreate, ClaimUpdate


async def create_claim(db: AsyncSession, obj_in: ClaimCreate) -> Claim:
    claim = Claim(**obj_in.model_dump())
    db.add(claim)
    await db.flush()
    return claim


async def get_claim(db: AsyncSession, claim_id: UUID) -> Optional[Claim]:
    result = await db.execute(select(Claim).where(Claim.id == claim_id))
    return result.scalar_one_or_none()


async def get_claims(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    policy_id: Optional[UUID] = None,
    lead_id: Optional[UUID] = None,
    status: Optional[str] = None,
) -> List[Claim]:
    stmt = select(Claim).order_by(Claim.filed_date.desc())
    if policy_id:
        stmt = stmt.where(Claim.policy_id == policy_id)
    if lead_id:
        stmt = stmt.where(Claim.lead_id == lead_id)
    if status:
        stmt = stmt.where(Claim.status == status)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_claim(db: AsyncSession, db_obj: Claim, obj_in: ClaimUpdate) -> Claim:
    for field, value in obj_in.model_dump(exclude_unset=True).items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    await db.flush()
    return db_obj
