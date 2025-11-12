"""
Modelos SQLAlchemy para Sistema de Produção - Sprint 10-11
Modelos avançados para planejamento, execução e monitoramento de produção
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from uuid import uuid4
from enum import Enum

from sqlalchemy import (
    Boolean, Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, 
    JSON, Numeric, String, Text, UniqueConstraint, Float
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from . import User, Project, IntelligentBudget as Budget

Base = declarative_base()

class ProductionStatus(Enum):
    """Status da ordem de produção"""
    PLANNING = "planning"
    SCHEDULED = "scheduled" 
    IN_PROGRESS = "in_progress"
    QUALITY_CHECK = "quality_check"
    COMPLETED = "completed"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"

class Priority(Enum):
    """Prioridade da ordem de produção"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class ProductionType(Enum):
    """Tipo de produção"""
    PROTOTYPE = "prototype"
    BATCH_SMALL = "batch_small"    # 1-10 unidades
    BATCH_MEDIUM = "batch_medium"  # 11-100 unidades
    BATCH_LARGE = "batch_large"    # 100+ unidades
    CUSTOM = "custom"
    SERIES = "series"

class QualityStatus(Enum):
    """Status do controle de qualidade"""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    REWORK_REQUIRED = "rework_required"
    CONDITIONAL_ACCEPTANCE = "conditional_acceptance"

