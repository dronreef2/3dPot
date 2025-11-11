"""
Modelos SQLAlchemy para Sistema de Simulação Física
Tabelas para armazenar dados de simulações, resultados e templates
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey, Boolean, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..models import Base

# ========== MODELO PRINCIPAL DE SIMULAÇÃO ==========

class Simulation(Base):
    """
    Tabela principal para armazenar dados das simulações
    """
    __tablename__ = "simulations"
    
    # Campos obrigatórios
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    nome = Column(String(200), nullable=False, comment="Nome da simulação")
    tipo_simulacao = Column(String(50), nullable=False, comment="Tipo (drop_test, stress_test, etc)")
    
    # Relacionamentos
    modelo_3d_id = Column(UUID(as_uuid=True), ForeignKey("models_3d.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Status e controle
    status = Column(String(20), nullable=False, default="pending", index=True)
    progress = Column(Float, default=0.0, comment="Progresso da simulação (0-100%)")
    error_message = Column(Text, comment="Mensagem de erro se falhou")
    
    # Configuração
    parametros = Column(JSON, default=dict, comment="Parâmetros da simulação")
    condicoes_iniciais = Column(JSON, default=dict, comment="Condições iniciais")
    
    # Resultados
    results = Column(JSON, comment="Resultados completos da simulação")
    metrics = Column(JSON, default=dict, comment="Métricas calculadas")
    
    # Controle temporal
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), comment="Quando começou a execução")
    completed_at = Column(DateTime(timezone=True), comment="Quando foi concluída")
    estimated_completion = Column(DateTime(timezone=True), comment="Previsão de conclusão")
    
    # Configurações avançadas
    physics_engine = Column(String(50), default="pybullet", comment="Engine de física usado")
    time_step = Column(Float, default=1/240, comment="Passo de tempo da simulação")
    max_iterations = Column(Integer, default=10000, comment="Máximo de iterações")
    
    # Controle de execução
    celery_task_id = Column(String(100), comment="ID da tarefa Celery")
    is_cancelled = Column(Boolean, default=False, comment="Se foi cancelada")
    retry_count = Column(Integer, default=0, comment="Número de tentativas")
    
    # Metadados
    ip_address = Column(String(45), comment="IP do usuário")
    user_agent = Column(Text, comment="User agent do navegador")
    version = Column(String(20), default="1.0", comment="Versão da simulação")
    
    # Relacionamentos
    model_3d = relationship("Model3D", back_populates="simulations")
    user = relationship("User", back_populates="simulations")
    
    def __repr__(self):
        return f"<Simulation(id={self.id}, nome='{self.nome}', tipo='{self.tipo_simulacao}', status='{self.status}')>"
    
    @property
    def duration(self) -> Optional[float]:
        """Calcular duração da simulação em segundos"""
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    @property
    def is_completed(self) -> bool:
        """Verificar se a simulação foi concluída"""
        return self.status == "completed"
    
    @property
    def has_error(self) -> bool:
        """Verificar se houve erro"""
        return self.status == "failed" or self.error_message is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            "id": str(self.id),
            "nome": self.nome,
            "tipo_simulacao": self.tipo_simulacao,
            "status": self.status,
            "progress": self.progress,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "modelo_3d_id": str(self.modelo_3d_id),
            "parametros": self.parametros or {},
            "results": self.results,
            "duration": self.duration
        }

# ========== MODELO DE TEMPLATES ==========

class SimulationTemplate(Base):
    """
    Templates pré-configurados de simulação
    """
    __tablename__ = "simulation_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(100), nullable=False, unique=True, index=True)
    descricao = Column(Text, nullable=False)
    
    # Configuração
    tipo_simulacao = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)  # basic, comprehensive, mechanical, etc
    
    # Parâmetros do template
    parametros_padrao = Column(JSON, default=dict, comment="Parâmetros padrão")
    validacao_regra = Column(JSON, default=dict, comment="Regras de validação")
    
    # Metadados
    is_public = Column(Boolean, default=True, comment="Se é público")
    is_default = Column(Boolean, default=False, comment="Se é padrão do sistema")
    usage_count = Column(Integer, default=0, comment="Número de usos")
    
    # Controle temporal
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relacionamento
    creator = relationship("User")
    
    def __repr__(self):
        return f"<SimulationTemplate(nome='{self.nome}', tipo='{self.tipo_simulacao}')>"

# ========== MODELO DE RESULTADOS DETALHADOS ==========

class SimulationResult(Base):
    """
    Resultados detalhados das simulações (separados para performance)
    """
    __tablename__ = "simulation_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_id = Column(UUID(as_uuid=True), ForeignKey("simulations.id"), nullable=False)
    
    # Dados estruturados por tipo
    drop_test_data = Column(JSON, comment="Dados do teste de queda")
    stress_test_data = Column(JSON, comment="Dados do teste de stress")
    motion_test_data = Column(JSON, comment="Dados do teste de movimento")
    fluid_test_data = Column(JSON, comment="Dados do teste de fluido")
    
    # Métricas calculadas
    quality_score = Column(Float, comment="Score de qualidade (0-10)")
    printable = Column(Boolean, comment="Se é imprimível")
    structural_integrity = Column(String(20), comment="Integridade estrutural")
    
    # Análise e recomendações
    recommendations = Column(JSON, default=list, comment="Lista de recomendações")
    design_improvements = Column(JSON, default=list, comment="Melhorias sugeridas")
    warnings = Column(JSON, default=list, comment="Avisos")
    
    # Dados técnicos
    convergence_data = Column(JSON, comment="Dados de convergência")
    performance_metrics = Column(JSON, comment="Métricas de performance")
    visualization_data = Column(JSON, default=dict, comment="Dados para visualização")
    
    # Controle temporal
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamento
    simulation = relationship("Simulation", back_populates="detailed_results")
    
    def __repr__(self):
        return f"<SimulationResult(simulation_id={self.simulation_id})>"
    
    @property
    def result_data(self) -> Dict[str, Any]:
        """Obter dados do resultado baseado no tipo"""
        if self.simulation and self.simulation.tipo_simulacao == "drop_test":
            return self.drop_test_data or {}
        elif self.simulation and self.simulation.tipo_simulacao == "stress_test":
            return self.stress_test_data or {}
        elif self.simulation and self.simulation.tipo_simulacao == "motion":
            return self.motion_test_data or {}
        elif self.simulation and self.simulation.tipo_simulacao == "fluid":
            return self.fluid_test_data or {}
        return {}

# ========== MODELO DE HISTÓRICO DE EXECUÇÃO ==========

class SimulationExecutionLog(Base):
    """
    Log detalhado de execução das simulações
    """
    __tablename__ = "simulation_execution_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_id = Column(UUID(as_uuid=True), ForeignKey("simulations.id"), nullable=False)
    
    # Dados do log
    step_name = Column(String(100), nullable=False, comment="Nome da etapa")
    step_description = Column(Text, comment="Descrição da etapa")
    status = Column(String(20), nullable=False)  # started, completed, failed
    
    # Dados técnicos
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True))
    duration = Column(Float, comment="Duração em segundos")
    
    # Dados específicos da etapa
    step_data = Column(JSON, comment="Dados específicos da etapa")
    error_details = Column(JSON, comment="Detalhes de erro se falhou")
    
    # Controle de sequencia
    sequence_number = Column(Integer, nullable=False, comment="Ordem da etapa")
    
    # Relacionamento
    simulation = relationship("Simulation")
    
    def __repr__(self):
        return f"<SimulationExecutionLog(sim_id={self.simulation_id}, step='{self.step_name}')>"

# ========== MODELO DE CONFIGURAÇÕES DE MATERIAL ==========

class MaterialProperties(Base):
    """
    Propriedades de materiais para simulações
    """
    __tablename__ = "material_properties"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(100), nullable=False, unique=True, index=True)
    categoria = Column(String(50), nullable=False)  # plastic, metal, ceramic, etc
    
    # Propriedades físicas
    densidade = Column(Float, nullable=False, comment="Densidade kg/m³")
    modulo_young = Column(Float, comment="Módulo de Young GPa")
    coeficiente_poisson = Column(Float, comment="Coeficiente de Poisson")
    resistencia_tracao = Column(Float, comment="Resistência à tração MPa")
    resistencia_compressao = Column(Float, comment="Resistência à compressão MPa")
    limite_escoamento = Column(Float, comment="Limite de escoamento MPa")
    
    # Propriedades térmicas
    condutividade_termica = Column(Float, comment="Condutividade térmica W/m·K")
    calor_especifico = Column(Float, comment="Calor específico J/kg·K")
    coeficiente_expansao = Column(Float, comment="Coeficiente de expansão térmica 1/K")
    
    # Propriedades de impressão 3D
    temperatura_filamento = Column(Float, comment="Temperatura de impressão °C")
    temperatura_cama = Column(Float, comment="Temperatura da cama °C")
    velocidade_impressao = Column(Float, comment="Velocidade de impressão mm/s")
    
    # Configurações de simulação
    parametros_simulacao = Column(JSON, default=dict, comment="Parâmetros específicos para simulação")
    
    # Metadados
    fonte = Column(String(100), comment="Fonte dos dados")
    confiabilidade = Column(String(20), default="medium")  # high, medium, low
    observacoes = Column(Text, comment="Observações adicionais")
    
    # Controle temporal
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<MaterialProperties(nome='{self.nome}', categoria='{self.categoria}')>"

# ========== MODELO DE ANÁLISE COMPARATIVA ==========

class SimulationComparison(Base):
    """
    Comparações entre simulações diferentes
    """
    __tablename__ = "simulation_comparisons"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(200), nullable=False, comment="Nome da comparação")
    descricao = Column(Text, comment="Descrição da análise")
    
    # Simulações envolvidas
    simulation_ids = Column(JSON, nullable=False, comment="Lista de IDs das simulações")
    
    # Resultados da comparação
    metrics_comparison = Column(JSON, comment="Comparação de métricas")
    ranking = Column(JSON, comment="Ranking das simulações")
    trends = Column(JSON, comment="Tendências identificadas")
    
    # Conclusões
    best_simulation_id = Column(UUID(as_uuid=True), ForeignKey("simulations.id"))
    conclusions = Column(JSON, default=list, comment="Conclusões da análise")
    recommendations = Column(JSON, default=list, comment="Recomendações")
    
    # Controle
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False)
    
    # Temporal
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    user = relationship("User")
    best_simulation = relationship("Simulation")
    
    def __repr__(self):
        return f"<SimulationComparison(nome='{self.nome}')>"

# ========== FUNÇÕES AUXILIARES ==========

def get_default_templates():
    """Obter templates padrão do sistema"""
    return [
        {
            "nome": "Teste de Queda - Rápido",
            "descricao": "Simulação básica de queda com 5 testes de 1m",
            "tipo_simulacao": "drop_test",
            "category": "basic",
            "parametros_padrao": {
                "drop_height": 1.0,
                "num_drops": 5,
                "gravity": -9.8
            },
            "is_default": True,
            "is_public": True
        },
        {
            "nome": "Teste de Queda - Completo",
            "descricao": "Análise completa de resistência com múltiplas alturas",
            "tipo_simulacao": "drop_test",
            "category": "comprehensive",
            "parametros_padrao": {
                "drop_height": 2.0,
                "num_drops": 10,
                "gravity": -9.8,
                "surface_type": "concrete"
            },
            "is_default": True,
            "is_public": True
        },
        {
            "nome": "Teste de Stress - Mecânico",
            "descricao": "Teste de resistência mecânica padrão",
            "tipo_simulacao": "stress_test",
            "category": "mechanical",
            "parametros_padrao": {
                "max_force": 1000,
                "force_increment": 100,
                "force_direction": [0, 0, 1],
                "test_duration": 5
            },
            "is_default": True,
            "is_public": True
        }
    ]

def get_default_materials():
    """Obter propriedades padrão de materiais"""
    return [
        {
            "nome": "PLA",
            "categoria": "plastic",
            "densidade": 1.24,
            "modulo_young": 3.5,
            "coeficiente_poisson": 0.33,
            "resistencia_tracao": 60.0,
            "resistencia_compressao": 80.0,
            "limite_escoamento": 45.0,
            "temperatura_filamento": 200.0,
            "temperatura_cama": 60.0,
            "velocidade_impressao": 50.0,
            "confiabilidade": "high"
        },
        {
            "nome": "ABS",
            "categoria": "plastic",
            "densidade": 1.04,
            "modulo_young": 2.2,
            "coeficiente_poisson": 0.35,
            "resistencia_tracao": 40.0,
            "resistencia_compressao": 65.0,
            "limite_escoamento": 35.0,
            "temperatura_filamento": 240.0,
            "temperatura_cama": 90.0,
            "velocidade_impressao": 40.0,
            "confiabilidade": "high"
        }
    ]