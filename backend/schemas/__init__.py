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
    tipo: str = Field(..., pattern="^(sensor|atuador|microcontroller|display|comunicacao)$")
    especificacao: str
    quantidade: int = Field(..., gt=0)
    preco_unitario: Optional[float] = Field(None, ge=0)

class Funcionalidade(BaseModel):
    nome: str
    descricao: str
    prioridade: str = Field(..., pattern="^(alta|media|baixa)$")

class Restricao(BaseModel):
    tipo: str = Field(..., pattern="^(dimensional|mecanico|eletronico|custo)$")
    descricao: str
    valor: Optional[float] = Field(None, ge=0)
    unidade: Optional[str] = None

class ProjectBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    descricao_usuario: str = Field(..., min_length=10)
    categoria: str = Field(..., pattern="^(mecanico|eletronico|mixto|arquitetura)$")
    
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
    categoria: Optional[str] = Field(None, pattern="^(mecanico|eletronico|mixto|arquitetura)$")
    
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
    papel: str = Field(..., pattern="^(user|assistant)$")
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
    status: str = Field(default="especificando", pattern="^(especificando|clarificando|validando|completo)$")
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
    engine: str = Field(..., pattern="^(cadquery|openscad|slant3d|manual)$")
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
    tipo_simulacao: str = Field(..., pattern="^(drop_test|stress_test|motion|fluid)$")
    parametros: Dict[str, Any] = Field(default_factory=dict)
    condicoes_iniciais: Dict[str, Any] = Field(default_factory=dict)

class SimulationCreate(SimulationBase):
    modelo_3d_id: UUID

class Simulation(SimulationBase):
    id: UUID
    modelo_3d_id: UUID
    status: str = Field(default="pending", pattern="^(pending|running|completed|failed)$")
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
    status: str = Field(..., pattern="^(PENDING|RUNNING|SUCCESS|FAILURE)$")
    result: Optional[Any] = None
    error: Optional[str] = None

class APIResponse(BaseModel):
    """Resposta padrão da API"""
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None

# Authentication Schemas - Complete JWT OAuth2 System

# Password validation patterns
PASSWORD_REGEX = {
    'upper': r'[A-Z]',
    'lower': r'[a-z]', 
    'digit': r'\d',
    'special': r'[!@#$%^&*(),.?":{}|<>]'
}

class PasswordValidation(BaseModel):
    """Validação de senha"""
    has_uppercase: bool = False
    has_lowercase: bool = False
    has_digit: bool = False
    has_special: bool = False
    min_length: bool = False
    
    @classmethod
    def validate_password(cls, password: str, 
                         min_length: int = 8,
                         require_upper: bool = True,
                         require_lower: bool = True,
                         require_digit: bool = True,
                         require_special: bool = True) -> 'PasswordValidation':
        """Valida senha e retorna resultado detalhado"""
        import re
        
        return cls(
            has_uppercase=bool(re.search(PASSWORD_REGEX['upper'], password)) or not require_upper,
            has_lowercase=bool(re.search(PASSWORD_REGEX['lower'], password)) or not require_lower,
            has_digit=bool(re.search(PASSWORD_REGEX['digit'], password)) or not require_digit,
            has_special=bool(re.search(PASSWORD_REGEX['special'], password)) or not require_special,
            min_length=len(password) >= min_length
        )

# Auth requests
class UserRegister(BaseModel):
    """Registro de novo usuário"""
    email: EmailStr = Field(..., description="Email do usuário")
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_-]+$',
                         description="Nome de usuário único")
    full_name: Optional[str] = Field(None, max_length=100, description="Nome completo")
    password: str = Field(..., min_length=8, description="Senha")
    company: Optional[str] = Field(None, max_length=100, description="Empresa")
    website: Optional[str] = Field(None, max_length=200, description="Site pessoal")
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username deve conter apenas letras, números, underscore e hífen')
        return v
    
    @validator('password')
    def password_complexity(cls, v):
        validation = PasswordValidation.validate_password(v)
        if not all([validation.has_uppercase, validation.has_lowercase, 
                   validation.has_digit, validation.min_length]):
            raise ValueError('Senha deve conter pelo menos 8 caracteres, 1 letra maiúscula, 1 letra minúscula e 1 número')
        return v

