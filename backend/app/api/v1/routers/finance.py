from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.schemas.business import TransactionInDB, TransactionCreate, LoanInDB, LoanCreate, LoanUpdate
from app.crud import crud_transaction, crud_loan
from app.models.user import User
from app.services.activity_log_service import log_action

router = APIRouter()

@router.get("/transactions/", response_model=List[TransactionInDB])
async def list_transactions(
    skip: int = 0,
    limit: int = 50,
    type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await crud_transaction.get_transactions(db, skip=skip, limit=limit, type=type)

@router.post("/transactions/", response_model=TransactionInDB)
async def create_transaction(
    *,
    db: AsyncSession = Depends(get_db),
    obj_in: TransactionCreate,
    current_user: User = Depends(get_current_user),
):
    transaction = await crud_transaction.create_transaction(db, obj_in=obj_in)
    await db.commit()
    return transaction

@router.get("/loans/", response_model=List[LoanInDB])
async def list_loans(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await crud_loan.get_loans(db, skip=skip, limit=limit, status=status)

@router.post("/loans/", response_model=LoanInDB)
async def create_loan(
    *,
    db: AsyncSession = Depends(get_db),
    obj_in: LoanCreate,
    current_user: User = Depends(get_current_user),
):
    loan = await crud_loan.create_loan(db, obj_in=obj_in)
    await log_action(db, user=current_user, action="created_loan", entity_type="loan", entity_id=loan.id)
    await db.commit()
    return loan
