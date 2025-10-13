from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import get_settings
from app.api.v1.endpoints.health import router as health_router

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
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rotas v1
    app.include_router(health_router, prefix="/api/v1", tags=["Health"])

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
