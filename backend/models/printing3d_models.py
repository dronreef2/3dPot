"""
Modelos SQLAlchemy - 3D Printing Suite (Sprint 6+)
=================================================

Modelos para gerenciamento de impressão 3D, incluindo:
- Tarefas de impressão (PrintJob)
- Configuração de impressoras (Printer)
- Perfis de materiais (Material)
- Fila de impressão (PrintQueue)

Autor: MiniMax Agent
Data: 2025-11-13
Versão: 2.0.0 - Sprint 6+
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import uuid4, UUID
from decimal import Decimal

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey, Integer, 
    JSON, Numeric, String, Text, Float, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from . import Base


class Printer(Base):
    """Configurações de impressoras 3D"""
    __tablename__ = "printers"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Informações básicas
    nome = Column(String(100), nullable=False)
    marca = Column(String(50), nullable=False)
    modelo = Column(String(50), nullable=False)
    tipo_impressora = Column(Enum('fdm', 'sla', 'sls', 'bjm', 'mjf', name='printer_type'), 
                            nullable=False)
    
    # Configurações técnicas
    volume_impressao_x = Column(Float, nullable=False)  # mm
    volume_impressao_y = Column(Float, nullable=False)  # mm
    volume_impressao_z = Column(Float, nullable=False)  # mm
    
    temperatura_bico_max = Column(Integer, nullable=False)
    temperatura_bico_min = Column(Integer, nullable=False)
    temperatura_mesa_max = Column(Integer, nullable=False)
    temperatura_mesa_min = Column(Integer, nullable=False)
    
    # Configurações de qualidade
    resolucao_camada_padrao = Column(Float, default=0.2)  # mm
    velocidade_impressao_padrao = Column(Integer, default=50)  # mm/s
    velocidade_viagem_padrao = Column(Integer, default=150)  # mm/s
    
    # Material suportado
    materiais_compatíveis = Column(JSON, default=list)  # Lista de material_ids
    
    # Status e disponibilidade
    status = Column(Enum('available', 'printing', 'maintenance', 'offline', name='printer_status'), 
                   default='available')
    esta_conectado = Column(Boolean, default=False)
    conectado_em = Column(DateTime, nullable=True)
    ultimo_sinal_vida = Column(DateTime, nullable=True)
    
    # Configurações de rede (opcional)
    endereco_ip = Column(String(45), nullable=True)
    porta_api = Column(Integer, nullable=True)
    endpoint_websocket = Column(String(200), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="printers")
    print_jobs = relationship("PrintJob", back_populates="printer")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'nome', name='uq_printer_user_name'),
    )


class Material(Base):
    """Catálogo de materiais para impressão 3D"""
    __tablename__ = "materials"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Informações básicas
    nome = Column(String(100), nullable=False)
    categoria = Column(Enum('pla', 'abs', 'petg', 'asa', 'nylon', 'tpu', 
                           'epoxy', 'resina', 'metal', name='material_category'), 
                      nullable=False)
    fabricante = Column(String(50), nullable=False)
    codigo_produto = Column(String(100), nullable=True)
    
    # Propriedades físicas
    temperatura_bico_recomendada = Column(Integer, nullable=False)
    temperatura_mesa_recomendada = Column(Integer, nullable=False)
    velocidade_impressao_recomendada = Column(Integer, default=50)  # mm/s
    
    # Características técnicas
    densidade = Column(Float, nullable=False)  # g/cm³
    modulo_elasticidade = Column(Float, nullable=True)  # MPa
    resistencia_tracao = Column(Float, nullable=True)  # MPa
    temperatura_transicao_vidrosa = Column(Float, nullable=True)  # °C
    temperatura_maxima_uso = Column(Float, nullable=True)  # °C
    
    # Configurações avançadas
    retração_ativada = Column(Boolean, default=True)
    distancia_retração = Column(Float, default=4.0)  # mm
    velocidade_retração = Column(Integer, default=25)  # mm/s
    ventilador_camadas_suporte = Column(Float, default=100)  # %
    ventilador_camadas_normais = Column(Float, default=50)  # %
    
    # Configurações de impressão
    suportes_necessarios = Column(Boolean, default=False)
    bridge_suporte = Column(Boolean, default=True)
    raio_minimo_curvatura = Column(Float, default=0.5)  # mm
    altura_camada_minima = Column(Float, default=0.1)  # mm
    altura_camada_maxima = Column(Float, default=0.3)  # mm
    percentual_preenchimento_padrao = Column(Float, default=20)  # %
    
    # Custo e disponibilidade
    preco_por_kg = Column(Numeric(10, 2), nullable=False)
    estoque_disponivel = Column(Boolean, default=False)
    ativo = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    print_jobs = relationship("PrintJob", back_populates="material")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('nome', 'fabricante', 'codigo_produto', name='uq_material_unique'),
    )


class PrintJob(Base):
    """Tarefas de impressão 3D"""
    __tablename__ = "print_jobs"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Relacionamentos
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(PGUUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    printer_id = Column(PGUUID(as_uuid=True), ForeignKey("printers.id"), nullable=False)
    material_id = Column(PGUUID(as_uuid=True), ForeignKey("materials.id"), nullable=False)
    
    # Informações do job
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    arquivo_modelo = Column(String(500), nullable=False)  # Caminho para arquivo 3D
    arquivo_gcode = Column(String(500), nullable=True)   # Caminho para G-code gerado
    
    # Configurações de impressão
    altura_camada = Column(Float, default=0.2)  # mm
    percentual_preenchimento = Column(Float, default=20)  # %
    velocidade_impressao = Column(Integer, default=50)  # mm/s
    temperatura_bico = Column(Integer, nullable=True)
    temperatura_mesa = Column(Integer, nullable=True)
    
    # Suportes e estruturas
    suportes_suporte = Column(Enum('none', 'tree', 'lines', 'grid', name='support_type'), 
                             default='none')
    paredes_duplas = Column(Boolean, default=True)
    velocidade_ventilador = Column(Float, default=50)  # %
    
    # Métricas do job
    tempo_estimado_segundos = Column(Integer, nullable=True)
    tempo_real_segundos = Column(Integer, nullable=True)
    peso_material_g = Column(Float, nullable=True)
    custo_material = Column(Numeric(10, 2), nullable=True)
    consumo_energia_kwh = Column(Float, nullable=True)
    
    # Dimensões e volume
    dimensao_x = Column(Float, nullable=True)
    dimensao_y = Column(Float, nullable=True)
    dimensao_z = Column(Float, nullable=True)
    volume_impressao_cm3 = Column(Float, nullable=True)
    
    # Status do job
    status = Column(Enum('pending', 'queueing', 'preparing', 'printing', 'paused', 
                        'completed', 'failed', 'cancelled', 'maintenance', name='print_job_status'),
                   default='pending')
    
    # Progresso
    progresso_percentual = Column(Integer, default=0)
    camadas_totais = Column(Integer, nullable=True)
    camada_atual = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    paused_at = Column(DateTime, nullable=True)
    resumed_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    
    # Logs e erros
    log_impressao = Column(Text, nullable=True)
    error_log = Column(Text, nullable=True)
    warnings = Column(JSON, default=list)
    
    # Prioridade e fila
    prioridade = Column(Enum('low', 'normal', 'high', 'urgent', name='job_priority'), 
                       default='normal')
    fila_posicao = Column(Integer, nullable=True)
    
    # Resultados
    rating_qualidade = Column(Integer, nullable=True)  # 1-5 estrelas
    comentarios = Column(Text, nullable=True)
    reincidencia_preferida = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", backref="print_jobs")
    project = relationship("Project", backref="print_jobs")
    printer = relationship("Printer", back_populates="print_jobs")
    material = relationship("Material", back_populates="print_jobs")
    
    # Status helpers
    @property
    def is_active(self) -> bool:
        """Verifica se o job está ativo (imprimindo ou em pausa)"""
        return self.status in ['printing', 'paused']
    
    @property
    def is_completed(self) -> bool:
        """Verifica se o job foi concluído com sucesso"""
        return self.status == 'completed'
    
    @property
    def is_failed(self) -> bool:
        """Verifica se o job falhou"""
        return self.status == 'failed'


class PrintQueue(Base):
    """Fila de impressão para organizar jobs"""
    __tablename__ = "print_queue"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    printer_id = Column(PGUUID(as_uuid=True), ForeignKey("printers.id"), nullable=False)
    print_job_id = Column(PGUUID(as_uuid=True), ForeignKey("print_jobs.id"), nullable=False)
    
    # Posição na fila
    posicao = Column(Integer, nullable=False)
    
    # Configurações da fila
    estimado_inicio = Column(DateTime, nullable=True)
    estimado_conclusao = Column(DateTime, nullable=True)
    
    # Status
    status = Column(Enum('queued', 'processing', 'paused', 'cancelled', name='queue_status'), 
                   default='queued')
    
    # Configurações de execução automática
    auto_start = Column(Boolean, default=False)
    start_after = Column(DateTime, nullable=True)  # Início programado
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    printer = relationship("Printer", backref="print_queue")
    print_job = relationship("PrintJob", backref="print_queue_item")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('printer_id', 'posicao', name='uq_queue_position'),
    )


class PrintSettings(Base):
    """Configurações personalizadas de impressão"""
    __tablename__ = "print_settings"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    printer_id = Column(PGUUID(as_uuid=True), ForeignKey("printers.id"), nullable=True)
    material_id = Column(PGUUID(as_uuid=True), ForeignKey("materials.id"), nullable=True)
    
    # Nome das configurações
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    tipo_configuracao = Column(Enum('personal', 'shared', 'public', name='config_type'), 
                              default='personal')
    
    # Configurações técnicas
    configuracoes = Column(JSON, default=dict)  # Configurações detalhadas em JSON
    
    # Métricas de sucesso
    jobs_sucesso = Column(Integer, default=0)
    taxa_sucesso = Column(Float, default=100)  # %
    
    # Status
    ativo = Column(Boolean, default=True)
    favorites = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="print_settings")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'nome', name='uq_settings_user_name'),
    )


class PrintJobLog(Base):
    """Logs detalhados de impressão"""
    __tablename__ = "print_job_logs"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    print_job_id = Column(PGUUID(as_uuid=True), ForeignKey("print_jobs.id"), nullable=False)
    
    # Informações do log
    tipo_log = Column(Enum('info', 'warning', 'error', 'progress', name='log_type'), 
                     nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Contexto adicional
    camada_atual = Column(Integer, nullable=True)
    temperatura_bico = Column(Float, nullable=True)
    temperatura_mesa = Column(Float, nullable=True)
    posicao_z = Column(Float, nullable=True)
    
    # Dados técnicos
    dados_tecnicos = Column(JSON, default=dict)
    
    # Relationships
    print_job = relationship("PrintJob", backref="detailed_logs")
    
    # Indexes para performance
    __table_args__ = (
        {'extend_existing': True},
    )