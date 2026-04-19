from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from fastapi import HTTPException

from app.crud import crud_lead
from app.schemas.lead import LeadCreate, LeadUpdate
from app.models.insurance import Lead
from app.models.user import User
from app.services.activity_log_service import log_action


async def create_new_lead(db: AsyncSession, lead_in: LeadCreate, current_user: User) -> Lead:
    new_lead = await crud_lead.create_lead(db=db, lead_in=lead_in, user_id=current_user.id)

    await log_action(
        db, user=current_user,
        action="created_lead",
        entity_type="lead",
        entity_id=new_lead.id,
        meta={"client_name": new_lead.client_name, "status": new_lead.status},
    )
    await db.commit()
    return new_lead


async def update_existing_lead(
    db: AsyncSession, lead_id: UUID, obj_in: LeadUpdate, current_user: User
) -> Lead:
    db_obj = await crud_lead.get_lead(db, lead_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Lead not found")

    old_status = db_obj.status
    updated_lead = await crud_lead.update_lead(db=db, db_obj=db_obj, obj_in=obj_in)

    await log_action(
        db, user=current_user,
        action="updated_lead",
        entity_type="lead",
        entity_id=updated_lead.id,
        meta={
            **obj_in.model_dump(exclude_unset=True),
            "old_status": old_status,
            "new_status": updated_lead.status,
        },
    )
    await db.commit()
    return updated_lead


async def delete_lead(db: AsyncSession, lead_id: UUID, current_user: User) -> None:
    db_obj = await crud_lead.get_lead(db, lead_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Lead not found")

    await log_action(
        db, user=current_user,
        action="deleted_lead",
        entity_type="lead",
        entity_id=db_obj.id,
        meta={"client_name": db_obj.client_name},
    )
    await db.delete(db_obj)
    await db.commit()
