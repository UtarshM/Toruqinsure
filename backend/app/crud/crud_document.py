from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List, Optional

from app.models.insurance import Document
from app.schemas.document import DocumentCreate, DocumentUpdate

async def get_document(db: AsyncSession, document_id: UUID) -> Optional[Document]:
    result = await db.execute(select(Document).filter(Document.id == document_id))
    return result.scalar_one_or_none()

async def get_documents(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Document]:
    result = await db.execute(select(Document).offset(skip).limit(limit))
    return list(result.scalars().all())

async def create_document(db: AsyncSession, obj_in: DocumentCreate) -> Document:
    db_obj = Document(
        entity_type=obj_in.entity_type,
        entity_id=obj_in.entity_id,
        file_name=obj_in.file_name,
        file_path=obj_in.file_path,
        uploaded_by=obj_in.uploaded_by
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_document(db: AsyncSession, db_obj: Document, obj_in: DocumentUpdate) -> Document:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
