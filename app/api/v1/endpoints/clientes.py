from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps.db import get_db
from app.schemas.cliente import ClienteCreate, ClienteOut, ClienteUpdate
from app.repositories import cliente as repo

router = APIRouter()

@router.post("/clientes", response_model=ClienteOut, status_code=status.HTTP_201_CREATED)
async def create_cliente(payload: ClienteCreate, db: AsyncSession = Depends(get_db)):
    return await repo.create(db, payload)

@router.get("/clientes", response_model=list[ClienteOut])
async def list_clientes(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    return await repo.list_(db, skip=skip, limit=limit)

@router.get("/clientes/{cliente_id}", response_model=ClienteOut)
async def get_cliente(cliente_id: int, db: AsyncSession = Depends(get_db)):
    obj = await repo.get(db, cliente_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return obj

@router.put("/clientes/{cliente_id}", response_model=ClienteOut)
async def update_cliente(cliente_id: int, payload: ClienteUpdate, db: AsyncSession = Depends(get_db)):
    obj = await repo.update(db, cliente_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return obj

@router.delete("/clientes/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cliente(cliente_id: int, db: AsyncSession = Depends(get_db)):
    ok = await repo.delete(db, cliente_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return None
