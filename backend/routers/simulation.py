"""
API Routes para Sistema de Simulação Física
Endpoints para criação, monitoramento e resultados de simulações
"""

import logging
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from backend.database import get_db
from backend.middleware.auth import get_current_user
from backend.models import User, Simulation, Model3D
from backend.schemas.simulation import (
    SimulationCreate, SimulationResponse, SimulationResult,
    SimulationStatusResponse, SimulationTemplate,
    DropTestConfig, StressTestConfig, MotionTestConfig, FluidTestConfig,
    ValidationResult
)
from backend.services.simulation_service import SimulationService

logger = logging.getLogger(__name__)
router = APIRouter()

# Instância global do serviço de simulação
simulation_service = SimulationService()

@router.post("/simulations/create", response_model=SimulationResponse)
async def create_simulation(
    simulation_data: SimulationCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Criar nova simulação física
    
    - **modelo_3d_id**: ID do modelo 3D a ser simulado
    - **nome**: Nome descritivo da simulação
    - **tipo_simulacao**: Tipo (drop_test, stress_test, motion, fluid)
    - **parametros**: Parâmetros específicos do teste
    - **condicoes_iniciais**: Condições iniciais da simulação
    """
    try:
        # Verificar se modelo 3D existe e pertence ao usuário
        model_3d = db.query(Model3D).filter(
            Model3D.id == simulation_data.modelo_3d_id,
            Model3D.user_id == current_user.id
        ).first()
        
        if not model_3d:
            raise HTTPException(
                status_code=404,
                detail="Modelo 3D não encontrado ou acesso negado"
            )
        
        # Validar parâmetros
        validation = simulation_service.validate_simulation_parameters(
            simulation_data.tipo_simulacao,
            simulation_data.parametros
        )
        
        if not validation["valid"]:
            raise HTTPException(
                status_code=400,
                detail=f"Parâmetros inválidos: {', '.join(validation['errors'])}"
            )
        
        # Aplicar parâmetros sugeridos se houver warnings
        if validation["suggested_parameters"]:
            simulation_data.parametros.update(validation["suggested_parameters"])
        
        # Criar registro da simulação
        simulation = Simulation(
            modelo_3d_id=simulation_data.modelo_3d_id,
            nome=simulation_data.nome,
            tipo_simulacao=simulation_data.tipo_simulacao,
            parametros=simulation_data.parametros,
            condicoes_iniciais=simulation_data.condicoes_iniciais,
            status="pending",
            user_id=current_user.id
        )
        
        db.add(simulation)
        db.commit()
        db.refresh(simulation)
        
        # Iniciar simulação em background via Celery
        from celery_app import run_simulation_task
        run_simulation_task.delay(
            simulation.id,
            str(model_3d.arquivo_path),
            {
                "tipo": simulation_data.tipo_simulacao,
                "parametros": simulation_data.parametros,
                "condicoes_iniciais": simulation_data.condicoes_iniciais
            }
        )
        
        logger.info(f"Simulação {simulation.id} criada para usuário {current_user.id}")
        
        return SimulationResponse(
            id=simulation.id,
            nome=simulation.nome,
            tipo_simulacao=simulation.tipo_simulacao,
            status=simulation.status,
            created_at=simulation.created_at,
            model_3d_id=simulation.modelo_3d_id,
            parametros=simulation.parametros,
            warning_messages=validation.get("warnings", [])
        )
        
    except SQLAlchemyError as e:
        logger.error(f"Erro no banco de dados: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno no banco de dados")
    except Exception as e:
        logger.error(f"Erro ao criar simulação: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/simulations/{simulation_id}", response_model=SimulationResponse)
async def get_simulation(
    simulation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter detalhes de uma simulação específica"""
    try:
        simulation = db.query(Simulation).filter(
            Simulation.id == simulation_id,
            Simulation.user_id == current_user.id
        ).first()
        
        if not simulation:
            raise HTTPException(status_code=404, detail="Simulação não encontrada")
        
        return SimulationResponse(
            id=simulation.id,
            nome=simulation.nome,
            tipo_simulacao=simulation.tipo_simulacao,
            status=simulation.status,
            created_at=simulation.created_at,
            updated_at=simulation.updated_at,
            model_3d_id=simulation.modelo_3d_id,
            parametros=simulation.parametros,
            results=simulation.results,
            error_message=simulation.error_message
        )
        
    except SQLAlchemyError as e:
        logger.error(f"Erro no banco de dados: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no banco de dados")

@router.get("/simulations/{simulation_id}/results", response_model=SimulationResult)
async def get_simulation_results(
    simulation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter resultados detalhados da simulação"""
    try:
        simulation = db.query(Simulation).filter(
            Simulation.id == simulation_id,
            Simulation.user_id == current_user.id
        ).first()
        
        if not simulation:
            raise HTTPException(status_code=404, detail="Simulação não encontrada")
        
        if simulation.status != "completed":
            raise HTTPException(
                status_code=400, 
                detail=f"Simulação ainda em andamento (status: {simulation.status})"
            )
        
        if not simulation.results:
            raise HTTPException(
                status_code=404, 
                detail="Resultados não encontrados para esta simulação"
            )
        
        return SimulationResult(
            simulation_id=simulation.id,
            tipo_simulacao=simulation.tipo_simulacao,
            status=simulation.status,
            results=simulation.results,
            created_at=simulation.created_at,
            completed_at=simulation.updated_at,
            duration=simulation.completed_at - simulation.created_at if simulation.completed_at else None
        )
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Erro no banco de dados: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no banco de dados")

@router.get("/simulations/{simulation_id}/status", response_model=SimulationStatusResponse)
async def get_simulation_status(
    simulation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter status atual da simulação"""
    try:
        simulation = db.query(Simulation).filter(
            Simulation.id == simulation_id,
            Simulation.user_id == current_user.id
        ).first()
        
        if not simulation:
            raise HTTPException(status_code=404, detail="Simulação não encontrada")
        
        return SimulationStatusResponse(
            simulation_id=simulation.id,
            status=simulation.status,
            progress=simulation.progress or 0,
            estimated_completion=simulation.estimated_completion,
            error_message=simulation.error_message,
            last_updated=simulation.updated_at
        )
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Erro no banco de dados: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no banco de dados")

@router.delete("/simulations/{simulation_id}")
async def delete_simulation(
    simulation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancelar e excluir uma simulação"""
    try:
        simulation = db.query(Simulation).filter(
            Simulation.id == simulation_id,
            Simulation.user_id == current_user.id
        ).first()
        
        if not simulation:
            raise HTTPException(status_code=404, detail="Simulação não encontrada")
        
        if simulation.status == "running":
            raise HTTPException(
                status_code=400,
                detail="Não é possível excluir simulação em andamento"
            )
        
        # Cancelar tarefa Celery se estiver pendente
        if simulation.status == "pending":
            from celery_app import cancel_simulation_task
            cancel_simulation_task.delay(simulation_id)
        
        # Remover do banco
        db.delete(simulation)
        db.commit()
        
        logger.info(f"Simulação {simulation_id} excluída pelo usuário {current_user.id}")
        
        return {"message": "Simulação excluída com sucesso"}
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Erro no banco de dados: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno no banco de dados")

@router.get("/simulations/templates", response_model=List[SimulationTemplate])
async def get_simulation_templates(
    current_user: User = Depends(get_current_user)
):
    """Obter templates de simulação pré-configurados"""
    templates = [
        SimulationTemplate(
            id="drop_test_quick",
            nome="Teste de Queda - Rápido",
            tipo_simulacao="drop_test",
            descricao="Simulação básica de queda com 5 testes de 1m",
            parametros={
                "drop_height": 1.0,
                "num_drops": 5,
                "gravity": -9.8
            },
            category="basic"
        ),
        SimulationTemplate(
            id="drop_test_comprehensive",
            nome="Teste de Queda - Completo",
            tipo_simulacao="drop_test",
            descricao="Análise completa de resistência com múltiplas alturas",
            parametros={
                "drop_height": 2.0,
                "num_drops": 10,
                "gravity": -9.8,
                "surface_type": "concrete"
            },
            category="comprehensive"
        ),
        SimulationTemplate(
            id="stress_test_mechanical",
            nome="Teste de Stress - Mecânico",
            tipo_simulacao="stress_test",
            descricao="Teste de resistência mecânica padrão",
            parametros={
                "max_force": 1000,
                "force_increment": 100,
                "force_direction": [0, 0, 1],
                "test_duration": 5
            },
            category="mechanical"
        ),
        SimulationTemplate(
            id="motion_test_circular",
            nome="Teste de Movimento - Circular",
            tipo_simulacao="motion",
            descricao="Análise de estabilidade em trajetória circular",
            parametros={
                "trajectory_type": "circular",
                "duration": 10.0,
                "velocity": 1.0,
                "radius": 1.0
            },
            category="dynamic"
        ),
        SimulationTemplate(
            id="fluid_test_air",
            nome="Teste de Fluido - Ar",
            tipo_simulacao="fluid",
            descricao="Análise de resistência do ar",
            parametros={
                "fluid_density": 1.2,
                "drag_coefficient": 0.47,
                "test_duration": 10.0
            },
            category="fluid"
        )
    ]
    
    return templates

@router.get("/simulations/history", response_model=List[SimulationResponse])
async def get_simulation_history(
    limit: int = Query(50, ge=1, le=100, description="Número máximo de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    status_filter: Optional[str] = Query(None, description="Filtrar por status"),
    tipo_filter: Optional[str] = Query(None, description="Filtrar por tipo"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter histórico de simulações do usuário"""
    try:
        query = db.query(Simulation).filter(Simulation.user_id == current_user.id)
        
        # Aplicar filtros
        if status_filter:
            query = query.filter(Simulation.status == status_filter)
        
        if tipo_filter:
            query = query.filter(Simulation.tipo_simulacao == tipo_filter)
        
        # Ordenar por data de criação (mais recentes primeiro)
        query = query.order_by(Simulation.created_at.desc())
        
        # Aplicar paginação
        simulations = query.offset(offset).limit(limit).all()
        
        result = []
        for sim in simulations:
            result.append(SimulationResponse(
                id=sim.id,
                nome=sim.nome,
                tipo_simulacao=sim.tipo_simulacao,
                status=sim.status,
                created_at=sim.created_at,
                updated_at=sim.updated_at,
                model_3d_id=sim.modelo_3d_id,
                parametros=sim.parametros,
                results=sim.results
            ))
        
        return result
        
    except SQLAlchemyError as e:
        logger.error(f"Erro no banco de dados: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no banco de dados")

@router.post("/simulations/{simulation_id}/validate", response_model=ValidationResult)
async def validate_simulation_parameters(
    simulation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Validar parâmetros de uma simulação existente"""
    try:
        simulation = db.query(Simulation).filter(
            Simulation.id == simulation_id,
            Simulation.user_id == current_user.id
        ).first()
        
        if not simulation:
            raise HTTPException(status_code=404, detail="Simulação não encontrada")
        
        # Validar parâmetros
        validation = simulation_service.validate_simulation_parameters(
            simulation.tipo_simulacao,
            simulation.parametros
        )
        
        return ValidationResult(
            simulation_id=simulation.id,
            valid=validation["valid"],
            errors=validation["errors"],
            warnings=validation["warnings"],
            suggested_parameters=validation["suggested_parameters"]
        )
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Erro no banco de dados: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no banco de dados")

@router.get("/simulations/{simulation_id}/download-results")
async def download_simulation_results(
    simulation_id: UUID,
    format: str = Query("json", regex="^(json|pdf)$", description="Formato de download"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download dos resultados da simulação"""
    try:
        simulation = db.query(Simulation).filter(
            Simulation.id == simulation_id,
            Simulation.user_id == current_user.id
        ).first()
        
        if not simulation:
            raise HTTPException(status_code=404, detail="Simulação não encontrada")
        
        if simulation.status != "completed" or not simulation.results:
            raise HTTPException(
                status_code=400,
                detail="Resultados não disponíveis para download"
            )
        
        filename = f"simulation_{simulation_id}_{simulation.tipo_simulacao}.{format}"
        
        if format == "json":
            from fastapi.responses import JSONResponse
            return JSONResponse(
                content={
                    "simulation": {
                        "id": str(simulation.id),
                        "nome": simulation.nome,
                        "tipo_simulacao": simulation.tipo_simulacao,
                        "created_at": simulation.created_at.isoformat(),
                        "completed_at": simulation.updated_at.isoformat() if simulation.updated_at else None
                    },
                    "results": simulation.results
                },
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        else:  # PDF
            # TODO: Implementar geração de PDF com matplotlib/reportlab
            raise HTTPException(
                status_code=501,
                detail="Download em PDF ainda não implementado"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar download: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no servidor")

@router.get("/models/{model_id}/simulations")
async def get_model_simulations(
    model_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter todas as simulações de um modelo específico"""
    try:
        # Verificar se modelo existe e pertence ao usuário
        model = db.query(Model3D).filter(
            Model3D.id == model_id,
            Model3D.user_id == current_user.id
        ).first()
        
        if not model:
            raise HTTPException(status_code=404, detail="Modelo não encontrado")
        
        simulations = db.query(Simulation).filter(
            Simulation.modelo_3d_id == model_id,
            Simulation.user_id == current_user.id
        ).order_by(Simulation.created_at.desc()).all()
        
        result = []
        for sim in simulations:
            result.append(SimulationResponse(
                id=sim.id,
                nome=sim.nome,
                tipo_simulacao=sim.tipo_simulacao,
                status=sim.status,
                created_at=sim.created_at,
                updated_at=sim.updated_at,
                model_3d_id=sim.modelo_3d_id,
                parametros=sim.parametros,
                results=sim.results
            ))
        
        return {
            "model_id": model_id,
            "model_name": model.nome,
            "total_simulations": len(simulations),
            "simulations": result
        }
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Erro no banco de dados: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no banco de dados")