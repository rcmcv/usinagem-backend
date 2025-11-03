from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps.db import get_db
from app.deps.auth import get_current_user, require_roles
from app.deps.pagination import get_pagination
from app.core.api import ok, created
from app.repositories import contrato_hh_preco as repo
from app.schemas.contrato_hh_preco import (
    ContratoHHPrecoCreate, ContratoHHPrecoUpdate, ContratoHHPrecoOut
)

router = APIRouter()

@router.post(
    "/contratos/hh-precos",
    status_code=status.HTTP_201_CREATED,
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def create_contrato_hh_preco(
    payload: ContratoHHPrecoCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    obj = await repo.create(db, payload)
    data = {
        "id": obj.id,
        "contrato_id": obj.contrato_id,
        "maquina_id": obj.maquina_id,
        "tipo_hh": obj.tipo_hh,
        "uom_id": obj.uom_id,
        "preco_hora": float(obj.preco_hora),
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
        "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
    }
    return created(data=data, message="Preço de HH por máquina criado com sucesso.", request=request)

@router.get("/contratos/hh-precos", response_model=None)
async def list_contrato_hh_precos(
    request: Request,
    pagination = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
    contrato_id: int | None = Query(None, ge=1),
    maquina_id: int | None = Query(None, ge=1),
    tipo_hh: str | None = Query(None),
):
    items = await repo.list_(db, skip=pagination.skip, limit=pagination.limit,
                             contrato_id=contrato_id, maquina_id=maquina_id, tipo_hh=tipo_hh)
    meta = {"page": pagination.page, "size": pagination.size, "count": len(items)}
    data = [
        {
            "id": i.id,
            "contrato_id": i.contrato_id,
            "maquina_id": i.maquina_id,
            "tipo_hh": i.tipo_hh,
            "uom_id": i.uom_id,
            "preco_hora": float(i.preco_hora),
            "created_at": i.created_at.isoformat() if i.created_at else None,
            "updated_at": i.updated_at.isoformat() if i.updated_at else None,
        } for i in items
    ]
    return ok(data=data, meta=meta, request=request)

@router.get("/contratos/hh-precos/{preco_id}", response_model=ContratoHHPrecoOut)
async def get_contrato_hh_preco(
    preco_id: int,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
):
    obj = await repo.get(db, preco_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Preço de HH de contrato não encontrado")
    return obj

@router.put(
    "/contratos/hh-precos/{preco_id}",
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def update_contrato_hh_preco(
    preco_id: int,
    payload: ContratoHHPrecoUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    obj = await repo.update(db, preco_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Preço de HH de contrato não encontrado")
    data = {
        "id": obj.id,
        "contrato_id": obj.contrato_id,
        "maquina_id": obj.maquina_id,
        "tipo_hh": obj.tipo_hh,
        "uom_id": obj.uom_id,
        "preco_hora": float(obj.preco_hora),
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
        "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
    }
    return ok(data=data, message="Preço de HH por máquina atualizado com sucesso.", request=request)

@router.delete(
    "/contratos/hh-precos/{preco_id}",
    status_code=status.HTTP_200_OK,
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def delete_contrato_hh_preco(
    preco_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    removed = await repo.delete(db, preco_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Preço de HH de contrato não encontrado")
    return ok(message="Preço de HH por máquina removido com sucesso.", data=None, request=request)
