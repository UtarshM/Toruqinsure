from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from fastapi import HTTPException

from app.crud import crud_document
from app.schemas.document import DocumentCreate
from app.models.insurance import Document
from app.models.user import User
from app.services.activity_log_service import log_action


async def create_document_record(
    db: AsyncSession, document_in: DocumentCreate, current_user: User
) -> Document:
    document_in.uploaded_by = current_user.id
    new_doc = await crud_document.create_document(db=db, obj_in=document_in)

    await log_action(
        db, user=current_user,
        action="uploaded_document",
        entity_type=document_in.entity_type,
        entity_id=document_in.entity_id,
        meta={"file_name": new_doc.file_name, "file_path": new_doc.file_path},
    )
    await db.commit()
    return new_doc


async def delete_document_record(
    db: AsyncSession, document_id: UUID, current_user: User
) -> None:
    db_obj = await crud_document.get_document(db, document_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Document not found")

    await log_action(
        db, user=current_user,
        action="deleted_document",
        entity_type=db_obj.entity_type,
        entity_id=db_obj.entity_id,
        meta={"file_name": db_obj.file_name},
    )
    await db.delete(db_obj)
    await db.commit()
