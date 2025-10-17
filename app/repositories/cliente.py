from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteUpdate

def create(db: Session, data: ClienteCreate) -> Cliente:
    obj = Cliente(nome=data.nome, email=data.email, telefone=data.telefone)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def get(db: Session, cliente_id: int) -> Optional[Cliente]:
    return db.get(Cliente, cliente_id)

def list_(db: Session, skip: int = 0, limit: int = 50) -> List[Cliente]:
    return db.query(Cliente).offset(skip).limit(limit).all()

def update(db: Session, cliente_id: int, data: ClienteUpdate) -> Optional[Cliente]:
    obj = db.get(Cliente, cliente_id)
    if not obj:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj

def delete(db: Session, cliente_id: int) -> bool:
    obj = db.get(Cliente, cliente_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True
