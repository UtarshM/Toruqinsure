import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify the JWT token sent from the frontend using the Supabase JWT Secret.
    """
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )
        return payload["sub"] # Returns user UUID as string
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(
    user_id: str = Depends(verify_token), 
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Fetch the currently authenticated user from the database.
    """
    stmt = select(User).options(selectinload(User.role)).filter(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return user

def require_permissions(required_permissions: list[str]):
    """
    Dependency generator for RBAC.
    Checks if the user's role contains all of the required permissions.
    """
    async def role_checker(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        if not current_user.role:
            raise HTTPException(status_code=403, detail="User has no assigned role")
            
        # The role's permissions were loaded via selectinload in get_current_user
        user_perms = [p.name for p in current_user.role.permissions]
        
        # Check if all required permissions are in the user's permissions
        if not all(perm in user_perms for perm in required_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
            
        return current_user
        
    return role_checker
