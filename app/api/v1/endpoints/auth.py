from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.db import get_db
from app.deps.auth import get_current_user
from app.repositories import user as repo
from app.schemas.user import LoginInput, TokenPair, UserCreate, UserOut
from app.core.security import create_access_token, create_refresh_token, decode_token
from jose import JWTError

router = APIRouter()

@router.post("/auth/login", response_model=TokenPair)
async def login(payload: LoginInput, db: AsyncSession = Depends(get_db)):
    user = await repo.authenticate(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return TokenPair(
        access_token=create_access_token(user.email, extra={"role": user.role}),
        refresh_token=create_refresh_token(user.email),
    )

@router.post("/auth/refresh", response_model=TokenPair)
async def refresh(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing refresh token")
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    # Gera novos tokens
    return TokenPair(
        access_token=create_access_token(email),
        refresh_token=create_refresh_token(email),
    )

@router.get("/auth/me", response_model=UserOut)
async def me(user=Depends(get_current_user)):
    return user

# (Provisório) endpoint para criar o primeiro usuário (abriremos depois só p/ ADMIN)
@router.post("/users", response_model=UserOut, status_code=201)
async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    exists = await repo.get_by_email(db, payload.email)
    if exists:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    return await repo.create(db, payload)
