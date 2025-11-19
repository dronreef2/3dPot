"""
API Routes - Sistema de Orçamento Automatizado Inteligente - Sprint 5
Endpoints REST para orçamentos baseados em simulações físicas
"""

from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from backend.database import get_db
from backend.middleware.auth import get_current_user
from backend.models import User, Project, IntelligentBudget as Budget
from backend.schemas.budgeting import (
    IntelligentBudgetCreate, IntelligentBudgetResponse, 
    BudgetRecalculateRequest, SupplierComparisonRequest,
    Slant3DQuoteRequest, BudgetReport, BudgetExport,
    MaterialRecommendation, SupplierComparison, BudgetUpdate
)
from backend.services.intelligent_budgeting_service import IntelligentBudgetingService
from backend.services.slant3d_service import Slant3DService
from backend.services.suppliers_service import SuppliersService

router = APIRouter(prefix="/api/v1/budgeting", tags=["budgeting"])

# Dependency injection
def get_budgeting_service():
    return IntelligentBudgetingService()

def get_slant3d_service():
    return Slant3DService()

def get_suppliers_service():
    return SuppliersService()

# ========== ENDPOINTS PRINCIPAIS ==========

@router.post("/intelligent/create", response_model=IntelligentBudgetResponse)
async def create_intelligent_budget(
    budget_data: IntelligentBudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    budgeting_service: IntelligentBudgetingService = Depends(get_budgeting_service)
):
    """
    Criar orçamento automatizado inteligente baseado em simulações físicas
    
    Integra com Sprint 4 para usar resultados de simulação na precificação
    """
    try:
        # Verificar se o projeto pertence ao usuário
        project = db.query(Project).filter(
            and_(
                Project.id == budget_data.projeto_id,
                Project.owner_id == current_user.id
            )
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Projeto não encontrado ou sem permissão"
            )
        
        # Criar orçamento inteligente
        budget = await budgeting_service.create_intelligent_budget(db, budget_data)
        
        # Converter para schema de resposta
        response = await budgeting_service._budget_to_response(budget)
        
        logger.info(f"Orçamento inteligente criado: {budget.id} para usuário {current_user.id}")
        
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao criar orçamento inteligente: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar orçamento"
        )

@router.get("/{budget_id}", response_model=IntelligentBudgetResponse)
async def get_budget_details(
    budget_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    budgeting_service: IntelligentBudgetingService = Depends(get_budgeting_service)
):
    """Obter detalhes completos de um orçamento"""
    
    try:
        # Buscar orçamento
        budget = await budgeting_service.get_budget_by_id(db, budget_id)
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orçamento não encontrado"
            )
        
        # Verificar permissão
        project = db.query(Project).filter(Project.id == budget.projeto_id).first()
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para acessar este orçamento"
            )
        
        # Converter para resposta
        response = await budgeting_service._budget_to_response(budget)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar orçamento {budget_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar orçamento"
        )

@router.post("/{budget_id}/recalculate")
async def recalculate_budget(
    budget_id: UUID,
    recalculation_data: BudgetRecalculateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    budgeting_service: IntelligentBudgetingService = Depends(get_budgeting_service)
):
    """Recalcular orçamento com novos parâmetros"""
    
    try:
        # Verificar permissão
        budget = db.query(Budget).filter(
            and_(
                Budget.id == budget_id,
                Budget.projeto_id.in_(
                    db.query(Project.id).filter(Project.owner_id == current_user.id)
                )
            )
        ).first()
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orçamento não encontrado"
            )
        
        # Recalcular
        updated_budget = await budgeting_service.recalculate_budget(
            db, budget_id,
            new_quality_score=recalculation_data.new_quality_score,
            new_margin=recalculation_data.new_margin
        )
        
        # Se solicitado incluir simulação
        if recalculation_data.include_simulation and budget.simulation_id:
            # TODO: Integrar com novos resultados de simulação
            pass
        
        return {
            "message": "Orçamento recalculado com sucesso",
            "budget_id": budget_id,
            "updated_at": updated_budget.atualizado_em.isoformat(),
            "new_price": float(updated_budget.preco_final)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao recalcular orçamento {budget_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao recalcular orçamento"
        )

# ========== ENDPOINTS DE MATERIAIS ==========

@router.get("/{budget_id}/materials", response_model=List[MaterialRecommendation])
async def get_material_recommendations(
    budget_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    budgeting_service: IntelligentBudgetingService = Depends(get_budgeting_service)
):
    """Obter recomendações de materiais baseadas em simulações"""
    
    try:
        # Verificar permissão
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orçamento não encontrado"
            )
        
        project = db.query(Project).filter(Project.id == budget.projeto_id).first()
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão"
            )
        
        # Obter recomendações
        recommendations = await budgeting_service.get_material_recommendations(db, budget_id)
        
        return recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar recomendações de material: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar recomendações"
        )

