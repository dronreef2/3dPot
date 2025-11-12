"""
3D Model Database Models
Sprint 4-5: Complete 3D Model Generation with NVIDIA NIM
"""

from sqlalchemy import Column, String, DateTime, JSON, Float, Integer, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Model3D(Base):
    """3D Model database model"""
    __tablename__ = "models_3d"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    spec_id = Column(String, nullable=True)  # Reference to specification that generated this model
    
    # Model data
    geometries = Column(JSON, nullable=False)  # List of geometry objects
    materials = Column(JSON, nullable=False)   # List of material objects
    settings = Column(JSON, nullable=False)    # Model settings
    
    # Metadata
    metadata = Column(JSON, nullable=False)    # Processing metadata
    
    # Status
    status = Column(String, default="active")  # active, deleted, archived
    is_public = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # File references
    file_path = Column(String, nullable=True)  # Path to exported file
    preview_path = Column(String, nullable=True)  # Path to preview image
    
    # Processing status
    processing_status = Column(String, default="completed")  # pending, processing, completed, failed
    processing_progress = Column(Integer, default=100)  # 0-100
    processing_error = Column(Text, nullable=True)
    
    # AI Generation data
    nvidia_nim_request_id = Column(String, nullable=True)
    generation_options = Column(JSON, nullable=True)
    
    # Relationships
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    session_id = Column(String, ForeignKey("conversation_sessions.id"), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    session = relationship("ConversationSession", foreign_keys=[session_id])
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "spec_id": self.spec_id,
            "geometries": self.geometries,
            "materials": self.materials,
            "settings": self.settings,
            "metadata": self.metadata,
            "status": self.status,
            "is_public": self.is_public,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "file_path": self.file_path,
            "preview_path": self.preview_path,
            "processing_status": self.processing_status,
            "processing_progress": self.processing_progress,
            "processing_error": self.processing_error,
            "nvidia_nim_request_id": self.nvidia_nim_request_id,
            "generation_options": self.generation_options,
            "user_id": self.user_id,
            "session_id": self.session_id
        }
    
    @classmethod
    def from_generation_response(cls, response_data: dict):
        """Create model from generation response"""
        model_data = response_data.get("model", {})
        
        return cls(
            id=model_data.get("id"),
            name=model_data.get("name", "Generated Model"),
            description=model_data.get("description", "AI-generated 3D model"),
            spec_id=model_data.get("spec_id"),
            geometries=model_data.get("geometries", []),
            materials=model_data.get("materials", []),
            settings=model_data.get("settings", {}),
            metadata=model_data.get("metadata", {}),
            processing_status="completed",
            processing_progress=100,
            nvidia_nim_request_id=response_data.get("nvidia_nim_request_id"),
            generation_options=response_data.get("options", {})
        )

class ModelGenerationJob(Base):
    """3D Model generation job tracking"""
    __tablename__ = "model_generation_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    model_id = Column(String, ForeignKey("models_3d.id"), nullable=True)
    
    # Job details
    specifications = Column(JSON, nullable=False)
    settings = Column(JSON, nullable=True)
    options = Column(JSON, nullable=True)
    
    # Status
    status = Column(String, default="pending")  # pending, processing, completed, failed, cancelled
    progress = Column(Integer, default=0)  # 0-100
    current_stage = Column(String, default="initializing")
    message = Column(String, default="")
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # seconds
    
    # Results
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    warnings = Column(JSON, nullable=True)
    
    # Processing details
    nvidia_nim_tokens_used = Column(Integer, default=0)
    processing_time = Column(Float, default=0.0)
    memory_usage = Column(Float, nullable=True)
    cpu_usage = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    
    def to_dict(self):
        """Convert job to dictionary"""
        return {
            "id": self.id,
            "model_id": self.model_id,
            "specifications": self.specifications,
            "settings": self.settings,
            "options": self.options,
            "status": self.status,
            "progress": self.progress,
            "current_stage": self.current_stage,
            "message": self.message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "estimated_duration": self.estimated_duration,
            "result": self.result,
            "error_message": self.error_message,
            "warnings": self.warnings,
            "nvidia_nim_tokens_used": self.nvidia_nim_tokens_used,
            "processing_time": self.processing_time,
            "memory_usage": self.memory_usage,
            "cpu_usage": self.cpu_usage,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "user_id": self.user_id
        }

class ModelExport(BaseModel):
    """3D Model export tracking"""
    __tablename__ = "model_exports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    model_id = Column(String, ForeignKey("models_3d.id"), nullable=False)
    
    # Export details
    format = Column(String, nullable=False)  # obj, stl, gltf, objmtl, ply
    options = Column(JSON, nullable=True)
    
    # File information
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)
    file_hash = Column(String, nullable=True)
    
    # Status
    status = Column(String, default="pending")  # pending, processing, completed, failed
    progress = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    # Download tracking
    download_count = Column(Integer, default=0)
    last_downloaded_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert export to dictionary"""
        return {
            "id": self.id,
            "model_id": self.model_id,
            "format": self.format,
            "options": self.options,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "file_hash": self.file_hash,
            "status": self.status,
            "progress": self.progress,
            "error_message": self.error_message,
            "download_count": self.download_count,
            "last_downloaded_at": self.last_downloaded_at.isoformat() if self.last_downloaded_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class ModelTemplate(Base):
    """Predefined 3D model templates"""
    __tablename__ = "model_templates"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    
    # Template data
    template_data = Column(JSON, nullable=False)  # Predefined specifications
    
    # Metadata
    category = Column(String, nullable=True)  # container, electronics, furniture, etc.
    difficulty_level = Column(String, default="beginner")  # beginner, intermediate, advanced
    estimated_vertices = Column(Integer, default=0)
    estimated_faces = Column(Integer, default=0)
    
    # Usage statistics
    usage_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert template to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "template_data": self.template_data,
            "category": self.category,
            "difficulty_level": self.difficulty_level,
            "estimated_vertices": self.estimated_vertices,
            "estimated_faces": self.estimated_faces,
            "usage_count": self.usage_count,
            "rating": self.rating,
            "rating_count": self.rating_count,
            "is_active": self.is_active,
            "is_featured": self.is_featured,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }