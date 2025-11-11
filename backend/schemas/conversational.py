"""
Schemas para conversação com IA
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field

class ConversationCreate(BaseModel):
    """Schema para criar conversa"""
    project_id: Optional[UUID] = None
    context: Optional[Dict[str, Any]] = None

class ConversationResponse(BaseModel):
    """Schema para resposta de conversa"""
    id: UUID
    user_id: UUID
    project_id: Optional[UUID]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    minimax_conversation_id: Optional[str] = None
    
    class Config:
        orm_mode = True

class MessageCreate(BaseModel):
    """Schema para criar mensagem"""
    content: str = Field(..., min_length=1, max_length=2000)
    metadata: Optional[Dict[str, Any]] = None

class MessageResponse(BaseModel):
    """Schema para resposta de mensagem"""
    id: UUID
    role: str
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    extracted_specs: Optional[Dict[str, Any]] = None
    
    class Config:
        orm_mode = True

class SpecExtractionResponse(BaseModel):
    """Schema para resposta de extração de especificações"""
    conversation_id: UUID
    specifications: Dict[str, Any]
    extracted_at: datetime