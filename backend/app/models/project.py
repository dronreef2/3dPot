"""
3dPot Backend - Modelo de Projeto
Sistema de Prototipagem Sob Demanda
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum as PyEnum
from sqlalchemy import String, Boolean, DateTime, Integer, Float, Text, Column, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class ProjectStatus(PyEnum):
    """Status do projeto"""
    DRAFT = "draft"           # Rascunho
    PLANNING = "planning"     # Planejamento
    IN_PROGRESS = "in_progress"  # Em andamento
    TESTING = "testing"       # Testando
    COMPLETED = "completed"   # Concluído
    ON_HOLD = "on_hold"       # Pausado
    CANCELLED = "cancelled"   # Cancelado


class ProjectPriority(PyEnum):
    """Prioridade do projeto"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ProjectType(PyEnum):
    """Tipo de projeto"""
    PROTOTYPE = "prototype"
    PRODUCTION = "production"
    RESEARCH = "research"
    EDUCATION = "education"
    COMMERCIAL = "commercial"


class Project(Base):
    """Modelo de Projeto para organização de trabalhos"""
    __tablename__ = "projects"
    
    # === PRIMARY KEYS ===
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # === PROJECT INFO ===
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    project_type = Column(String(50), default=ProjectType.PROTOTYPE.value, nullable=False)
    priority = Column(String(20), default=ProjectPriority.MEDIUM.value, nullable=False)
    status = Column(String(20), default=ProjectStatus.DRAFT.value, nullable=False)
    
    # === OWNER & TEAM ===
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    team_members = Column(JSON, nullable=True)  # Lista de IDs dos membros da equipe
    
    # === DATES ===
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)
    
    # === BUDGET & RESOURCES ===
    budget = Column(Float, nullable=True)
    currency = Column(String(10), default="BRL", nullable=False)
    estimated_hours = Column(Float, nullable=True)
    actual_hours = Column(Float, default=0.0, nullable=False)
    
    # === SPECIFICATIONS ===
    requirements = Column(Text, nullable=True)
    specifications = Column(JSON, nullable=True)
    technical_details = Column(JSON, nullable=True)
    materials_needed = Column(JSON, nullable=True)
    
    # === 3D MODELING ===
    model_files = Column(JSON, nullable=True)  # Lista de arquivos de modelo
    renderings = Column(JSON, nullable=True)   # Lista de renderizações
    simulation_results = Column(JSON, nullable=True)  # Resultados de simulação
    print_settings = Column(JSON, nullable=True)  # Configurações de impressão
    
    # === FILAMENT TRACKING ===
    filament_type = Column(String(100), nullable=True)
    filament_color = Column(String(50), nullable=True)
    filament_weight_start = Column(Float, nullable=True)  # Peso inicial em g
    filament_weight_end = Column(Float, nullable=True)    # Peso final em g
    filament_cost = Column(Float, nullable=True)          # Custo total
    
    # === PRINTING INFO ===
    print_time_estimated = Column(Integer, nullable=True)  # Tempo estimado em minutos
    print_time_actual = Column(Integer, nullable=True)     # Tempo real em minutos
    print_temperature = Column(Integer, nullable=True)     # Temperatura em °C
    print_bed_temperature = Column(Integer, nullable=True) # Temperatura da mesa em °C
    print_speed = Column(Integer, nullable=True)           # Velocidade em mm/s
    layer_height = Column(Float, nullable=True)            # Altura da camada em mm
    
    # === QUALITY CONTROL ===
    quality_score = Column(Float, nullable=True)  # Pontuação de qualidade 0-10
    quality_issues = Column(JSON, nullable=True)  # Lista de problemas de qualidade
    inspection_results = Column(JSON, nullable=True)  # Resultados de inspeção
    
    # === FILES & ATTACHMENTS ===
    attachments = Column(JSON, nullable=True)     # Lista de arquivos anexos
    documentation = Column(JSON, nullable=True)   # Documentação do projeto
    notes = Column(Text, nullable=True)           # Observações gerais
    
    # === TAGS & CATEGORIES ===
    tags = Column(JSON, nullable=True)            # Tags para organização
    category = Column(String(100), nullable=True) # Categoria do projeto
    
    # === PROGRESS ===
    progress_percentage = Column(Integer, default=0, nullable=False)  # 0-100%
    completion_criteria = Column(JSON, nullable=True)  # Critérios de conclusão
    
    # === METADATA ===
    is_public = Column(Boolean, default=False, nullable=False)
    is_template = Column(Boolean, default=False, nullable=False)
    version = Column(String(20), default="1.0", nullable=False)
    
    # === TIMESTAMPS ===
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # === RELATIONSHIPS ===
    owner = relationship("User", back_populates="projects")
    sensor_data = relationship("SensorData", back_populates="project")
    alerts = relationship("Alert", back_populates="project")
    
    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status}', progress={self.progress_percentage}%)>"
    
    def is_active(self) -> bool:
        """Retorna True se o projeto está ativo"""
        return self.status in [
            ProjectStatus.PLANNING.value,
            ProjectStatus.IN_PROGRESS.value,
            ProjectStatus.TESTING.value
        ]
    
    def is_completed(self) -> bool:
        """Retorna True se o projeto foi concluído"""
        return self.status == ProjectStatus.COMPLETED.value
    
    def is_overdue(self) -> bool:
        """Retorna True se o projeto está atrasado"""
        if not self.deadline:
            return False
        return datetime.utcnow() > self.deadline.replace(tzinfo=None)
    
    def get_days_remaining(self) -> Optional[int]:
        """Retorna dias restantes até o deadline"""
        if not self.deadline:
            return None
        delta = self.deadline.replace(tzinfo=None) - datetime.utcnow()
        return max(0, delta.days)
    
    def get_filament_used(self) -> Optional[float]:
        """Calcula o filamento usado baseado no peso inicial e final"""
        if not self.filament_weight_start or not self.filament_weight_end:
            return None
        return max(0, self.filament_weight_start - self.filament_weight_end)
    
    def get_filament_cost_per_gram(self) -> Optional[float]:
        """Calcula o custo por grama de filamento"""
        used = self.get_filament_used()
        if not used or not self.filament_cost:
            return None
        return self.filament_cost / used
    
    def calculate_efficiency(self) -> Optional[float]:
        """Calcula a eficiência do projeto (tempo real vs estimado)"""
        if not self.print_time_estimated or not self.print_time_actual:
            return None
        if self.print_time_estimated == 0:
            return 100.0
        return min(100.0, (self.print_time_estimated / self.print_time_actual) * 100)
    
    def update_progress(self, new_progress: int):
        """Atualiza o progresso do projeto"""
        self.progress_percentage = max(0, min(100, new_progress))
        
        # Auto-atualizar status baseado no progresso
        if self.progress_percentage == 100:
            self.status = ProjectStatus.COMPLETED.value
        elif self.progress_percentage > 0 and self.status == ProjectStatus.DRAFT.value:
            self.status = ProjectStatus.IN_PROGRESS.value
    
    def add_team_member(self, user_id: int):
        """Adiciona um membro à equipe"""
        if not self.team_members:
            self.team_members = []
        if user_id not in self.team_members:
            self.team_members.append(user_id)
    
    def remove_team_member(self, user_id: int):
        """Remove um membro da equipe"""
        if self.team_members and user_id in self.team_members:
            self.team_members.remove(user_id)
    
    def add_file(self, file_path: str, file_type: str = "model"):
        """Adiciona um arquivo ao projeto"""
        if not self.model_files:
            self.model_files = []
        self.model_files.append({
            "path": file_path,
            "type": file_type,
            "uploaded_at": datetime.utcnow().isoformat()
        })
    
    def add_tag(self, tag: str):
        """Adiciona uma tag ao projeto"""
        if not self.tags:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o projeto para dicionário"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "project_type": self.project_type,
            "priority": self.priority,
            "status": self.status,
            "owner_id": self.owner_id,
            "progress_percentage": self.progress_percentage,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "budget": self.budget,
            "estimated_hours": self.estimated_hours,
            "actual_hours": self.actual_hours,
            "filament_used": self.get_filament_used(),
            "efficiency": self.calculate_efficiency(),
            "is_overdue": self.is_overdue(),
            "days_remaining": self.get_days_remaining(),
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def create_prototype_project(
        cls,
        name: str,
        owner_id: int,
        description: str = None,
        filament_type: str = None
    ) -> "Project":
        """Helper para criar um projeto de protótipo"""
        return cls(
            name=name,
            description=description,
            project_type=ProjectType.PROTOTYPE.value,
            owner_id=owner_id,
            filament_type=filament_type,
            status=ProjectStatus.DRAFT.value,
            priority=ProjectPriority.MEDIUM.value
        )
    
    class Config:
        from_attributes = True


# Índices para otimização
Index('idx_projects_owner_status', Project.owner_id, Project.status)
Index('idx_projects_priority_status', Project.priority, Project.status)
Index('idx_projects_deadline', Project.deadline)
Index('idx_projects_created_at', Project.created_at)
Index('idx_projects_tags', Project.tags)
Index('idx_projects_active', Project.status)