@router.post("/materials/compare")
async def compare_materials(
    material_request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    slant3d_service: Slant3DService = Depends(get_slant3d_service)
):
    """Comparar preços de materiais entre fornecedores"""
    
    try:
        budget_id = material_request.get("budget_id")
        model_info = material_request.get("model_info", {})
        quantity = material_request.get("quantity", 1)
        
        if not budget_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="budget_id é obrigatório"
            )
        
        # Verificar permissão
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orçamento não encontrado"
            )
        
        project = db.query(Project).filter(Project.id == budget.projeto_id).first()
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão"
            )
        
        # Comparar materiais
        comparisons = await slant3d_service.compare_materials(
            db, budget_id, model_info, quantity
        )
        
        return {
            "budget_id": budget_id,
            "comparisons": [comp.dict() for comp in comparisons],
            "recommended_material": comparisons[0].material if comparisons else "PLA",
            "price_range": {
                "min": min(comp.total_price for comp in comparisons) if comparisons else 0,
                "max": max(comp.total_price for comp in comparisons) if comparisons else 0
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao comparar materiais: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao comparar materiais"
        )

# ========== ENDPOINTS DE FORNECEDORES ==========

@router.get("/{budget_id}/suppliers", response_model=SupplierComparison)
async def compare_suppliers(
    budget_id: UUID,
    include_shipping: bool = Query(True, description="Incluir custo de frete"),
    max_suppliers: int = Query(5, ge=1, le=20, description="Número máximo de fornecedores"),
    region: Optional[str] = Query(None, description="Região de entrega"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    suppliers_service: SuppliersService = Depends(get_suppliers_service)
):
    """Comparar fornecedores para um orçamento"""
    
    try:
        # Verificar permissão
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orçamento não encontrado"
            )
        
        project = db.query(Project).filter(Project.id == budget.projeto_id).first()
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão"
            )
        
        # Criar request de comparação
        comparison_request = SupplierComparisonRequest(
            include_shipping=include_shipping,
            max_suppliers=max_suppliers,
            region=region
        )
        
        # Executar comparação
        comparison = await suppliers_service.compare_suppliers(
            db, budget_id, comparison_request
        )
        
        return comparison
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao comparar fornecedores: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao comparar fornecedores"
        )

@router.post("/suppliers/recommendations")
async def get_supplier_recommendations(
    recommendation_request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    suppliers_service: SuppliersService = Depends(get_suppliers_service)
):
    """Obter recomendações de fornecedores"""
    
    try:
        budget_data = recommendation_request.get("budget_data", {})
        criteria = recommendation_request.get("criteria", [])
        
        recommendations = await suppliers_service.get_supplier_recommendations(
            budget_data, criteria
        )
        
        return {
            "recommendations": recommendations,
            "total_found": len(recommendations),
            "criteria_applied": criteria
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter recomendações de fornecedores: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter recomendações"
        )

# ========== ENDPOINTS SLANT3D ==========

