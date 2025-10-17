from fastapi import APIRouter, Depends, HTTPException, status, Security, Header
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from app.deps.db import get_db
from app.deps.auth import bearer_scheme, get_current_user
from app.repositories import user as repo
from app.schemas.user import LoginInput, TokenPair, UserCreate, UserOut
from app.core.security import create_access_token, create_refresh_token, decode_token

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

@router.post("/users", response_model=UserOut, status_code=201)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
):
    """
    Bootstrapping:
    - Se a tabela estiver VAZIA, permite criar usuário sem autenticação (primeiro admin).
    - Se já existir usuário, EXIGE ACCESS TOKEN com role=ADMIN.
    """
    total = await repo.count_all(db)
    if total > 0:
        if not credentials or credentials.scheme.lower() != "bearer":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        token = credentials.credentials
        try:
            payload_token = decode_token(token)
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
        if payload_token.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")

        email = payload_token.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        current_user = await repo.get_by_email(db, email)
        if not current_user or not current_user.is_active:
            raise HTTPException(status_code=401, detail="Inactive or not found")
        if current_user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Not enough permissions")

    exists = await repo.get_by_email(db, payload.email)
    if exists:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    return await repo.create(db, payload)
