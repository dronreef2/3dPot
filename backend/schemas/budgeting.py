"""
Schemas Pydantic para Sistema de Orçamento Automatizado Inteligente - Sprint 5
Validação e serialização de dados para API REST
"""

from typing import Dict, List, Optional, Any, Union
from uuid import UUID
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
import numpy as np

# ========== ENUMS ==========

class QualityScore(Enum):
    """Classificação de qualidade baseada em simulações"""
    EXCELLENT = "excellent"      # 90-100
    GOOD = "good"               # 75-89
    ACCEPTABLE = "acceptable"   # 60-74
    POOR = "poor"               # 40-59
    FAILED = "failed"           # 0-39

class BudgetStatus(Enum):
    """Status do orçamento"""
    DRAFT = "draft"
    CALCULATED = "calculated"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

class MaterialType(Enum):
    """Tipos de materiais suportados"""
    PLA = "PLA"
    ABS = "ABS"
    PETG = "PETG"
    NYLON = "Nylon"
    METAL = "Metal"
    COMPOSITE = "Composite"
    RESIN = "Resin"
    TPU = "TPU"

# ========== SCHEMAS DE SIMULAÇÃO ==========

class SimulationIntegration(BaseModel):
    """Integração com resultados de simulação"""
    simulation_id: Optional[UUID] = Field(None, description="ID da simulação")
    quality_score: float = Field(..., ge=0, le=100, description="Score de qualidade (0-100)")
    test_completion_rate: float = Field(..., ge=0, le=1, description="Taxa de conclusão dos testes")
    recommended_material: Optional[str] = Field(None, description="Material recomendado")
    performance_metrics: Dict[str, Any] = Field(default_factory=dict, description="Métricas de performance")
    failure_points: List[str] = Field(default_factory=list, description="Pontos de falha")

class QualityBasedPricing(BaseModel):
    """Precificação baseada em qualidade"""
    base_cost: float = Field(..., description="Custo base sem ajustes")
    quality_multiplier: float = Field(..., description="Multiplicador de qualidade")
    adjusted_cost: float = Field(..., description="Custo ajustado pela qualidade")
    quality_score: float = Field(..., description="Score de qualidade")
    quality_classification: QualityScore = Field(..., description="Classificação da qualidade")
    confidence_level: float = Field(..., description="Nível de confiança (0-1)")

# ========== SCHEMAS DE ENTRADA ==========

