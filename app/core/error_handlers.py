from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.api import fail

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
        # 422 em formato padronizado
        payload = fail(
            message="Erro de validação",
            errors=exc.errors(),
            status_code=422,
            request=request,
        )
        return JSONResponse(status_code=422, content=payload)

    @app.middleware("http")
    async def catch_all_exceptions(request: Request, call_next):
        # fallback para exceptions não tratadas (500)
        try:
            return await call_next(request)
        except Exception as e:
            payload = fail(
                message="Erro interno no servidor",
                errors=str(e),
                status_code=500,
                request=request,
            )
            return JSONResponse(status_code=500, content=payload)
