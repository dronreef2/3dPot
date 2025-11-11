"""
Schemas Pydantic - 3dPot v2.0
Validação de dados e serialização
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)

class User(UserBase):
    id: UUID
    is_active: bool
    role: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Project Schemas
class ComponenteEletronico(BaseModel):
    tipo: str = Field(..., regex="^(sensor|atuador|microcontroller|display|comunicacao)$")
    especificacao: str
    quantidade: int = Field(..., gt=0)
    preco_unitario: Optional[float] = Field(None, ge=0)

class Funcionalidade(BaseModel):
    nome: str
    descricao: str
    prioridade: str = Field(..., regex="^(alta|media|baixa)$")

class Restricao(BaseModel):
    tipo: str = Field(..., regex="^(dimensional|mecanico|eletronico|custo)$")
    descricao: str
    valor: Optional[float] = Field(None, ge=0)
    unidade: Optional[str] = None

class ProjectBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    descricao_usuario: str = Field(..., min_length=10)
    categoria: str = Field(..., regex="^(mecanico|eletronico|mixto|arquitetura)$")
    
    # Especificações físicas
    dimensoes_largura: Optional[float] = Field(None, gt=0)
    dimensoes_altura: Optional[float] = Field(None, gt=0)
    dimensoes_profundidade: Optional[float] = Field(None, gt=0)
    dimensoes_unidade: str = Field(default="mm")
    
    material_tipo: Optional[str] = None
    material_densidade: Optional[float] = Field(None, gt=0)
    material_preco_por_kg: Optional[float] = Field(None, gt=0)
    
    peso_estimado: Optional[float] = Field(None, gt=0)
    volume_impressao: Optional[float] = Field(None, gt=0)
    
    componentes_eletronicos: List[ComponenteEletronico] = Field(default_factory=list)
    funcionalidades: List[Funcionalidade] = Field(default_factory=list)
    restricoes: List[Restricao] = Field(default_factory=list)

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    descricao_usuario: Optional[str] = Field(None, min_length=10)
    categoria: Optional[str] = Field(None, regex="^(mecanico|eletronico|mixto|arquitetura)$")
    
    # Especificações físicas
    dimensoes_largura: Optional[float] = Field(None, gt=0)
    dimensoes_altura: Optional[float] = Field(None, gt=0)
    dimensoes_profundidade: Optional[float] = Field(None, gt=0)
    dimensoes_unidade: Optional[str] = None
    
    material_tipo: Optional[str] = None
    material_densidade: Optional[float] = Field(None, gt=0)
    material_preco_por_kg: Optional[float] = Field(None, gt=0)
    
    peso_estimado: Optional[float] = Field(None, gt=0)
    volume_impressao: Optional[float] = Field(None, gt=0)
    
    componentes_eletronicos: Optional[List[ComponenteEletronico]] = None
    funcionalidades: Optional[List[Funcionalidade]] = None
    restricoes: Optional[List[Restricao]] = None

class Project(ProjectBase):
    id: UUID
    owner_id: UUID
    status: str
    conversacao_id: Optional[UUID] = None
    modelo_3d_id: Optional[UUID] = None
    simulacao_id: Optional[UUID] = None
    orcamento_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    conversacao_iniciada: Optional[datetime] = None
    modelo_gerado: Optional[datetime] = None
    simulacao_concluida: Optional[datetime] = None
    orcamento_gerado: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Conversation Schemas
class ConversationMessageBase(BaseModel):
    papel: str = Field(..., regex="^(user|assistant)$")
    conteudo: str = Field(..., min_length=1)

class ConversationMessageCreate(ConversationMessageBase):
    pass

class ConversationMessage(ConversationMessageBase):
    id: UUID
    conversation_id: UUID
    timestamp: datetime
    metadados: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    status: str = Field(default="especificando", regex="^(especificando|clarificando|validando|completo)$")
    especificacoes_extraidas: Dict[str, Any] = Field(default_factory=dict)
    clarificacoes_pendentes: List[str] = Field(default_factory=list)
    contexto_conversacao: Dict[str, Any] = Field(default_factory=dict)

class ConversationCreate(ConversationBase):
    pass

class Conversation(ConversationBase):
    id: UUID
    user_id: UUID
    project_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    messages: List[ConversationMessage] = Field(default_factory=list)
    
    class Config:
        from_attributes = True

# Model 3D Schemas
class Model3DBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    engine: str = Field(..., regex="^(cadquery|openscad|slant3d|manual)$")
    parametros_geracao: Dict[str, Any] = Field(default_factory=dict)

class Model3DCreate(Model3DBase):
    projeto_id: UUID

class Model3D(Model3DBase):
    id: UUID
    projeto_id: UUID
    arquivo_path: str
    arquivo_tamanho: Optional[int] = None
    formato_arquivo: str
    versao: int
    numero_vertices: Optional[int] = None
    numero_faces: Optional[int] = None
    volume_calculado: Optional[float] = None
    area_superficie: Optional[float] = None
    imprimivel: bool
    erros_validacao: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    otimizado: bool
    nvidia_nim_processado: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Simulation Schemas
class SimulationBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    tipo_simulacao: str = Field(..., regex="^(drop_test|stress_test|motion|fluid)$")
    parametros: Dict[str, Any] = Field(default_factory=dict)
    condicoes_iniciais: Dict[str, Any] = Field(default_factory=dict)

class SimulationCreate(SimulationBase):
    modelo_3d_id: UUID

class Simulation(SimulationBase):
    id: UUID
    modelo_3d_id: UUID
    status: str = Field(default="pending", regex="^(pending|running|completed|failed)$")
    resultado: Dict[str, Any] = Field(default_factory=dict)
    metricas_eficiencia: Dict[str, Any] = Field(default_factory=dict)
    video_simulacao_path: Optional[str] = None
    dados_trajetoria: Optional[Dict[str, Any]] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Budget Schemas
class ItemDetalhado(BaseModel):
    descricao: str
    quantidade: int = Field(..., gt=0)
    preco_unitario: float = Field(..., ge=0)
    preco_total: float = Field(..., ge=0)
    fornecedor: Optional[str] = None

class Fornecedor(BaseModel):
    nome: str
    url: Optional[str] = None
    tempo_entrega_dias: Optional[int] = Field(None, ge=0)
    confiabilidade: float = Field(default=1.0, ge=0, le=1)

class BudgetBase(BaseModel):
    margem_lucro_percentual: float = Field(default=30, ge=0, le=100)

class BudgetCreate(BudgetBase):
    projeto_id: UUID

class Budget(BudgetBase):
    id: UUID
    projeto_id: UUID
    custo_material: float = 0
    custo_componentes: float = 0
    custo_impressao: float = 0
    custo_mao_obra: float = 0
    tempo_impressao_horas: Optional[float] = None
    tempo_montagem_horas: Optional[float] = None
    itens_detalhados: List[ItemDetalhado] = Field(default_factory=list)
    fornecedores: List[Fornecedor] = Field(default_factory=list)
    preco_final: Optional[float] = None
    proposta_pdf_path: Optional[str] = None
    numero_proposta: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Response Schemas
class ProjectList(BaseModel):
    """Lista paginada de projetos"""
    items: List[Project]
    total: int
    page: int
    per_page: int
    pages: int

class TaskStatus(BaseModel):
    """Status de tarefa assíncrona"""
    task_id: str
    status: str = Field(..., regex="^(PENDING|RUNNING|SUCCESS|FAILURE)$")
    result: Optional[Any] = None
    error: Optional[str] = None

class APIResponse(BaseModel):
    """Resposta padrão da API"""
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None

# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

# Conversational AI Schemas
class ConversationalRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[UUID] = None
    project_id: Optional[UUID] = None

class ConversationalResponse(BaseModel):
    response: str
    conversation_id: UUID
    message_id: UUID
    clarifications_needed: List[str] = Field(default_factory=list)
    extracted_specs: Dict[str, Any] = Field(default_factory=dict)

class ClarificationRequest(BaseModel):
    question_id: str
    user_answer: str