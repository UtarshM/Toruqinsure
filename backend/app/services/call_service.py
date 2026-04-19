from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime

from app.crud import crud_call
from app.crud.crud_lead import get_lead, update_lead
from app.schemas.call import CallCreate
from app.schemas.lead import LeadUpdate
from app.models.call import Call
from app.models.user import User
from app.services.activity_log_service import log_action


async def log_new_call(db: AsyncSession, call_in: CallCreate, current_user: User) -> Call:
    """
    Save a call log entry.
    Side effects:
    - If outcome is 'callback' and follow_up_date set, updates lead status to 'Contacted'.
    - Writes activity log.
    """
    new_call = await crud_call.create_call(db=db, obj_in=call_in, user_id=current_user.id)

    # If linked to a lead, auto-update lead status to 'Contacted'
    if call_in.lead_id:
        lead = await get_lead(db, call_in.lead_id)
        if lead and lead.status == 'New':
            lead.status = 'Contacted'
            db.add(lead)

    await log_action(
        db, user=current_user,
        action="logged_call",
        entity_type="call",
        entity_id=new_call.id,
        meta={
            "lead_name": call_in.lead_name,
            "outcome": call_in.outcome,
            "status": call_in.status,
            "follow_up_date": str(call_in.follow_up_date) if call_in.follow_up_date else None,
        },
    )
    await db.commit()
    return new_call
