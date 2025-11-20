"""
Modelos de Dados - 3dPot v2.0
SQLAlchemy models para PostgreSQL
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey, Integer, 
    JSON, Numeric, String, Text, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    """Modelo de usuário com autenticação completa"""
    __tablename__ = "users"
    
    # Basic info
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # Role and permissions
    role = Column(Enum('user', 'premium', 'admin', name='user_role'), default='user')
    permissions = Column(JSON, default=list)
    
    # Auth fields
    refresh_tokens = Column(JSON, default=list)  # List of active refresh tokens
    last_login = Column(DateTime, nullable=True)
    login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    
    # Password reset
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    
    # Email verification
    verification_token = Column(String(255), nullable=True)
    verification_token_expires = Column(DateTime, nullable=True)
    
    # MFA/2FA (Sprint 9)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)  # TOTP secret
    mfa_backup_codes = Column(JSON, default=list)  # Backup codes for recovery
    
    # Profile
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    company = Column(String(100), nullable=True)
    website = Column(String(200), nullable=True)
    preferences = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete
    
    # Relationships
    projects = relationship("Project", back_populates="owner")
    conversations = relationship("Conversation", back_populates="user")
    refresh_token_records = relationship("RefreshToken", back_populates="user")
    simulations = relationship("Simulation", back_populates="user")
    
    def is_locked(self) -> bool:
        """Verifica se a conta está bloqueada"""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until

class Project(Base):
    """Modelo de projeto de prototipagem"""
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    nome = Column(String(100), nullable=False)
    descricao_usuario = Column(Text, nullable=False)
    categoria = Column(Enum('mecanico', 'eletronico', 'mixto', 'arquitetura', 
                           name='project_category'), nullable=False)
    
    # Especificações físicas
    dimensoes_largura = Column(Numeric(10, 3), nullable=True)
    dimensoes_altura = Column(Numeric(10, 3), nullable=True)
    dimensoes_profundidade = Column(Numeric(10, 3), nullable=True)
    dimensoes_unidade = Column(String(10), default='mm')
    
    material_tipo = Column(String(50), nullable=True)
    material_densidade = Column(Numeric(8, 3), nullable=True)
    material_preco_por_kg = Column(Numeric(10, 2), nullable=True)
    
    peso_estimado = Column(Numeric(8, 3), nullable=True)
    volume_impressao = Column(Numeric(10, 3), nullable=True)
    
    # Dados estruturados
    componentes_eletronicos = Column(JSON, default=list)
    funcionalidades = Column(JSON, default=list)
    restricoes = Column(JSON, default=list)
    
    # Status tracking
    status = Column(Enum('draft', 'conversando', 'modelando', 'simulando', 
                        'orcando', 'completo', 'error', name='project_status'), 
                    default='draft')
    
    # Relacionamentos
    conversacao_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)
    modelo_3d_id = Column(UUID(as_uuid=True), ForeignKey("model_3d.id"), nullable=True)
    simulacao_id = Column(UUID(as_uuid=True), ForeignKey("simulation.id"), nullable=True)
    orcamento_id = Column(UUID(as_uuid=True), ForeignKey("budget.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    conversacao_iniciada = Column(DateTime, nullable=True)
    modelo_gerado = Column(DateTime, nullable=True)
    simulacao_concluida = Column(DateTime, nullable=True)
    orcamento_gerado = Column(DateTime, nullable=True)
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    conversation = relationship("Conversation", back_populates="project")

class Conversation(Base):
    """Modelo de conversação com IA"""
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    
    status = Column(Enum('active', 'especificando', 'clarificando', 'validando', 'complete', 
                        name='conversation_status'), default='active')
    
    especificacoes_extraidas = Column(JSON, default=dict)
    clarificacoes_pendentes = Column(JSON, default=list)
    contexto_conversacao = Column(JSON, default=dict)
    specs = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    project = relationship("Project", back_populates="conversation")
    messages = relationship("ConversationMessage", back_populates="conversation")

class ConversationMessage(Base):
    """Mensagens da conversação"""
    __tablename__ = "conversation_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    
    papel = Column(Enum('user', 'assistant', name='message_role'), nullable=False)
    conteudo = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadados = Column(JSON, default=dict)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

class Model3D(Base):
    """Modelos 3D gerados"""
    __tablename__ = "model_3d"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    nome = Column(String(100), nullable=False)
    projeto_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    
    # Arquivo e formato
    arquivo_path = Column(String(500), nullable=False)
    arquivo_tamanho = Column(Integer, nullable=True)
    formato_arquivo = Column(String(10), nullable=False)  # .stl, .obj, .gltf
    versao = Column(Integer, default=1)
    
    # Propriedades do modelo
    numero_vertices = Column(Integer, nullable=True)
    numero_faces = Column(Integer, nullable=True)
    volume_calculado = Column(Numeric(12, 3), nullable=True)
    area_superficie = Column(Numeric(12, 3), nullable=True)
    
    # Engine de geração
    engine = Column(Enum('cadquery', 'openscad', 'slant3d', 'manual', name='model_engine'))
    parametros_geracao = Column(JSON, default=dict)
    
    # Validação
    imprimivel = Column(Boolean, default=False)
    erros_validacao = Column(JSON, default=list)
    warnings = Column(JSON, default=list)
    
    # Otimização
    otimizado = Column(Boolean, default=False)
    nvidia_nim_processado = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="model_3d")
    simulations = relationship("Simulation", back_populates="model_3d")

class Budget(Base):
    """Orçamentos automatizados"""
    __tablename__ = "budget"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    projeto_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    
    # Componentes e materiais
    custo_material = Column(Numeric(10, 2), default=0)
    custo_componentes = Column(Numeric(10, 2), default=0)
    custo_impressao = Column(Numeric(10, 2), default=0)
    custo_mao_obra = Column(Numeric(10, 2), default=0)
    
    # Tempo estimado
    tempo_impressao_horas = Column(Numeric(6, 2), nullable=True)
    tempo_montagem_horas = Column(Numeric(6, 2), nullable=True)
    
    # Detalhamento
    itens_detalhados = Column(JSON, default=list)
    fornecedores = Column(JSON, default=list)
    
    # Margem e preço final
    margem_lucro_percentual = Column(Numeric(5, 2), default=30)
    preco_final = Column(Numeric(10, 2), nullable=True)
    
    # Proposta
    proposta_pdf_path = Column(String(500), nullable=True)
    numero_proposta = Column(String(50), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="budget")

class TaskQueue(Base):
    """Fila de tarefas assíncronas"""
    __tablename__ = "task_queue"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    task_name = Column(String(100), nullable=False)
    task_type = Column(Enum('modeling', 'simulation', 'budget', 'optimization', 
                           name='task_type'), nullable=False)
    
    # Dados da tarefa
    task_data = Column(JSON, default=dict)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    
    # Status
    status = Column(Enum('pending', 'processing', 'completed', 'failed', 'cancelled', 
                        name='task_status'), default='pending')
    
    # Celery tracking
    celery_task_id = Column(String(100), nullable=True)
    
    # Progresso e resultados
    progress = Column(Integer, default=0)
    resultado = Column(JSON, default=dict)
    erro_detalhes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('celery_task_id', name='uq_task_celery_id'),
    )

class AuditLog(Base):
    """Log de auditoria"""
    __tablename__ = "audit_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    
    acao = Column(String(50), nullable=False)  # create, update, delete, etc.
    tabela = Column(String(50), nullable=False)
    registro_id = Column(String(100), nullable=True)
    
    dados_antigos = Column(JSON, nullable=True)
    dados_novos = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow)

class RefreshToken(Base):
    """Modelo para refresh tokens"""
    __tablename__ = "refresh_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Token info
    token = Column(String(500), unique=True, nullable=False, index=True)
    hashed_token = Column(String(255), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_revoked = Column(Boolean, default=False)
    
    # Device and location info
    device_info = Column(JSON, default=dict)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    last_used = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="refresh_token_records")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('token', name='uq_refresh_token'),
    )

# Import simulation models to ensure they're loaded
from .simulation import (
    Simulation, 
    SimulationTemplate, 
    SimulationResult, 
    SimulationExecutionLog,
    MaterialProperties,
    SimulationComparison,
    get_default_templates,
    get_default_materials
)

# Import intelligent budgeting models for Sprint 5
from .budgeting import (
    IntelligentBudget,
    BudgetMaterial,
    BudgetSupplier,
    SupplierQuote,
    Slant3DQuote,
    BudgetTimeline,
    BudgetAnalytics,
    BudgetCache,
    Budget  # Backwards compatibility alias
)

# Import Sprint 6+ models
from .printing3d_models import (
    Printer,
    Material,
    PrintJob,
    PrintQueue,
    PrintSettings,
    PrintJobLog
)

from .collaboration_models import (
    CollaborationSession,
    Participant,
    Message,
    VideoCall,
    VideoCallParticipant,
    ScreenShare,
    FileVersion,
    CollaborationSetting,
    add_user_collaboration_relationships,
    add_project_collaboration_relationships
)

from .marketplace_models import (
    Category,
    Tag,
    MarketplaceListing,
    ListingTag,
    Transaction,
    Review,
    License,
    PaymentMethod,
    Wishlist,
    Promotion,
    add_user_marketplace_relationships
)

from .cloud_rendering_models import (
    GPUCluster,
    RenderJob,
    RenderSettings,
    QualityPreset,
    BatchRenderConfig,
    CostEstimate,
    RenderNode,
    RenderJobLog,
    add_user_cloud_rendering_relationships,
    add_project_cloud_rendering_relationships
)