@router.post("/slant3d/quote")
async def get_slant3d_quote(
    quote_request: Slant3DQuoteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    slant3d_service: Slant3DService = Depends(get_slant3d_service)
):
    """Obter cotação do Slant3D"""
    
    try:
        # Verificar permissão do orçamento
        budget = db.query(Budget).filter(
            and_(
                Budget.id == quote_request.model_id,  # Usar como budget_id temporariamente
                Budget.projeto_id.in_(
                    db.query(Project.id).filter(Project.owner_id == current_user.id)
                )
            )
        ).first()
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orçamento não encontrado ou sem permissão"
            )
        
        # Obter cotação
        quote = await slant3d_service.get_quote(db, budget.id, quote_request)
        
        return {
            "quote": quote.dict(),
            "budget_id": budget.id,
            "material": quote_request.material.value if hasattr(quote_request.material, 'value') else quote_request.material,
            "quantity": quote_request.quantidade
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter cotação Slant3D: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter cotação"
        )

@router.post("/slant3d/availability")
async def check_material_availability(
    availability_request: Dict[str, Any],
    slant3d_service: Slant3DService = Depends(get_slant3d_service)
):
    """Verificar disponibilidade de material"""
    
    try:
        material = availability_request.get("material", "PLA")
        color = availability_request.get("color", "white")
        finish_type = availability_request.get("finish_type", "standard")
        
        availability = await slant3d_service.check_availability(
            material, color, finish_type
        )
        
        return {
            "material": material,
            "color": color,
            "finish_type": finish_type,
            "availability": availability
        }
        
    except Exception as e:
        logger.error(f"Erro ao verificar disponibilidade: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao verificar disponibilidade"
        )

@router.post("/slant3d/shipping-estimate")
async def estimate_shipping(
    shipping_request: Dict[str, Any],
    slant3d_service: Slant3DService = Depends(get_slant3d_service)
):
    """Estimar custo de frete"""
    
    try:
        estimate = await slant3d_service.estimate_shipping(
            destination_country=shipping_request.get("country", "BR"),
            destination_state=shipping_request.get("state", "SP"),
            destination_city=shipping_request.get("city", "São Paulo"),
            postal_code=shipping_request.get("postal_code", "01310-100"),
            weight_kg=shipping_request.get("weight_kg", 0.5)
        )
        
        return {
            "shipping_estimate": estimate,
            "request_params": shipping_request
        }
        
    except Exception as e:
        logger.error(f"Erro ao estimar frete: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao estimar frete"
        )

# ========== ENDPOINTS DE TIMELINE E RELATÓRIOS ==========

@router.get("/{budget_id}/timeline")
async def get_budget_timeline(
    budget_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    budgeting_service: IntelligentBudgetingService = Depends(get_budgeting_service)
):
    """Obter cronograma detalhado do orçamento"""
    
    try:
        # Verificar permissão
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orçamento não encontrado"
            )
        
        project = db.query(Project).filter(Project.id == budget.projeto_id).first()
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão"
            )
        
        # Gerar timeline baseado no orçamento
        timeline = await budgeting_service._generate_timeline(budget)
        
        return {
            "budget_id": budget_id,
            "timeline": timeline,
            "total_duration_days": sum(fase["duracao_dias"] for fase in timeline),
            "critical_path": budgeting_service._get_critical_path(timeline)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar timeline: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao gerar cronograma"
        )

@router.get("/{budget_id}/report")
async def generate_budget_report(
    budget_id: UUID,
    format: str = Query("json", regex="^(json|pdf)$", description="Formato do relatório"),
    include_charts: bool = Query(True, description="Incluir gráficos"),
    include_supplier_details: bool = Query(True, description="Incluir detalhes dos fornecedores"),
    language: str = Query("pt-BR", description="Idioma do relatório"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    budgeting_service: IntelligentBudgetingService = Depends(get_budgeting_service)
):
    """Gerar relatório completo do orçamento"""
    
    try:
        # Verificar permissão
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orçamento não encontrado"
            )
        
        project = db.query(Project).filter(Project.id == budget.projeto_id).first()
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão"
            )
        
        # Gerar relatório
        report = await budgeting_service._generate_comprehensive_report(
            budget, format, include_charts, include_supplier_details, language
        )
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao gerar relatório"
        )

# ========== ENDPOINTS DE HISTÓRICO E ESTATÍSTICAS ==========

