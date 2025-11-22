"""
Schemas Pydantic para Sistema de Produção - Sprint 10-11
Validação de dados para produção avançada
"""

from typing import Optional, Dict, List, Any
from uuid import UUID
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

from backend.schemas.budgeting import IntelligentBudgetResponse

# Enums
class ProductionStatusEnum(str, Enum):
    PLANNING = "planning"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    QUALITY_CHECK = "quality_check"
    COMPLETED = "completed"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"

class PriorityEnum(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class ProductionTypeEnum(str, Enum):
    PROTOTYPE = "prototype"
    BATCH_SMALL = "batch_small"
    BATCH_MEDIUM = "batch_medium"
    BATCH_LARGE = "batch_large"
    CUSTOM = "custom"
    SERIES = "series"

class QualityStatusEnum(str, Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    REWORK_REQUIRED = "rework_required"
    CONDITIONAL_ACCEPTANCE = "conditional_acceptance"

# Production Order Schemas
class ProductionOrderCreate(BaseModel):
    """Schema para criar ordem de produção"""
    budget_id: UUID = Field(..., description="ID do orçamento inteligente")
    quantity: int = Field(..., ge=1, le=1000, description="Quantidade a produzir")
    priority: PriorityEnum = Field(default=PriorityEnum.NORMAL, description="Prioridade da produção")
    production_type: Optional[ProductionTypeEnum] = Field(None, description="Tipo de produção (auto-detectado se não fornecido)")
    requested_delivery_date: Optional[datetime] = Field(None, description="Data solicitada de entrega")
    special_requirements: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Requisitos especiais")
    notes: Optional[str] = Field(None, description="Observações adicionais")

class ProductionOrderResponse(BaseModel):
    """Schema para resposta de ordem de produção"""
    id: UUID
    budget_id: UUID
    project_id: UUID
    production_type: ProductionTypeEnum
    quantity: int
    priority: PriorityEnum
    status: ProductionStatusEnum
    
    # Scheduling
    scheduled_start: Optional[datetime]
    scheduled_end: Optional[datetime]
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    
    # Costs
    estimated_cost: Optional[float]
    actual_cost: Optional[float]
    cost_variance: Optional[float]
    
    # Resources
    required_materials: List[Dict[str, Any]]
    equipment_needed: List[Dict[str, Any]]
    labor_hours_estimated: Optional[float]
    labor_hours_actual: Optional[float]
    
    # Quality & delivery
    quality_notes: Optional[str]
    delivery_notes: Optional[str]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class ProductionOrderUpdate(BaseModel):
    """Schema para atualizar ordem de produção"""
    status: Optional[ProductionStatusEnum] = None
    priority: Optional[PriorityEnum] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    actual_cost: Optional[float] = None
    labor_hours_actual: Optional[float] = None
    quality_notes: Optional[str] = None
    delivery_notes: Optional[str] = None
    notes: Optional[str] = None

# Production Schedule Schemas
class ProductionScheduleCreate(BaseModel):
    """Schema para criar cronograma de produção"""
    production_order_id: UUID
    operation_name: str
    operation_order: int
    duration_hours: float
    depends_on: List[str] = Field(default_factory=list)
    equipment_required: List[Dict[str, str]] = Field(default_factory=list)
    materials_needed: List[Dict[str, Any]] = Field(default_factory=list)
    quality_gate: bool = False
    quality_check_required: bool = False

class ProductionScheduleResponse(BaseModel):
    """Schema para resposta de cronograma"""
    id: UUID
    production_order_id: UUID
    operation_name: str
    operation_order: int
    duration_hours: float
    depends_on: List[str]
    equipment_required: List[Dict[str, str]]
    materials_needed: List[Dict[str, Any]]
    
    # Scheduling
    earliest_start: Optional[datetime]
    latest_finish: Optional[datetime]
    actual_start: Optional[datetime]
    actual_finish: Optional[datetime]
    
    # Status
    status: str
    completed: bool
    progress_percentage: int
    quality_gate: bool
    quality_check_required: bool
    
    # Cost tracking
    estimated_cost: Optional[float]
    actual_cost: Optional[float]
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Quality Check Schemas
class QualityCheckCreate(BaseModel):
    """Schema para criar controle de qualidade"""
    production_order_id: UUID
    check_type: str
    inspector: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    
class QualityCheckResponse(BaseModel):
    """Schema para resposta de controle de qualidade"""
    id: UUID
    production_order_id: UUID
    check_type: str
    inspector: Optional[str]
    status: QualityStatusEnum
    
    # Metrics
    quality_metrics: Dict[str, Any]
    test_results: Dict[str, Any]
    visual_inspection: Dict[str, Any]
    
    # Results
    passed_criteria: List[str]
    failed_criteria: List[str]
    recommendations: List[str]
    
    # Documentation
    photos: List[str]
    notes: Optional[str]
    
    # Timestamps
    scheduled_date: Optional[datetime]
    actual_date: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class QualityCheckUpdate(BaseModel):
    """Schema para atualizar controle de qualidade"""
    status: Optional[QualityStatusEnum] = None
    quality_metrics: Optional[Dict[str, Any]] = None
    test_results: Optional[Dict[str, Any]] = None
    visual_inspection: Optional[Dict[str, Any]] = None
    passed_criteria: Optional[List[str]] = None
    failed_criteria: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    photos: Optional[List[str]] = None
    notes: Optional[str] = None
    actual_date: Optional[datetime] = None

# Production Event Schemas
class ProductionEventCreate(BaseModel):
    """Schema para criar evento de produção"""
    production_order_id: UUID
    event_type: str
    description: str
    event_data: Dict[str, Any] = Field(default_factory=dict)
    scheduled_time: Optional[datetime] = None

class ProductionEventResponse(BaseModel):
    """Schema para resposta de evento"""
    id: UUID
    production_order_id: UUID
    event_type: str
    description: str
    event_data: Dict[str, Any]
    status: str
    completed: bool
    scheduled_time: Optional[datetime]
    actual_time: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Production Capacity Schemas
class ProductionCapacityCreate(BaseModel):
    """Schema para criar capacidade de produção"""
    equipment_name: str
    equipment_type: str
    location: Optional[str] = None
    max_output_per_hour: float
    current_output_per_hour: Optional[float] = None
    efficiency_rating: Optional[float] = None
    last_maintenance: Optional[datetime] = None
    next_maintenance: Optional[datetime] = None
    available_from: Optional[datetime] = None
    available_until: Optional[datetime] = None

class ProductionCapacityResponse(BaseModel):
    """Schema para resposta de capacidade"""
    id: UUID
    equipment_name: str
    equipment_type: str
    location: Optional[str]
    max_output_per_hour: float
    current_output_per_hour: Optional[float]
    efficiency_rating: Optional[float]
    last_maintenance: Optional[datetime]
    next_maintenance: Optional[datetime]
    maintenance_status: str
    available_from: Optional[datetime]
    available_until: Optional[datetime]
    booked_slots: List[Dict[str, Any]]
    status: str
    operational: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Production Metrics Schemas
class ProductionMetricsCreate(BaseModel):
    """Schema para criar métricas de produção"""
    period_type: str
    period_start: datetime
    period_end: datetime

class ProductionMetricsResponse(BaseModel):
    """Schema para resposta de métricas"""
    id: UUID
    period_type: str
    period_start: datetime
    period_end: datetime
    
    # Production metrics
    total_orders: int
    completed_orders: int
    on_time_delivery: int
    quality_pass_rate: Optional[float]
    
    # Performance metrics
    efficiency_score: Optional[float]
    utilization_rate: Optional[float]
    throughput: Optional[float]
    
    # Cost metrics
    total_production_cost: float
    average_cost_per_unit: Optional[float]
    cost_variance_percentage: Optional[float]
    
    # Quality metrics
    defect_rate: Optional[float]
    rework_rate: Optional[float]
    customer_satisfaction: Optional[float]
    
    # Efficiency metrics
    setup_time_average: Optional[float]
    cycle_time_average: Optional[float]
    downtime_hours: Optional[float]
    
    # Equipment metrics
    equipment_utilization: Dict[str, Any]
    maintenance_hours: Optional[float]
    
    # Customer metrics
    delivery_accuracy: Optional[float]
    lead_time_average: Optional[float]
    
    calculated_at: datetime
    
    class Config:
        from_attributes = True

# Optimization Schemas
class ProductionOptimizationCreate(BaseModel):
    """Schema para criar otimização"""
    optimization_type: str
    title: str
    description: str
    current_state: Dict[str, Any] = Field(default_factory=dict)
    optimized_state: Dict[str, Any] = Field(default_factory=dict)
    improvement_potential: Optional[float] = None
    implementation_difficulty: Optional[str] = None
    implementation_cost: Optional[float] = None
    implementation_time: Optional[int] = None

class ProductionOptimizationResponse(BaseModel):
    """Schema para resposta de otimização"""
    id: UUID
    optimization_type: str
    title: str
    description: str
    current_state: Dict[str, Any]
    optimized_state: Dict[str, Any]
    improvement_potential: Optional[float]
    
    # Benefits
    cost_savings: Optional[float]
    time_savings: Optional[float]
    quality_improvement: Optional[float]
    
    # Implementation
    implementation_difficulty: Optional[str]
    implementation_cost: Optional[float]
    implementation_time: Optional[int]
    
    # ROI analysis
    roi_percentage: Optional[float]
    payback_period: Optional[int]
    
    # Status
    status: str
    priority: PriorityEnum
    
    # Tracking
    identified_by: Optional[str]
    analyzed_by: Optional[str]
    implemented_by: Optional[str]
    
    # Results
    actual_cost_savings: Optional[float]
    actual_time_savings: Optional[float]
    actual_quality_improvement: Optional[float]
    
    # Timestamps
    identified_at: datetime
    analyzed_at: Optional[datetime]
    approved_at: Optional[datetime]
    implemented_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Dashboard and Analytics Schemas
class ProductionDashboardData(BaseModel):
    """Schema para dados do dashboard de produção"""
    overview: Dict[str, Any]
    distributions: Dict[str, Any]
    recent_orders: List[Dict[str, Any]]
    kpis: Dict[str, Any]

class ProductionStatusDetail(BaseModel):
    """Schema para status detalhado da produção"""
    production_order: Dict[str, Any]
    schedule: List[Dict[str, Any]]
    quality: List[Dict[str, Any]]
    recent_events: List[Dict[str, Any]]
    metrics: Dict[str, Any]

class ProductionReportRequest(BaseModel):
    """Schema para solicitação de relatório"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_trends: bool = True
    include_recommendations: bool = True
    format: str = Field(default="json", pattern="^(json|pdf|csv)$")

class ProductionReportResponse(BaseModel):
    """Schema para resposta de relatório"""
    report_period: Dict[str, Any]
    financial_summary: Dict[str, Any]
    operational_summary: Dict[str, Any]
    quality_summary: Dict[str, Any]
    production_trends: Dict[str, Any]
    recommendations: List[Dict[str, Any]]

# Optimization Request Schema
class OptimizationRequest(BaseModel):
    """Schema para solicitação de otimização"""
    optimization_types: List[str] = Field(default_factory=lambda: [
        "parallel_processing", "setup_optimization", "quality_gate_optimization", 
        "equipment_optimization", "material_optimization", "workflow_optimization"
    ])
    target_improvements: Dict[str, float] = Field(
        default_factory=lambda: {
            "cost_reduction": 10.0,
            "time_reduction": 15.0,
            "quality_improvement": 5.0
        }
    )
    constraints: Dict[str, Any] = Field(default_factory=dict)

# Capacity Planning Schema
class CapacityPlanningRequest(BaseModel):
    """Schema para planejamento de capacidade"""
    start_date: datetime
    end_date: datetime
    order_forecast: List[Dict[str, Any]] = Field(default_factory=list)
    equipment_constraints: Dict[str, Any] = Field(default_factory=dict)
    optimization_goals: Dict[str, float] = Field(
        default_factory=lambda: {
            "maximize_utilization": 85.0,
            "minimize_setup_time": 20.0,
            "balance_workload": True
        }
    )

class CapacityPlanningResponse(BaseModel):
    """Schema para resposta de planejamento"""
    planning_period: Dict[str, Any]
    resource_requirements: Dict[str, Any]
    recommended_schedule: List[Dict[str, Any]]
    capacity_utilization: Dict[str, Any]
    bottleneck_analysis: Dict[str, Any]
    optimization_suggestions: List[Dict[str, Any]]

# Real-time Production Update Schema
class ProductionUpdate(BaseModel):
    """Schema para atualizações em tempo real da produção"""
    production_order_id: UUID
    event_type: str
    event_data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = "production_system"

# Quality Gate Schema
class QualityGateCheck(BaseModel):
    """Schema para portões de qualidade"""
    production_order_id: UUID
    gate_name: str
    criteria: List[Dict[str, Any]]
    auto_approve: bool = False
    requires_manual_review: bool = True

class QualityGateResult(BaseModel):
    """Schema para resultado de portão de qualidade"""
    gate_name: str
    passed: bool
    criteria_results: List[Dict[str, Any]]
    recommendations: List[str]
    next_actions: List[str]

# Supply Chain Integration Schema
class SupplyChainStatus(BaseModel):
    """Schema para status da cadeia de suprimentos"""
    material_availability: Dict[str, Any]
    supplier_status: Dict[str, Any]
    delivery_status: Dict[str, Any]
    risk_assessment: Dict[str, Any]

class SupplyChainAlert(BaseModel):
    """Schema para alertas da cadeia de suprimentos"""
    alert_type: str
    severity: str  # low, medium, high, critical
    message: str
    affected_materials: List[str]
    recommended_actions: List[str]
    estimated_impact: Dict[str, Any]