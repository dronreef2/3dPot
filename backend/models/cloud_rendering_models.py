"""
Modelos SQLAlchemy - Cloud Rendering (Sprint 6+)
================================================

Modelos para renderização em nuvem e processamento GPU distribuído, incluindo:
- Tarefas de renderização (RenderJob)
- Clusters de GPU (GPUCluster)
- Configurações de renderização (RenderSettings)
- Templates de qualidade (QualityPreset)
- Estimativas de custo (CostEstimate)

Autor: MiniMax Agent
Data: 2025-11-13
Versão: 2.0.0 - Sprint 6+
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from uuid import uuid4, UUID
from decimal import Decimal

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey, Integer, 
    JSON, Numeric, String, Text, Float, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from . import Base


class GPUCluster(Base):
    """Clusters de GPU para renderização em nuvem"""
    __tablename__ = "gpu_clusters"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Informações básicas
    nome = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False)  # AWS, Google, Azure, Local
    region = Column(String(50), nullable=False)
    zona = Column(String(50), nullable=True)
    
    # Especificações técnicas
    tipo_cluster = Column(Enum('cpu', 'gpu', 'hybrid', name='cluster_type'), 
                         default='gpu')
    
    # GPUs
    gpu_model = Column(String(100), nullable=True)  # RTX 4090, A100, etc.
    gpu_count = Column(Integer, nullable=False)
    gpu_memory_gb = Column(Float, nullable=True)
    
    # CPUs
    cpu_cores = Column(Integer, nullable=False)
    cpu_model = Column(String(100), nullable=True)
    cpu_memory_gb = Column(Float, nullable=False)
    
    # Armazenamento
    storage_gb = Column(Float, nullable=False)
    storage_type = Column(String(50), nullable=True)  # SSD, NVMe, HDD
    
    # Rede
    bandwidth_gbps = Column(Float, nullable=True)
    latency_ms = Column(Float, nullable=True)
    
    # Status e disponibilidade
    status = Column(Enum('available', 'busy', 'maintenance', 'offline', 'error', name='cluster_status'),
                   default='available')
    
    # Configurações de custo
    custo_por_hora = Column(Numeric(10, 4), nullable=False)
    moeda = Column(String(3), default='USD')
    
    # Performance
    benchmarks = Column(JSON, default=dict)  # Resultados de benchmarks
    throughput_score = Column(Float, nullable=True)  # Score relativo de performance
    
    # Configurações de escalabilidade
    auto_scaling = Column(Boolean, default=False)
    min_instances = Column(Integer, default=1)
    max_instances = Column(Integer, default=10)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_health_check = Column(DateTime, nullable=True)
    
    # Relationships
    render_jobs = relationship("RenderJob", back_populates="gpu_cluster")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('nome', 'provider', 'region', name='uq_cluster_unique'),
    )


class RenderJob(Base):
    """Tarefas de renderização em nuvem"""
    __tablename__ = "render_jobs"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(PGUUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    
    # Informações do job
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    modelo_3d_path = Column(String(500), nullable=False)
    configuracao_path = Column(String(500), nullable=True)
    
    # Configurações de renderização
    resolution_x = Column(Integer, nullable=False)
    resolution_y = Column(Integer, nullable=False)
    framerate = Column(Integer, default=30)
    duracao_segundos = Column(Integer, nullable=True)
    
    # Qualidade
    qualidade = Column(Enum('draft', 'standard', 'high', 'ultra', 'cinema', name='render_quality'),
                      default='standard')
    samples = Column(Integer, default=128)
    denoise = Column(Boolean, default=True)
    motion_blur = Column(Boolean, default=True)
    depth_of_field = Column(Boolean, default=True)
    
    # Configurações de render
    render_engine = Column(Enum('cycles', 'eevee', 'octane', 'vray', 'arnold', name='render_engine'),
                          default='cycles')
    device = Column(Enum('cpu', 'gpu', name='render_device'), default='gpu')
    
    # Cluster e recursos
    gpu_cluster_id = Column(PGUUID(as_uuid=True), ForeignKey("gpu_clusters.id"), nullable=False)
    gpu_memory_required_gb = Column(Float, nullable=True)
    cpu_cores_required = Column(Integer, nullable=True)
    
    # Status do job
    status = Column(Enum('queued', 'preparing', 'rendering', 'post_processing', 'completed', 
                        'failed', 'cancelled', 'timeout', name='render_job_status'), default='queued')
    
    # Progresso
    progresso_percentual = Column(Integer, default=0)
    frames_total = Column(Integer, nullable=True)
    frames_completados = Column(Integer, default=0)
    frame_atual = Column(Integer, nullable=True)
    
    # Métricas de performance
    tempo_estimado_segundos = Column(Integer, nullable=True)
    tempo_real_segundos = Column(Integer, nullable=True)
    frames_por_segundo = Column(Float, nullable=True)
    
    # Custo e recursos
    custo_estimado = Column(Numeric(10, 4), nullable=True)
    custo_real = Column(Numeric(10, 4), nullable=True)
    energia_consumida_kwh = Column(Float, nullable=True)
    carbon_footprint_g = Column(Float, nullable=True)
    
    # Saída
    arquivo_output_path = Column(String(500), nullable=True)
    arquivo_output_format = Column(String(10), default='mp4')
    tamanho_output_mb = Column(Float, nullable=True)
    
    # Preview e thumbnails
    thumbnail_path = Column(String(500), nullable=True)
    preview_video_path = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    queued_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    timeout_at = Column(DateTime, nullable=True)
    
    # Logs e erros
    render_log = Column(Text, nullable=True)
    error_log = Column(Text, nullable=True)
    performance_metrics = Column(JSON, default=dict)
    
    # Configurações especiais
    render_layers = Column(JSON, default=list)
    compositing_nodes = Column(JSON, default=dict)
    custom_scripts = Column(JSON, default=list)
    
    # Notifications
    notify_on_completion = Column(Boolean, default=True)
    notify_on_failure = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="render_jobs")
    project = relationship("Project", back_populates="render_jobs")
    gpu_cluster = relationship("GPUCluster", back_populates="render_jobs")
    batch_config = relationship("BatchRenderConfig", back_populates="batch_jobs", uselist=False)
    
    # Status helpers
    @property
    def is_active(self) -> bool:
        """Verifica se o job está ativo (renderizando)"""
        return self.status in ['rendering', 'post_processing']
    
    @property
    def is_completed(self) -> bool:
        """Verifica se o job foi concluído com sucesso"""
        return self.status == 'completed'
    
    @property
    def is_failed(self) -> bool:
        """Verifica se o job falhou"""
        return self.status in ['failed', 'timeout']


class RenderSettings(Base):
    """Configurações de renderização salvas"""
    __tablename__ = "render_settings"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Identificação
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    tipo_configuracao = Column(Enum('personal', 'shared', 'template', name='settings_type'), 
                              default='personal')
    
    # Configurações técnicas
    configuracoes = Column(JSON, default=dict)  # Todas as configurações em JSON
    
    # Métricas de uso
    vezes_usado = Column(Integer, default=0)
    tempo_total_renderizado = Column(Integer, default=0)  # em segundos
    
    # Qualidade de output
    preset_quality = Column(Enum('draft', 'standard', 'high', 'ultra', 'cinema', name='quality_preset'),
                          default='standard')
    
    # Configurações avançadas
    gpu_requirements = Column(JSON, default=dict)
    fallback_options = Column(JSON, default=list)
    
    # Status
    ativo = Column(Boolean, default=True)
    favoritos = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="render_settings")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'nome', name='uq_settings_user_name'),
    )


class QualityPreset(Base):
    """Templates de qualidade de renderização"""
    __tablename__ = "quality_presets"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Identificação
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    categoria = Column(Enum('draft', 'production', 'cinema', 'interactive', name='preset_category'))
    
    # Configurações de qualidade
    samples_per_pixel = Column(Integer, nullable=False)
    max_bounces = Column(Integer, default=12)
    transparent_max_bounces = Column(Integer, default=8)
    
    # Configurações de rede
    use_denoising = Column(Boolean, default=True)
    denoise_method = Column(String(50), default='optix')
    use_caustics = Column(Boolean, default=False)
    
    # Performance
    tile_size = Column(Integer, default=256)
    threads_per_device = Column(Integer, default=1)
    use_progressive = Column(Boolean, default=True)
    
    # Filtros e pós-processamento
    use_motion_blur = Column(Boolean, default=False)
    use_depth_of_field = Column(Boolean, default=False)
    film_transparency = Column(Boolean, default=False)
    
    # Configurações de memória
    experimental_features = Column(Boolean, default=False)
    high_precision = Column(Boolean, default=False)
    
    # Métricas
    tempo_relativo = Column(Float, nullable=False)  # Multiplicador de tempo vs draft
    qualidade_relativa = Column(Float, nullable=False)  # Score de qualidade 1-100
    
    # Status
    ativo = Column(Boolean, default=True)
    uso_padrao = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BatchRenderConfig(Base):
    """Configurações para renderização em lote"""
    __tablename__ = "batch_render_configs"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Informações do batch
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    
    # Configurações comuns
    qualidade_padrao = Column(Enum('draft', 'standard', 'high', 'ultra', 'cinema', name='quality_preset'),
                            default='standard')
    engine_padrao = Column(Enum('cycles', 'eevee', 'octane', 'vray', 'arnold', name='render_engine'),
                         default='cycles')
    
    # Otimizações
    parallell_jobs = Column(Integer, default=1)
    priority = Column(Enum('low', 'normal', 'high', 'urgent', name='batch_priority'), 
                     default='normal')
    
    # Status do batch
    status = Column(Enum('queued', 'processing', 'paused', 'completed', 'failed', 'cancelled', 
                        name='batch_status'), default='queued')
    
    # Progresso geral
    total_jobs = Column(Integer, nullable=False)
    completed_jobs = Column(Integer, default=0)
    failed_jobs = Column(Integer, default=0)
    progresso_geral = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="batch_render_configs")
    batch_jobs = relationship("RenderJob", back_populates="batch_config", cascade="all, delete-orphan")


class CostEstimate(Base):
    """Estimativas de custo de renderização"""
    __tablename__ = "cost_estimates"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(PGUUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    
    # Configurações do job estimado
    job_config = Column(JSON, default=dict)
    
    # Estimativas de recurso
    tempo_estimado_horas = Column(Float, nullable=False)
    gpu_cluster_sugerido_id = Column(PGUUID(as_uuid=True), ForeignKey("gpu_clusters.id"), nullable=True)
    
    # Custos detalhados
    custo_computacao = Column(Numeric(10, 4), nullable=False)
    custo_armazenamento = Column(Numeric(10, 4), nullable=False)
    custo_tranferencia = Column(Numeric(10, 4), nullable=False)
    custo_total = Column(Numeric(10, 4), nullable=False)
    
    # Descontos
    desconto_percentual = Column(Float, default=0)
    valor_desconto = Column(Numeric(10, 4), default=0)
    custo_final = Column(Numeric(10, 4), nullable=False)
    
    # Moeda e valor
    moeda = Column(String(3), default='USD')
    valor_em_reais = Column(Numeric(10, 2), nullable=True)
    taxa_cambio_usd_brl = Column(Numeric(8, 4), default=5.0)
    
    # Comparação de opções
    alternativas_cluster = Column(JSON, default=list)  # Lista de alternativas com custos
    
    # Validade
    estimativa_valida_por_horas = Column(Integer, default=24)
    created_at = Column(DateTime, default=datetime.utcnow)
    expira_em = Column(DateTime, nullable=True)
    
    # Precisão da estimativa
    precisao_estimada = Column(Float, default=85)  # % de precisão esperada
    
    # Relationships
    user = relationship("User", back_populates="cost_estimates")
    project = relationship("Project", back_populates="cost_estimates")
    gpu_cluster = relationship("GPUCluster")


class RenderNode(Base):
    """Nodes de renderização individuais (para clusters híbridos)"""
    __tablename__ = "render_nodes"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    cluster_id = Column(PGUUID(as_uuid=True), ForeignKey("gpu_clusters.id"), nullable=False)
    
    # Identificação do node
    node_name = Column(String(50), nullable=False)
    node_id = Column(String(100), nullable=False)
    
    # Recursos do node
    gpu_count = Column(Integer, nullable=False)
    gpu_memory_gb = Column(Float, nullable=False)
    cpu_cores = Column(Integer, nullable=False)
    cpu_memory_gb = Column(Float, nullable=False)
    storage_gb = Column(Float, nullable=False)
    
    # Status
    status = Column(Enum('available', 'busy', 'maintenance', 'offline', 'error', name='node_status'),
                   default='available')
    
    # Jobs atualmente em execução
    current_jobs = Column(Integer, default=0)
    max_concurrent_jobs = Column(Integer, default=2)
    
    # Performance
    last_benchmark_score = Column(Float, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cluster = relationship("GPUCluster", backref="nodes")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('cluster_id', 'node_name', name='uq_node_cluster_name'),
    )


class RenderJobLog(Base):
    """Logs detalhados de renderização"""
    __tablename__ = "render_job_logs"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    render_job_id = Column(PGUUID(as_uuid=True), ForeignKey("render_jobs.id"), nullable=False)
    
    # Tipo de log
    tipo_log = Column(Enum('info', 'progress', 'warning', 'error', 'performance', name='log_type'), 
                     nullable=False)
    
    # Conteúdo
    message = Column(Text, nullable=False)
    detalhes = Column(JSON, default=dict)
    
    # Contexto
    frame_atual = Column(Integer, nullable=True)
    tempo_decorrido = Column(Integer, nullable=True)  # segundos
    memoria_usada_mb = Column(Float, nullable=True)
    temperatura_gpu = Column(Float, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    render_job = relationship("RenderJob", backref="detailed_logs")


# Adicionar relacionamentos ao modelo User
def add_user_cloud_rendering_relationships():
    """Adicionar relacionamentos ao modelo User"""
    from ..models import User
    
    if not hasattr(User, 'render_jobs'):
        User.render_jobs = relationship(
            "RenderJob", 
            back_populates="user"
        )
    
    if not hasattr(User, 'render_settings'):
        User.render_settings = relationship(
            "RenderSettings",
            back_populates="user"
        )
    
    if not hasattr(User, 'batch_render_configs'):
        User.batch_render_configs = relationship(
            "BatchRenderConfig",
            back_populates="user"
        )
    
    if not hasattr(User, 'cost_estimates'):
        User.cost_estimates = relationship(
            "CostEstimate",
            back_populates="user"
        )


# Adicionar relacionamentos ao modelo Project
def add_project_cloud_rendering_relationships():
    """Adicionar relacionamentos ao modelo Project"""
    from ..models import Project
    
    if not hasattr(Project, 'render_jobs'):
        Project.render_jobs = relationship(
            "RenderJob",
            back_populates="project"
        )
    
    if not hasattr(Project, 'cost_estimates'):
        Project.cost_estimates = relationship(
            "CostEstimate",
            back_populates="project"
        )