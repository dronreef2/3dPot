"""
3dPot Platform - Database Configuration
Criado em: 2025-11-12 22:42:43
Autor: MiniMax Agent

Configurações e conexões para PostgreSQL
"""

import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from contextlib import asynccontextmanager

# Import the models
from models.database_models import Base

class DatabaseConfig:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "postgresql://3dpot:3dpot123@localhost:5432/3dpot_dev")
        self.echo = os.getenv("DATABASE_ECHO", "false").lower() == "true"
        self.pool_size = int(os.getenv("DB_POOL_SIZE", "20"))
        self.max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "30"))
        
    @property
    def async_url(self) -> str:
        """Converte sync URL para async URL"""
        return self.database_url.replace("postgresql://", "postgresql+asyncpg://")

# Database configuration
config = DatabaseConfig()

# Sync engine (para Alembic migrations)
engine = create_engine(
    config.database_url,
    echo=config.echo,
    pool_size=config.pool_size,
    max_overflow=config.max_overflow,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Async engine (para aplicação)
async_engine = create_async_engine(
    config.async_url,
    echo=config.echo,
    pool_size=config.pool_size,
    max_overflow=config.max_overflow,
    pool_pre_ping=True,
    pool_recycle=3600,
    future=True,
)

# Session makers
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

class DatabaseManager:
    """Gerenciador de database com métodos utilitários"""
    
    @staticmethod
    @asynccontextmanager
    async def get_session():
        """Context manager para sessões async"""
        async with AsyncSessionLocal() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    @staticmethod
    async def create_tables():
        """Cria todas as tabelas"""
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    @staticmethod
    async def drop_tables():
        """Remove todas as tabelas (apenas para desenvolvimento)"""
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    @staticmethod
    async def health_check() -> bool:
        """Verifica se a conexão com database está funcionando"""
        try:
            async with DatabaseManager.get_session() as session:
                result = await session.execute("SELECT 1")
                return result.scalar() == 1
        except Exception:
            return False

# Dependency para FastAPI
async def get_database():
    """Dependency que retorna uma sessão do database"""
    async with DatabaseManager.get_session() as session:
        try:
            yield session
        finally:
            await session.close()

# Export para uso em outros módulos
__all__ = [
    "engine",
    "async_engine", 
    "SessionLocal",
    "AsyncSessionLocal",
    "DatabaseManager",
    "get_database",
    "Base"
]