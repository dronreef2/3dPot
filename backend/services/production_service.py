"""
Serviço de Produção - Sprint 10-11
Sistema completo de planejamento, execução e otimização de produção
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from enum import Enum

import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func

from backend.models.production_models import (
    ProductionOrder, ProductionStatus, Priority, ProductionType, QualityStatus,
    ProductionEvent, QualityCheck, ProductionCapacity, ProductionSchedule,
    ProductionMetrics, ProductionOptimization
)
from backend.models import IntelligentBudget as Budget, Project, User
from backend.schemas.budgeting import IntelligentBudgetResponse

logger = logging.getLogger(__name__)

class ProductionService:
    """
    Serviço principal para gerenciamento de produção
    Integra com orçamentos inteligentes para planejamento automático
    """
    
    def __init__(self):
        # Configurações de produção
        self.standard_setup_time = 0.5  # horas
        self.standard_cycle_time = 2.0  # horas por unidade
        self.max_daily_capacity = 24.0  # horas por dia
        
        # Multiplicadores de tempo por tipo de produção
        self.production_type_multipliers = {
            ProductionType.PROTOTYPE: 1.5,
            ProductionType.BATCH_SMALL: 1.0,
            ProductionType.BATCH_MEDIUM: 0.9,
            ProductionType.BATCH_LARGE: 0.8,
            ProductionType.CUSTOM: 1.3,
            ProductionType.SERIES: 0.7
        }
        
        # Tolerâncias de qualidade
        self.quality_tolerances = {
            "dimensional": 0.1,  # mm
            "surface_finish": 0.05,  # Ra em micrômetros
            "strength": 0.05  # 5% tolerância
        }
    
    async def create_production_order(
        self, 
        db: Session, 
        budget_id: UUID,
        production_config: Dict[str, Any]
    ) -> ProductionOrder:
        """
        Criar ordem de produção baseada em orçamento inteligente
        
        Args:
            db: Sessão do banco de dados
            budget_id: ID do orçamento inteligente
            production_config: Configurações da produção (quantidade, prioridade, etc.)
            
        Returns:
            Ordem de produção criada e planejada
        """
        try:
            # 1. Obter dados do orçamento
            budget = db.query(Budget).filter(Budget.id == budget_id).first()
            if not budget:
                raise ValueError("Orçamento não encontrado")
            
            project = db.query(Project).filter(Project.id == budget.projeto_id).first()
            
            # 2. Determinar tipo de produção baseado na quantidade
            quantity = production_config.get("quantity", 1)
            production_type = self._determine_production_type(quantity)
            
            # 3. Criar ordem de produção
            production_order = ProductionOrder(
                budget_id=budget_id,
                project_id=project.id,
                production_type=production_type,
                quantity=quantity,
                priority=production_config.get("priority", Priority.NORMAL),
                
                # Custos baseados no orçamento
                estimated_cost=float(budget.preco_final) * quantity,
                
                # Recursos necessários do orçamento
                required_materials=self._extract_materials_from_budget(budget),
                equipment_needed=self._determine_required_equipment(production_type),
                labor_hours_estimated=self._calculate_labor_hours(budget, quantity, production_type)
            )
            
            db.add(production_order)
            db.commit()
            db.refresh(production_order)
            
            # 4. Planejar cronograma da produção
            await self._create_production_schedule(db, production_order, budget)
            
            # 5. Criar eventos de produção
            await self._create_production_events(db, production_order)
            
            # 6. Agendar controles de qualidade
            await self._schedule_quality_checks(db, production_order)
            
            logger.info(f"Ordem de produção criada: {production_order.id}")
            return production_order
            
        except Exception as e:
            logger.error(f"Erro ao criar ordem de produção: {e}")
            db.rollback()
            raise
    
    def _determine_production_type(self, quantity: int) -> ProductionType:
        """Determinar tipo de produção baseado na quantidade"""
        if quantity == 1:
            return ProductionType.PROTOTYPE
        elif 2 <= quantity <= 10:
            return ProductionType.BATCH_SMALL
        elif 11 <= quantity <= 100:
            return ProductionType.BATCH_MEDIUM
        elif quantity > 100:
            return ProductionType.BATCH_LARGE
        else:
            return ProductionType.CUSTOM
    
    def _extract_materials_from_budget(self, budget: Budget) -> List[Dict[str, Any]]:
        """Extrair materiais necessários do orçamento"""
        materials = []
        
        if budget.itens_detalhados:
            for item in budget.itens_detalhados:
                if "material" in item.get("descricao", "").lower():
                    materials.append({
                        "name": item.get("descricao", ""),
                        "quantity": item.get("quantidade", ""),
                        "cost": float(item.get("preco_total", 0)),
                        "supplier": item.get("fornecedor", ""),
                        "critical": True
                    })
        
        return materials
    
    def _determine_required_equipment(self, production_type: ProductionType) -> List[Dict[str, str]]:
        """Determinar equipamentos necessários baseado no tipo de produção"""
        equipment_map = {
            ProductionType.PROTOTYPE: [
                {"type": "3d_printer", "model": "Professional Grade"},
                {"type": "post_processor", "model": "Standard"},
                {"type": "quality_control", "model": "Manual"}
            ],
            ProductionType.BATCH_SMALL: [
                {"type": "3d_printer", "model": "Industrial Grade"},
                {"type": "post_processor", "model": "Semi-automated"},
                {"type": "quality_control", "model": "Automated"}
            ],
            ProductionType.BATCH_MEDIUM: [
                {"type": "3d_printer", "model": "Multi-slot Industrial"},
                {"type": "post_processor", "model": "Fully automated"},
                {"type": "quality_control", "model": "Automated + Manual verification"}
            ],
            ProductionType.BATCH_LARGE: [
                {"type": "3d_printer", "model": "Production Line"},
                {"type": "post_processor", "model": "Fully automated"},
                {"type": "quality_control", "model": "Automated + Sample verification"}
            ]
        }
        
        return equipment_map.get(production_type, equipment_map[ProductionType.BATCH_SMALL])
    
    def _calculate_labor_hours(
        self, 
        budget: Budget, 
        quantity: int, 
        production_type: ProductionType
    ) -> float:
        """Calcular horas de mão de obra necessárias"""
        
        # Base hours from budget
        setup_hours = float(budget.tempo_montagem_horas or 0)
        per_unit_hours = float(budget.tempo_impressao_horas or 0)
        
        # Adjust for production type
        type_multiplier = self.production_type_multipliers.get(production_type, 1.0)
        
        # Calculate total labor
        total_hours = (
            setup_hours * type_multiplier +  # Setup time
            per_unit_hours * quantity * type_multiplier  # Per-unit time
        )
        
        # Add buffer for production complexities
        buffer_multiplier = 1.2 if production_type == ProductionType.CUSTOM else 1.1
        
        return round(total_hours * buffer_multiplier, 2)
    
    async def _create_production_schedule(
        self, 
        db: Session, 
        production_order: ProductionOrder, 
        budget: Budget
    ):
        """Criar cronograma detalhado da produção"""
        
        operations = [
            {
                "name": "Setup e Preparação",
                "order": 1,
                "duration": self.standard_setup_time,
                "dependencies": [],
                "quality_gate": False
            },
            {
                "name": "Impressão 3D",
                "order": 2,
                "duration": float(budget.tempo_impressao_horas or 2.0) * production_order.quantity,
                "dependencies": ["Setup e Preparação"],
                "quality_gate": False
            },
            {
                "name": "Pós-processamento",
                "order": 3,
                "duration": float(budget.tempo_montagem_horas or 1.0),
                "dependencies": ["Impressão 3D"],
                "quality_gate": True,
                "quality_check_required": True
            },
            {
                "name": "Controle de Qualidade",
                "order": 4,
                "duration": 0.5,
                "dependencies": ["Pós-processamento"],
                "quality_gate": True,
                "quality_check_required": True
            },
            {
                "name": "Embalagem e Entrega",
                "order": 5,
                "duration": 0.3,
                "dependencies": ["Controle de Qualidade"],
                "quality_gate": False
            }
        ]
        
        # Calculate schedule based on dependencies
        current_time = datetime.utcnow()
        
        for operation in operations:
            # Calculate earliest start based on dependencies
            earliest_start = current_time
            if operation["dependencies"]:
                # Find latest finish time of dependencies
                dep_finishes = []
                for dep_name in operation["dependencies"]:
                    dep_schedule = db.query(ProductionSchedule).filter(
                        and_(
                            ProductionSchedule.production_order_id == production_order.id,
                            ProductionSchedule.operation_name == dep_name
                        )
                    ).first()
                    if dep_schedule and dep_schedule.actual_finish:
                        dep_finishes.append(dep_schedule.actual_finish)
                
                if dep_finishes:
                    earliest_start = max(dep_finishes)
            
            # Create schedule entry
            schedule = ProductionSchedule(
                production_order_id=production_order.id,
                operation_name=operation["name"],
                operation_order=operation["order"],
                duration_hours=operation["duration"],
                depends_on=operation["dependencies"],
                earliest_start=earliest_start,
                quality_gate=operation["quality_gate"],
                quality_check_required=operation.get("quality_check_required", False),
                estimated_cost=float(budget.preco_final) / len(operations)
            )
            
            db.add(schedule)
            
            # Update current time for next operation
            current_time = earliest_start + timedelta(hours=operation["duration"])
        
        db.commit()
    
    async def _create_production_events(self, db: Session, production_order: ProductionOrder):
        """Criar eventos da linha de produção"""
        
        events = [
            {
                "type": "order_created",
                "description": "Ordem de produção criada",
                "event_data": {
                    "order_id": str(production_order.id),
                    "quantity": production_order.quantity,
                    "type": production_order.production_type.value
                }
            },
            {
                "type": "materials_required",
                "description": "Materiais necessários identificados",
                "event_data": {
                    "materials_count": len(production_order.required_materials)
                }
            },
            {
                "type": "capacity_check",
                "description": "Verificação de capacidade de produção",
                "event_data": {
                    "equipment_needed": len(production_order.equipment_needed)
                }
            }
        ]
        
        for event_data in events:
            event = ProductionEvent(
                production_order_id=production_order.id,
                event_type=event_data["type"],
                description=event_data["description"],
                event_data=event_data["event_data"],
                scheduled_time=datetime.utcnow()
            )
            
            db.add(event)
        
        db.commit()
    
    async def _schedule_quality_checks(self, db: Session, production_order: ProductionOrder):
        """Agendar controles de qualidade"""
        
        quality_checks = [
            {
                "type": "dimensional_inspection",
                "description": "Inspeção dimensional",
                "quality_gate": True
            },
            {
                "type": "surface_finish",
                "description": "Acabamento superficial",
                "quality_gate": False
            },
            {
                "type": "strength_test",
                "description": "Teste de resistência",
                "quality_gate": True
            }
        ]
        
        for check_data in quality_checks:
            check = QualityCheck(
                production_order_id=production_order.id,
                check_type=check_data["type"],
                inspector="Sistema Automático",
                scheduled_date=datetime.utcnow() + timedelta(hours=2)
            )
            
            db.add(check)
        
        db.commit()
    
    async def get_production_status(
        self, 
        db: Session, 
        production_order_id: UUID
    ) -> Dict[str, Any]:
        """Obter status detalhado da produção"""
        
        order = db.query(ProductionOrder).filter(
            ProductionOrder.id == production_order_id
        ).first()
        
        if not order:
            raise ValueError("Ordem de produção não encontrada")
        
        # Get schedule progress
        schedules = db.query(ProductionSchedule).filter(
            ProductionSchedule.production_order_id == production_order_id
        ).order_by(ProductionSchedule.operation_order).all()
        
        # Calculate progress percentage
        total_operations = len(schedules)
        completed_operations = sum(1 for s in schedules if s.completed)
        progress_percentage = (completed_operations / total_operations * 100) if total_operations > 0 else 0
        
        # Get quality checks status
        quality_checks = db.query(QualityCheck).filter(
            QualityCheck.production_order_id == production_order_id
        ).all()
        
        # Get events
        events = db.query(ProductionEvent).filter(
            ProductionEvent.production_order_id == production_order_id
        ).order_by(ProductionEvent.created_at.desc()).limit(10).all()
        
        return {
            "production_order": {
                "id": str(order.id),
                "status": order.status.value,
                "progress_percentage": progress_percentage,
                "quantity": order.quantity,
                "type": order.production_type.value,
                "priority": order.priority.value,
                "scheduled_start": order.scheduled_start.isoformat() if order.scheduled_start else None,
                "estimated_completion": order.scheduled_end.isoformat() if order.scheduled_end else None
            },
            "schedule": [
                {
                    "operation": s.operation_name,
                    "order": s.operation_order,
                    "status": s.status,
                    "progress": s.progress_percentage,
                    "duration": float(s.duration_hours),
                    "start_time": s.actual_start.isoformat() if s.actual_start else s.earliest_start.isoformat() if s.earliest_start else None,
                    "quality_gate": s.quality_gate
                }
                for s in schedules
            ],
            "quality": [
                {
                    "type": q.check_type,
                    "status": q.status.value,
                    "scheduled": q.scheduled_date.isoformat() if q.scheduled_date else None,
                    "completed": q.actual_date.isoformat() if q.actual_date else None
                }
                for q in quality_checks
            ],
            "recent_events": [
                {
                    "type": e.event_type,
                    "description": e.description,
                    "timestamp": e.created_at.isoformat(),
                    "completed": e.completed
                }
                for e in events
            ],
            "metrics": {
                "cost_variance": float(order.cost_variance or 0),
                "time_variance": self._calculate_time_variance(order),
                "efficiency_score": self._calculate_efficiency_score(order, schedules)
            }
        }
    
    def _calculate_time_variance(self, order: ProductionOrder) -> float:
        """Calcular variação de tempo da produção"""
        if not order.scheduled_end or not order.actual_end:
            return 0.0
        
        scheduled_duration = (order.scheduled_end - order.scheduled_start).total_seconds() / 3600
        actual_duration = (order.actual_end - order.actual_start).total_seconds() / 3600
        
        if scheduled_duration == 0:
            return 0.0
        
        return ((actual_duration - scheduled_duration) / scheduled_duration) * 100
    
    def _calculate_efficiency_score(
        self, 
        order: ProductionOrder, 
        schedules: List[ProductionSchedule]
    ) -> float:
        """Calcular score de eficiência da produção"""
        if not schedules:
            return 0.0
        
        # Base efficiency on schedule adherence
        on_time_operations = sum(1 for s in schedules if s.completed and s.actual_finish <= s.latest_finish)
        total_operations = len(schedules)
        
        schedule_efficiency = (on_time_operations / total_operations) if total_operations > 0 else 0
        
        # Quality factor
        quality_factor = 0.9 if order.status == ProductionStatus.COMPLETED else 0.7
        
        return round(schedule_efficiency * quality_factor * 100, 2)
    
    async def update_production_status(
        self,
        db: Session,
        production_order_id: UUID,
        new_status: ProductionStatus,
        event_data: Optional[Dict[str, Any]] = None
    ) -> ProductionOrder:
        """Atualizar status da produção e registrar evento"""
        
        order = db.query(ProductionOrder).filter(
            ProductionOrder.id == production_order_id
        ).first()
        
        if not order:
            raise ValueError("Ordem de produção não encontrada")
        
        # Update status
        old_status = order.status
        order.status = new_status
        
        # Handle status-specific updates
        if new_status == ProductionStatus.IN_PROGRESS:
            if not order.actual_start:
                order.actual_start = datetime.utcnow()
        
        elif new_status == ProductionStatus.COMPLETED:
            order.actual_end = datetime.utcnow()
            order.completed_at = datetime.utcnow()
            
            # Calculate final cost variance
            if order.actual_cost and order.estimated_cost:
                order.cost_variance = float(order.actual_cost) - float(order.estimated_cost)
        
        db.commit()
        db.refresh(order)
        
        # Create status change event
        event = ProductionEvent(
            production_order_id=production_order_id,
            event_type="status_change",
            description=f"Status alterado de {old_status.value} para {new_status.value}",
            event_data={
                "old_status": old_status.value,
                "new_status": new_status.value,
                "updated_by": "system",
                "additional_data": event_data or {}
            },
            actual_time=datetime.utcnow()
        )
        
        db.add(event)
        db.commit()
        
        return order
    
    async def get_production_dashboard_data(
        self, 
        db: Session, 
        user_id: UUID
    ) -> Dict[str, Any]:
        """Obter dados para dashboard de produção"""
        
        # Get user's production orders
        orders = db.query(ProductionOrder).filter(
            ProductionOrder.project_id.in_(
                db.query(Project.id).filter(Project.owner_id == user_id)
            )
        ).all()
        
        # Calculate metrics
        total_orders = len(orders)
        completed_orders = sum(1 for o in orders if o.status == ProductionStatus.COMPLETED)
        in_progress_orders = sum(1 for o in orders if o.status == ProductionStatus.IN_PROGRESS)
        pending_orders = sum(1 for o in orders if o.status in [ProductionStatus.PLANNING, ProductionStatus.SCHEDULED])
        
        # Calculate costs
        total_estimated_cost = sum(float(o.estimated_cost or 0) for o in orders)
        total_actual_cost = sum(float(o.actual_cost or 0) for o in orders if o.actual_cost)
        
        # Status distribution
        status_distribution = {}
        for status in ProductionStatus:
            status_distribution[status.value] = sum(
                1 for o in orders if o.status == status
            )
        
        # Priority distribution
        priority_distribution = {}
        for priority in Priority:
            priority_distribution[priority.value] = sum(
                1 for o in orders if o.priority == priority
            )
        
        # Production type distribution
        type_distribution = {}
        for prod_type in ProductionType:
            type_distribution[prod_type.value] = sum(
                1 for o in orders if o.production_type == prod_type
            )
        
        # Recent orders (last 10)
        recent_orders = sorted(
            orders, 
            key=lambda x: x.created_at, 
            reverse=True
        )[:10]
        
        # Calculate efficiency metrics
        on_time_delivery = sum(
            1 for o in orders 
            if o.status == ProductionStatus.COMPLETED and 
               o.actual_end and o.scheduled_end and 
               o.actual_end <= o.scheduled_end
        )
        
        efficiency_rate = (
            (on_time_delivery / completed_orders * 100) if completed_orders > 0 else 0
        )
        
        return {
            "overview": {
                "total_orders": total_orders,
                "completed_orders": completed_orders,
                "in_progress_orders": in_progress_orders,
                "pending_orders": pending_orders,
                "efficiency_rate": round(efficiency_rate, 2),
                "total_estimated_cost": total_estimated_cost,
                "total_actual_cost": total_actual_cost,
                "cost_variance": total_actual_cost - total_estimated_cost
            },
            "distributions": {
                "status": status_distribution,
                "priority": priority_distribution,
                "type": type_distribution
            },
            "recent_orders": [
                {
                    "id": str(o.id),
                    "status": o.status.value,
                    "priority": o.priority.value,
                    "quantity": o.quantity,
                    "estimated_cost": float(o.estimated_cost or 0),
                    "created_at": o.created_at.isoformat(),
                    "scheduled_end": o.scheduled_end.isoformat() if o.scheduled_end else None
                }
                for o in recent_orders
            ],
            "kpis": {
                "average_lead_time": self._calculate_average_lead_time(orders),
                "quality_pass_rate": await self._calculate_quality_pass_rate(db, orders),
                "resource_utilization": self._calculate_resource_utilization(orders)
            }
        }
    
    def _calculate_average_lead_time(self, orders: List[ProductionOrder]) -> float:
        """Calcular tempo médio de entrega (lead time)"""
        completed_orders = [
            o for o in orders 
            if o.status == ProductionStatus.COMPLETED and o.actual_start and o.actual_end
        ]
        
        if not completed_orders:
            return 0.0
        
        lead_times = [
            (o.actual_end - o.actual_start).total_seconds() / 3600  # Convert to hours
            for o in completed_orders
        ]
        
        return round(np.mean(lead_times), 2)
    
    async def _calculate_quality_pass_rate(
        self, 
        db: Session, 
        orders: List[ProductionOrder]
    ) -> float:
        """Calcular taxa de aprovação de qualidade"""
        
        order_ids = [o.id for o in orders]
        
        if not order_ids:
            return 0.0
        
        total_checks = db.query(QualityCheck).filter(
            QualityCheck.production_order_id.in_(order_ids)
        ).count()
        
        passed_checks = db.query(QualityCheck).filter(
            and_(
                QualityCheck.production_order_id.in_(order_ids),
                QualityCheck.status == QualityStatus.PASSED
            )
        ).count()
        
        return round((passed_checks / total_checks * 100) if total_checks > 0 else 0, 2)
    
    def _calculate_resource_utilization(self, orders: List[ProductionOrder]) -> float:
        """Calcular taxa de utilização de recursos"""
        # Simplified calculation based on labor hours
        total_estimated_hours = sum(float(o.labor_hours_estimated or 0) for o in orders)
        total_available_hours = len(orders) * 24 * 30  # Assume 30 days, 24 hours/day
        
        if total_available_hours == 0:
            return 0.0
        
        return round((total_estimated_hours / total_available_hours) * 100, 2)
    
    async def optimize_production_schedule(
        self,
        db: Session,
        production_order_id: UUID
    ) -> List[Dict[str, Any]]:
        """Otimizar cronograma de produção para melhorar eficiência"""
        
        order = db.query(ProductionOrder).filter(
            ProductionOrder.id == production_order_id
        ).first()
        
        if not order:
            raise ValueError("Ordem de produção não encontrada")
        
        # Get current schedule
        schedules = db.query(ProductionSchedule).filter(
            ProductionSchedule.production_order_id == production_order_id
        ).order_by(ProductionSchedule.operation_order).all()
        
        optimizations = []
        
        # 1. Parallel processing optimization
        parallel_ops = self._identify_parallel_operations(schedules)
        if parallel_ops:
            optimizations.append({
                "type": "parallel_processing",
                "title": "Processamento Paralelo",
                "description": f"As operações {', '.join(parallel_ops)} podem ser executadas em paralelo",
                "time_savings": 2.5,  # hours
                "cost_savings": 150.0,  # BRL
                "implementation_difficulty": "medium",
                "priority": "high"
            })
        
        # 2. Setup time optimization
        setup_ops = [s for s in schedules if "setup" in s.operation_name.lower()]
        if setup_ops and len(schedules) > 2:
            optimizations.append({
                "type": "setup_optimization",
                "title": "Otimização de Setup",
                "description": "Reduzir tempo de setup através de preparação prévia de ferramentas",
                "time_savings": 0.5,  # hours
                "cost_savings": 75.0,  # BRL
                "implementation_difficulty": "easy",
                "priority": "medium"
            })
        
        # 3. Quality gate optimization
        qc_ops = [s for s in schedules if s.quality_gate]
        if len(qc_ops) > 1:
            optimizations.append({
                "type": "quality_gate_optimization",
                "title": "Consolidação de Controle de Qualidade",
                "description": "Consolidar múltiplos controles de qualidade em pontos estratégicos",
                "time_savings": 1.0,  # hours
                "cost_savings": 100.0,  # BRL
                "implementation_difficulty": "hard",
                "priority": "low"
            })
        
        # 4. Equipment utilization optimization
        equipment_ops = [s for s in schedules if s.equipment_required]
        if equipment_ops and len(equipment_ops) > 3:
            optimizations.append({
                "type": "equipment_optimization",
                "title": "Otimização de Utilização de Equipamentos",
                "description": "Reorganizar operações para melhor utilização de equipamentos",
                "time_savings": 1.5,  # hours
                "cost_savings": 200.0,  # BRL
                "implementation_difficulty": "medium",
                "priority": "high"
            })
        
        return optimizations
    
    def _identify_parallel_operations(self, schedules: List[ProductionSchedule]) -> List[str]:
        """Identificar operações que podem ser executadas em paralelo"""
        parallel_candidates = []
        
        for i, schedule in enumerate(schedules):
            # Look for operations that don't depend on each other
            depends_on = schedule.depends_on or []
            
            # Find operations that could run in parallel
            for j, other_schedule in enumerate(schedules):
                if i != j:
                    other_depends_on = other_schedule.depends_on or []
                    
                    # Check if they don't depend on each other
                    if (schedule.operation_name not in other_depends_on and 
                        other_schedule.operation_name not in depends_on and
                        "setup" not in schedule.operation_name.lower() and
                        "setup" not in other_schedule.operation_name.lower()):
                        parallel_candidates.extend([
                            schedule.operation_name,
                            other_schedule.operation_name
                        ])
        
        return list(set(parallel_candidates))
    
    async def generate_production_report(
        self,
        db: Session,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Gerar relatório completo de produção"""
        
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Get orders in date range
        orders = db.query(ProductionOrder).filter(
            and_(
                ProductionOrder.project_id.in_(
                    db.query(Project.id).filter(Project.owner_id == user_id)
                ),
                ProductionOrder.created_at >= start_date,
                ProductionOrder.created_at <= end_date
            )
        ).all()
        
        # Calculate comprehensive metrics
        total_orders = len(orders)
        completed_orders = [o for o in orders if o.status == ProductionStatus.COMPLETED]
        
        # Financial metrics
        total_revenue = sum(float(o.estimated_cost or 0) for o in orders)
        total_costs = sum(float(o.actual_cost or o.estimated_cost or 0) for o in orders)
        gross_profit = total_revenue - total_costs
        profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Operational metrics
        on_time_delivery = sum(
            1 for o in completed_orders
            if o.actual_end and o.scheduled_end and o.actual_end <= o.scheduled_end
        )
        on_time_rate = (on_time_delivery / len(completed_orders) * 100) if completed_orders else 0
        
        # Quality metrics
        quality_metrics = await self._calculate_quality_metrics(db, orders)
        
        # Time metrics
        avg_lead_time = self._calculate_average_lead_time(orders)
        efficiency_score = self._calculate_overall_efficiency_score(orders)
        
        return {
            "report_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": (end_date - start_date).days
            },
            "financial_summary": {
                "total_revenue": round(total_revenue, 2),
                "total_costs": round(total_costs, 2),
                "gross_profit": round(gross_profit, 2),
                "profit_margin": round(profit_margin, 2),
                "cost_per_order": round(total_costs / total_orders, 2) if total_orders > 0 else 0
            },
            "operational_summary": {
                "total_orders": total_orders,
                "completed_orders": len(completed_orders),
                "on_time_delivery_rate": round(on_time_rate, 2),
                "average_lead_time_hours": round(avg_lead_time, 2),
                "efficiency_score": round(efficiency_score, 2)
            },
            "quality_summary": quality_metrics,
            "production_trends": await self._calculate_production_trends(orders, start_date, end_date),
            "recommendations": await self._generate_production_recommendations(orders, quality_metrics)
        }
    
    async def _calculate_quality_metrics(self, db: Session, orders: List[ProductionOrder]) -> Dict[str, float]:
        """Calcular métricas de qualidade"""
        
        order_ids = [o.id for o in orders]
        
        if not order_ids:
            return {"overall_rate": 0, "defect_rate": 0, "rework_rate": 0}
        
        total_checks = db.query(QualityCheck).filter(
            QualityCheck.production_order_id.in_(order_ids)
        ).count()
        
        passed_checks = db.query(QualityCheck).filter(
            and_(
                QualityCheck.production_order_id.in_(order_ids),
                QualityCheck.status == QualityStatus.PASSED
            )
        ).count()
        
        failed_checks = db.query(QualityCheck).filter(
            and_(
                QualityCheck.production_order_id.in_(order_ids),
                QualityCheck.status == QualityStatus.FAILED
            )
        ).count()
        
        rework_checks = db.query(QualityCheck).filter(
            and_(
                QualityCheck.production_order_id.in_(order_ids),
                QualityCheck.status == QualityStatus.REWORK_REQUIRED
            )
        ).count()
        
        return {
            "overall_pass_rate": round((passed_checks / total_checks * 100) if total_checks > 0 else 0, 2),
            "defect_rate": round((failed_checks / total_checks * 100) if total_checks > 0 else 0, 2),
            "rework_rate": round((rework_checks / total_checks * 100) if total_checks > 0 else 0, 2)
        }
    
    def _calculate_overall_efficiency_score(self, orders: List[ProductionOrder]) -> float:
        """Calcular score geral de eficiência"""
        if not orders:
            return 0.0
        
        # Multiple factors for efficiency
        completion_rate = len([o for o in orders if o.status == ProductionStatus.COMPLETED]) / len(orders)
        
        # Cost variance factor
        cost_variances = [float(o.cost_variance or 0) for o in orders if o.cost_variance]
        avg_cost_variance = abs(np.mean(cost_variances)) if cost_variances else 0
        
        # Time variance factor
        time_variances = []
        for o in orders:
            if o.actual_start and o.actual_end and o.scheduled_start and o.scheduled_end:
                actual_duration = (o.actual_end - o.actual_start).total_seconds() / 3600
                scheduled_duration = (o.scheduled_end - o.scheduled_start).total_seconds() / 3600
                if scheduled_duration > 0:
                    time_variance = abs((actual_duration - scheduled_duration) / scheduled_duration)
                    time_variances.append(time_variance)
        
        avg_time_variance = np.mean(time_variances) if time_variances else 0
        
        # Combined efficiency score
        base_score = completion_rate * 100
        cost_penalty = min(avg_cost_variance / 100, 20)  # Max 20% penalty
        time_penalty = min(avg_time_variance * 100, 15)  # Max 15% penalty
        
        efficiency_score = max(0, base_score - cost_penalty - time_penalty)
        
        return round(efficiency_score, 2)
    
    async def _calculate_production_trends(
        self, 
        orders: List[ProductionOrder], 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Calcular tendências de produção"""
        
        # Group orders by day
        daily_orders = {}
        daily_revenue = {}
        
        for order in orders:
            day = order.created_at.date()
            daily_orders[day] = daily_orders.get(day, 0) + 1
            daily_revenue[day] = daily_revenue.get(day, 0) + float(order.estimated_cost or 0)
        
        # Calculate trends
        orders_trend = "stable"
        revenue_trend = "stable"
        
        if len(daily_orders) > 7:
            first_half = list(daily_orders.values())[:len(daily_orders)//2]
            second_half = list(daily_orders.values())[len(daily_orders)//2:]
            
            first_avg = np.mean(first_half)
            second_avg = np.mean(second_half)
            
            if second_avg > first_avg * 1.1:
                orders_trend = "increasing"
            elif second_avg < first_avg * 0.9:
                orders_trend = "decreasing"
        
        return {
            "orders_per_day": daily_orders,
            "revenue_per_day": daily_revenue,
            "orders_trend": orders_trend,
            "revenue_trend": revenue_trend,
            "peak_day": max(daily_orders, key=daily_orders.get) if daily_orders else None,
            "lowest_day": min(daily_orders, key=daily_orders.get) if daily_orders else None
        }
    
    async def _generate_production_recommendations(
        self, 
        orders: List[ProductionOrder], 
        quality_metrics: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Gerar recomendações para melhoria da produção"""
        
        recommendations = []
        
        # Quality recommendations
        if quality_metrics.get("defect_rate", 0) > 5:
            recommendations.append({
                "type": "quality_improvement",
                "priority": "high",
                "title": "Melhoria de Qualidade",
                "description": "Taxa de defeitos acima de 5%. Revisar processo de controle de qualidade.",
                "potential_savings": "Redução de 30% nos custos de retrabalho"
            })
        
        # Efficiency recommendations
        completed_orders = [o for o in orders if o.status == ProductionStatus.COMPLETED]
        if completed_orders:
            avg_cost_variance = np.mean([abs(float(o.cost_variance or 0)) for o in completed_orders])
            if avg_cost_variance > 50:
                recommendations.append({
                    "type": "cost_optimization",
                    "priority": "medium",
                    "title": "Otimização de Custos",
                    "description": "Alta variabilidade nos custos. Padronizar processos para maior previsibilidade.",
                    "potential_savings": "Economia de R$ 25% nos custos de produção"
                })
        
        # Throughput recommendations
        if len(orders) > 20:
            batch_orders = [o for o in orders if o.production_type in [ProductionType.BATCH_MEDIUM, ProductionType.BATCH_LARGE]]
            if len(batch_orders) < len(orders) * 0.3:
                recommendations.append({
                    "type": "throughput_optimization",
                    "priority": "medium",
                    "title": "Otimização de Throughput",
                    "description": "Aumentar produção em lote para melhorar eficiência operacional.",
                    "potential_savings": "Aumento de 40% na capacidade de produção"
                })
        
        return recommendations