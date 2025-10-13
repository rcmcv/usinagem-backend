from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health")
def healthcheck():
    """
    Endpoint simples para ver se a API está rodando.
    Retorna status e timestamp do servidor.
    """
    return {
        "status": "ok",
        "service": "usinagem-backend",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
