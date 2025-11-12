"""
Aplicação FastAPI Principal - 3dPot v2.0 (Versão Mínima)
Sistema de Prototipagem Sob Demanda com Autenticação JWT OAuth2 Completa
"""

import logging
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Core imports
from core.config import DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, MODELS_STORAGE_PATH, settings
from models import Base, User, Project, Conversation, Model3D, Simulation
from schemas import UserCreate, User as UserSchema, ProjectCreate, Project as ProjectSchema
from schemas import ConversationalRequest, ConversationalResponse
from schemas import SimulationCreate, Simulation as SimulationSchema
from schemas import BudgetCreate, Budget as BudgetSchema

# Services
from services.conversational_service import ConversationalService
from services.budgeting_service import BudgetingService

# Sprint 6+ Services
from services.print3d_service import Print3DService
from services.collaboration_service import CollaborationService
from services.cloud_rendering_service import CloudRenderingService

# Routes & Middleware
from routes.auth import auth_router
from routes.conversational import router as conversational_router
from routes.budgeting import router as budgeting_router

# Sprint 10-11: Production System
from routes.production import router as production_router

# Database
from sqlalchemy.orm import Session
from database import get_db

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="3dPot - Sistema de Prototipagem",
    description="Sistema completo de prototipagem sob demanda com IA",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])

# Include conversational routes
app.include_router(conversational_router, prefix="/api/v1/conversational", tags=["conversational"])

# Include intelligent budgeting routes (Sprint 5)
app.include_router(budgeting_router, prefix="/api/v1/budgeting", tags=["budgeting"])

# Include production system routes (Sprint 10-11)
app.include_router(production_router, prefix="/api/v1/production", tags=["production"])

# Initialize services
budgeting_service = BudgetingService()

@app.get("/")
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "3dPot v2.0 - Sistema de Prototipagem Sob Demanda",
        "version": "2.0.0",
        "status": "online",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_minimal:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )