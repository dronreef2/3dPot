"""
Rotas para conversação com IA
API para interação com Minimax M2
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_db
from middleware.auth import get_current_user
from models import User, Conversation, ConversationMessage
from schemas import (
    ConversationCreate,
    ConversationalResponse,
    ConversationMessageCreate,
    ConversationMessage,
    APIResponse
)
from services.minimax_service import MinimaxService

router = APIRouter(prefix="/conversational", tags=["conversational"])

@router.post("/conversations", response_model=ConversationalResponse)
async def create_conversation(
    conversation: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar nova conversa"""
    # Criar conversa no banco
    db_conversation = Conversation(
        user_id=current_user.id,
        project_id=conversation.project_id,
        status="active"
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    
    # Inicializar serviço Minimax
    minimax_service = MinimaxService()
    
    # Iniciar conversa no Minimax
    minimax_conversation = await minimax_service.start_conversation(
        user_id=current_user.id,
        project_id=conversation.project_id
    )
    
    return ConversationalResponse(
        id=db_conversation.id,
        user_id=current_user.id,
        project_id=conversation.project_id,
        status=db_conversation.status,
        created_at=db_conversation.created_at,
        minimax_conversation_id=minimax_conversation["id"]
    )

@router.get("/conversations", response_model=List[ConversationalResponse])
async def list_conversations(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar conversas do usuário"""
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        ConversationalResponse(
            id=c.id,
            user_id=c.user_id,
            project_id=c.project_id,
            status=c.status,
            created_at=c.created_at,
            updated_at=c.updated_at,
            completed_at=c.completed_at
        )
        for c in conversations
    ]

@router.get("/conversations/{conversation_id}", response_model=ConversationalResponse)
async def get_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter detalhes de uma conversa"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversa não encontrada"
        )
    
    return ConversationalResponse(
        id=conversation.id,
        user_id=conversation.user_id,
        project_id=conversation.project_id,
        status=conversation.status,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        completed_at=conversation.completed_at
    )

@router.get("/conversations/{conversation_id}/messages", response_model=List[ConversationMessage])
async def get_messages(
    conversation_id: UUID,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter mensagens de uma conversa"""
    # Verificar se a conversa existe e pertence ao usuário
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversa não encontrada"
        )
    
    # Obter mensagens
    messages = db.query(ConversationMessage).filter(
        ConversationMessage.conversation_id == conversation_id
    ).order_by(ConversationMessage.timestamp).offset(skip).limit(limit).all()
    
    return [
        ConversationMessage(
            id=m.id,
            role=m.role,
            content=m.content,
            timestamp=m.timestamp,
            metadata=m.metadata
        )
        for m in messages
    ]

@router.post("/conversations/{conversation_id}/messages", response_model=ConversationMessage)
async def send_message(
    conversation_id: UUID,
    message: ConversationMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enviar mensagem para a conversa"""
    # Verificar se a conversa existe e pertence ao usuário
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversa não encontrada"
        )
    
    # Obter histórico de mensagens
    messages = db.query(ConversationMessage).filter(
        ConversationMessage.conversation_id == conversation_id
    ).order_by(ConversationMessage.timestamp).all()
    
    # Preparar histórico para o Minimax
    conversation_history = [
        {
            "role": m.role,
            "content": m.content
        }
        for m in messages
    ]
    
    # Inicializar serviço Minimax
    minimax_service = MinimaxService()
    
    # Enviar mensagem para Minimax
    minimax_response = await minimax_service.send_message(
        message=message.content,
        conversation_history=conversation_history
    )
    
    # Salvar mensagem do usuário no banco
    user_message = ConversationMessage(
        conversation_id=conversation_id,
        role="user",
        content=message.content,
        timestamp=datetime.utcnow(),
        metadata={}
    )
    db.add(user_message)
    
    # Salvar resposta do assistente no banco
    assistant_message = ConversationMessage(
        conversation_id=conversation_id,
        role="assistant",
        content=minimax_response["content"],
        timestamp=datetime.utcnow(),
        metadata=minimax_response.get("usage", {})
    )
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)
    
    # Extrair especificações
    extracted_specs = minimax_service.extract_specifications(minimax_response["content"])
    
    # Atualizar conversa com especificações extraídas
    if not conversation.specs:
        conversation.specs = {}
    
    conversation.specs.update(extracted_specs)
    db.commit()
    
    return ConversationMessage(
        id=assistant_message.id,
        role="assistant",
        content=assistant_message.content,
        timestamp=assistant_message.timestamp,
        metadata=assistant_message.metadata,
        extracted_specs=extracted_specs
    )

@router.get("/conversations/{conversation_id}/extract-specs", response_model=APIResponse)
async def extract_specifications(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Extrair especificações completas da conversa"""
    # Verificar se a conversa existe e pertence ao usuário
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversa não encontrada"
        )
    
    # Obter todas as mensagens
    messages = db.query(ConversationMessage).filter(
        ConversationMessage.conversation_id == conversation_id
    ).order_by(ConversationMessage.timestamp).all()
    
    # Concatenar todas as respostas do assistente
    assistant_responses = [m.content for m in messages if m.role == "assistant"]
    combined_content = "\n\n".join(assistant_responses)
    
    # Extrair especificações do conteúdo combinado
    minimax_service = MinimaxService()
    extracted_specs = minimax_service.extract_specifications(combined_content)
    
    # Salvar especificações na conversa
    conversation.specs = extracted_specs
    db.commit()
    
    return APIResponse(
        success=True,
        message="Especificações extraídas com sucesso",
        data={
            "conversation_id": str(conversation_id),
            "specifications": extracted_specs,
            "extracted_at": datetime.utcnow()
        }
    )