class UserLogin(BaseModel):
    """Login de usuário"""
    username: str = Field(..., description="Username ou email")
    password: str = Field(..., description="Senha")
    remember_me: bool = Field(default=False, description="Manter login por mais tempo")
    device_info: Optional[Dict[str, Any]] = Field(default_factory=dict, 
                                                 description="Informações do dispositivo")

class UserLoginResponse(BaseModel):
    """Resposta de login"""
    access_token: str = Field(..., description="Token de acesso JWT")
    refresh_token: str = Field(..., description="Token de refresh")
    token_type: str = Field(default="bearer", description="Tipo do token")
    expires_in: int = Field(..., description="Tempo de expiração em segundos")
    user: 'UserPublic' = Field(..., description="Dados públicos do usuário")
    # Sprint 9: MFA challenge support
    mfa_required: Optional[bool] = Field(default=False, description="Indica se MFA é obrigatório")
    mfa_token: Optional[str] = Field(default=None, description="Token temporário para challenge MFA")

class RefreshTokenRequest(BaseModel):
    """Request para renovar token"""
    refresh_token: str = Field(..., description="Token de refresh")
    
class PasswordResetRequest(BaseModel):
    """Solicitação de reset de senha"""
    email: EmailStr = Field(..., description="Email do usuário")
    
class PasswordResetConfirm(BaseModel):
    """Confirmação de reset de senha"""
    token: str = Field(..., description="Token de reset")
    new_password: str = Field(..., min_length=8, description="Nova senha")

class ChangePasswordRequest(BaseModel):
    """Troca de senha para usuário logado"""
    current_password: str = Field(..., description="Senha atual")
    new_password: str = Field(..., min_length=8, description="Nova senha")
    
    @validator('new_password')
    def password_complexity(cls, v):
        validation = PasswordValidation.validate_password(v)
        if not all([validation.has_uppercase, validation.has_lowercase, 
                   validation.has_digit, validation.min_length]):
            raise ValueError('Senha deve conter pelo menos 8 caracteres, 1 letra maiúscula, 1 letra minúscula e 1 número')
        return v

class EmailVerificationRequest(BaseModel):
    """Solicitação de verificação de email"""
    email: EmailStr = Field(..., description="Email para verificar")

class MFALoginVerification(BaseModel):
    """Verificação MFA durante login - Sprint 9"""
    mfa_token: str = Field(..., description="Token temporário da etapa de login")
    code: str = Field(..., min_length=6, max_length=8, description="Código MFA (TOTP ou backup)")
    remember_device: bool = Field(default=False, description="Lembrar este dispositivo (futuro)")

# Auth responses
class Token(BaseModel):
    """Token JWT simples"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    """Dados decodificados do token"""
    user_id: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None
    
class UserPublic(BaseModel):
    """Dados públicos do usuário"""
    id: UUID
    email: str
    username: str
    full_name: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    company: Optional[str]
    website: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    """Atualização de perfil do usuário"""
    full_name: Optional[str] = Field(None, max_length=100)
    company: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=200)
    bio: Optional[str] = Field(None, max_length=500)
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)

class AuthMessage(BaseModel):
    """Mensagens de autenticação"""
    message: str
    type: str = Field(default="info", pattern="^(info|success|warning|error)$")
    code: Optional[str] = None

class AuthResponse(BaseModel):
    """Resposta padronizada de autenticação"""
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None

# Session management
class SessionInfo(BaseModel):
    """Informações da sessão"""
    session_id: str
    device_info: Dict[str, Any]
    ip_address: str
    user_agent: str
    created_at: datetime
    last_used: datetime
    is_active: bool

class SessionList(BaseModel):
    """Lista de sessões do usuário"""
    sessions: List[SessionInfo]
    current_session_id: str

class RevokeSessionRequest(BaseModel):
    """Revogar sessão específica"""
    session_id: str = Field(..., description="ID da sessão para revogar")

class RevokeAllSessionsRequest(BaseModel):
    """Revogar todas as sessões exceto a atual"""
    confirm: bool = Field(..., description="Confirmação para revogar todas as sessões")

# Rate limiting
class RateLimitInfo(BaseModel):
    """Informações de rate limiting"""
    requests_per_minute: int
    requests_per_hour: int
    remaining_minute: int
    remaining_hour: int
    reset_time: datetime

# Old schemas compatibility
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