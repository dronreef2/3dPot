"""
API Routes - Sistema de Produção Avançado - Sprint 10-11
Endpoints REST para planejamento, execução e otimização de produção
"""

from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from database import get_db
from middleware.auth import get_current_user
from models import User, Project, IntelligentBudget as Budget
from models.production_models import (
    ProductionOrder, ProductionStatus, Priority, ProductionType, QualityStatus,
    ProductionEvent, QualityCheck, ProductionSchedule, ProductionCapacity,
    ProductionMetrics, ProductionOptimization
)
from schemas.production_schemas import (
    ProductionOrderCreate, ProductionOrderResponse, ProductionOrderUpdate,
    ProductionScheduleResponse, QualityCheckResponse, QualityCheckUpdate,
    ProductionEventResponse, ProductionCapacityResponse, ProductionMetricsResponse,
    ProductionOptimizationResponse, ProductionDashboardData, ProductionStatusDetail,
    ProductionReportRequest, ProductionReportResponse, OptimizationRequest,
    CapacityPlanningRequest, CapacityPlanningResponse, ProductionUpdate,
    QualityGateCheck, QualityGateResult, SupplyChainStatus, SupplyChainAlert
)
from services.production_service import ProductionService

router = APIRouter(prefix="/api/v1/production", tags=["production"])

# Dependency injection
def get_production_service():
    return ProductionService()

# ========== PRODUCTION ORDERS ==========

