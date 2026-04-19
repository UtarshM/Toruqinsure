from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from fastapi import HTTPException

from app.crud import crud_policy, crud_lead
from app.schemas.policy import PolicyCreate, PolicyUpdate
from app.models.insurance import Policy
from app.models.user import User
from app.services.activity_log_service import log_action


async def create_new_policy(db: AsyncSession, policy_in: PolicyCreate, current_user: User) -> Policy:
    lead = await crud_lead.get_lead(db, policy_in.lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Assigned Lead not found")

    new_policy = await crud_policy.create_policy(db=db, policy_in=policy_in)

    # Auto-update lead status to Converted
    if lead.status in ("New", "Quoted"):
        lead.status = "Converted"
        db.add(lead)

    await log_action(
        db, user=current_user,
        action="created_policy",
        entity_type="policy",
        entity_id=new_policy.id,
        meta={
            "policy_number": new_policy.policy_number,
            "provider": new_policy.provider,
            "lead_id": str(lead.id),
        },
    )
    await db.commit()
    return new_policy


async def update_existing_policy(
    db: AsyncSession, policy_id: UUID, obj_in: PolicyUpdate, current_user: User
) -> Policy:
    db_obj = await crud_policy.get_policy(db, policy_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Policy not found")

    old_status = db_obj.status
    updated_policy = await crud_policy.update_policy(db=db, db_obj=db_obj, obj_in=obj_in)

    await log_action(
        db, user=current_user,
        action="updated_policy",
        entity_type="policy",
        entity_id=updated_policy.id,
        meta={
            **obj_in.model_dump(exclude_unset=True, exclude_none=True),
            "old_status": old_status,
            "new_status": updated_policy.status,
        },
    )
    await db.commit()
    return updated_policy
