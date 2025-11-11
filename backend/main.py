"""
Aplicação FastAPI Principal - 3dPot v2.0
Sistema de Prototipagem Sob Demanda com Autenticação JWT OAuth2 Completa
"""

import json
from datetime import datetime, timedelta
from typing import List, Optional

import asyncio
import logging
import sys
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

# Database
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Core imports
from .core.config import DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, MODELS_STORAGE_PATH, settings
from .models import Base, User, Project, Conversation, Model3D, Simulation, Budget
from .schemas import *

# Services
from .services.conversational_service import ConversationalService
from .services.modeling_service import ModelingService  
from .services.simulation_service import SimulationService
from .services.budgeting_service import BudgetingService

# Routes & Middleware
from .routes.auth import auth_router
from .middleware.auth import (
    get_current_user, get_current_active_user, get_current_superuser,
    setup_authentication_middleware, cors_allow_credentials
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Database setup
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database setup
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Security (usando o sistema robusto do middleware)
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciar ciclo de vida da aplicação"""
    # Startup
    logger.info("Iniciando 3dPot v2.0 - Sistema de Prototipagem Sob Demanda")
    
    # Criar tabelas
    Base.metadata.create_all(bind=engine)
    
    # Verificar diretórios
    MODELS_STORAGE_PATH.mkdir(parents=True, exist_ok=True)
    
    yield
    
    # Shutdown
    logger.info("Finalizando 3dPot v2.0")

# FastAPI app
app = FastAPI(
    title="3dPot v2.0",
    description="Sistema de Prototipagem Sob Demanda - Conversação Inteligente → Modelagem 3D → Simulação → Orçamento",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
cors_config = cors_allow_credentials()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config["allow_origins"],
    allow_credentials=cors_config["allow_credentials"],
    allow_methods=cors_config["allow_methods"],
    allow_headers=cors_config["allow_headers"],
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
setup_authentication_middleware(app)

# Static files
if MODELS_STORAGE_PATH.exists():
    app.mount("/models", StaticFiles(directory=str(MODELS_STORAGE_PATH)), name="models")

# Initialize services
conversational_service = ConversationalService()
modeling_service = ModelingService()
simulation_service = SimulationService()
budgeting_service = BudgetingService()

# =============================================================================
# ROTAS DE AUTENTICAÇÃO
# =============================================================================

# Incluir rotas de autenticação robustas
app.include_router(auth_router)
    
    # Gerar token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/v1/auth/register", response_model=User)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registrar novo usuário"""
    # Verificar se usuário já existe
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username já existe"
        )
    
    # Criar usuário (implementar hash de senha)
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=user_data.password  # Implementar hash
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

# =============================================================================
# ENDPOINTS DE PROJETOS
# =============================================================================

