# 3dPot v2.0 - Sprint 2: Integração Minimax M2 API

## 📋 Resumo do Sprint 2

O Sprint 2 focará na implementação da integração com a API do Minimax M2, permitindo que o sistema tenha conversação inteligente para extração de especificações de projetos. Este é um passo fundamental no desenvolvimento do sistema 3dPot v2.0.

## 🎯 Objetivos do Sprint

1. **Integração completa com Minimax M2**
   - Configurar serviço para comunicação com a API
   - Implementar endpoints para conversação
   - Desenvolver extração automática de especificações
   
2. **Interface Conversacional**
   - Implementar frontend React para chat
   - Conectar com backend via API
   - Adicionar recursos de clarificação
   
3. **Gerenciamento de Conversas**
   - Salvar histórico de conversas
   - Manter contexto durante conversação
   - Associar conversas a projetos
   
4. **Validação e Testes**
   - Testes unitários
   - Testes de integração
   - Documentação de API

## 📁 Estrutura de Arquivos

```
/workspace/backend/
├── services/
│   ├── conversational_service.py      # Serviço de conversação com IA
│   ├── minimax_service.py             # Nova implementação para Minimax
│   └── __init__.py
├── routes/
│   ├── __init__.py
│   └── conversational.py              # Rotas para conversação
├── models/
│   ├── __init__.py                    # Modelos Conversation e ConversationMessage
│   └── conversational.py              # Modelos adicionais (se necessário)
└── schemas/
    ├── __init__.py
    └── conversational.py              # Schemas para Pydantic

/workspace/frontend/
└── src/
    ├── components/
    │   ├── conversational/
    │   │   ├── ConversationalInterface.tsx
    │   │   └── ChatMessage.tsx
    │   └── shared/
    ├── services/
    │   └── api.ts                     # Cliente API para conversação
    └── store/
        └── conversationalStore.ts    # Estado para conversação
```

## 🗺️ Plano de Implementação

### 1. Configuração da API Minimax

#### 1.1 Verificar dependências

- Atualizar arquivo requirements.txt com as dependências necessárias
- Configurar variáveis de ambiente em .env.example

#### 1.2 Implementar serviço Minimax

- Criar serviço de interação com API Minimax
- Implementar método para iniciar conversa
- Implementar método para enviar mensagens
- Implementar resposta de fallback em caso de erro

### 2. Desenvolver endpoints de API

#### 2.1 Implementar rotas de conversação

- `/api/v1/conversations` - Listar conversas
- `/api/v1/conversations/{id}` - Obter conversa específica
- `/api/v1/conversations/{id}/messages` - Listar mensagens
- `/api/v1/conversations` - Criar nova conversa
- `/api/v1/conversations/{id}/messages` - Enviar mensagem
- `/api/v1/conversations/{id}/extract-specs` - Extrair especificações

#### 2.2 Atualizar main.py

- Registrar rotas de conversação
- Adicionar middleware de autenticação

### 3. Implementar frontend React

#### 3.1 Melhorar interface conversacional

- Implementar visualização de especificações extraídas
- Adicionar indicadores de progresso
- Implementar sistema de clarificação
- Adicionar capacidades de upload de imagens para contexto

#### 3.2 Conectar com API

- Implementar cliente para endpoints de conversação
- Implementar WebSocket para atualizações em tempo real (opcional)
- Adicionar tratamento de erros

### 4. Testes e validação

#### 4.1 Testes unitários

- Testar serviço Minimax
- Testar endpoints de API
- Testar extração de especificações

#### 4.2 Testes de integração

- Testar fluxo completo de conversação
- Testar extração de especificações
- Testar interface frontend

### 5. Documentação

- Documentar API endpoints
- Adicionar exemplos de uso
- Criar guia de configuração

## 🔧 Implementação Detalhada

### 1. Serviço Minimax (backend/services/minimax_service.py)

```python
"""
Serviço para interação com a API Minimax M2
Implementa conversação natural para extração de especificações
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

import httpx
from sqlalchemy.orm import Session

from ..core.config import MINIMAX_API_KEY, MINIMAX_BASE_URL, MINIMAX_MODEL

logger = logging.getLogger(__name__)

class MinimaxService:
    """Serviço para interação com API Minimax M2"""
    
    def __init__(self):
        self.api_key = MINIMAX_API_KEY
        self.base_url = MINIMAX_BASE_URL
        self.model = MINIMAX_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def start_conversation(self, user_id: UUID, project_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Iniciar uma nova conversa"""
        return {
            "id": str(uuid4()),
            "user_id": str(user_id),
            "project_id": str(project_id) if project_id else None,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "messages": []
        }
    
    async def send_message(self, message: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Enviar mensagem para a API Minimax e obter resposta
        
        Args:
            message: Mensagem do usuário
            conversation_history: Histórico da conversa
            
        Returns:
            Resposta da API
        """
        try:
            # Preparar histórico da conversa
            messages = conversation_history or []
            
            # Adicionar system prompt
            system_prompt = self._get_system_prompt()
            
            # Montar payload da API
            payload = {
                "model": self.model,
                "messages": [system_prompt] + messages + [{"role": "user", "content": message}],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            # Fazer chamada para API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/text/chatcompletion_pro",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Extrair resposta
                ai_response = data["choices"][0]["message"]["content"]
                
                return {
                    "success": True,
                    "content": ai_response,
                    "usage": data.get("usage", {})
                }
                
        except Exception as e:
            logger.error(f"Erro na API Minimax: {e}")
            # Resposta de fallback
            return {
                "success": False,
                "error": str(e),
                "content": await self._fallback_response(message)
            }
    
    def _get_system_prompt(self) -> Dict[str, str]:
        """Retornar prompt do sistema para Minimax"""
        return {
            "role": "system",
            "content": """Você é um assistente especializado em extrair especificações técnicas para projetos de prototipagem 3D. 

Sua função é:
1. Entender as necessidades do usuário através de conversação natural
2. Extrair especificações técnicas de forma incremental
3. Fazer perguntas de clarificação quando necessário
4. Organizar as informações coletadas em um formato estruturado

Formato de extração esperado:
{
  "projeto": {
    "categoria": "mecanico|eletronico|mixto|arquitetura",
    "dimensoes": {
      "largura": number,
      "altura": number,
      "profundidade": number,
      "unidade": "mm"
    },
    "material": "PLA|ABS|PETG|nylon|metal|composite",
    "componentes": [
      {
        "tipo": "sensor|atuador|microcontroller|display",
        "especificacao": "string",
        "quantidade": number
      }
    ],
    "funcionalidades": [
      {
        "nome": "string",
        "descricao": "string"
      }
    ],
    "restricoes": [
      {
        "tipo": "dimensional|mecanico|eletronico|custo",
        "descricao": "string"
      }
    ]
  },
  "clarificacoes_pendentes": ["pergunta1", "pergunta2"]
}

Seja direto, faça perguntas específicas e colete todas as informações necessárias para a prototipagem."""
        }
    
    async def _fallback_response(self, message: str) -> str:
        """Resposta de fallback quando API Minimax não está disponível"""
        return "Desculpe, houve um problema com o serviço de IA. Para prosseguir, forneça detalhes sobre: dimensões (largura x altura x profundidade), material desejado (PLA, ABS, metal), funcionalidades principais e quaisquer restrições."
    
    def extract_specifications(self, ai_response: str) -> Dict[str, Any]:
        """Extrair especificações do conteúdo da resposta da IA"""
        # Implementação básica - pode ser aprimorada com NLP mais avançado
        extracted = {
            "categoria": None,
            "dimensoes": {},
            "material": None,
            "componentes": [],
            "funcionalidades": [],
            "restricoes": []
        }
        
        # Detecção básica de padrões (melhorar com NLP mais avançado)
        if "mecânico" in ai_response.lower() or "mecanica" in ai_response.lower():
            extracted["categoria"] = "mecanico"
        elif "eletrônico" in ai_response.lower() or "eletronico" in ai_response.lower():
            extracted["categoria"] = "eletronico"
        elif "arquitetura" in ai_response.lower():
            extracted["categoria"] = "arquitetura"
        else:
            extracted["categoria"] = "mixto"
        
        # Detecção de materiais
        materiais = ["pla", "abs", "petg", "nylon", "metal", "alumínio", "aço"]
        for material in materiais:
            if material in ai_response.lower():
                extracted["material"] = material.upper()
                break
        
        return extracted
```

### 2. Rotas de API (backend/routes/conversational.py)

```python
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

from ..core.config import get_db
from ..middleware.auth import get_current_user
from ..models import User, Conversation, ConversationMessage
from ..schemas import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
    SpecExtractionResponse
)
from ..services.minimax_service import MinimaxService

router = APIRouter(prefix="/conversational", tags=["conversational"])

@router.post("/conversations", response_model=ConversationResponse)
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
    
    return ConversationResponse(
        id=db_conversation.id,
        user_id=current_user.id,
        project_id=conversation.project_id,
        status=db_conversation.status,
        created_at=db_conversation.created_at,
        minimax_conversation_id=minimax_conversation["id"]
    )

@router.get("/conversations", response_model=List[ConversationResponse])
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
        ConversationResponse(
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

@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
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
    
    return ConversationResponse(
        id=conversation.id,
        user_id=conversation.user_id,
        project_id=conversation.project_id,
        status=conversation.status,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        completed_at=conversation.completed_at
    )

@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
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
        MessageResponse(
            id=m.id,
            role=m.role,
            content=m.content,
            timestamp=m.timestamp,
            metadata=m.metadata
        )
        for m in messages
    ]

@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: UUID,
    message: MessageCreate,
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
    
    return MessageResponse(
        id=assistant_message.id,
        role="assistant",
        content=assistant_message.content,
        timestamp=assistant_message.timestamp,
        metadata=assistant_message.metadata,
        extracted_specs=extracted_specs
    )

@router.get("/conversations/{conversation_id}/extract-specs", response_model=SpecExtractionResponse)
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
    
    return SpecExtractionResponse(
        conversation_id=conversation_id,
        specifications=extracted_specs,
        extracted_at=datetime.utcnow()
    )
```

### 3. Schemas Pydantic (backend/schemas/conversational.py)

```python
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
```

### 4. Cliente API no Frontend (frontend/src/services/api.ts)

```typescript
/**
 * Cliente API para conversação
 * Implementa comunicação com backend para funcionalidades de IA conversacional
 */

import { apiClient } from './apiClient';
import { ConversationResponse, MessageResponse, SpecExtractionResponse, ConversationCreate, MessageCreate } from '../types/conversational';

// Criar nova conversa
export async function createConversation(projectId?: string): Promise<ConversationResponse> {
    const payload: ConversationCreate = {
        project_id: projectId ? undefined : undefined, // Ajuste conforme necessário
    };
    
    return apiClient.post<ConversationResponse>('/conversational/conversations', payload);
}

// Listar conversas do usuário
export async function listConversations(skip = 0, limit = 20): Promise<ConversationResponse[]> {
    return apiClient.get<ConversationResponse[]>(`/conversational/conversations?skip=${skip}&limit=${limit}`);
}

// Obter detalhes de uma conversa
export async function getConversation(conversationId: string): Promise<ConversationResponse> {
    return apiClient.get<ConversationResponse>(`/conversational/conversations/${conversationId}`);
}

// Obter mensagens de uma conversa
export async function getMessages(conversationId: string, skip = 0, limit = 50): Promise<MessageResponse[]> {
    return apiClient.get<MessageResponse[]>(`/conversational/conversations/${conversationId}/messages?skip=${skip}&limit=${limit}`);
}

// Enviar mensagem para conversa
export async function sendMessage(conversationId: string, content: string): Promise<MessageResponse> {
    const payload: MessageCreate = {
        content,
    };
    
    return apiClient.post<MessageResponse>(`/conversational/conversations/${conversationId}/messages`, payload);
}

// Extrair especificações de uma conversa
export async function extractSpecs(conversationId: string): Promise<SpecExtractionResponse> {
    return apiClient.get<SpecExtractionResponse>(`/conversational/conversations/${conversationId}/extract-specs`);
}
```

### 5. Loja de Estado no Frontend (frontend/src/store/conversationalStore.ts)

