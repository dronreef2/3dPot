"""
Database Models for 3D Pot Platform
Unified model definitions for all database entities
"""

from sqlalchemy import Column, String, DateTime, Integer, Boolean, Text, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    """User model for authentication and data association"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    
    # Profile
    full_name = Column(String, nullable=True)
    company = Column(String, nullable=True)
    role = Column(String, default="user")
    
    # Preferences
    preferred_language = Column(String, default="pt-BR")
    theme = Column(String, default="light")
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)

class ConversationSession(Base):
    """Chat session model for AI conversations"""
    __tablename__ = "conversation_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=True)
    
    # Status
    status = Column(String, default="active")  # active, archived, deleted
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    
    # User association
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")

class Message(Base):
    """Individual message in a conversation"""
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    
    # AI metadata
    confidence_score = Column(Float, nullable=True)
    tokens_used = Column(Integer, default=0)
    processing_time = Column(Float, nullable=True)
    
    # Content metadata
    has_attachments = Column(Boolean, default=False)
    attachment_count = Column(Integer, default=0)
    
    # Status
    is_deleted = Column(Boolean, default=False)
    is_edited = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session_id = Column(String, ForeignKey("conversation_sessions.id"), nullable=False)
    session = relationship("ConversationSession", back_populates="messages")
    
    # Extracted data
    extracted_specs = Column(JSON, nullable=True)

# Import 3D Models
from .models_3d import Model3D, ModelGenerationJob, ModelExport, ModelTemplate

# Export all models
__all__ = [
    'User',
    'ConversationSession', 
    'Message',
    'Model3D',
    'ModelGenerationJob',
    'ModelExport',
    'ModelTemplate'
]