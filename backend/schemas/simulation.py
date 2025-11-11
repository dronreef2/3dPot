"""
Schemas Pydantic para Sistema de Simulação Física
Definições de modelos para requests, responses e validação
"""

from typing import Dict, List, Optional, Any, Union
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

# ========== ENUMS ==========

class SimulationType(str, Enum):
    """Tipos de simulação disponíveis"""
    DROP_TEST = "drop_test"
    STRESS_TEST = "stress_test"
    MOTION = "motion"
    FLUID = "fluid"

class SimulationStatus(str, Enum):
    """Status possíveis de uma simulação"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TemplateCategory(str, Enum):
    """Categorias de templates"""
    BASIC = "basic"
    COMPREHENSIVE = "comprehensive"
    MECHANICAL = "mechanical"
    DYNAMIC = "dynamic"
    FLUID = "fluid"

class ForceDirection(str, Enum):
    """Direções de força para testes"""
    UPWARD = [0, 0, 1]
    DOWNWARD = [0, 0, -1]
    SIDEWAYS_X = [1, 0, 0]
    SIDEWAYS_Y = [0, 1, 0]
    DIAGONAL = [1, 1, 1]

# ========== SCHEMAS DE CONFIGURAÇÃO ==========

class DropTestConfig(BaseModel):
    """Configuração para teste de queda"""
    drop_height: float = Field(1.0, ge=0.1, le=10.0, description="Altura de queda em metros")
    num_drops: int = Field(5, ge=1, le=50, description="Número de testes de queda")
    gravity: float = Field(-9.8, description="Gravidade em m/s²")
    surface_type: str = Field("concrete", description="Tipo de superfície de impacto")
    restitution: float = Field(0.3, ge=0.0, le=1.0, description="Coeficiente de restituição")
    
    @validator('drop_height')
    def validate_height(cls, v):
        if v > 5.0:
            raise ValueError('Altura máxima permitida: 5.0 metros')
        return v

class StressTestConfig(BaseModel):
    """Configuração para teste de stress"""
    max_force: float = Field(1000.0, ge=1.0, le=50000.0, description="Força máxima em Newtons")
    force_increment: float = Field(100.0, ge=1.0, le=5000.0, description="Incremento de força")
    force_direction: List[float] = Field([0, 0, 1], description="Direção da força (x, y, z)")
    test_duration: float = Field(5.0, ge=1.0, le=60.0, description="Duração do teste em segundos")
    
    @validator('force_direction')
    def validate_direction(cls, v):
        if len(v) != 3:
            raise ValueError('Direção deve ter 3 componentes (x, y, z)')
        magnitude = (v[0]**2 + v[1]**2 + v[2]**2)**0.5
        if magnitude < 0.1:
            raise ValueError('Direção não pode ser [0, 0, 0]')
        return v

class MotionTestConfig(BaseModel):
    """Configuração para teste de movimento"""
    trajectory_type: str = Field("circular", description="Tipo de trajetória")
    duration: float = Field(10.0, ge=1.0, le=300.0, description="Duração em segundos")
    velocity: float = Field(1.0, ge=0.1, le=20.0, description="Velocidade em m/s")
    radius: float = Field(1.0, ge=0.1, le=10.0, description="Raio para trajetória circular")
    acceleration: float = Field(0.0, ge=0.0, le=10.0, description="Aceleração em m/s²")
    
    @validator('trajectory_type')
    def validate_trajectory(cls, v):
        allowed = ["circular", "linear", "figure_8", "spiral"]
        if v not in allowed:
            raise ValueError(f'Trajetória deve ser uma de: {allowed}')
        return v

class FluidTestConfig(BaseModel):
    """Configuração para teste de fluido"""
    fluid_density: float = Field(1.2, ge=0.1, le=2000.0, description="Densidade do fluido em kg/m³")
    drag_coefficient: float = Field(0.47, ge=0.0, le=2.0, description="Coeficiente de arrasto")
    viscosity: float = Field(0.001, ge=0.0, le=100.0, description="Viscosidade dinâmica")
    flow_direction: List[float] = Field([0, 0, -1], description="Direção do fluxo")
    
    @validator('flow_direction')
    def validate_flow_direction(cls, v):
        if len(v) != 3:
            raise ValueError('Direção do fluxo deve ter 3 componentes (x, y, z)')
        return v

# ========== SCHEMAS DE REQUISIÇÃO ==========

class SimulationCreate(BaseModel):
    """Schema para criação de simulação"""
    modelo_3d_id: UUID = Field(..., description="ID do modelo 3D a ser simulado")
    nome: str = Field(..., min_length=1, max_length=200, description="Nome da simulação")
    tipo_simulacao: SimulationType = Field(..., description="Tipo de simulação")
    parametros: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parâmetros específicos do tipo de simulação"
    )
    condicoes_iniciais: Dict[str, Any] = Field(
        default_factory=dict,
        description="Condições iniciais da simulação"
    )
    
    @validator('nome')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Nome não pode ser vazio')
        return v.strip()

class SimulationPreviewRequest(BaseModel):
    """Schema para preview de simulação"""
    tipo_simulacao: SimulationType
    parametros: Dict[str, Any]

# ========== SCHEMAS DE RESPOSTA ==========

class SimulationResponse(BaseModel):
    """Schema de resposta padrão para simulação"""
    id: UUID
    nome: str
    tipo_simulacao: SimulationType
    status: SimulationStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    model_3d_id: UUID
    parametros: Dict[str, Any]
    results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    progress: Optional[float] = None
    estimated_completion: Optional[datetime] = None
    warning_messages: List[str] = Field(default_factory=list)

class SimulationStatusResponse(BaseModel):
    """Schema para status da simulação"""
    simulation_id: UUID
    status: SimulationStatus
    progress: float = Field(ge=0.0, le=100.0)
    estimated_completion: Optional[datetime] = None
    error_message: Optional[str] = None
    last_updated: datetime

class SimulationResult(BaseModel):
    """Schema para resultados detalhados"""
    simulation_id: UUID
    tipo_simulacao: SimulationType
    status: SimulationStatus
    results: Dict[str, Any]
    created_at: datetime
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None  # em segundos
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SimulationTemplate(BaseModel):
    """Schema para templates de simulação"""
    id: str
    nome: str
    tipo_simulacao: SimulationType
    descricao: str
    parametros: Dict[str, Any]
    category: TemplateCategory
    is_default: bool = True

class ValidationResult(BaseModel):
    """Schema para resultado de validação"""
    simulation_id: Optional[UUID] = None
    valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggested_parameters: Dict[str, Any] = Field(default_factory=dict)

# ========== SCHEMAS ESPECÍFICOS POR TIPO DE SIMULAÇÃO ==========

class DropTestResult(BaseModel):
    """Resultados específicos do teste de queda"""
    tipo: str = "drop_test"
    testes: List[Dict[str, Any]]
    metricas: Dict[str, Any]
    duracao_total: float
    velocidade_impacto_max: float
    numero_impactos_total: int
    classificado_como: str  # "resistente", "moderado", "frágil"

class StressTestResult(BaseModel):
    """Resultados específicos do teste de stress"""
    tipo: str = "stress_test"
    testes_forca: List[Dict[str, Any]]
    metricas: Dict[str, Any]
    ponto_ruptura: Optional[float]
    rigidez_calculada: float
    limite_elastico: float
    classificado_como: str  # "muito_resistente", "resistente", "moderado", "frágil"

class MotionTestResult(BaseModel):
    """Resultados específicos do teste de movimento"""
    tipo: str = "motion_test"
    trajetoria: List[Dict[str, Any]]
    metricas: Dict[str, Any]
    energia_consumida: float
    estabilidade: str  # "estável", "moderadamente_estável", "instável"

class FluidTestResult(BaseModel):
    """Resultados específicos do teste de fluido"""
    tipo: str = "fluid_test"
    resistencia: List[Dict[str, Any]]
    metricas: Dict[str, Any]
    velocidade_terminal: float
    coeficiente_arrasto: float
    classificado_como: str  # "aerodinâmico", "moderado", "arrasto_alto"

# ========== SCHEMAS DE MONITORAMENTO ==========

class SimulationProgress(BaseModel):
    """Schema para progresso da simulação"""
    simulation_id: UUID
    status: SimulationStatus
    progress_percentage: float
    current_step: str
    estimated_remaining_time: Optional[float] = None
    steps_total: int
    steps_completed: int

class SimulationMetrics(BaseModel):
    """Schema para métricas da simulação"""
    execution_time: float
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None
    iterations_per_second: Optional[float] = None
    convergence_status: Optional[str] = None

# ========== SCHEMAS DE EXPORTAÇÃO ==========

class SimulationExportRequest(BaseModel):
    """Schema para exportação de simulação"""
    simulation_ids: List[UUID]
    format: str = Field("json", pattern="^(json|csv|pdf)$")
    include_raw_data: bool = False
    include_visualizations: bool = True

class SimulationSummary(BaseModel):
    """Resumo de simulação para listas"""
    id: UUID
    nome: str
    tipo_simulacao: SimulationType
    status: SimulationStatus
    created_at: datetime
    model_3d_name: str
    key_results: Dict[str, Any] = Field(default_factory=dict)

# ========== SCHEMAS DE ANÁLISE ==========

class SimulationAnalysis(BaseModel):
    """Análise completa da simulação"""
    simulation_id: UUID
    summary: SimulationSummary
    results: Union[
        DropTestResult,
        StressTestResult,
        MotionTestResult,
        FluidTestResult
    ]
    recommendations: List[str] = Field(default_factory=list)
    quality_score: float = Field(ge=0.0, le=10.0)
    printable: bool
    design_improvements: List[str] = Field(default_factory=list)

class ComparativeAnalysis(BaseModel):
    """Análise comparativa entre simulações"""
    model_id: UUID
    simulations: List[SimulationSummary]
    comparison_metrics: Dict[str, Any]
    best_simulation_id: Optional[UUID] = None
    trends: Dict[str, Any]
    recommendations: List[str] = Field(default_factory=list)

# ========== SCHEMAS DE CONFIGURAÇÃO AVANÇADA ==========

class AdvancedSimulationConfig(BaseModel):
    """Configuração avançada para simulações complexas"""
    physics_engine: str = Field("pybullet", description="Engine de física")
    time_step: float = Field(1/240, ge=1/1000, le=1/10, description="Passo de tempo")
    max_iterations: int = Field(10000, ge=100, le=100000, description="Máximo de iterações")
    convergence_threshold: float = Field(1e-6, ge=1e-12, le=1e-3, description="Threshold de convergência")
    parallel_processing: bool = Field(True, description="Processamento paralelo")
    gpu_acceleration: bool = Field(False, description="Aceleração GPU")
    custom_physics: Dict[str, Any] = Field(default_factory=dict, description="Física customizada")

class MaterialProperties(BaseModel):
    """Propriedades do material"""
    density: float = Field(..., ge=0.1, le=10000.0, description="Densidade kg/m³")
    young_modulus: float = Field(..., ge=0.1, le=1000.0, description="Módulo de Young GPa")
    poisson_ratio: float = Field(..., ge=0.0, le=0.5, description="Coeficiente de Poisson")
    yield_strength: float = Field(..., ge=1.0, le=10000.0, description="Tensão de escoamento MPa")
    ultimate_tensile_strength: float = Field(..., ge=1.0, le=10000.0, description="Resistência à tração MPa")

# ========== SCHEMAS DE NOTIFICAÇÃO ==========

class SimulationNotification(BaseModel):
    """Notificação sobre simulação"""
    simulation_id: UUID
    user_id: UUID
    type: str  # "started", "completed", "failed", "cancelled"
    message: str
    timestamp: datetime
    priority: str = "normal"  # "low", "normal", "high", "critical"
    action_required: bool = False