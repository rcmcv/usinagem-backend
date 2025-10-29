from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import get_settings
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.clientes import router as clientes_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.fornecedores import router as fornecedores_router
from app.api.v1.endpoints.tipos_servico import router as tipos_servico_router
from app.api.v1.endpoints.unidades_medida import router as unidades_medida_router

from app.core.error_handlers import register_error_handlers
from app.core.middlewares import RequestIDMiddleware

settings = get_settings()

def create_app() -> FastAPI:
    """
    Fábrica da aplicação para facilitar testes e futuras configurações.
    Agora usa Settings (Pydantic) para metadados e CORS.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Backend inicial do sistema de gestão de usinagem."
    )

    # CORS: em dev liberado; em prod restrito (defina CORS_ORIGINS no ambiente)
    app.add_middleware(RequestIDMiddleware)  # <-- Request ID
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Handlers globais
    register_error_handlers(app)             # <-- registra handlers

    # Rotas v1
    app.include_router(health_router, prefix="/api/v1", tags=["Health"])
    app.include_router(auth_router, prefix="/api/v1", tags=["Auth & Users"])
    app.include_router(clientes_router, prefix="/api/v1", tags=["Clientes"])
    app.include_router(fornecedores_router, prefix="/api/v1", tags=["Fornecedores"])
    app.include_router(tipos_servico_router, prefix="/api/v1", tags=["Tipos de Serviço"])
    app.include_router(unidades_medida_router, prefix="/api/v1", tags=["Unidades de Medida"])
    
    @app.get("/", tags=["Root"])
    def root():
        """
        Endpoint raiz para validar se a API está no ar e ver o ambiente ativo.
        Não expõe segredos.
        """
        return {
            "message": "API de Usinagem no ar. Veja /api/v1/health",
            "env": settings.ENV,
            "version": settings.VERSION
        }

    return app

app = create_app()
