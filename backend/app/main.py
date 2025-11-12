"""
3dPot Backend - Aplicação FastAPI Principal
Sistema de Prototipagem Sob Demanda
"""

import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
# from prometheus_fastapi_instrumentator import PrometheusFastApiInstrumentator
from contextlib import asynccontextmanager
from loguru import logger
import sys
import os

from .config import settings
from .database import create_tables, get_db_health, close_db_connection
from .routers import (
    auth_router,
    devices_router,
    monitoring_router,
    projects_router,
    alerts_router,
    health_router,
    websocket_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Startup
    logger.info(f"Iniciando {settings.PROJECT_NAME} v1.0.0")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug: {settings.DEBUG}")
    
    try:
        # Verificar conexão com banco
        db_health = await get_db_health()
        if not db_health:
            raise Exception("Falha na conexão com o banco de dados")
        
        # Criar tabelas (apenas em desenvolvimento)
        if settings.ENVIRONMENT == "development":
            await create_tables()
            logger.info("Tabelas do banco de dados criadas")
        
        logger.info("✅ 3dPot Backend iniciado com sucesso")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Falha ao iniciar aplicação: {e}")
        raise
    
    finally:
        # Shutdown
        logger.info("Encerrando 3dPot Backend...")
        await close_db_connection()
        logger.info("✅ Conexões com banco fechadas")


# Criar aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    🎯 **3dPot Backend API** - Sistema de Prototipagem Sob Demanda
    
    Esta API centralizada fornece backend unificado para todos os dispositivos IoT do projeto 3dPot.
    
    ## 🚀 Funcionalidades Principais
    
    - ✅ **Autenticação JWT** - Sistema seguro de login e autorização
    - ✅ **Gerenciamento de Dispositivos** - CRUD completo para dispositivos IoT
    - ✅ **Monitoramento em Tempo Real** - Coleta e análise de dados de sensores
    - ✅ **Sistema de Alertas** - Notificações automáticas para problemas
    - ✅ **Gestão de Projetos** - Organização de trabalhos e protótipos
    - ✅ **WebSocket** - Comunicação em tempo real com dispositivos
    - ✅ **MQTT Integration** - Protocolo IoT para coleta de dados
    - ✅ **Dashboard Unificado** - Visualização centralizada de todas as informações
    
    ## 📡 Dispositivos Suportados
    
    - **ESP32 Monitor** - Monitor de filamento com WiFi e MQTT
    - **Arduino Esteira** - Sistema de transporte automatizado
    - **Raspberry QC** - Estação de controle de qualidade com câmera
    - **Sensores IoT** - Temperatura, umidade, peso, vibração, etc.
    
    ## 🔧 Configuração
    
    Configure as variáveis de ambiente em `.env` para personalizar a aplicação.
    
    ## 📚 Documentação API
    
    - **Swagger UI**: http://localhost:8000/docs
    - **ReDoc**: http://localhost:8000/redoc
    - **OpenAPI**: http://localhost:8000/openapi.json
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# === MIDDLEWARE ===

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compressão GZip
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Prometheus Metrics (se habilitado)
# if settings.PROMETHEUS_ENABLED:
#     instrumentator = PrometheusFastApiInstrumentator()
#     instrumentator.instrument(app).expose(app, endpoint="/metrics")


# === ROUTERS ===

# Health Check
app.include_router(
    health_router,
    prefix="/health",
    tags=["health"]
)

# Authentication
app.include_router(
    auth_router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["authentication"]
)

# Devices Management
app.include_router(
    devices_router,
    prefix=f"{settings.API_V1_STR}/devices",
    tags=["devices"]
)

# Monitoring & Sensors
app.include_router(
    monitoring_router,
    prefix=f"{settings.API_V1_STR}/monitoring",
    tags=["monitoring"]
)

# Projects Management
app.include_router(
    projects_router,
    prefix=f"{settings.API_V1_STR}/projects",
    tags=["projects"]
)

# Alerts
app.include_router(
    alerts_router,
    prefix=f"{settings.API_V1_STR}/alerts",
    tags=["alerts"]
)

# WebSocket (tempo real)
app.include_router(
    websocket_router,
    prefix="/ws",
    tags=["websocket"]
)


# === EXCEPTION HANDLERS ===

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handler para exceções HTTP"""
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "http_error"
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handler para exceções gerais"""
    logger.error(f"Unhandled Exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Erro interno do servidor",
                "type": "server_error"
            }
        }
    )


# === ROOT ENDPOINTS ===

@app.get("/", tags=["root"])
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "🎯 3dPot Backend API",
        "version": "1.0.0",
        "status": "online",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/ping", tags=["root"])
async def ping():
    """Endpoint de ping para verificar disponibilidade"""
    return {"status": "pong", "timestamp": "2025-11-12T12:50:10Z"}


# === DEVELOPMENT SERVER ===

if __name__ == "__main__":
    # Configurar logging para desenvolvimento
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG" if settings.DEBUG else "INFO"
    )
    
    # Executar servidor de desenvolvimento
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
        access_log=True
    )
