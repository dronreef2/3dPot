"""
Modelos SQLAlchemy para Sistema de Orçamento Automatizado Inteligente - Sprint 5
Modelos de banco de dados para PostgreSQL
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey, Integer, 
    JSON, Numeric, String, Text, UniqueConstraint, Float
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class IntelligentBudget(Base):
    """
    Orçamento inteligente baseado em simulações físicas (Sprint 5)
    Substitui o Budget básico com funcionalidades avançadas
    """
    __tablename__ = "intelligent_budgets"
    
    # IDs
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    projeto_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    simulation_id = Column(UUID(as_uuid=True), ForeignKey("simulations.id"), nullable=True)
    
    # Qualidade e classificação (Sprint 4 integration)
    quality_score = Column(Float, default=50.0, comment="Score de qualidade (0-100)")
    quality_classification = Column(Enum('excellent', 'good', 'acceptable', 'poor', 'failed', 
                                         name='quality_classification'), 
                                   default='acceptable')
    quality_multiplier = Column(Float, default=1.0, comment="Multiplicador de qualidade")
    
    # Custos detalhados
    custo_material = Column(Numeric(12, 2), default=0.0, comment="Custo do material")
    custo_componentes = Column(Numeric(12, 2), default=0.0, comment="Custo dos componentes eletrônicos")
    custo_impressao = Column(Numeric(12, 2), default=0.0, comment="Custo da impressão 3D")
    custo_mao_obra = Column(Numeric(12, 2), default=0.0, comment="Custo da mão de obra")
    
    # Tempos estimados
    tempo_impressao_horas = Column(Numeric(8, 2), default=0.0, comment="Tempo de impressão em horas")
    tempo_montagem_horas = Column(Numeric(8, 2), default=0.0, comment="Tempo de montagem em horas")
    tempo_entrega_estimado = Column(Integer, default=0, comment="Tempo de entrega em dias")
    
    # Detalhamento inteligente
    itens_detalhados = Column(JSON, default=list, comment="Itens detalhados com justificativas")
    fornecedores = Column(JSON, default=list, comment="Lista de fornecedores")
    margens_lucro = Column(JSON, default=dict, comment="Margens de lucro e multiplicadores")
    justificativas = Column(JSON, default=list, comment="Justificativas automáticas")
    
    # Material e complexidade
    material_recomendado = Column(String(50), default="PLA", comment="Material recomendado pela simulação")
    complexidade_score = Column(Float, default=0.5, comment="Score de complexidade (0-1)")
    
    # Status e metadados
    status = Column(Enum('draft', 'calculated', 'review', 'approved', 'rejected', 'expired',
                        name='budget_status'), default='draft')
    
    # Timestamps
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expirado_em = Column(DateTime, nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="intelligent_budgets")
    simulation = relationship("Simulation", back_populates="intelligent_budgets")
    material_recommendations = relationship("BudgetMaterial", back_populates="budget")
    supplier_comparisons = relationship("BudgetSupplier", back_populates="budget")

class BudgetMaterial(Base):
    """
    Recomendações de materiais baseadas em simulações físicas
    """
    __tablename__ = "budget_materials"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    budget_id = Column(UUID(as_uuid=True), ForeignKey("intelligent_budgets.id"), nullable=False)
    
    # Material info
    material = Column(String(50), nullable=False, comment="Tipo do material")
    confidence = Column(Float, default=0.5, comment="Nível de confiança (0-1)")
    reason = Column(Text, nullable=False, comment="Justificativa da recomendação")
    is_premium = Column(Boolean, default=False, comment="Se é material premium")
    
    # Performance metrics
    performance_score = Column(Float, nullable=True, comment="Score de performance")
    stress_resistance = Column(Float, nullable=True, comment="Resistência ao stress")
    impact_resistance = Column(Float, nullable=True, comment="Resistência ao impacto")
    durability_rating = Column(Float, nullable=True, comment="Rating de durabilidade")
    
    # Cost info
    estimated_cost = Column(Numeric(10, 2), nullable=True, comment="Custo estimado")
    cost_per_gram = Column(Numeric(8, 4), nullable=True, comment="Custo por grama")
    
    # Simulation data
    simulation_tests_passed = Column(Integer, default=0, comment="Testes simulados aprovados")
    recommended_by_tests = Column(JSON, default=list, comment="Testes que recomendam este material")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    budget = relationship("IntelligentBudget", back_populates="material_recommendations")

class BudgetSupplier(Base):
    """
    Comparação de fornecedores para orçamento inteligente
    """
    __tablename__ = "budget_suppliers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    budget_id = Column(UUID(as_uuid=True), ForeignKey("intelligent_budgets.id"), nullable=False)
    
    # Supplier info
    nome = Column(String(100), nullable=False, comment="Nome do fornecedor")
    tipo = Column(Enum('print_service', 'materials', 'electronics', 'assembly', 'integrated',
                      name='supplier_type'), nullable=False)
    url = Column(String(500), nullable=True, comment="URL do fornecedor")
    
    # Cost information
    preco_total = Column(Numeric(12, 2), nullable=False, comment="Preço total")
    preco_unitario = Column(Numeric(10, 4), nullable=True, comment="Preço unitário")
    custo_frete = Column(Numeric(8, 2), nullable=True, comment="Custo de frete")
    desconto_percentual = Column(Numeric(5, 2), nullable=True, comment="Desconto oferecido")
    
    # Delivery and quality
    tempo_entrega = Column(Integer, nullable=True, comment="Tempo de entrega em dias")
    confiabilidade = Column(Float, default=0.8, comment="Confiabilidade (0-1)")
    rating = Column(Float, nullable=True, comment="Avaliação (0-5)")
    qualidade_material = Column(Float, nullable=True, comment="Qualidade do material (0-1)")
    
    # Location and shipping
    pais = Column(String(50), default="Brasil", comment="País do fornecedor")
    estado = Column(String(50), nullable=True, comment="Estado")
    cidade = Column(String(100), nullable=True, comment="Cidade")
    cep_atende = Column(String(20), nullable=True, comment="CEPs que atende")
    
    # Technical specs
    materiais_suportados = Column(JSON, default=list, comment="Materiais suportados")
    formatos_suportados = Column(JSON, default=list, comment="Formatos de arquivo suportados")
    servicos_adicionais = Column(JSON, default=list, comment="Serviços adicionais")
    
    # API integration
    api_key_configurada = Column(Boolean, default=False, comment="Se a API está configurada")
    ultimo_preco_sync = Column(DateTime, nullable=True, comment="Última sincronização de preços")
    
    # Comparison metrics
    custo_beneficio_score = Column(Float, nullable=True, comment="Score custo-benefício")
    recomendado = Column(Boolean, default=False, comment="Se é o fornecedor recomendado")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    budget = relationship("IntelligentBudget", back_populates="supplier_comparisons")
    quotes = relationship("SupplierQuote", back_populates="supplier")

class SupplierQuote(Base):
    """
    Cotações específicas de fornecedores
    """
    __tablename__ = "supplier_quotes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("budget_suppliers.id"), nullable=False)
    budget_id = Column(UUID(as_uuid=True), ForeignKey("intelligent_budgets.id"), nullable=False)
    
    # Quote details
    quote_id_externo = Column(String(100), nullable=True, comment="ID da cotação externa")
    item_descricao = Column(Text, nullable=False, comment="Descrição do item cotado")
    quantidade = Column(Integer, nullable=False, comment="Quantidade cotada")
    
    # Pricing
    preco_unitario = Column(Numeric(10, 4), nullable=False, comment="Preço unitário")
    preco_total = Column(Numeric(12, 2), nullable=False, comment="Preço total")
    moeda = Column(String(3), default="BRL", comment="Moeda da cotação")
    
    # Delivery
    tempo_entrega = Column(Integer, nullable=False, comment="Tempo de entrega em dias")
    data_entrega_estimada = Column(DateTime, nullable=True, comment="Data estimada de entrega")
    
    # Status
    status = Column(Enum('active', 'expired', 'cancelled', 'accepted', 'rejected',
                        name='quote_status'), default='active')
    
    # Validity
    validade_dias = Column(Integer, default=30, comment="Validade da cotação em dias")
    expira_em = Column(DateTime, nullable=True, comment="Data de expiração")
    
    # Technical details
    especificacoes = Column(JSON, default=dict, comment="Especificações técnicas")
    disponivel = Column(Boolean, default=True, comment="Se está disponível")
    
    # Source
    fonte_api = Column(String(50), nullable=True, comment="API de origem da cotação")
    cotado_em = Column(DateTime, default=datetime.utcnow, comment="Quando foi cotado")
    
    # Relationships
    supplier = relationship("BudgetSupplier", back_populates="quotes")
    budget = relationship("IntelligentBudget")

class Slant3DQuote(Base):
    """
    Cotações específicas do Slant3D para integração externa
    """
    __tablename__ = "slant3d_quotes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    budget_id = Column(UUID(as_uuid=True), ForeignKey("intelligent_budgets.id"), nullable=False)
    
    # Slant3D data
    slant3d_quote_id = Column(String(100), unique=True, nullable=False, comment="ID da cotação Slant3D")
    model_url = Column(String(500), nullable=False, comment="URL do modelo no Slant3D")
    
    # Material and quantity
    material = Column(String(50), nullable=False, comment="Material selecionado")
    quantidade = Column(Integer, default=1, comment="Quantidade solicitada")
    color = Column(String(50), nullable=True, comment="Cor selecionada")
    finish_type = Column(String(50), nullable=True, comment="Tipo de acabamento")
    
    # Pricing
    preco_unitario = Column(Numeric(10, 2), nullable=False, comment="Preço unitário")
    preco_total = Column(Numeric(12, 2), nullable=False, comment="Preço total")
    
    # Delivery
    processing_days = Column(Integer, nullable=False, comment="Dias de processamento")
    estimated_delivery = Column(Integer, nullable=False, comment="Entrega estimada em dias")
    shipping_cost = Column(Numeric(8, 2), nullable=True, comment="Custo de frete")
    
    # Status
    disponivel = Column(Boolean, default=True, comment="Se está disponível")
    active = Column(Boolean, default=True, comment="Se a cotação está ativa")
    
    # Technical info
    file_size = Column(Integer, nullable=True, comment="Tamanho do arquivo em bytes")
    print_volume_required = Column(JSON, nullable=True, comment="Volume de impressão necessário")
    layer_height_suggested = Column(Float, nullable=True, comment="Altura de camada sugerida")
    
    # Timestamps
    quoted_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True, comment="Data de expiração")
    
    # Budget relationship
    budget = relationship("IntelligentBudget")

class BudgetTimeline(Base):
    """
    Cronograma detalhado do orçamento com marcos
    """
    __tablename__ = "budget_timelines"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    budget_id = Column(UUID(as_uuid=True), ForeignKey("intelligent_budgets.id"), nullable=False)
    
    # Timeline info
    fase = Column(String(100), nullable=False, comment="Nome da fase")
    ordem = Column(Integer, nullable=False, comment="Ordem da fase")
    duracao_horas = Column(Numeric(6, 2), nullable=False, comment="Duração em horas")
    
    # Dependencies and resources
    dependencia_fase = Column(String(100), nullable=True, comment="Fase dependente")
    recursos = Column(JSON, default=list, comment="Recursos necessários")
    marcos = Column(JSON, default=list, comment="Marcos importantes")
    
    # Scheduling
    inicio_estimado = Column(DateTime, nullable=True, comment="Início estimado")
    fim_estimado = Column(DateTime, nullable=True, comment="Fim estimado")
    
    # Progress tracking
    completada = Column(Boolean, default=False, comment="Se a fase foi completada")
    progresso_percentual = Column(Integer, default=0, comment="Progresso (0-100)")
    
    # Metadata
    observacoes = Column(Text, nullable=True, comment="Observações da fase")
    criada_em = Column(DateTime, default=datetime.utcnow)
    
    # Budget relationship
    budget = relationship("IntelligentBudget")

class BudgetAnalytics(Base):
    """
    Análises e métricas do orçamento
    """
    __tablename__ = "budget_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    budget_id = Column(UUID(as_uuid=True), ForeignKey("intelligent_budgets.id"), nullable=False)
    
    # Cost metrics
    cost_per_gram = Column(Numeric(8, 4), nullable=True, comment="Custo por grama")
    cost_per_cm3 = Column(Numeric(8, 4), nullable=True, comment="Custo por cm³")
    material_waste_percentage = Column(Numeric(5, 2), nullable=True, comment="% de desperdício")
    
    # Quality metrics
    quality_cost_ratio = Column(Numeric(6, 3), nullable=True, comment="Razão custo/qualidade")
    efficiency_score = Column(Numeric(5, 3), nullable=True, comment="Score de eficiência")
    competitiveness_index = Column(Numeric(6, 3), nullable=True, comment="Índice de competitividade")
    
    # Performance metrics
    simulation_confidence = Column(Numeric(5, 3), nullable=True, comment="Confiança na simulação")
    delivery_accuracy = Column(Numeric(5, 3), nullable=True, comment="Precisão de entrega")
    cost_prediction_accuracy = Column(Numeric(5, 3), nullable=True, comment="Precisão de custo")
    
    # Market comparison
    market_price_avg = Column(Numeric(10, 2), nullable=True, comment="Preço médio de mercado")
    price_percentile = Column(Numeric(5, 2), nullable=True, comment="Percentil do preço")
    
    # Risk assessment
    risk_score = Column(Numeric(5, 3), nullable=True, comment="Score de risco")
    quality_risk_factors = Column(JSON, default=list, comment="Fatores de risco de qualidade")
    cost_risk_factors = Column(JSON, default=list, comment="Fatores de risco de custo")
    
    # Timestamps
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    
    # Budget relationship
    budget = relationship("IntelligentBudget")

class BudgetCache(Base):
    """
    Cache para otimização de cálculos de orçamento
    """
    __tablename__ = "budget_cache"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Cache key
    cache_key = Column(String(255), unique=True, nullable=False, index=True)
    tipo_calculo = Column(Enum('material', 'supplier', 'simulation', 'quality', 'general',
                               name='calculation_type'), nullable=False)
    
    # Cached data
    parametros_entrada = Column(JSON, default=dict, comment="Parâmetros de entrada")
    resultado_cacheado = Column(JSON, default=dict, comment="Resultado em cache")
    
    # Metadata
    tamanho_bytes = Column(Integer, default=0, comment="Tamanho em bytes")
    hit_count = Column(Integer, default=0, comment="Número de hits")
    accuracy_score = Column(Numeric(5, 3), nullable=True, comment="Score de precisão")
    
    # Expiration
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False, comment="Data de expiração")
    last_accessed = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('cache_key', name='uq_budget_cache_key'),
    )

# Backwards compatibility alias
Budget = IntelligentBudget

# Update existing Project relationship
from . import Project
Project.intelligent_budgets = relationship("IntelligentBudget", back_populates="project")

# Update existing Simulation relationship
from . import Simulation
Simulation.intelligent_budgets = relationship("IntelligentBudget", back_populates="simulation")