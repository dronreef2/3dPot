"""
3dPot Backend - Unified FastAPI Application
Sistema de Prototipagem Sob Demanda + IoT Monitoring

This unified backend combines:
- 3D Modeling, Simulation, and Budgeting APIs (Sprints 1-6+)
- IoT Device Monitoring and Management APIs
- WebSocket support for real-time updates
"""

import logging
import uvicorn
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from loguru import logger as loguru_logger
import sys

# Core imports
from backend.core.config import settings, DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, MODELS_STORAGE_PATH

# Database
from backend.database import get_db

# === LIFESPAN MANAGEMENT ===

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Startup
    loguru_logger.info(f"Iniciando {settings.PROJECT_NAME} v2.0.0 (Unified)")
    loguru_logger.info(f"Environment: {getattr(settings, 'ENVIRONMENT', 'production')}")
    loguru_logger.info(f"Database: {DATABASE_URL[:20]}...")
    
    try:
        loguru_logger.info("✅ 3dPot Backend Unified iniciado com sucesso")
        yield
    except Exception as e:
        loguru_logger.error(f"❌ Falha ao iniciar aplicação: {e}")
        raise
    finally:
        # Shutdown
        loguru_logger.info("Encerrando 3dPot Backend Unified...")
        loguru_logger.info("✅ Aplicação encerrada")


# === CREATE FASTAPI APP ===

app = FastAPI(
    title="3dPot - Unified Backend API",
    description="""
    🎯 **3dPot Unified Backend API** - Sistema Completo de Prototipagem e IoT
    
    ## 🚀 Funcionalidades Principais
    
    ### 🎨 Modelagem e Prototipagem
    - ✅ **Conversacional IA** - Geração de modelos 3D por conversação
    - ✅ **Modelagem 3D** - Suporte a CADQuery, OpenSCAD, Slant3D
    - ✅ **Simulação** - Análise estrutural e validação de modelos
    - ✅ **Orçamento Inteligente** - Cálculo automático de custos
    - ✅ **Impressão 3D** - Gerenciamento de impressoras e materiais
    - ✅ **Colaboração** - Sistema de trabalho em equipe
    - ✅ **Marketplace** - Venda e compra de modelos 3D
    - ✅ **Cloud Rendering** - Renderização em GPU clusters
    
    ### 📡 IoT e Monitoramento
    - ✅ **Gerenciamento de Dispositivos** - CRUD completo para dispositivos IoT
    - ✅ **Monitoramento em Tempo Real** - Coleta e análise de dados de sensores
    - ✅ **Sistema de Alertas** - Notificações automáticas para problemas
    - ✅ **Gestão de Projetos IoT** - Organização de trabalhos e protótipos
    - ✅ **WebSocket** - Comunicação em tempo real com dispositivos
    - ✅ **MQTT Integration** - Protocolo IoT para coleta de dados
    
    ### 🔐 Segurança e Autenticação
    - ✅ **Autenticação JWT** - Sistema seguro de login e autorização
    - ✅ **OAuth2** - Integração com provedores externos
    - ✅ **RBAC** - Controle de acesso baseado em roles
    
    ## 📚 Documentação
    - **Swagger UI**: http://localhost:8000/docs
    - **ReDoc**: http://localhost:8000/redoc
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# === MIDDLEWARE ===

# CORS
allowed_origins = getattr(settings, 'ALLOWED_ORIGINS', ["*"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compressão GZip
app.add_middleware(GZipMiddleware, minimum_size=1000)


# === IMPORT ROUTERS ===

# Modeling & Simulation routers (from backend/routes/)
from backend.routers.auth import auth_router
from backend.routers.conversational import router as conversational_router
from backend.routers.budgeting import router as budgeting_router
from backend.routers.modeling import router as modeling_router
from backend.routers.simulation import router as simulation_router
from backend.routers.simulation_reports import router as simulation_reports_router
from backend.routers.production import router as production_router

# Sprint 6+ routers
from backend.routers.printing3d import router as printing3d_router
from backend.routers.collaboration import router as collaboration_router
from backend.routers.marketplace import router as marketplace_router
from backend.routers.cloud_rendering import router as cloud_rendering_router

# IoT routers (from backend/app/routers/)
from backend.routers.devices import router as devices_router
from backend.routers.alerts import router as alerts_router
from backend.routers.monitoring import router as monitoring_router
from backend.routers.projects import router as projects_router
from backend.routers.health import router as health_router
from backend.routers.websocket import router as websocket_router


# === REGISTER ROUTERS ===

# Health Check (no prefix)
app.include_router(
    health_router,
    prefix="/health",
    tags=["health"]
)

# Authentication
app.include_router(
    auth_router,
    prefix="/api/auth",
    tags=["authentication"]
)

# === MODELING & PROTOTYPING APIs ===

# Conversational AI
app.include_router(
    conversational_router,
    prefix="/api/v1/conversational",
    tags=["conversational"]
)

# 3D Modeling
app.include_router(
    modeling_router,
    prefix="/api/v1/modeling",
    tags=["modeling"]
)

# Simulation
app.include_router(
    simulation_router,
    prefix="/api/v1/simulation",
    tags=["simulation"]
)

# Simulation Reports
app.include_router(
    simulation_reports_router,
    prefix="/api/v1/simulation/reports",
    tags=["simulation-reports"]
)

# Budgeting
app.include_router(
    budgeting_router,
    prefix="/api/v1/budgeting",
    tags=["budgeting"]
)

# Production System (Sprint 10-11)
app.include_router(
    production_router,
    prefix="/api/v1/production",
    tags=["production"]
)

# === SPRINT 6+ APIs ===

# 3D Printing
app.include_router(
    printing3d_router,
    prefix="/api/v1/printing",
    tags=["printing3d"]
)

# Collaboration
app.include_router(
    collaboration_router,
    prefix="/api/v1/collaboration",
    tags=["collaboration"]
)

# Marketplace
app.include_router(
    marketplace_router,
    prefix="/api/v1/marketplace",
    tags=["marketplace"]
)

# Cloud Rendering
app.include_router(
    cloud_rendering_router,
    prefix="/api/v1/cloud-rendering",
    tags=["cloud-rendering"]
)

# === IoT APIs ===

# Devices Management
app.include_router(
    devices_router,
    prefix="/api/v1/iot/devices",
    tags=["iot-devices"]
)

# Monitoring & Sensors
app.include_router(
    monitoring_router,
    prefix="/api/v1/iot/monitoring",
    tags=["iot-monitoring"]
)

# Projects Management (IoT-specific)
app.include_router(
    projects_router,
    prefix="/api/v1/iot/projects",
    tags=["iot-projects"]
)

# Alerts
app.include_router(
    alerts_router,
    prefix="/api/v1/iot/alerts",
    tags=["iot-alerts"]
)

# WebSocket (real-time)
app.include_router(
    websocket_router,
    prefix="/ws",
    tags=["websocket"]
)


# === EXCEPTION HANDLERS ===

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handler para exceções HTTP"""
    loguru_logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
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
    loguru_logger.error(f"Unhandled Exception: {exc}", exc_info=True)
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
        "message": "🎯 3dPot Unified Backend API",
        "version": "2.0.0",
        "status": "online",
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "modeling": "enabled",
            "simulation": "enabled",
            "budgeting": "enabled",
            "iot": "enabled",
            "websocket": "enabled",
            "collaboration": "enabled",
            "marketplace": "enabled",
            "cloud_rendering": "enabled"
        },
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/ping", tags=["root"])
async def ping():
    """Endpoint de ping para verificar disponibilidade"""
    return {
        "status": "pong",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/health", tags=["root"])
@app.get("/healthz", tags=["root"])
async def health_check():
    """Endpoint de verificação de saúde (compatibilidade)"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    }


# === DEVELOPMENT SERVER ===

if __name__ == "__main__":
    # Configurar logging para desenvolvimento
    loguru_logger.remove()
    loguru_logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG"
    )
    
    # Executar servidor de desenvolvimento
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug",
        access_log=True
    )
