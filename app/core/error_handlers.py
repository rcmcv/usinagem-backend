# app/core/error_handlers.py

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from sqlalchemy.exc import IntegrityError  # <-- NOVO
from app.core.api import fail


def _msg_unique(e_msg: str) -> str:
    txt = (e_msg or "").lower()
    if "contrato_hh_precos" in txt:
        return "Já existe um preço de HH para esta combinação (Contrato, Máquina, Tipo de Hora)."
    if "contrato_material_precos" in txt:
        return "Já existe um preço de material para esta combinação (Contrato, Material)."
    if "unique" in txt or "duplicate key" in txt:
        return "Registro duplicado: violação de unicidade."
    return "Violação de unicidade."

def _msg_fk(e_msg: str) -> str:
    return "Violação de integridade referencial: verifique se os IDs relacionados existem."


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exc_handler(request: Request, exc: StarletteHTTPException):
        payload = fail(
            message=exc.detail if isinstance(exc.detail, str) else "Erro HTTP",
            errors=None if isinstance(exc.detail, str) else exc.detail,
            status_code=exc.status_code,
            request=request,
        )
        return JSONResponse(status_code=exc.status_code, content=payload)

    @app.exception_handler(RequestValidationError)
    async def validation_exc_handler(request: Request, exc: RequestValidationError):
        payload = fail(
            message="Erro de validação",
            errors=exc.errors(),
            status_code=422,
            request=request,
        )
        return JSONResponse(status_code=422, content=payload)

    # === NOVO: handler específico para erros de integridade (UNIQUE / FK etc.) ===
    @app.exception_handler(IntegrityError)
    async def integrity_exc_handler(request: Request, exc: IntegrityError):
        raw = ""
        if getattr(exc, "orig", None) and getattr(exc.orig, "args", None):
            raw = str(exc.orig.args[0])
        else:
            raw = str(exc)

        msg_lower = raw.lower()
        if "unique" in msg_lower or "duplicate key" in msg_lower:
            friendly = _msg_unique(raw)
            status_code = 409
        elif "foreign key" in msg_lower or ("constraint failed" in msg_lower and "references" in msg_lower):
            friendly = _msg_fk(raw)
            status_code = 400
        else:
            friendly = "Erro de integridade do banco de dados."
            status_code = 400

        payload = fail(
            message=friendly,
            errors=None,  # se quiser, pode enviar {"detail": raw} para debug
            status_code=status_code,
            request=request,
        )
        return JSONResponse(status_code=status_code, content=payload)

    @app.middleware("http")
    async def catch_all_exceptions(request: Request, call_next):
        # Fallback 500 — mas NÃO deve engolir exceções que já têm handler (ex.: IntegrityError).
        try:
            return await call_next(request)
        except IntegrityError:        # <-- deixe o handler acima tratar
            raise
        except RequestValidationError:  # idem
            raise
        except StarletteHTTPException:  # idem
            raise
        except Exception as e:
            payload = fail(
                message="Erro interno no servidor",
                errors=str(e),
                status_code=500,
                request=request,
            )
            return JSONResponse(status_code=500, content=payload)
