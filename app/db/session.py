# Cria engine e fábrica de sessões (sincrona) usando DATABASE_URL do Settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.settings import get_settings

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # valida conexões antes de usar
)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)
