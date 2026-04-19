from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_user, require_permissions
from app.schemas.policy import PolicyInDB, PolicyCreate, PolicyUpdate
from app.crud import crud_policy
from app.services import policy_service
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[PolicyInDB])
async def read_policies(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve policies.
    """
    policies = await crud_policy.get_policies(db, skip=skip, limit=limit)
    return policies

@router.post("/", response_model=PolicyInDB, dependencies=[Depends(require_permissions(["create_policy"]))])
async def create_policy(
    *,
    db: AsyncSession = Depends(get_db),
    policy_in: PolicyCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create new policy.
    Requires 'create_policy' permission.
    """
    return await policy_service.create_new_policy(db=db, policy_in=policy_in, current_user=current_user)

@router.put("/{policy_id}", response_model=PolicyInDB, dependencies=[Depends(require_permissions(["update_policy"]))])
async def update_policy(
    *,
    db: AsyncSession = Depends(get_db),
    policy_id: UUID,
    policy_in: PolicyUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing policy.
    Requires 'update_policy' permission.
    """
    return await policy_service.update_existing_policy(db=db, policy_id=policy_id, obj_in=policy_in, current_user=current_user)