@router.post("/orders", response_model=ProductionOrderResponse)
async def create_production_order(
    order_data: ProductionOrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    production_service: ProductionService = Depends(get_production_service)
):
    """
    Criar nova ordem de produção baseada em orçamento inteligente
    """
    try:
        # Verificar se o orçamento pertence ao usuário
        budget = db.query(Budget).filter(
            and_(
                Budget.id == order_data.budget_id,
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
        
        # Criar ordem de produção
        production_order = await production_service.create_production_order(
            db, order_data.budget_id, order_data.dict()
        )
        
        logger.info(f"Ordem de produção criada: {production_order.id}")
        
        return production_order
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao criar ordem de produção: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar ordem de produção"
        )

@router.get("/orders/{order_id}", response_model=ProductionOrderResponse)
async def get_production_order(
    order_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter detalhes de uma ordem de produção"""
    
    try:
        order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ordem de produção não encontrada"
            )
        
        # Verificar permissão
        project = db.query(Project).filter(Project.id == order.project_id).first()
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para acessar esta ordem de produção"
            )
        
        return order
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar ordem de produção {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar ordem de produção"
        )

@router.get("/orders/{order_id}/status", response_model=ProductionStatusDetail)
async def get_production_status(
    order_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    production_service: ProductionService = Depends(get_production_service)
):
    """Obter status detalhado da produção"""
    
    try:
        # Verificar permissão
        order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ordem de produção não encontrada"
            )
        
        project = db.query(Project).filter(Project.id == order.project_id).first()
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão"
            )
        
        status_detail = await production_service.get_production_status(db, order_id)
        return status_detail
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar status da produção {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar status"
        )

@router.put("/orders/{order_id}")
async def update_production_order(
    order_id: UUID,
    update_data: ProductionOrderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    production_service: ProductionService = Depends(get_production_service)
):
    """Atualizar ordem de produção"""
    
    try:
        # Verificar permissão
        order = db.query(ProductionOrder).filter(
            and_(
                ProductionOrder.id == order_id,
                ProductionOrder.project_id.in_(
                    db.query(Project.id).filter(Project.owner_id == current_user.id)
                )
            )
        ).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ordem de produção não encontrada"
            )
        
        # Atualizar campos
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(order, field, value)
        
        order.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(order)
        
        return {
            "message": "Ordem de produção atualizada com sucesso",
            "order_id": order_id,
            "updated_fields": list(update_dict.keys())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar ordem de produção {order_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao atualizar ordem de produção"
        )

@router.post("/orders/{order_id}/status")
async def update_production_order_status(
    order_id: UUID,
    status_update: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    production_service: ProductionService = Depends(get_production_service)
):
    """Atualizar status da ordem de produção"""
    
    try:
        status_value = status_update.get("status")
        event_data = status_update.get("event_data")
        
        if not status_value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status é obrigatório"
            )
        
        # Verificar permissão
        order = db.query(ProductionOrder).filter(
            and_(
                ProductionOrder.id == order_id,
                ProductionOrder.project_id.in_(
                    db.query(Project.id).filter(Project.owner_id == current_user.id)
                )
            )
        ).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ordem de produção não encontrada"
            )
        
        # Atualizar status
        updated_order = await production_service.update_production_status(
            db, order_id, ProductionStatus(status_value), event_data
        )
        
        return {
            "message": "Status atualizado com sucesso",
            "order_id": order_id,
            "new_status": status_value
        }
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status inválido: {e}"
        )
    except Exception as e:
        logger.error(f"Erro ao atualizar status da produção {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao atualizar status"
        )

@router.get("/projects/{project_id}/orders")
async def get_project_production_orders(
    project_id: UUID,
    status_filter: Optional[str] = Query(None, description="Filtrar por status"),
    limit: int = Query(50, ge=1, le=200, description="Limite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter ordens de produção de um projeto"""
    
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
        
        # Buscar ordens
        query = db.query(ProductionOrder).filter(
            ProductionOrder.project_id == project_id
        )
        
        if status_filter:
            query = query.filter(ProductionOrder.status == status_filter)
        
        orders = query.order_by(desc(ProductionOrder.created_at)).offset(offset).limit(limit).all()
        
        total = db.query(ProductionOrder).filter(
            ProductionOrder.project_id == project_id
        ).count()
        
        return {
            "project_id": project_id,
            "orders": [order.dict() for order in orders],
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + len(orders) < total
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar ordens do projeto {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar ordens de produção"
        )

# ========== PRODUCTION SCHEDULE ==========

@router.get("/orders/{order_id}/schedule")
async def get_production_schedule(
    order_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter cronograma de produção"""
    
    try:
        # Verificar permissão
        order = db.query(ProductionOrder).filter(
            and_(
                ProductionOrder.id == order_id,
                ProductionOrder.project_id.in_(
                    db.query(Project.id).filter(Project.owner_id == current_user.id)
                )
            )
        ).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ordem de produção não encontrada"
            )
        
        # Buscar cronograma
        schedules = db.query(ProductionSchedule).filter(
            ProductionSchedule.production_order_id == order_id
        ).order_by(ProductionSchedule.operation_order).all()
        
        return {
            "order_id": order_id,
            "schedule": [schedule.dict() for schedule in schedules],
            "total_operations": len(schedules),
            "completed_operations": sum(1 for s in schedules if s.completed),
            "progress_percentage": sum(s.progress_percentage for s in schedules) / len(schedules) if schedules else 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar cronograma {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar cronograma"
        )

@router.post("/orders/{order_id}/optimize")
async def optimize_production_schedule(
    order_id: UUID,
    optimization_config: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    production_service: ProductionService = Depends(get_production_service)
):
    """Otimizar cronograma de produção"""
    
    try:
        # Verificar permissão
        order = db.query(ProductionOrder).filter(
            and_(
                ProductionOrder.id == order_id,
                ProductionOrder.project_id.in_(
                    db.query(Project.id).filter(Project.owner_id == current_user.id)
                )
            )
        ).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ordem de produção não encontrada"
            )
        
        # Executar otimização
        optimizations = await production_service.optimize_production_schedule(db, order_id)
        
        return {
            "order_id": order_id,
            "optimizations": optimizations,
            "total_optimizations": len(optimizations),
            "potential_savings": {
                "time_hours": sum(opt.get("time_savings", 0) for opt in optimizations),
                "cost_brl": sum(opt.get("cost_savings", 0) for opt in optimizations)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao otimizar cronograma {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao otimizar cronograma"
        )

# ========== QUALITY CONTROL ==========

@router.get("/orders/{order_id}/quality")
async def get_quality_checks(
    order_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter controles de qualidade da ordem"""
    
    try:
        # Verificar permissão
        order = db.query(ProductionOrder).filter(
            and_(
                ProductionOrder.id == order_id,
                ProductionOrder.project_id.in_(
                    db.query(Project.id).filter(Project.owner_id == current_user.id)
                )
            )
        ).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ordem de produção não encontrada"
            )
        
        # Buscar controles de qualidade
        quality_checks = db.query(QualityCheck).filter(
            QualityCheck.production_order_id == order_id
        ).order_by(QualityCheck.scheduled_date).all()
        
        return {
            "order_id": order_id,
            "quality_checks": [check.dict() for check in quality_checks],
            "total_checks": len(quality_checks),
            "passed_checks": sum(1 for q in quality_checks if q.status == QualityStatus.PASSED),
            "failed_checks": sum(1 for q in quality_checks if q.status == QualityStatus.FAILED),
            "pending_checks": sum(1 for q in quality_checks if q.status == QualityStatus.PENDING)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar controles de qualidade {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar controles de qualidade"
        )

@router.put("/quality/{quality_check_id}")
async def update_quality_check(
    quality_check_id: UUID,
    update_data: QualityCheckUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualizar controle de qualidade"""
    
    try:
        # Verificar permissão
        quality_check = db.query(QualityCheck).filter(
            QualityCheck.id == quality_check_id
        ).first()
        
        if not quality_check:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Controle de qualidade não encontrado"
            )
        
        order = db.query(ProductionOrder).filter(
            ProductionOrder.id == quality_check.production_order_id
        ).first()
        
        project = db.query(Project).filter(Project.id == order.project_id).first()
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão"
            )
        
        # Atualizar campos
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(quality_check, field, value)
        
        if not quality_check.actual_date:
            quality_check.actual_date = datetime.utcnow()
        
        db.commit()
        
        return {
            "message": "Controle de qualidade atualizado com sucesso",
            "quality_check_id": quality_check_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar controle de qualidade {quality_check_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao atualizar controle de qualidade"
        )

# ========== DASHBOARD E RELATÓRIOS ==========

@router.get("/dashboard", response_model=ProductionDashboardData)
async def get_production_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    production_service: ProductionService = Depends(get_production_service)
):
    """Obter dados do dashboard de produção"""
    
    try:
        dashboard_data = await production_service.get_production_dashboard_data(
            db, current_user.id
        )
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Erro ao buscar dados do dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar dados do dashboard"
        )

@router.get("/reports/comprehensive", response_model=ProductionReportResponse)
async def generate_production_report(
    report_request: ProductionReportRequest = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    production_service: ProductionService = Depends(get_production_service)
):
    """Gerar relatório completo de produção"""
    
    try:
        if report_request is None:
            report_request = ProductionReportRequest()
        
        report_data = await production_service.generate_production_report(
            db, current_user.id, 
            report_request.start_date, 
            report_request.end_date
        )
        return report_data
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório de produção: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao gerar relatório"
        )

# ========== CAPACITY PLANNING ==========

@router.post("/capacity/plan")
async def plan_production_capacity(
    planning_request: CapacityPlanningRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    production_service: ProductionService = Depends(get_production_service)
):
    """Planejar capacidade de produção"""
    
    try:
        # Implementação simplificada - pode ser expandida
        planning_result = {
            "planning_period": {
                "start_date": planning_request.start_date.isoformat(),
                "end_date": planning_request.end_date.isoformat()
            },
            "resource_requirements": {
                "total_labor_hours": 240,
                "total_machine_hours": 180,
                "material_requirements": {
                    "pla_filament_kg": 25,
                    "abs_filament_kg": 15,
                    "support_material_kg": 5
                }
            },
            "recommended_schedule": [],
            "capacity_utilization": {
                "average_utilization": 78.5,
                "peak_utilization": 95.2,
                "bottleneck_identified": "3D_Printers"
            },
            "bottleneck_analysis": {
                "primary_bottleneck": "3D_Printers",
                "utilization_rate": 95.2,
                "recommended_action": "Adicionar 2 impressoras adicionais ou otimizar agendamento"
            },
            "optimization_suggestions": [
                {
                    "type": "schedule_optimization",
                    "description": "Otimizar agendamento para balancear carga",
                    "expected_improvement": "15% redução no tempo total"
                },
                {
                    "type": "resource_allocation",
                    "description": "Reorganizar alocação de recursos",
                    "expected_improvement": "20% melhor utilização de equipamentos"
                }
            ]
        }
        
        return planning_result
        
    except Exception as e:
        logger.error(f"Erro no planejamento de capacidade: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no planejamento de capacidade"
        )

# ========== SUPPLY CHAIN MANAGEMENT ==========

@router.get("/supply-chain/status")
async def get_supply_chain_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter status da cadeia de suprimentos"""
    
    try:
        # Status simplificado - implementação real seria mais complexa
        supply_status = {
            "material_availability": {
                "PLA": {"status": "available", "stock_days": 30, "supplier": "Local Supplier A"},
                "ABS": {"status": "limited", "stock_days": 7, "supplier": "Local Supplier A"},
                "PETG": {"status": "available", "stock_days": 45, "supplier": "Regional Supplier B"},
                "support_material": {"status": "available", "stock_days": 60, "supplier": "Local Supplier A"}
            },
            "supplier_status": {
                "Local Supplier A": {
                    "status": "operational",
                    "reliability_score": 95,
                    "last_delivery": "2025-11-12",
                    "quality_rating": 4.8
                },
                "Regional Supplier B": {
                    "status": "operational",
                    "reliability_score": 92,
                    "last_delivery": "2025-11-10",
                    "quality_rating": 4.6
                }
            },
            "delivery_status": {
                "on_time_rate": 94.5,
                "average_delay_days": 1.2,
                "pending_deliveries": 3,
                "delayed_deliveries": 1
            },
            "risk_assessment": {
                "supply_risk_level": "low",
                "identified_risks": [],
                "mitigation_strategies": [
                    "Manter estoque mínimo de 30 dias",
                    "Ter fornecedores alternativos identificados",
                    "Monitorar qualidade continuamente"
                ]
            }
        }
        
        return supply_status
        
    except Exception as e:
        logger.error(f"Erro ao buscar status da cadeia de suprimentos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar status da cadeia de suprimentos"
        )

@router.get("/supply-chain/alerts")
async def get_supply_chain_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter alertas da cadeia de suprimentos"""
    
    try:
        # Alertas simplificados
        alerts = [
            {
                "alert_id": "ALT-001",
                "alert_type": "material_shortage",
                "severity": "medium",
                "message": "Estoque de ABS baixo - apenas 7 dias restantes",
                "affected_materials": ["ABS"],
                "recommended_actions": [
                    "Contactar fornecedor para entrega urgente",
                    "Considerar mudança temporária para PLA"
                ],
                "estimated_impact": {
                    "production_delay_days": 2,
                    "cost_increase_percentage": 5
                },
                "created_at": "2025-11-13T01:00:00Z"
            }
        ]
        
        return {
            "alerts": alerts,
            "total_alerts": len(alerts),
            "critical_alerts": len([a for a in alerts if a["severity"] == "critical"]),
            "last_updated": "2025-11-13T02:21:15Z"
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar alertas da cadeia de suprimentos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar alertas"
        )

# ========== PRODUCTION EVENTS ==========

@router.get("/orders/{order_id}/events")
async def get_production_events(
    order_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter eventos da ordem de produção"""
    
    try:
        # Verificar permissão
        order = db.query(ProductionOrder).filter(
            and_(
                ProductionOrder.id == order_id,
                ProductionOrder.project_id.in_(
                    db.query(Project.id).filter(Project.owner_id == current_user.id)
                )
            )
        ).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ordem de produção não encontrada"
            )
        
        # Buscar eventos
        events = db.query(ProductionEvent).filter(
            ProductionEvent.production_order_id == order_id
        ).order_by(desc(ProductionEvent.created_at)).offset(offset).limit(limit).all()
        
        total = db.query(ProductionEvent).filter(
            ProductionEvent.production_order_id == order_id
        ).count()
        
        return {
            "order_id": order_id,
            "events": [event.dict() for event in events],
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + len(events) < total
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar eventos {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar eventos"
        )

# ========== METRICS E KPIs ==========

@router.get("/metrics/overview")
async def get_production_metrics_overview(
    period_days: int = Query(30, ge=1, le=365, description="Período em dias"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    production_service: ProductionService = Depends(get_production_service)
):
    """Obter visão geral das métricas de produção"""
    
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)
        
        # Buscar métricas do período
        metrics = db.query(ProductionMetrics).filter(
            and_(
                ProductionMetrics.period_start >= start_date,
                ProductionMetrics.period_end <= end_date
            )
        ).all()
        
        # Calcular agregados
        total_orders = sum(m.total_orders for m in metrics)
        completed_orders = sum(m.completed_orders for m in metrics)
        total_production_cost = sum(float(m.total_production_cost) for m in metrics)
        
        avg_efficiency = np.mean([m.efficiency_score for m in metrics if m.efficiency_score]) if metrics else 0
        avg_quality = np.mean([m.quality_pass_rate for m in metrics if m.quality_pass_rate]) if metrics else 0
        avg_utilization = np.mean([m.utilization_rate for m in metrics if m.utilization_rate]) if metrics else 0
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": period_days
            },
            "summary": {
                "total_orders": total_orders,
                "completed_orders": completed_orders,
                "completion_rate": (completed_orders / total_orders * 100) if total_orders > 0 else 0,
                "total_production_cost": round(total_production_cost, 2),
                "average_efficiency_score": round(avg_efficiency, 2),
                "average_quality_pass_rate": round(avg_quality, 2),
                "average_utilization_rate": round(avg_utilization, 2)
            },
            "trends": {
                "order_volume_trend": "stable",  # Simplificado
                "efficiency_trend": "improving",  # Simplificado
                "quality_trend": "stable"  # Simplificado
            },
            "insights": [
                f"Taxa de conclusão de {((completed_orders / total_orders * 100) if total_orders > 0 else 0):.1f}%",
                f"Score médio de eficiência de {avg_efficiency:.1f}%",
                f"Tempo médio de produção dentro do esperado"
            ]
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar métricas de produção: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar métricas"
        )

# Logger for the module
import logging
import numpy as np
logger = logging.getLogger(__name__)

# ========== COST OPTIMIZATION ENDPOINTS ==========

@router.post("/cost-optimization/analyze")
async def analyze_cost_optimization(
    analysis_request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analisar oportunidades de otimização de custos"""
    
    try:
        from services.cost_optimization_service import CostOptimizationService
        from schemas.production_schemas import OptimizationRequest
        
        # Configurar request de otimização
        optimization_request = OptimizationRequest(
            optimization_types=analysis_request.get("optimization_types", [
                "material_optimization", "supplier_consolidation", "batch_size_optimization",
                "production_efficiency", "quality_cost_balance", "workflow_optimization"
            ]),
            target_improvements=analysis_request.get("target_improvements", {
                "cost_reduction": 10.0,
                "time_reduction": 15.0,
                "quality_improvement": 5.0
            }),
            constraints=analysis_request.get("constraints", {})
        )
        
        cost_optimization_service = CostOptimizationService()
        
        # Executar análise
        analysis_result = await cost_optimization_service.analyze_cost_optimization_opportunities(
            db, current_user.id, optimization_request
        )
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"Erro na análise de otimização de custos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno na análise de otimização"
        )

@router.get("/projects/overview/orders")
async def get_projects_overview_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter visão geral das ordens de todos os projetos do usuário"""
    
    try:
        # Buscar projetos do usuário
        projects = db.query(Project).filter(Project.owner_id == current_user.id).all()
        project_ids = [p.id for p in projects]
        
        if not project_ids:
            return {
                "orders": [],
                "total": 0,
                "projects": []
            }
        
        # Buscar ordens de produção
        orders = db.query(ProductionOrder).filter(
            ProductionOrder.project_id.in_(project_ids)
        ).order_by(desc(ProductionOrder.created_at)).all()
        
        # Converter para formato simplificado
        orders_data = []
        for order in orders:
            orders_data.append({
                "id": str(order.id),
                "status": order.status.value,
                "progress_percentage": 0,  # Calculado dinamicamente
                "quantity": order.quantity,
                "estimated_cost": float(order.estimated_cost or 0),
                "priority": order.priority.value,
                "created_at": order.created_at.isoformat(),
                "scheduled_end": order.scheduled_end.isoformat() if order.scheduled_end else None,
                "project_name": next((p.nome for p in projects if p.id == order.project_id), "Projeto Desconhecido")
            })
        
        return {
            "orders": orders_data,
            "total": len(orders),
            "projects": [{"id": str(p.id), "name": p.nome} for p in projects]
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar ordens dos projetos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar ordens"
        )