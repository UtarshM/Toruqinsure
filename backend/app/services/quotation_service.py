from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from fastapi import HTTPException

from app.crud import crud_quotation, crud_lead
from app.schemas.quotation import QuotationCreate, QuotationUpdate
from app.models.insurance import Quotation
from app.models.user import User
from app.services.activity_log_service import log_action


async def create_new_quotation(
    db: AsyncSession, quotation_in: QuotationCreate, current_user: User
) -> Quotation:
    if quotation_in.lead_id:
        lead = await crud_lead.get_lead(db, quotation_in.lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        if lead.status == "New":
            lead.status = "Quoted"
            db.add(lead)

    quotation_in.created_by = current_user.id
    new_quotation = await crud_quotation.create_quotation(db=db, obj_in=quotation_in)

    await log_action(
        db, user=current_user,
        action="created_quotation",
        entity_type="quotation",
        entity_id=new_quotation.id,
        meta={"amount": str(new_quotation.amount), "lead_id": str(quotation_in.lead_id)},
    )
    await db.commit()
    return new_quotation


async def update_existing_quotation(
    db: AsyncSession, quotation_id: UUID, obj_in: QuotationUpdate, current_user: User
) -> Quotation:
    db_obj = await crud_quotation.get_quotation(db, quotation_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Quotation not found")

    old_status = db_obj.status
    updated = await crud_quotation.update_quotation(db=db, db_obj=db_obj, obj_in=obj_in)

    await log_action(
        db, user=current_user,
        action="updated_quotation",
        entity_type="quotation",
        entity_id=updated.id,
        meta={
            **obj_in.model_dump(exclude_unset=True, exclude_none=True),
            "old_status": old_status,
            "new_status": updated.status,
        },
    )
    await db.commit()
    return updated