```typescript
/**
 * Loja de estado para conversação com IA
 * Gerencia estado relacionado a conversas e especificações extraídas
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { 
    ConversationResponse, 
    MessageResponse, 
    SpecExtractionResponse 
} from '../types/conversational';
import * as api from '../services/api';

interface ConversationalState {
    conversations: ConversationResponse[];
    currentConversation: ConversationResponse | null;
    messages: MessageResponse[];
    isLoading: boolean;
    error: string | null;
    
    // Actions
    fetchConversations: () => Promise<void>;
    createConversation: (projectId?: string) => Promise<string | null>;
    selectConversation: (conversationId: string) => Promise<void>;
    sendMessage: (conversationId: string, content: string) => Promise<void>;
    extractSpecs: (conversationId: string) => Promise<SpecExtractionResponse | null>;
    clearError: () => void;
}

export const useConversationalStore = create<ConversationalState>()(
    devtools(
        (set, get) => ({
            conversations: [],
            currentConversation: null,
            messages: [],
            isLoading: false,
            error: null,

            fetchConversations: async () => {
                try {
                    set({ isLoading: true, error: null });
                    const conversations = await api.listConversations();
                    set({ conversations, isLoading: false });
                } catch (error) {
                    console.error('Erro ao buscar conversas:', error);
                    set({ error: 'Não foi possível buscar as conversas', isLoading: false });
                }
            },

            createConversation: async (projectId?: string) => {
                try {
                    set({ isLoading: true, error: null });
                    const conversation = await api.createConversation(projectId);
                    
                    // Atualizar lista de conversas
                    const currentConversations = get().conversations;
                    set({ 
                        conversations: [conversation, ...currentConversations],
                        isLoading: false 
                    });
                    
                    return conversation.id;
                } catch (error) {
                    console.error('Erro ao criar conversa:', error);
                    set({ error: 'Não foi possível criar a conversa', isLoading: false });
                    return null;
                }
            },

            selectConversation: async (conversationId: string) => {
                try {
                    set({ isLoading: true, error: null });
                    
                    // Buscar detalhes da conversa
                    const conversation = await api.getConversation(conversationId);
                    
                    // Buscar mensagens
                    const messages = await api.getMessages(conversationId);
                    
                    set({
                        currentConversation: conversation,
                        messages,
                        isLoading: false
                    });
                } catch (error) {
                    console.error('Erro ao buscar conversa:', error);
                    set({ error: 'Não foi possível buscar a conversa', isLoading: false });
                }
            },

            sendMessage: async (conversationId: string, content: string) => {
                try {
                    set({ isLoading: true, error: null });
                    
                    // Enviar mensagem
                    const message = await api.sendMessage(conversationId, content);
                    
                    // Atualizar lista de mensagens
                    const currentMessages = get().messages;
                    set({ 
                        messages: [...currentMessages, message],
                        isLoading: false 
                    });
                } catch (error) {
                    console.error('Erro ao enviar mensagem:', error);
                    set({ error: 'Não foi possível enviar a mensagem', isLoading: false });
                }
            },

            extractSpecs: async (conversationId: string) => {
                try {
                    set({ isLoading: true, error: null });
                    
                    // Extrair especificações
                    const specs = await api.extractSpecs(conversationId);
                    
                    set({ isLoading: false });
                    return specs;
                } catch (error) {
                    console.error('Erro ao extrair especificações:', error);
                    set({ error: 'Não foi possível extrair especificações', isLoading: false });
                    return null;
                }
            },

            clearError: () => set({ error: null })
        })
    )
);
```

### 6. Melhoria na Interface Conversacional (frontend/src/components/conversational/ConversationalInterface.tsx)

