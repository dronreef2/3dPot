"""
3dPot Backend - Rotas de Health Check
Sistema de Prototipagem Sob Demanda
"""

import time
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from loguru import logger

from ..database import get_db, get_db_health
from ..config import settings


router = APIRouter()


# === HEALTH CHECK ENDPOINTS ===

@router.get("/", response_model=Dict[str, Any])
async def health_check():
    """
    Health check básico da aplicação.
    
    Retorna status geral da API sem verificar dependências externas.
    """
    return {
        "status": "healthy",
        "service": "3dPot Backend API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": time.time() - start_time
    }


@router.get("/detailed", response_model=Dict[str, Any])
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check detalhado com verificação de dependências.
    
    Verifica:
    - Status da aplicação
    - Conexão com banco de dados
    - Conectividade Redis
    - Status do MQTT
    - Uso de memória
    """
    health_status = {
        "status": "healthy",
        "service": "3dPot Backend API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": time.time() - start_time,
        "checks": {}
    }
    
    # Verificar banco de dados
    try:
        db_health = await get_db_health()
        health_status["checks"]["database"] = {
            "status": "healthy" if db_health else "unhealthy",
            "message": "PostgreSQL connection" if db_health else "PostgreSQL connection failed"
        }
        if not db_health:
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database check failed: {str(e)}"
        }
        health_status["status"] = "unhealthy"
    
    # Verificar Redis (se configurado)
    try:
        import redis.asyncio as redis
        redis_client = redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        await redis_client.close()
        
        health_status["checks"]["redis"] = {
            "status": "healthy",
            "message": "Redis connection"
        }
    except Exception as e:
        health_status["checks"]["redis"] = {
            "status": "degraded",
            "message": f"Redis check failed: {str(e)}"
        }
        if health_status["status"] == "healthy":
            health_status["status"] = "degraded"
    
    # Verificar MQTT (se configurado)
    try:
        import asyncio
        import paho.mqtt.client as mqtt
        
        def check_mqtt():
            client = mqtt.Client()
            try:
                client.connect(settings.MQTT_BROKER_URL, settings.MQTT_BROKER_PORT, 5)
                client.disconnect()
                return True
            except:
                return False
        
        # Executar em thread pool para não bloquear
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            mqtt_healthy = await asyncio.get_event_loop().run_in_executor(
                executor, check_mqtt
            )
        
        health_status["checks"]["mqtt"] = {
            "status": "healthy" if mqtt_healthy else "degraded",
            "message": "MQTT broker connection" if mqtt_healthy else "MQTT broker unavailable"
        }
    except Exception as e:
        health_status["checks"]["mqtt"] = {
            "status": "degraded", 
            "message": f"MQTT check failed: {str(e)}"
        }
        if health_status["status"] == "healthy":
            health_status["status"] = "degraded"
    
    # Informações do sistema
    try:
        import psutil
        
        health_status["checks"]["system"] = {
            "status": "healthy",
            "cpu_usage_percent": psutil.cpu_percent(interval=1),
            "memory_usage_percent": psutil.virtual_memory().percent,
            "disk_usage_percent": psutil.disk_usage('/').percent
        }
        
        # Alertas de recursos
        cpu_usage = health_status["checks"]["system"]["cpu_usage_percent"]
        memory_usage = health_status["checks"]["system"]["memory_usage_percent"]
        disk_usage = health_status["checks"]["system"]["disk_usage_percent"]
        
        if cpu_usage > 90 or memory_usage > 90 or disk_usage > 90:
            health_status["status"] = "degraded"
            health_status["checks"]["system"]["warning"] = "High resource usage detected"
        
    except Exception as e:
        health_status["checks"]["system"] = {
            "status": "degraded",
            "message": f"System info check failed: {str(e)}"
        }
    
    # Determinar código de status HTTP final
    status_code = status.HTTP_200_OK
    if health_status["status"] == "unhealthy":
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif health_status["status"] == "degraded":
        status_code = status.HTTP_206_PARTIAL_CONTENT
    
    return health_status, status_code


@router.get("/ready", response_model=Dict[str, Any])
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Readiness probe para Kubernetes/Docker.
    
    Indica se a aplicação está pronta para receber tráfego.
    """
    try:
        # Verificar conexão com banco
        await db.execute(text("SELECT 1"))
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service not ready: {str(e)}"
        )


@router.get("/live", response_model=Dict[str, Any])
async def liveness_check():
    """
    Liveness probe para Kubernetes/Docker.
    
    Indica se a aplicação está viva e funcionando.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": time.time() - start_time
    }


@router.get("/metrics")
async def metrics():
    """
    Endpoint para métricas Prometheus.
    
    Retorna métricas de performance da aplicação.
    """
    try:
        return generate_latest()
    except Exception as e:
        logger.error(f"Metrics generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate metrics"
        )


# Tempo de início da aplicação (inicializado quando o módulo é importado)
start_time = time.time()



