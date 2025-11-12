"""
3dPot Backend - Routers Package
Sistema de Prototipagem Sob Demanda
"""

from .auth import router as auth_router
from .devices import router as devices_router
from .monitoring import router as monitoring_router
from .projects import router as projects_router
from .alerts import router as alerts_router
from .health import router as health_router

__all__ = [
    "auth_router",
    "devices_router", 
    "monitoring_router",
    "projects_router",
    "alerts_router",
    "health_router"
]
