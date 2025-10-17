from typing import Optional
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password, verify_password

async def count_all(db: AsyncSession) -> int:
    res = await db.execute(select(func.count()).select_from(User))
    return res.scalar_one()

async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
    res = await db.execute(select(User).where(User.email == email))
    return res.scalar_one_or_none()

async def create(db: AsyncSession, data: UserCreate) -> User:
    obj = User(
        email=data.email,
        full_name=data.full_name,
        role=data.role,
        hashed_password=hash_password(data.password),
        is_active=True,
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def authenticate(db: AsyncSession, email: str, password: str) -> Optional[User]:
    user = await get_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user
