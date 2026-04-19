from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.schemas.user import UserInDB
from app.crud import crud_user
from app.models.user import User

router = APIRouter()


@router.get("/me", response_model=UserInDB, summary="Get current user profile")
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """
    Returns the currently authenticated user's profile including their role and permissions.
    This is called by the frontend immediately after login to hydrate the auth store.
    """
    return current_user
