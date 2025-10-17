from fastapi import Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.deps.db import get_db
from app.repositories.user import get_by_email

async def get_current_user(db: AsyncSession = Depends(get_db), authorization: str | None = None):
    """
    Lê o header Authorization: Bearer <token> e valida o JWT de access.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = await get_by_email(db, email)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive or not found")
    return user

def require_roles(*roles: str):
    async def _checker(user=Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return user
    return _checker