class ProductionOrder(Base):
    """Ordem de produção baseada em orçamento inteligente"""
    __tablename__ = "production_orders"
    
    # IDs
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    budget_id = Column(UUID(as_uuid=True), ForeignKey("intelligent_budgets.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    
    # Produção info
    production_type = Column(SQLEnum(ProductionType), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    priority = Column(SQLEnum(Priority), default=Priority.NORMAL)
    
    # Status e timeline
    status = Column(SQLEnum(ProductionStatus), default=ProductionStatus.PLANNING)
    
    # Scheduling
    scheduled_start = Column(DateTime, nullable=True)
    scheduled_end = Column(DateTime, nullable=True)
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)
    
    # Custos de produção
    estimated_cost = Column(Numeric(12, 2), nullable=True)
    actual_cost = Column(Numeric(12, 2), nullable=True)
    cost_variance = Column(Numeric(12, 2), nullable=True)  # Diferença
    
    # Recursos necessários
    required_materials = Column(JSON, default=list, comment="Lista de materiais necessários")
    equipment_needed = Column(JSON, default=list, comment="Equipamentos necessários")
    labor_hours_estimated = Column(Numeric(8, 2), nullable=True)
    labor_hours_actual = Column(Numeric(8, 2), nullable=True)
    
    # Dependências
    dependencies = Column(JSON, default=list, comment="Dependências com outras ordens")
    blocking_issues = Column(JSON, default=list, comment="Problemas bloqueantes")
    
    # Notas e observações
    notes = Column(Text, nullable=True)
    quality_notes = Column(Text, nullable=True)
    delivery_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    budget = relationship("IntelligentBudget", back_populates="production_orders")
    project = relationship("Project")
    quality_checks = relationship("QualityCheck", back_populates="production_order")
    production_events = relationship("ProductionEvent", back_populates="production_order")

class ProductionEvent(Base):
    """Eventos da linha de produção"""
    __tablename__ = "production_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    production_order_id = Column(UUID(as_uuid=True), ForeignKey("production_orders.id"), nullable=False)
    
    # Event info
    event_type = Column(String(50), nullable=False, comment="Tipo do evento")
    description = Column(Text, nullable=False, comment="Descrição do evento")
    event_data = Column(JSON, default=dict, comment="Dados específicos do evento")
    
    # Status
    status = Column(String(20), default="pending", comment="Status do evento")
    completed = Column(Boolean, default=False)
    
    # Timestamps
    scheduled_time = Column(DateTime, nullable=True)
    actual_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    production_order = relationship("ProductionOrder", back_populates="production_events")

class QualityCheck(Base):
    """Controle de qualidade da produção"""
    __tablename__ = "quality_checks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    production_order_id = Column(UUID(as_uuid=True), ForeignKey("production_orders.id"), nullable=False)
    
    # Check info
    check_type = Column(String(50), nullable=False, comment="Tipo da verificação")
    inspector = Column(String(100), nullable=True, comment="Inspetor responsável")
    
    # Status
    status = Column(SQLEnum(QualityStatus), default=QualityStatus.PENDING)
    
    # Métricas de qualidade
    quality_metrics = Column(JSON, default=dict, comment="Métricas coletadas")
    test_results = Column(JSON, default=dict, comment="Resultados de testes")
    visual_inspection = Column(JSON, default=dict, comment="Inspeção visual")
    
    # Decisões
    passed_criteria = Column(JSON, default=list, comment="Critérios aprovados")
    failed_criteria = Column(JSON, default=list, comment="Critérios falharam")
    recommendations = Column(JSON, default=list, comment="Recomendações")
    
    # Documentação
    photos = Column(JSON, default=list, comment="Fotos da peça")
    notes = Column(Text, nullable=True, comment="Observações do inspector")
    
    # Timestamps
    scheduled_date = Column(DateTime, nullable=True)
    actual_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    production_order = relationship("ProductionOrder", back_populates="quality_checks")

class ProductionCapacity(Base):
    """Capacidade de produção das máquinas"""
    __tablename__ = "production_capacities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Equipamento info
    equipment_name = Column(String(100), nullable=False, comment="Nome do equipamento")
    equipment_type = Column(String(50), nullable=False, comment="Tipo do equipamento")
    location = Column(String(100), nullable=True, comment="Localização")
    
    # Capacidade
    max_output_per_hour = Column(Numeric(8, 2), nullable=False, comment="Output máximo/hora")
    current_output_per_hour = Column(Numeric(8, 2), nullable=True, comment="Output atual/hora")
    efficiency_rating = Column(Float, nullable=True, comment="Rating de eficiência (0-1)")
    
    # Maintenance
    last_maintenance = Column(DateTime, nullable=True)
    next_maintenance = Column(DateTime, nullable=True)
    maintenance_status = Column(String(20), default="ok", comment="Status da manutenção")
    
    # Scheduling
    available_from = Column(DateTime, nullable=True)
    available_until = Column(DateTime, nullable=True)
    booked_slots = Column(JSON, default=list, comment="Horários agendados")
    
    # Status
    status = Column(String(20), default="available", comment="Status do equipamento")
    operational = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProductionSchedule(Base):
    """Cronograma detalhado de produção"""
    __tablename__ = "production_schedules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    production_order_id = Column(UUID(as_uuid=True), ForeignKey("production_orders.id"), nullable=False)
    
    # Schedule info
    operation_name = Column(String(100), nullable=False, comment="Nome da operação")
    operation_order = Column(Integer, nullable=False, comment="Ordem da operação")
    duration_hours = Column(Numeric(6, 2), nullable=False, comment="Duração estimada (horas)")
    
    # Dependencies
    depends_on = Column(JSON, default=list, comment="Operações dependentes")
    blocked_by = Column(JSON, default=list, comment="Operações bloqueadoras")
    
    # Resources
    equipment_required = Column(JSON, default=list, comment="Equipamentos necessários")
    materials_needed = Column(JSON, default=list, comment="Materiais necessários")
    labor_skills = Column(JSON, default=list, comment="Habilidades necessárias")
    
    # Scheduling
    earliest_start = Column(DateTime, nullable=True, comment="Início mais cedo")
    latest_finish = Column(DateTime, nullable=True, comment="Fim mais tarde")
    actual_start = Column(DateTime, nullable=True)
    actual_finish = Column(DateTime, nullable=True)
    
    # Status
    status = Column(String(20), default="pending", comment="Status da operação")
    completed = Column(Boolean, default=False)
    progress_percentage = Column(Integer, default=0, comment="Progresso (0-100)")
    
    # Quality gates
    quality_gate = Column(Boolean, default=False, comment="Portão de qualidade")
    quality_check_required = Column(Boolean, default=False)
    
    # Cost tracking
    estimated_cost = Column(Numeric(10, 2), nullable=True)
    actual_cost = Column(Numeric(10, 2), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    production_order = relationship("ProductionOrder")

class ProductionMetrics(Base):
    """Métricas e KPIs de produção"""
    __tablename__ = "production_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Time period
    period_type = Column(String(20), nullable=False, comment="daily, weekly, monthly")
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Production metrics
    total_orders = Column(Integer, default=0)
    completed_orders = Column(Integer, default=0)
    on_time_delivery = Column(Integer, default=0)
    quality_pass_rate = Column(Float, nullable=True, comment="Taxa de aprovação de qualidade")
    
    # Performance metrics
    efficiency_score = Column(Float, nullable=True, comment="Score de eficiência")
    utilization_rate = Column(Float, nullable=True, comment="Taxa de utilização")
    throughput = Column(Numeric(8, 2), nullable=True, comment="Throughput médio")
    
    # Cost metrics
    total_production_cost = Column(Numeric(12, 2), default=0.0)
    average_cost_per_unit = Column(Numeric(10, 2), nullable=True)
    cost_variance_percentage = Column(Float, nullable=True)
    
    # Quality metrics
    defect_rate = Column(Float, nullable=True, comment="Taxa de defeitos")
    rework_rate = Column(Float, nullable=True, comment="Taxa de retrabalho")
    customer_satisfaction = Column(Float, nullable=True, comment="Satisfação do cliente")
    
    # Efficiency metrics
    setup_time_average = Column(Numeric(6, 2), nullable=True)
    cycle_time_average = Column(Numeric(6, 2), nullable=True)
    downtime_hours = Column(Numeric(6, 2), nullable=True)
    
    # Equipment metrics
    equipment_utilization = Column(JSON, default=dict, comment="Utilização por equipamento")
    maintenance_hours = Column(Numeric(6, 2), nullable=True)
    
    # Customer metrics
    delivery_accuracy = Column(Float, nullable=True, comment="Precisão de entrega")
    lead_time_average = Column(Numeric(8, 2), nullable=True, comment="Lead time médio")
    
    # Timestamps
    calculated_at = Column(DateTime, default=datetime.utcnow)
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('period_type', 'period_start', 'period_end', name='uq_production_metrics_period'),
    )

class ProductionOptimization(Base):
    """Sugestões e otimizações de produção"""
    __tablename__ = "production_optimizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Optimization info
    optimization_type = Column(String(50), nullable=False, comment="Tipo da otimização")
    title = Column(String(200), nullable=False, comment="Título da otimização")
    description = Column(Text, nullable=False, comment="Descrição detalhada")
    
    # Analysis data
    current_state = Column(JSON, default=dict, comment="Estado atual")
    optimized_state = Column(JSON, default=dict, comment="Estado otimizado")
    improvement_potential = Column(Float, nullable=True, comment="Potencial de melhoria (%)")
    
    # Benefits
    cost_savings = Column(Numeric(12, 2), nullable=True, comment="Economia de custos")
    time_savings = Column(Numeric(8, 2), nullable=True, comment="Economia de tempo")
    quality_improvement = Column(Float, nullable=True, comment="Melhoria de qualidade")
    
    # Implementation
    implementation_difficulty = Column(String(20), nullable=True, comment="easy, medium, hard")
    implementation_cost = Column(Numeric(10, 2), nullable=True, comment="Custo de implementação")
    implementation_time = Column(Integer, nullable=True, comment="Tempo de implementação (dias)")
    
    # ROI analysis
    roi_percentage = Column(Float, nullable=True, comment="ROI da implementação")
    payback_period = Column(Integer, nullable=True, comment="Payback em meses")
    
    # Status
    status = Column(String(20), default="identified", comment="identified, analyzed, approved, implemented")
    priority = Column(SQLEnum(Priority), default=Priority.NORMAL)
    
    # Tracking
    identified_by = Column(String(100), nullable=True, comment="Identificado por")
    analyzed_by = Column(String(100), nullable=True, comment="Analisado por")
    implemented_by = Column(String(100), nullable=True, comment="Implementado por")
    
    # Results
    actual_cost_savings = Column(Numeric(12, 2), nullable=True)
    actual_time_savings = Column(Numeric(8, 2), nullable=True)
    actual_quality_improvement = Column(Float, nullable=True)
    
    # Timestamps
    identified_at = Column(DateTime, default=datetime.utcnow)
    analyzed_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    implemented_at = Column(DateTime, nullable=True)

# Relationships are defined inline in the IntelligentBudget class in budgeting.py