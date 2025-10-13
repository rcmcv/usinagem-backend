from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importa rotas da API v1 (por enquanto, só um healthcheck)
from app.api.v1.endpoints.health import router as health_router

def create_app() -> FastAPI:
    """
    Fábrica da aplicação para facilitar testes e futuras configurações.
    """
    app = FastAPI(
        title="Usinagem ERP API",
        version="0.1.0",
        description="Backend inicial do sistema de gestão de usinagem."
    )

    # CORS (por enquanto liberado para desenvolvimento; depois restringimos por domínio)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],   # TODO: restringir em produção
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rotas v1
    app.include_router(health_router, prefix="/api/v1", tags=["Health"])

    @app.get("/", tags=["Root"])
    def root():
        """
        Endpoint raiz para validar rapidamente se a API está no ar.
        """
        return {"message": "API de Usinagem no ar. Veja /api/v1/health"}

    return app

app = create_app()
