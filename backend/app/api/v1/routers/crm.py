from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.schemas.crm import CustomerInDB, CustomerCreate, VisitInDB, VisitCreate
from app.crud import crud_crm
from app.models.user import User

router = APIRouter()

@router.get("/customers/", response_model=List[CustomerInDB])
async def list_customers(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await crud_crm.get_customers(db, skip=skip, limit=limit)

@router.post("/customers/", response_model=CustomerInDB)
async def create_customer(
    obj_in: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = await crud_crm.create_customer(db, obj_in=obj_in)
    await db.commit()
    return customer

@router.get("/visits/", response_model=List[VisitInDB])
async def list_visits(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await crud_crm.get_visits(db, skip=skip, limit=limit)

@router.post("/visits/", response_model=VisitInDB)
async def create_visit(
    obj_in: VisitCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    visit = await crud_crm.create_visit(db, obj_in=obj_in)
    await db.commit()
    return visit