class IntelligentBudgetCreate(BaseModel):
    """Schema para criação de orçamento inteligente"""
    projeto_id: UUID = Field(..., description="ID do projeto")
    simulation_id: Optional[UUID] = Field(None, description="ID da simulação para integração")
    margem_lucro_percentual: Optional[float] = Field(25.0, ge=0, le=100, description="Margem de lucro em %")
    observacoes: Optional[str] = Field(None, description="Observações adicionais")
    urgente: bool = Field(False, description="Se o projeto é urgente")
    
    # Configurações avançadas
    forcar_material: Optional[MaterialType] = Field(None, description="Forçar uso de material específico")
    preco_maximo: Optional[float] = Field(None, description="Preço máximo aceitável")
    
    @validator('margem_lucro_percentual')
    def validate_margin(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Margem deve estar entre 0 e 100%')
        return v or 25.0

class BudgetRecalculateRequest(BaseModel):
    """Request para recalcular orçamento"""
    new_quality_score: Optional[float] = Field(None, ge=0, le=100, description="Novo score de qualidade")
    new_margin: Optional[float] = Field(None, ge=0, le=100, description="Nova margem de lucro")
    include_simulation: bool = Field(False, description="Incluir resultados de simulação")
    
    @validator('new_quality_score')
    def validate_quality_score(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Score de qualidade deve estar entre 0 e 100')
        return v

class SupplierComparisonRequest(BaseModel):
    """Request para comparar fornecedores"""
    include_shipping: bool = Field(True, description="Incluir custo de frete")
    max_suppliers: int = Field(5, ge=1, le=20, description="Número máximo de fornecedores")
    region: Optional[str] = Field(None, description="Região de entrega")

# ========== SCHEMAS DE RESPOSTA ==========

class MaterialRecommendation(BaseModel):
    """Recomendação de material baseada em simulação"""
    material: MaterialType = Field(..., description="Material recomendado")
    confidence: float = Field(..., ge=0, le=1, description="Nível de confiança")
    reason: str = Field(..., description="Justificativa da recomendação")
    is_premium: bool = Field(False, description="Se é um material premium")
    estimated_cost: Optional[float] = Field(None, description="Custo estimado")
    performance_score: Optional[float] = Field(None, description="Score de performance")
    alternatives: List[MaterialType] = Field(default_factory=list, description="Materiais alternativos")

class BudgetItem(BaseModel):
    """Item detalhado do orçamento"""
    descricao: str = Field(..., description="Descrição do item")
    quantidade: Union[str, float] = Field(..., description="Quantidade")
    preco_unitario: float = Field(..., ge=0, description="Preço unitário")
    preco_total: float = Field(..., ge=0, description="Preço total")
    fornecedor: str = Field(..., description="Fornecedor")
    confianca: Optional[float] = Field(None, ge=0, le=1, description="Nível de confiança")
    justificativa: Optional[str] = Field(None, description="Justificativa do item")
    categoria: Optional[str] = Field(None, description="Categoria do item")

class BudgetSupplier(BaseModel):
    """Fornecedor do orçamento"""
    nome: str = Field(..., description="Nome do fornecedor")
    url: Optional[str] = Field(None, description="URL do fornecedor")
    confiabilidade: float = Field(..., ge=0, le=1, description="Confiabilidade (0-1)")
    tempo_entrega: Optional[int] = Field(None, description="Tempo de entrega em dias")
    custo_frete: Optional[float] = Field(None, description="Custo de frete")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Avaliação (0-5)")

class QualityMetrics(BaseModel):
    """Métricas de qualidade da simulação"""
    overall_score: float = Field(..., ge=0, le=100, description="Score geral")
    classification: QualityScore = Field(..., description="Classificação")
    test_results: Dict[str, Any] = Field(default_factory=dict, description="Resultados dos testes")
    recommendations: List[str] = Field(default_factory=list, description="Recomendações")
    warnings: List[str] = Field(default_factory=list, description="Avisos")
    optimization_suggestions: List[str] = Field(default_factory=list, description="Sugestões de otimização")

class BudgetMargin(BaseModel):
    """Margens de lucro do orçamento"""
    margem_base_percentual: float = Field(..., description="Margem base em %")
    margem_valor: float = Field(..., description="Valor da margem")
    quality_multiplier: float = Field(..., description="Multiplicador de qualidade")
    adjusted_cost: float = Field(..., description="Custo ajustado")
    final_price: float = Field(..., description="Preço final")

class BudgetTimeline(BaseModel):
    """Cronograma do orçamento"""
    fase: str = Field(..., description="Fase do projeto")
    duracao_horas: float = Field(..., description="Duração em horas")
    dependencia: Optional[str] = Field(None, description="Dependência")
    recursos: List[str] = Field(default_factory=list, description="Recursos necessários")
    marcos: List[str] = Field(default_factory=list, description="Marcos importantes")

class IntelligentBudgetResponse(BaseModel):
    """Resposta completa do orçamento inteligente"""
    id: UUID = Field(..., description="ID do orçamento")
    projeto_id: UUID = Field(..., description="ID do projeto")
    simulation_id: Optional[UUID] = Field(None, description="ID da simulação")
    
    # Qualidade e classificação
    quality_score: float = Field(..., ge=0, le=100, description="Score de qualidade")
    quality_classification: QualityScore = Field(..., description="Classificação da qualidade")
    quality_multiplier: float = Field(..., description="Multiplicador de qualidade")
    
    # Custos
    custo_material: float = Field(..., ge=0, description="Custo do material")
    custo_componentes: float = Field(..., ge=0, description="Custo dos componentes")
    custo_impressao: float = Field(..., ge=0, description="Custo da impressão")
    custo_mao_obra: float = Field(..., ge=0, description="Custo da mão de obra")
    preco_final: float = Field(..., ge=0, description="Preço final")
    
    # Tempos
    tempo_impressao_horas: float = Field(..., ge=0, description="Tempo de impressão")
    tempo_montagem_horas: float = Field(..., ge=0, description="Tempo de montagem")
    tempo_entrega_estimado: int = Field(..., ge=0, description="Tempo de entrega em dias")
    
    # Detalhes
    itens_detalhados: List[BudgetItem] = Field(default_factory=list, description="Itens detalhados")
    fornecedores: List[BudgetSupplier] = Field(default_factory=list, description="Fornecedores")
    margens_lucro: BudgetMargin = Field(..., description="Margens de lucro")
    justificativas: List[str] = Field(default_factory=list, description="Justificativas")
    
    # Materiais e complexidade
    material_recomendado: str = Field(..., description="Material recomendado")
    complexidade_score: float = Field(..., ge=0, le=1, description="Score de complexidade")
    
    # Metadados
    status: BudgetStatus = Field(BudgetStatus.CALCULATED, description="Status do orçamento")
    criado_em: datetime = Field(..., description="Data de criação")
    atualizado_em: datetime = Field(..., description="Data de atualização")
    
    # Qualificação
    simulation_integration: Optional[SimulationIntegration] = Field(None, description="Integração com simulação")
    quality_metrics: Optional[QualityMetrics] = Field(None, description="Métricas de qualidade")
    timeline: List[BudgetTimeline] = Field(default_factory=list, description="Cronograma")

# ========== SCHEMAS PARA API SLANT3D ==========

class Slant3DQuoteRequest(BaseModel):
    """Request para cotação Slant3D"""
    model_id: UUID = Field(..., description="ID do modelo 3D")
    material: MaterialType = Field(..., description="Material desejado")
    quantity: int = Field(1, ge=1, le=1000, description="Quantidade")
    finish_type: Optional[str] = Field(None, description="Tipo de acabamento")
    color: Optional[str] = Field(None, description="Cor")
    
class Slant3DQuote(BaseModel):
    """Cotação do Slant3D"""
    quote_id: str = Field(..., description="ID da cotação")
    total_price: float = Field(..., description="Preço total")
    unit_price: float = Field(..., description="Preço unitário")
    quantity: int = Field(..., description="Quantidade")
    material: str = Field(..., description="Material")
    estimated_delivery: int = Field(..., description="Entrega estimada em dias")
    shipping_cost: Optional[float] = Field(None, description="Custo de frete")
    availability: bool = Field(..., description="Disponibilidade")
    processing_time: int = Field(..., description="Tempo de processamento em dias")
    
class Slant3DComparison(BaseModel):
    """Comparação de cotações Slant3D"""
    options: List[Slant3DQuote] = Field(..., description="Opções de cotação")
    best_option: Slant3DQuote = Field(..., description="Melhor opção")
    comparison_summary: Dict[str, Any] = Field(..., description="Resumo da comparação")

# ========== SCHEMAS PARA COMPARAÇÃO DE FORNECEDORES ==========

class SupplierQuote(BaseModel):
    """Cotação de fornecedor"""
    supplier_id: str = Field(..., description="ID do fornecedor")
    supplier_name: str = Field(..., description="Nome do fornecedor")
    total_cost: float = Field(..., description="Custo total")
    unit_cost: float = Field(..., description="Custo unitário")
    delivery_time: int = Field(..., description="Tempo de entrega")
    quality_rating: float = Field(..., ge=0, le=5, description="Avaliação de qualidade")
    reliability_score: float = Field(..., ge=0, le=1, description="Score de confiabilidade")
    shipping_cost: Optional[float] = Field(None, description="Custo de frete")

class SupplierComparison(BaseModel):
    """Comparação de fornecedores"""
    budget_id: UUID = Field(..., description="ID do orçamento")
    quotes: List[SupplierQuote] = Field(..., description="Cotações dos fornecedores")
    recommended_supplier: SupplierQuote = Field(..., description="Fornecedor recomendado")
    comparison_criteria: Dict[str, float] = Field(..., description="Critérios de comparação")
    reasoning: str = Field(..., description="Justificativa da recomendação")

# ========== SCHEMAS PARA RELATÓRIOS ==========

class BudgetReport(BaseModel):
    """Relatório completo do orçamento"""
    budget: IntelligentBudgetResponse = Field(..., description="Orçamento completo")
    executive_summary: str = Field(..., description="Resumo executivo")
    cost_breakdown: Dict[str, Any] = Field(..., description="Detalhamento de custos")
    quality_analysis: Dict[str, Any] = Field(..., description="Análise de qualidade")
    risk_assessment: List[str] = Field(default_factory=list, description="Avaliação de riscos")
    recommendations: List[str] = Field(default_factory=list, description="Recomendações")
    alternatives: List[Dict[str, Any]] = Field(default_factory=list, description="Alternativas")

class BudgetExport(BaseModel):
    """Dados para exportação do orçamento"""
    format: str = Field(..., description="Formato de exportação")
    include_charts: bool = Field(True, description="Incluir gráficos")
    include_supplier_details: bool = Field(True, description="Incluir detalhes dos fornecedores")
    language: str = Field("pt-BR", description="Idioma do relatório")
    
# ========== VALIDATORS ==========

class BudgetValidators:
    """Validators para schemas de orçamento"""
    
    @staticmethod
    def validate_quality_score(score: float) -> float:
        """Validar score de qualidade"""
        if not 0 <= score <= 100:
            raise ValueError("Score de qualidade deve estar entre 0 e 100")
        return round(score, 2)
    
    @staticmethod
    def validate_cost_breakdown(costs: Dict[str, float]) -> Dict[str, float]:
        """Validar breakdown de custos"""
        required_keys = ['custo_material', 'custo_componentes', 'custo_impressao', 'custo_mao_obra']
        for key in required_keys:
            if key not in costs or costs[key] < 0:
                raise ValueError(f"Custo inválido para {key}")
        return costs
    
    @staticmethod
    def validate_budget_consistency(budget: IntelligentBudgetResponse) -> bool:
        """Validar consistência do orçamento"""
        calculated_total = (
            budget.custo_material +
            budget.custo_componentes +
            budget.custo_impressao +
            budget.custo_mao_obra
        )
        
        # O preço final deve ser pelo menos o custo total
        if budget.preco_final < calculated_total:
            return False
        
        return True

# ========== SCHEMAS ADICIONAIS PARA API AVANÇADA ==========

class BudgetAnalytics(BaseModel):
    """Análises do orçamento"""
    budget_id: UUID = Field(..., description="ID do orçamento")
    cost_per_gram: float = Field(..., description="Custo por grama")
    cost_per_cm3: float = Field(..., description="Custo por cm³")
    quality_cost_ratio: float = Field(..., description="Razão custo/qualidade")
    efficiency_score: float = Field(..., description="Score de eficiência")
    competitiveness: float = Field(..., description="Competitividade do preço")

class BudgetOptimization(BaseModel):
    """Sugestões de otimização"""
    budget_id: UUID = Field(..., description="ID do orçamento")
    current_price: float = Field(..., description="Preço atual")
    optimized_price: float = Field(..., description="Preço otimizado")
    savings: float = Field(..., description="Economia potencial")
    optimization_strategies: List[str] = Field(..., description="Estratégias de otimização")
    trade_offs: List[str] = Field(..., description="Trade-offs")

# ========== SCHEMAS PARA WEBSOCKET/UPDATES ==========

class BudgetUpdate(BaseModel):
    """Update em tempo real do orçamento"""
    budget_id: UUID = Field(..., description="ID do orçamento")
    status: BudgetStatus = Field(..., description="Status atual")
    progress: float = Field(..., ge=0, le=1, description="Progresso (0-1)")
    current_step: str = Field(..., description="Etapa atual")
    estimated_completion: Optional[datetime] = Field(None, description="Estimativa de conclusão")
    message: Optional[str] = Field(None, description="Mensagem de status")

# ========== EXPORTS ==========

__all__ = [
    # Enums
    'QualityScore', 'BudgetStatus', 'MaterialType',
    
    # Simulação
    'SimulationIntegration', 'QualityBasedPricing',
    
    # Request/Response
    'IntelligentBudgetCreate', 'BudgetRecalculateRequest', 'SupplierComparisonRequest',
    'MaterialRecommendation', 'BudgetItem', 'BudgetSupplier', 'QualityMetrics',
    'BudgetMargin', 'BudgetTimeline', 'IntelligentBudgetResponse',
    
    # Slant3D
    'Slant3DQuoteRequest', 'Slant3DQuote', 'Slant3DComparison',
    
    # Fornecedores
    'SupplierQuote', 'SupplierComparison',
    
    # Relatórios
    'BudgetReport', 'BudgetExport', 'BudgetAnalytics', 'BudgetOptimization',
    
    # Updates
    'BudgetUpdate',
    
    # Validators
    'BudgetValidators'
]