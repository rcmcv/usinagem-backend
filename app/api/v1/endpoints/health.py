from fastapi import APIRouter, Depends
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.deps.db import get_db

router = APIRouter()

@router.get("/health")
def healthcheck(db: Session = Depends(get_db)):
    """
    Ping simples no DB: SELECT 1
    """
    try:
        db.scalar(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    return {
        "status": "ok",
        "service": "usinagem-backend",
        "db_ok": db_ok,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
