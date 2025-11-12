"""
3dPot Backend - Conexão com Banco de Dados
Sistema de Prototipagem Sob Demanda
"""

import asyncio
from typing import AsyncGenerator
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import NullPool, QueuePool
from loguru import logger

from .config import settings


class Base(DeclarativeBase):
    """Base class para todos os modelos ORM"""
    pass


# Criar engine assíncrono para PostgreSQL
DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

async_engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    poolclass=NullPool,
    future=True,
)

# Session maker assíncrono
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency para obter uma sessão de banco de dados assíncrona.
    
    Usage:
        @app.get("/users/")
        async def get_users(db: AsyncSession = Depends(get_db)):
            users = await db.execute(select(User))
            return users.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def get_db_health() -> bool:
    """
    Verifica a saúde da conexão com o banco de dados.
    
    Returns:
        bool: True se conexão OK, False se erro
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


async def create_tables():
    """
    Cria todas as tabelas no banco de dados.
    
    Usage:
        await create_tables()
    """
    try:
        async with async_engine.begin() as conn:
            # Importa todos os modelos para que SQLAlchemy possa encontrá-los
            from .models.user import User
            from .models.device import Device
            from .models.project import Project
            from .models.sensor_data import SensorData
            from .models.alert import Alert
            
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


async def drop_tables():
    """
    Remove todas as tabelas do banco de dados.
    
    Warning:
        Esta operação é irreversível e deve ser usada apenas em desenvolvimento.
    """
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.warning("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise


async def close_db_connection():
    """
    Fecha todas as conexões com o banco de dados.
    """
    try:
        await async_engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Failed to close database connections: {e}")


# Helper para migrações (Alembic)
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    poolclass=QueuePool,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_sync():
    """
    Dependency para obter uma sessão de banco de dados síncrona (usada por Alembic).
    
    Usage:
        def get_db():
            db = SessionLocal()
            try:
                yield db
            finally:
                db.close()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