```typescript
import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, MessageCircle, Sparkles, HelpCircle, Info, RefreshCw } from 'lucide-react';
import { toast } from 'react-hot-toast';

import { useConversationalStore } from '../../store/conversationalStore';
import { useAuthStore } from '../../store/authStore';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  clarifications?: string[];
  extractedSpecs?: Record<string, any>;
}

interface ConversationalInterfaceProps {
  projectId?: string;
  conversationId?: string;
  onSpecificationsExtracted?: (specs: Record<string, any>) => void;
}

export const ConversationalInterface: React.FC<ConversationalInterfaceProps> = ({
  projectId,
  conversationId,
  onSpecificationsExtracted,
}) => {
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const { user } = useAuthStore();
  
  const {
    currentConversation,
    messages,
    isLoading,
    error,
    createConversation,
    selectConversation,
    sendMessage,
    clearError,
  } = useConversationalStore();
  
  // Inicializar conversa se necessário
  useEffect(() => {
    const initializeConversation = async () => {
      if (!conversationId && !currentConversation) {
        const newConversationId = await createConversation(projectId);
        if (newConversationId) {
          await selectConversation(newConversationId);
        }
      } else if (conversationId && conversationId !== currentConversation?.id) {
        await selectConversation(conversationId);
      }
    };
    
    initializeConversation();
  }, [conversationId, currentConversation, projectId]);
  
  // Auto-scroll para última mensagem
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);
  
  // Focar input quando componente carregar
  useEffect(() => {
    inputRef.current?.focus();
  }, []);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || !currentConversation || isLoading) return;
    
    // Limpar erro anterior
    clearError();
    
    const message = inputMessage.trim();
    setInputMessage('');
    setIsTyping(true);
    
    try {
      // Enviar mensagem
      await sendMessage(currentConversation.id, message);
      
      // Verificar se foram extraídas especificações
      const latestMessage = messages[messages.length - 1];
      if (latestMessage?.extractedSpecs && onSpecificationsExtracted) {
        onSpecificationsExtracted(latestMessage.extractedSpecs);
        toast.success('Especificações extraídas com sucesso!');
      }
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      toast.error('Erro ao enviar mensagem');
    } finally {
      setIsTyping(false);
    }
  };
  
  const handleClarification = (clarification: string) => {
    setInputMessage(`Sobre ${clarification}: `);
    inputRef.current?.focus();
  };
  
  const formatMessage = (content: string) => {
    // Formatação básica de markdown
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code class="bg-gray-100 px-1 rounded">$1</code>')
      .replace(/\n/g, '<br />');
  };
  
  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-t-lg">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-white/20 rounded-full">
            <MessageCircle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-semibold">Assistente de Prototipagem</h3>
            <p className="text-blue-100 text-sm">
              Conversação Inteligente • Minimax M2 AI
            </p>
          </div>
        </div>
      </div>
      
      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 text-red-700 mb-2">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm">{error}</p>
            </div>
            <div className="ml-auto pl-3">
              <div className="-mx-1.5 -my-1.5">
                <button 
                  onClick={clearError}
                  className="inline-flex bg-red-50 rounded-md p-1.5 text-red-500 hover:bg-red-100"
                >
                  <span className="sr-only">Dismiss</span>
                  <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Mensagens */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4" style={{ maxHeight: '400px' }}>
        {currentConversation && (
          <div className="text-xs text-gray-500 mb-4">
            {new Date(currentConversation.created_at).toLocaleDateString()}
          </div>
        )}
        
        {currentConversation && messages.length === 0 && (
          <div className="text-center text-gray-500 py-8">
            <p>Inicie uma conversa sobre seu projeto de prototipagem. Seja detalhado sobre suas necessidades.</p>
            <div className="mt-4 grid grid-cols-2 gap-2">
              <button 
                onClick={() => setInputMessage('Quero criar um projeto para Arduino')}
                className="text-xs p-2 bg-gray-100 rounded hover:bg-gray-200"
              >
                Projeto para Arduino
              </button>
              <button 
                onClick={() => setInputMessage('Preciso de um gabinete para Raspberry Pi')}
                className="text-xs p-2 bg-gray-100 rounded hover:bg-gray-200"
              >
                Gabinete Raspberry Pi
              </button>
              <button 
                onClick={() => setInputMessage('Projeto mecânico com peças impressas')}
                className="text-xs p-2 bg-gray-100 rounded hover:bg-gray-200"
              >
                Projeto Mecânico
              </button>
              <button 
                onClick={() => setInputMessage('Preciso de componentes eletrônicos')}
                className="text-xs p-2 bg-gray-100 rounded hover:bg-gray-200"
              >
                Componentes Eletrônicos
              </button>
            </div>
          </div>
        )}
        
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                {message.role === 'assistant' && (
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="w-4 h-4 text-purple-600" />
                    <span className="text-xs font-medium text-purple-600">IA Assistant</span>
                  </div>
                )}
                
                <div
                  dangerouslySetInnerHTML={{
                    __html: formatMessage(message.content),
                  }}
                />
                
                <div className="text-xs opacity-70 mt-1">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </div>
                
                {/* Especificações extraídas */}
                {message.extractedSpecs && Object.keys(message.extractedSpecs).length > 0 && (
                  <div className="mt-3 p-2 bg-green-50 border border-green-200 rounded">
                    <p className="text-xs font-medium text-green-800 mb-1 flex items-center">
                      <Info className="w-3 h-3 mr-1" />
                      ✅ Especificações Extraídas:
                    </p>
                    <div className="text-xs text-green-700">
                      {message.extractedSpecs.categoria && (
                        <div>Categoria: {message.extractedSpecs.categoria}</div>
                      )}
                      {message.extractedSpecs.material && (
                        <div>Material: {message.extractedSpecs.material}</div>
                      )}
                    </div>
                  </div>
                )}
                
                {/* Clarificações necessárias */}
                {message.clarifications && message.clarifications.length > 0 && (
                  <div className="mt-3 space-y-1">
                    <p className="text-xs font-medium text-yellow-800 mb-2">
                      💡 Para melhorar, você poderia especificar:
                    </p>
                    {message.clarifications.map((clarification, index) => (
                      <button
                        key={index}
                        onClick={() => handleClarification(clarification)}
                        className="block w-full text-left text-xs p-2 bg-yellow-50 border border-yellow-200 rounded hover:bg-yellow-100 transition-colors"
                      >
                        <HelpCircle className="w-3 h-3 inline mr-1" />
                        {clarification}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        
        {/* Indicador de digitação */}
        {isTyping && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-start"
          >
            <div className="bg-gray-100 rounded-lg px-4 py-2 max-w-xs">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-purple-600" />
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
                <span className="text-xs text-gray-600">Pensando...</span>
              </div>
            </div>
          </motion.div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Descreva seu projeto em detalhes..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading || !currentConversation}
          />
          <button
            type="submit"
            disabled={!inputMessage.trim() || isLoading || !currentConversation}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        
        <div className="text-xs text-gray-500 mt-2 flex items-center justify-between">
          <span>💡 Dicas: Mencione dimensões, materiais, funcionalidades e restrições para melhor resultado</span>
          {currentConversation && (
            <button 
              className="text-blue-600 hover:text-blue-800 flex items-center gap-1"
              onClick={() => selectConversation(currentConversation.id)}
            >
              <RefreshCw className="w-3 h-3" />
              <span>Atualizar</span>
            </button>
          )}
        </div>
      </form>
    </div>
  );
};
```

## 📋 Cronograma de Implementação

1. **Configuração da API Minimax**
   - Atualizar requisitos e variáveis de ambiente
   - Implementar serviço Minimax
   
2. **Implementação de endpoints**
   - Desenvolver rotas de API
   - Conectar serviço Minimax com armazenamento
   
3. **Implementação do Frontend**
   - Melhorar interface conversacional
   - Conectar com endpoints do backend
   
4. **Testes e Validação**
   - Testes unitários
   - Testes de integração
   - Documentação de API
   
5. **Finalização**
   - Revisão de código
   - Implementação de melhorias finais
   - Documentação completa

## 📊 Critérios de Aceitação

- [ ] API Minimax integrada e funcionando
- [ ] Endpoints de conversação implementados e testados
- [ ] Interface React para conversação implementada e testada
- [ ] Sistema de extração de especificações implementado
- [ ] Testes unitários implementados com cobertura > 80%
- [ ] Documentação de API completa
- [ ] Deploy funcional do sistema de conversação

---

Este plano detalhado fornece uma visão abrangente da implementação do Sprint 2, focando na integração com a API Minimax M2 para conversação inteligente e extração de especificações.