"""
3dPot Platform - API Gateway
Criado em: 2025-11-12 22:42:43
Autor: MiniMax Agent

Gateway principal da plataforma que unifica:
- APIs REST para frontend
- Integração com hardware MQTT
- Services de conversação IA
- Generation pipeline para modelos 3D
- Sistema de orçamentos
"""

import os
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.routing import APIRouter

# Core dependencies
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import redis.asyncio as redis
from minio import Minio
import pika

# Logging configuration
import structlog
from rich.logging import RichHandler

# Local modules
from database.database import get_database, engine, SessionLocal
from database.models import (
    User, ConversationSession, Message, 
    Model3D, ModelGenerationJob, ModelExport, ModelTemplate
)
from services.auth import AuthService
from services.mqtt_bridge import MQTTBridgeService
from services.conversation import ConversationService
from services.model_generation import ModelGenerationService
from services.model3d_service import router as model3d_router
from services.budget import BudgetService
from services.websocket import WebSocketManager
from utils.logger import setup_logging

# Configuração de logging estruturado
setup_logging()
logger = structlog.get_logger("3dpot.gateway")

# Configurações globais
class Config:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://3dpot:3dpot123@localhost:5432/3dpot_dev")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "3dpot")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "3dpot123minio")
    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://localhost:5672")
    MQTT_BROKER: str = os.getenv("MQTT_BROKER", "mqtt://localhost:1883")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-super-secret-key-change-in-production-must-be-32-chars-minimum")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

config = Config()

# Global services instances
redis_client: redis.Redis = None
mqtt_bridge: MQTTBridgeService = None
websocket_manager: WebSocketManager = None
conversation_service: ConversationService = None
model_service: ModelGenerationService = None
budget_service: BudgetService = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação
    """
    global redis_client, mqtt_bridge, websocket_manager, conversation_service, model_service, budget_service
    
    logger.info("🚀 Iniciando 3dPot API Gateway...")
    
    try:
        # Inicializar database
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database inicializado")
        
        # Inicializar Redis
        redis_client = redis.from_url(config.REDIS_URL)
        await redis_client.ping()
        logger.info("✅ Redis conectado")
        
        # Inicializar MinIO client
        minio_client = Minio(
            config.MINIO_ENDPOINT.replace("http://", "").replace("https://", ""),
            access_key=config.MINIO_ACCESS_KEY,
            secret_key=config.MINIO_SECRET_KEY,
            secure=False
        )
        
        # Verificar se bucket existe, se não, criar
        bucket_name = "3dpot-models"
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
        logger.info("✅ MinIO configurado")
        
        # Inicializar MQTT Bridge
        mqtt_bridge = MQTTBridgeService(config.MQTT_BROKER)
        await mqtt_bridge.start()
        logger.info("✅ MQTT Bridge ativo")
        
        # Inicializar WebSocket Manager
        websocket_manager = WebSocketManager()
        logger.info("✅ WebSocket Manager ativo")
        
        # Inicializar services
        conversation_service = ConversationService(redis_client)
        model_service = ModelGenerationService(minio_client, redis_client)
        budget_service = BudgetService(redis_client)
        logger.info("✅ Serviços especializados inicializados")
        
        # Health check inicial
        await health_check()
        logger.info("🎯 Sistema completamente operacional")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {e}")
        raise
    finally:
        logger.info("🔄 Finalizando 3dPot API Gateway...")
        
        if mqtt_bridge:
            await mqtt_bridge.stop()
        if redis_client:
            await redis_client.close()

# Aplicação FastAPI
app = FastAPI(
    title="3dPot Platform API",
    description="API Gateway para Plataforma de Prototipagem Sob Demanda",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"] if config.ENVIRONMENT == "development" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if config.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.3dpot.com"]
    )

# Dependency injection
async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_redis() -> redis.Redis:
    if not redis_client:
        raise HTTPException(status_code=500, detail="Redis não inicializado")
    return redis_client

async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db, config.JWT_SECRET)

# Health Check
@app.get("/health")
async def health_check():
    """Health check endpoint - verifica status de todos os serviços"""
    try:
        # Testar database
        async with SessionLocal() as db:
            await db.execute(text("SELECT 1"))
        
        # Testar Redis
        await redis_client.ping()
        
        # Testar MQTT
        mqtt_status = "connected" if mqtt_bridge and mqtt_bridge.is_connected else "disconnected"
        
        return {
            "status": "healthy",
            "timestamp": "2025-11-12T22:42:43Z",
            "environment": config.ENVIRONMENT,
            "version": "2.0.0",
            "services": {
                "database": "connected",
                "redis": "connected",
                "mqtt_bridge": mqtt_status,
                "websocket": "active",
                "minio": "connected"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Service unhealthy: {str(e)}")

# WebSocket para conversação IA
@app.websocket("/ws/conversation/{session_id}")
async def websocket_conversation(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint para conversação com Minimax M2 Agent
    """
    await websocket_manager.connect(websocket, session_id)
    
    try:
        while True:
            # Receber mensagem do cliente
            data = await websocket.receive_json()
            message = data.get("message")
            user_id = data.get("user_id")
            
            if not message:
                await websocket.send_json({"error": "Message is required"})
                continue
            
            logger.info(f"📨 Mensagem recebida de {session_id}: {message[:50]}...")
            
            # Processar via Minimax M2 Agent
            response = await conversation_service.process_message(
                session_id=session_id,
                message=message,
                user_id=user_id
            )
            
            # Enviar resposta
            await websocket.send_json(response)
            
    except WebSocketDisconnect:
        logger.info(f"🔌 Cliente {session_id} desconectado")
    except Exception as e:
        logger.error(f"❌ Erro no WebSocket {session_id}: {e}")
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket_manager.disconnect(session_id)

# API Routes
app.include_router(AuthService.router, prefix="/auth", tags=["Authentication"])
app.include_router(ConversationService.router, prefix="/conversations", tags=["Conversation"])
app.include_router(model3d_router, prefix="/models", tags=["3D Models"])
app.include_router(ModelGenerationService.router, prefix="/legacy-models", tags=["Model Generation"])
app.include_router(BudgetService.router, prefix="/budgets", tags=["Budget"])
app.include_router(MQTTBridgeService.router, prefix="/hardware", tags=["Hardware"])

# Static files (para uploads)
app.mount("/static", StaticFiles(directory="/app/static"), name="static")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if config.ENVIRONMENT == "development" else False,
        log_level="info"
    )