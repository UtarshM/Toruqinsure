"""
File Storage Router
-------------------
Handles all file upload/download for documents (KYC, policies, claims, etc.)
using Supabase Storage as the backend.

Folder structure in Supabase bucket (bucket name: "documents"):
  /leads/{lead_id}/{filename}
  /policies/{policy_id}/{filename}
  /kyc/{user_id}/{filename}
  /quotations/{quotation_id}/{filename}
"""
import os
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from supabase import create_client, Client

from app.core.config import settings
from app.core.database import get_db
from app.api.dependencies import get_current_user, require_permissions
from app.schemas.document import DocumentInDB, DocumentCreate
from app.services import document_service
from app.models.user import User

router = APIRouter()

BUCKET_NAME = "documents"

# Valid entity types map to their storage folder
ENTITY_FOLDERS = {
    "lead": "leads",
    "policy": "policies",
    "quotation": "quotations",
    "kyc": "kyc",
    "claim": "claims",
}


def get_supabase_client() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


def _build_storage_path(entity_type: str, entity_id: str, filename: str) -> str:
    """Construct the path inside the Supabase Storage bucket."""
    folder = ENTITY_FOLDERS.get(entity_type, "misc")
    # Sanitise filename: replace spaces, keep extension
    safe_name = filename.replace(" ", "_")
    unique_name = f"{uuid.uuid4().hex}_{safe_name}"
    return f"{folder}/{entity_id}/{unique_name}"


@router.post("/upload", response_model=DocumentInDB, summary="Upload a file to Supabase Storage")
async def upload_file(
    entity_type: str = Form(..., description="Type: lead | policy | quotation | kyc | claim"),
    entity_id: str = Form(..., description="UUID of the related entity"),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions(["create_document"])),
):
    """
    1. Uploads the file to Supabase Storage.
    2. Saves a Document record in PostgreSQL.
    3. Writes an ActivityLog entry.
    Returns the Document row including the storage path.
    """
    if entity_type not in ENTITY_FOLDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid entity_type. Must be one of: {list(ENTITY_FOLDERS.keys())}",
        )

    # Read file bytes
    contents = await file.read()
    if len(contents) > 20 * 1024 * 1024:  # 20 MB limit
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 20 MB.")

    storage_path = _build_storage_path(entity_type, entity_id, file.filename or "upload")

    # Upload to Supabase Storage
    supabase: Client = get_supabase_client()
    try:
        supabase.storage.from_(BUCKET_NAME).upload(
            path=storage_path,
            file=contents,
            file_options={"content-type": file.content_type or "application/octet-stream"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage upload failed: {str(e)}")

    # Save document record to DB
    doc_in = DocumentCreate(
        entity_type=entity_type,
        entity_id=uuid.UUID(entity_id),
        file_name=file.filename or "upload",
        file_path=storage_path,
        uploaded_by=current_user.id,
    )
    return await document_service.create_document_record(db=db, document_in=doc_in, current_user=current_user)


@router.get("/{document_id}/signed-url", summary="Get a temporary signed URL for a file")
async def get_signed_url(
    document_id: uuid.UUID,
    expires_in: int = 3600,  # seconds — default 1 hour
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generates a temporary, expiring signed URL for secure file access.
    The file is NEVER made public — all access goes through this endpoint.
    """
    from app.crud import crud_document
    doc = await crud_document.get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    supabase: Client = get_supabase_client()
    try:
        response = supabase.storage.from_(BUCKET_NAME).create_signed_url(
            path=doc.file_path,
            expires_in=expires_in,
        )
        signed_url = response.get("signedURL") or response.get("signed_url")
        if not signed_url:
            raise ValueError("Supabase did not return a signed URL")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not generate signed URL: {str(e)}")

    return {
        "document_id": str(document_id),
        "file_name": doc.file_name,
        "signed_url": signed_url,
        "expires_in_seconds": expires_in,
    }


@router.delete("/{document_id}", summary="Delete a document record and its file from storage")
async def delete_file(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions(["delete_document"])),
):
    """
    Deletes the file from Supabase Storage AND removes the Document record from the DB.
    """
    from app.crud import crud_document
    doc = await crud_document.get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Remove from Supabase Storage first
    supabase: Client = get_supabase_client()
    try:
        supabase.storage.from_(BUCKET_NAME).remove([doc.file_path])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage deletion failed: {str(e)}")

    # Delete DB record + log activity
    await document_service.delete_document_record(db=db, document_id=document_id, current_user=current_user)

    return {"detail": "Document deleted successfully", "document_id": str(document_id)}