@router.get("/projects/{project_id}/budgets")
async def get_project_budgets(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter todos os orçamentos de um projeto"""
    
    try:
        # Verificar permissão do projeto
        project = db.query(Project).filter(
            and_(
                Project.id == project_id,
                Project.owner_id == current_user.id
            )
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Projeto não encontrado"
            )
        
        # Buscar orçamentos
        budgets = db.query(Budget).filter(
            Budget.projeto_id == project_id
        ).order_by(desc(Budget.criado_em)).all()
        
        # Converter para resumo
        budget_summaries = []
        for budget in budgets:
            budget_summaries.append({
                "id": budget.id,
                "material_recomendado": budget.material_recomendado,
                "quality_score": budget.quality_score,
                "preco_final": float(budget.preco_final),
                "status": budget.status,
                "criado_em": budget.criado_em.isoformat(),
                "quality_classification": budget.quality_classification
            })
        
        return {
            "project_id": project_id,
            "budgets": budget_summaries,
            "total_budgets": len(budgets),
            "latest_budget": budget_summaries[0] if budget_summaries else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar orçamentos do projeto: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar orçamentos"
        )

@router.get("/statistics/user")
async def get_user_budget_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    budgeting_service: IntelligentBudgetingService = Depends(get_budgeting_service)
):
    """Obter estatísticas de orçamentos do usuário"""
    
    try:
        stats = await budgeting_service._calculate_user_statistics(current_user.id, db)
        
        return stats
        
    except Exception as e:
        logger.error(f"Erro ao calcular estatísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao calcular estatísticas"
        )

# ========== ENDPOINTS DE ATUALIZAÇÃO EM TEMPO REAL ==========

@router.websocket("/updates/{budget_id}")
async def budget_updates_websocket(
    budget_id: UUID,
    websocket
):
    """WebSocket para atualizações em tempo real do orçamento"""
    
    try:
        await websocket.accept()
        
        # TODO: Implementar WebSocket para updates em tempo real
        # - Progresso de cálculos
        # - Status de fornecedores
        # - Cotações sendo processadas
        
        while True:
            # Manter conexão ativa
            data = await websocket.receive_text()
            
            # Processar mensagens do cliente se necessário
            if data == "ping":
                await websocket.send_text("pong")
            
    except Exception as e:
        logger.error(f"Erro no WebSocket: {e}")
        await websocket.close()

# ========== ENDPOINTS DE MANUTENÇÃO ==========

@router.delete("/{budget_id}")
async def delete_budget(
    budget_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Excluir um orçamento"""
    
    try:
        # Verificar permissão
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orçamento não encontrado"
            )
        
        project = db.query(Project).filter(Project.id == budget.projeto_id).first()
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para excluir"
            )
        
        # Verificar se é o último orçamento do projeto
        other_budgets = db.query(Budget).filter(
            and_(
                Budget.projeto_id == budget.projeto_id,
                Budget.id != budget_id
            )
        ).count()
        
        if other_budgets == 0:
            # Atualizar projeto se for o único orçamento
            project.orcamento_id = None
            db.add(project)
        
        # Excluir orçamento
        db.delete(budget)
        db.commit()
        
        return {"message": "Orçamento excluído com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao excluir orçamento {budget_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao excluir orçamento"
        )

@router.post("/cleanup/expired")
async def cleanup_expired_budgets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Limpar orçamentos expirados (apenas para admins)"""
    
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem executar limpeza"
        )
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        
        expired_budgets = db.query(Budget).filter(
            and_(
                Budget.atualizado_em < cutoff_date,
                Budget.status.in_(["draft", "expired"])
            )
        ).all()
        
        deleted_count = 0
        for budget in expired_budgets:
            # Verificar se o usuário ainda existe
            user = db.query(User).filter(User.id == current_user.id).first()
            if user:
                db.delete(budget)
                deleted_count += 1
        
        db.commit()
        
        return {
            "message": f"Limpeza concluída",
            "deleted_budgets": deleted_count,
            "cutoff_date": cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro na limpeza de orçamentos: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro na limpeza"
        )

# Logger para o módulo
import logging
logger = logging.getLogger(__name__)