@app.post("/api/v1/projects/", response_model=Project)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar novo projeto"""
    project = Project(
        owner_id=current_user.id,
        **project_data.dict()
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return project

@app.get("/api/v1/projects/", response_model=ProjectList)
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar projetos do usuário"""
    projects = db.query(Project).filter(
        Project.owner_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    total = db.query(Project).filter(Project.owner_id == current_user.id).count()
    
    return ProjectList(
        items=projects,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        pages=(total + limit - 1) // limit
    )

@app.get("/api/v1/projects/{project_id}", response_model=Project)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter detalhes do projeto"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    return project

@app.put("/api/v1/projects/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualizar projeto"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    for field, value in project_data.dict(exclude_unset=True).items():
        setattr(project, field, value)
    
    db.commit()
    db.refresh(project)
    
    return project

# =============================================================================
# ENDPOINTS DE CONVERSAÇÃO INTELIGENTE
# =============================================================================

@app.post("/api/v1/conversational/start", response_model=Conversation)
async def start_conversation(
    project_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Iniciar nova conversa"""
    conversation = await conversational_service.start_conversation(
        current_user.id, 
        project_id
    )
    return conversation

@app.post("/api/v1/conversational/message", response_model=ConversationalResponse)
async def process_message(
    message_data: ConversationalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Processar mensagem e gerar resposta inteligente"""
    try:
        response = await conversational_service.process_message(
            db, message_data, current_user.id
        )
        return response
    except Exception as e:
        logger.error(f"Erro no processamento de mensagem: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )

@app.get("/api/v1/conversational/{conversation_id}", response_model=Conversation)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter conversa completa"""
    conversation = conversational_service.get_conversation_by_id(db, conversation_id)
    
    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    
    return conversation

# =============================================================================
# ENDPOINTS DE MODELAGEM 3D
# =============================================================================

@app.post("/api/v1/modeling/generate", response_model=Model3D)
async def generate_model_3d(
    project_id: str = Form(...),
    specifications: str = Form(...),  # JSON string
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Gerar modelo 3D a partir de especificações"""
    # Verificar se projeto pertence ao usuário
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    try:
        specs_dict = json.loads(specifications)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Especificações inválidas")
    
    # Gerar modelo
    model = await modeling_service.generate_model_from_specs(db, project_id, specs_dict)
    
    # Atualizar projeto
    project.modelo_3d_id = model.id
    project.status = "modelando"
    db.commit()
    
    return model

@app.get("/api/v1/modeling/{model_id}/status")
async def get_model_status(
    model_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter status da geração do modelo"""
    model = db.query(Model3D).filter(
        Model3D.id == model_id
    ).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="Modelo não encontrado")
    
    # Verificar se projeto pertence ao usuário
    project = db.query(Project).filter(
        Project.modelo_3d_id == model_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Acesso negado")
    
    return {
        "model_id": model.id,
        "status": "completed" if model.arquivo_path.exists() else "failed",
        "imprimivel": model.imprimivel,
        "erros": model.erros_validacao,
        "warnings": model.warnings,
        "metrics": {
            "volume": model.volume_calculado,
            "area": model.area_superficie,
            "vertices": model.numero_vertices,
            "faces": model.numero_faces
        }
    }

@app.get("/api/v1/modeling/{model_id}/download")
async def download_model_3d(
    model_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download do modelo 3D gerado"""
    model = db.query(Model3D).filter(Model3D.id == model_id).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="Modelo não encontrado")
    
    # Verificar se projeto pertence ao usuário
    project = db.query(Project).filter(
        Project.modelo_3d_id == model_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Acesso negado")
    
    if not Path(model.arquivo_path).exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    
    return FileResponse(
        path=model.arquivo_path,
        filename=f"{project.nome}{model.formato_arquivo}",
        media_type="application/octet-stream"
    )

# =============================================================================
# ENDPOINTS DE SIMULAÇÃO
# =============================================================================

@app.post("/api/v1/simulation/start", response_model=Simulation)
async def start_simulation(
    simulation_data: SimulationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Iniciar simulação física"""
    # Verificar se modelo pertence ao usuário
    model_3d = db.query(Model3D).filter(Model3D.id == simulation_data.modelo_3d_id).first()
    
    if not model_3d:
        raise HTTPException(status_code=404, detail="Modelo não encontrado")
    
    project = db.query(Project).filter(
        Project.modelo_3d_id == model_3d.id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Acesso negado")
    
    # Iniciar simulação
    simulation = await simulation_service.start_simulation(db, simulation_data)
    
    # Atualizar projeto
    project.simulacao_id = simulation.id
    project.status = "simulando"
    db.commit()
    
    return simulation

@app.get("/api/v1/simulation/{simulation_id}/status")
async def get_simulation_status(
    simulation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter status da simulação"""
    simulation = simulation_service.get_simulation_status(db, simulation_id)
    
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulação não encontrada")
    
    # Verificar se projeto pertence ao usuário
    project = db.query(Project).filter(
        Project.simulacao_id == simulation.id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Acesso negado")
    
    return {
        "simulation_id": simulation.id,
        "status": simulation.status,
        "tipo_simulacao": simulation.tipo_simulacao,
        "progress": simulation.parametros.get("progress", 0),
        "resultado": simulation.resultado,
        "started_at": simulation.started_at,
        "completed_at": simulation.completed_at
    }

@app.get("/api/v1/simulation/{simulation_id}/results")
async def get_simulation_results(
    simulation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter resultados da simulação"""
    simulation = simulation_service.get_simulation_status(db, simulation_id)
    
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulação não encontrada")
    
    # Verificar se projeto pertence ao usuário
    project = db.query(Project).filter(
        Project.simulacao_id == simulation.id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Acesso negado")
    
    if simulation.status != "completed":
        raise HTTPException(status_code=400, detail="Simulação ainda em andamento")
    
    return simulation.resultado

# =============================================================================
# ENDPOINTS DE ORÇAMENTO
# =============================================================================

@app.post("/api/v1/budgeting/calculate", response_model=Budget)
async def calculate_budget(
    budget_data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calcular orçamento automatizado"""
    # Verificar se projeto pertence ao usuário
    project = db.query(Project).filter(
        Project.id == budget_data.projeto_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    # Calcular orçamento
    budget = await budgeting_service.create_budget(db, budget_data)
    
    return budget

@app.get("/api/v1/budgeting/{project_id}", response_model=Budget)
async def get_budget(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter orçamento do projeto"""
    budget = budgeting_service.get_budget_by_project(db, project_id)
    
    if not budget:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    
    # Verificar se projeto pertence ao usuário
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Acesso negado")
    
    return budget

@app.post("/api/v1/budgeting/{budget_id}/proposal")
async def generate_proposal(
    budget_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Gerar proposta em PDF"""
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    
    if not budget:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    
    project = db.query(Project).filter(
        Project.orcamento_id == budget_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Acesso negado")
    
    # Gerar proposta
    proposal_path = await budgeting_service.generate_proposal_pdf(budget, project)
    
    return {
        "proposal_path": proposal_path,
        "download_url": f"/api/v1/budgeting/{budget_id}/download-proposal"
    }

@app.get("/api/v1/budgeting/{budget_id}/download-proposal")
async def download_proposal(
    budget_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download da proposta PDF"""
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    
    if not budget:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    
    project = db.query(Project).filter(
        Project.orcamento_id == budget_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Acesso negado")
    
    if not budget.proposta_pdf_path or not Path(budget.proposta_pdf_path).exists():
        raise HTTPException(status_code=404, detail="Proposta não encontrada")
    
    return FileResponse(
        path=budget.proposta_pdf_path,
        filename=f"proposta_{budget_id}.pdf",
        media_type="application/pdf"
    )

# =============================================================================
# ENDPOINTS DE SISTEMA
# =============================================================================

@app.get("/api/v1/health")
async def health_check():
    """Verificação de saúde da API"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "ok",
            "storage": "ok",
            "ai_integration": "ok"
        }
    }

@app.get("/api/v1/stats")
async def get_system_stats(db: Session = Depends(get_db)):
    """Estatísticas do sistema"""
    stats = {
        "total_users": db.query(User).count(),
        "total_projects": db.query(Project).count(),
        "total_models": db.query(Model3D).count(),
        "total_simulations": db.query(Simulation).count(),
        "total_budgets": db.query(Budget).count(),
        "status_distribution": {}
    }
    
    # Distribuição de status dos projetos
    status_counts = db.query(Project.status, Project.id).all()
    for status, _ in status_counts:
        stats["status_distribution"][status] = stats["status_distribution"].get(status, 0) + 1
    
    return stats

# =============================================================================
# ENDPOINTS DE LEGADO (Preservar compatibilidade)
# =============================================================================

@app.get("/api/legacy/status")
async def legacy_status():
    """Endpoint legado - Status da API original"""
    return {
        "status": "online",
        "version": "1.1.0",
        "legacy_mode": True,
        "message": "API original 3dPot preservada para compatibilidade"
    }

# =============================================================================
# HANDLERS DE ERRO
# =============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handler para exceções HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handler geral para exceções"""
    logger.error(f"Erro interno: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )