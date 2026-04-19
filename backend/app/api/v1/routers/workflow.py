from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.schemas.workflow import RTOWorkInDB, RTOWorkCreate, FitnessWorkInDB, FitnessWorkCreate
from app.crud import crud_workflow
from app.models.user import User

router = APIRouter()

@router.get("/rto/", response_model=List[RTOWorkInDB])
async def list_rto_works(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await crud_workflow.get_rto_works(db, skip=skip, limit=limit, status=status)

@router.post("/rto/", response_model=RTOWorkInDB)
async def create_rto_work(
    obj_in: RTOWorkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rto = await crud_workflow.create_rto_work(db, obj_in=obj_in)
    await db.commit()
    return rto

@router.get("/fitness/", response_model=List[FitnessWorkInDB])
async def list_fitness_works(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await crud_workflow.get_fitness_works(db, skip=skip, limit=limit, status=status)

@router.post("/fitness/", response_model=FitnessWorkInDB)
async def create_fitness_work(
    obj_in: FitnessWorkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    fitness = await crud_workflow.create_fitness_work(db, obj_in=obj_in)
    await db.commit()
    return fitness
