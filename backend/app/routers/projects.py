"""
3dPot Backend - Rotas de Gerenciamento de Projetos
Sistema de Prototipagem Sob Demanda
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel, Field
from loguru import logger

from ..database import get_db
from ..models.user import User
from ..models.project import Project, ProjectStatus, ProjectType, ProjectPriority

router = APIRouter()


class ProjectCreate(BaseModel):
    """Schema para criação de projeto"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    project_type: str = Field(default="prototype")
    priority: str = Field(default="medium")
    deadline: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    budget: Optional[float] = None
    filament_type: Optional[str] = None


class ProjectUpdate(BaseModel):
    """Schema para atualização de projeto"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    project_type: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    deadline: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    budget: Optional[float] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    filament_type: Optional[str] = None
    filament_weight_start: Optional[float] = None
    filament_weight_end: Optional[float] = None


class ProjectResponse(BaseModel):
    """Schema para resposta de projeto"""
    id: int
    name: str
    description: Optional[str]
    project_type: str
    priority: str
    status: str
    owner_id: int
    progress_percentage: int
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    deadline: Optional[datetime]
    budget: Optional[float]
    estimated_hours: Optional[float]
    actual_hours: float
    filament_type: Optional[str]
    filament_weight_start: Optional[float]
    filament_weight_end: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    project_type: Optional[str] = Query(None),
    owner_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Lista projetos com filtros opcionais"""
    try:
        query = select(Project)
        
        if status:
            query = query.where(Project.status == status)
        
        if project_type:
            query = query.where(Project.project_type == project_type)
        
        if owner_id:
            query = query.where(Project.owner_id == owner_id)
        
        query = query.order_by(Project.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        projects = result.scalars().all()
        
        return projects
        
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list projects"
        )


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(lambda: None),  # Opcional por enquanto
    db: AsyncSession = Depends(get_db)
):
    """Cria um novo projeto"""
    try:
        db_project = Project(
            name=project_data.name,
            description=project_data.description,
            project_type=project_data.project_type,
            priority=project_data.priority,
            deadline=project_data.deadline,
            estimated_hours=project_data.estimated_hours,
            budget=project_data.budget,
            filament_type=project_data.filament_type,
            owner_id=current_user.id if current_user else 1,  # Usuário padrão
            status=ProjectStatus.DRAFT.value,
            progress_percentage=0
        )
        
        db.add(db_project)
        await db.commit()
        await db.refresh(db_project)
        
        logger.info(f"Project created: {db_project.name}")
        
        return db_project
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project"
        )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Retorna detalhes de um projeto"""
    try:
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        return project
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get project"
        )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_data: ProjectUpdate,
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Atualiza um projeto"""
    try:
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Aplicar atualizações
        update_data = project_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(project, field, value)
        
        project.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(project)
        
        logger.info(f"Project updated: {project.name}")
        
        return project
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update project"
        )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Remove um projeto"""
    try:
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        await db.delete(project)
        await db.commit()
        
        logger.info(f"Project deleted: {project.name}")
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project"
        )
