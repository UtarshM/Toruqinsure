from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_user, require_permissions
from app.schemas.quotation import QuotationInDB, QuotationCreate, QuotationUpdate
from app.crud import crud_quotation
from app.services import quotation_service
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[QuotationInDB], dependencies=[Depends(require_permissions(["read_quotations"]))])
async def read_quotations(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await crud_quotation.get_quotations(db, skip=skip, limit=limit)


@router.get("/{quotation_id}", response_model=QuotationInDB, dependencies=[Depends(require_permissions(["read_quotations"]))])
async def read_quotation(quotation_id: UUID, db: AsyncSession = Depends(get_db)):
    db_obj = await crud_quotation.get_quotation(db, quotation_id=quotation_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return db_obj


@router.post("/", response_model=QuotationInDB, dependencies=[Depends(require_permissions(["create_quotation"]))])
async def create_quotation(
    *,
    db: AsyncSession = Depends(get_db),
    quotation_in: QuotationCreate,
    current_user: User = Depends(get_current_user),
):
    return await quotation_service.create_new_quotation(db=db, quotation_in=quotation_in, current_user=current_user)


@router.put("/{quotation_id}", response_model=QuotationInDB, dependencies=[Depends(require_permissions(["update_quotation"]))])
async def update_quotation(
    *,
    db: AsyncSession = Depends(get_db),
    quotation_id: UUID,
    quotation_in: QuotationUpdate,
    current_user: User = Depends(get_current_user),
):
    return await quotation_service.update_existing_quotation(
        db=db, quotation_id=quotation_id, obj_in=quotation_in, current_user=current_user
    )
