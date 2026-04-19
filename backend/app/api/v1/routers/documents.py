from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_user, require_permissions
from app.schemas.document import DocumentInDB, DocumentCreate, DocumentUpdate
from app.crud import crud_document
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[DocumentInDB], dependencies=[Depends(require_permissions(["read_documents"]))])
async def read_documents(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    documents = await crud_document.get_documents(db, skip=skip, limit=limit)
    return documents

@router.post("/", response_model=DocumentInDB, dependencies=[Depends(require_permissions(["create_document"]))])
async def create_document(
    *,
    db: AsyncSession = Depends(get_db),
    document_in: DocumentCreate,
    current_user: User = Depends(get_current_user)
):
    document_in.uploaded_by = current_user.id
    return await crud_document.create_document(db=db, obj_in=document_in)

@router.put("/{document_id}", response_model=DocumentInDB, dependencies=[Depends(require_permissions(["update_document"]))])
async def update_document(
    *,
    db: AsyncSession = Depends(get_db),
    document_id: UUID,
    document_in: DocumentUpdate
):
    db_document = await crud_document.get_document(db, document_id=document_id)
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    return await crud_document.update_document(db=db, db_obj=db_document, obj_in=document_in)
