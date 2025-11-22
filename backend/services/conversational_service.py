"""
Serviço de Conversação Inteligente - Minimax M2
Extração de especificações de projetos via IA conversacional
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

import httpx
from sqlalchemy.orm import Session

from backend.core.config import MINIMAX_API_KEY
from backend.models import Conversation, ConversationMessage, User, Project
from backend.schemas import ConversationalResponse, ConversationalRequest

logger = logging.getLogger(__name__)

class ConversationalService:
    """Serviço para interação com Minimax M2 API"""
    
    def __init__(self):
        self.api_key = MINIMAX_API_KEY
        self.base_url = "https://api.minimax.chat/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    async def start_conversation(self, user_id: UUID, project_id: Optional[UUID] = None) -> Conversation:
        """Iniciar nova conversa"""
        # Lógica de criação de conversa será implementada no endpoint
        pass
    
    async def process_message(self, db: Session, request: ConversationalRequest, user_id: UUID) -> ConversationalResponse:
        """
        Processar mensagem do usuário e gerar resposta inteligente
        
        Args:
            db: Sessão do banco de dados
            request: Dados da mensagem
            user_id: ID do usuário
            
        Returns:
            Resposta conversacional com especificação extraída
        """
        try:
            # Obter ou criar conversa
            conversation = await self._get_or_create_conversation(db, request, user_id)
            
            # Adicionar mensagem do usuário
            user_message = self._add_message(db, conversation.id, "user", request.message)
            
            # Preparar contexto para Minimax
            context = await self._prepare_context(db, conversation)
            
            # Chamar Minimax M2 API
            ai_response = await self._call_minimax_api(context, request.message)
            
            # Adicionar resposta da IA
            assistant_message = self._add_message(db, conversation.id, "assistant", ai_response["content"])
            
            # Extrair especificações
            extracted_specs = self._extract_specifications(ai_response["content"])
            
            # Determinar se precisa de clarificações
            clarifications = self._identify_clarifications(db, conversation, ai_response["content"])
            
            # Atualizar conversa
            self._update_conversation(db, conversation, extracted_specs, clarifications)
            
            # Salvar mudanças
            db.commit()
            
            return ConversationalResponse(
                response=ai_response["content"],
                conversation_id=conversation.id,
                message_id=assistant_message.id,
                clarifications_needed=clarifications,
                extracted_specs=extracted_specs
            )
            
        except Exception as e:
            logger.error(f"Erro no processamento de mensagem: {e}")
            db.rollback()
            raise
    
    async def _get_or_create_conversation(self, db: Session, request: ConversationalRequest, user_id: UUID) -> Conversation:
        """Obter conversa existente ou criar nova"""
        if request.conversation_id:
            conversation = db.query(Conversation).filter(Conversation.id == request.conversation_id).first()
            if not conversation:
                raise ValueError("Conversa não encontrada")
            return conversation
        
        # Criar nova conversa
        conversation = Conversation(
            user_id=user_id,
            project_id=request.project_id,
            status="especificando"
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation
    
    def _add_message(self, db: Session, conversation_id: UUID, papel: str, conteudo: str) -> ConversationMessage:
        """Adicionar mensagem à conversa"""
        message = ConversationMessage(
            conversation_id=conversation_id,
            papel=papel,
            conteudo=conteudo
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
    
    async def _prepare_context(self, db: Session, conversation: Conversation) -> List[Dict]:
        """Preparar contexto da conversa para Minimax"""
        messages = db.query(ConversationMessage).filter(
            ConversationMessage.conversation_id == conversation.id
        ).order_by(ConversationMessage.timestamp).all()
        
        context = []
        for message in messages:
            context.append({
                "role": "user" if message.papel == "user" else "assistant",
                "content": message.conteudo
            })
        
        # Adicionar system prompt em português
        system_prompt = self._get_system_prompt()
        if context:
            context.insert(0, system_prompt)
        
        return context
    
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
    
    async def _call_minimax_api(self, context: List[Dict], user_message: str) -> Dict[str, Any]:
        """Chamar API do Minimax M2"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "model": "abab6.5-chat",
                    "messages": context,
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "stream": False
                }
                
                response = await client.post(
                    f"{self.base_url}/text/chatcompletion_pro",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                response.raise_for_status()
                data = response.json()
                
                return {
                    "content": data["choices"][0]["message"]["content"],
                    "usage": data.get("usage", {}),
                    "model": data["model"]
                }
                
        except httpx.HTTPError as e:
            logger.error(f"Erro na API Minimax: {e}")
            # Fallback para resposta local se API falhar
            return await self._fallback_response(user_message)
    
    async def _fallback_response(self, user_message: str) -> Dict[str, Any]:
        """Resposta de fallback quando API Minimax não está disponível"""
        return {
            "content": "Entendo que você quer criar um projeto. Para melhores resultados, forneça detalhes sobre: dimensões (largura x altura x profundidade), material desejado (PLA, ABS, metal), funcionalidades principais e quaisquer restrições.",
            "usage": {},
            "model": "fallback"
        }
    
    def _extract_specifications(self, ai_content: str) -> Dict[str, Any]:
        """Extrair especificações do conteúdo da IA"""
        # Esta função pode ser melhorada para usar NLP avançado
        # Por enquanto, vamos fazer uma extração básica
        
        extracted = {
            "categoria": None,
            "dimensoes": {},
            "material": None,
            "componentes": [],
            "funcionalidades": [],
            "restricoes": []
        }
        
        # Detecção básica de padrões (melhorar com NLP)
        if "mecânico" in ai_content.lower() or "mecanica" in ai_content.lower():
            extracted["categoria"] = "mecanico"
        elif "eletrônico" in ai_content.lower() or "eletronico" in ai_content.lower():
            extracted["categoria"] = "eletronico"
        elif "arquitetura" in ai_content.lower():
            extracted["categoria"] = "arquitetura"
        else:
            extracted["categoria"] = "mixto"
        
        # Detecção de materiais
        materiais = ["pla", "abs", "petg", "nylon", "metal", "alumínio", "aço"]
        for material in materiais:
            if material in ai_content.lower():
                extracted["material"] = material.upper()
                break
        
        return extracted
    
    def _identify_clarifications(self, db: Session, conversation: Conversation, ai_content: str) -> List[str]:
        """Identificar se são necessárias clarificações"""
        clarifications = []
        
        # Verificar se dimensão foi mencionada
        if "dimensão" in ai_content.lower() and "largura" not in ai_content.lower():
            clarifications.append("dimensions")
        
        # Verificar se material foi mencionado
        if "material" not in ai_content.lower() and "filamento" not in ai_content.lower():
            clarifications.append("material")
        
        # Verificar funcionalidades
        if "funcionalidade" not in ai_content.lower() and "funcionar" not in ai_content.lower():
            clarifications.append("functionality")
        
        return clarifications
    
    def _update_conversation(self, db: Session, conversation: Conversation, 
                           extracted_specs: Dict[str, Any], clarifications: List[str]):
        """Atualizar conversa com informações extraídas"""
        # Atualizar especificações extraídas
        current_specs = conversation.especificacoes_extraidas or {}
        current_specs.update(extracted_specs)
        
        # Atualizar clarificações pendentes
        current_clarifications = conversation.clarificacoes_pendentes or []
        for clarification in clarifications:
            if clarification not in current_clarifications:
                current_clarifications.append(clarification)
        
        # Atualizar status se especificação estiver completa
        if not clarifications:
            conversation.status = "completo"
            conversation.completed_at = datetime.utcnow()
        
        conversation.especificacoes_extraidas = current_specs
        conversation.clarificacoes_pendentes = current_clarifications
        
        db.commit()
    
    def get_conversation_by_id(self, db: Session, conversation_id: UUID) -> Optional[Conversation]:
        """Obter conversa por ID"""
        return db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    def get_user_conversations(self, db: Session, user_id: UUID, skip: int = 0, limit: int = 50) -> List[Conversation]:
        """Obter conversas do usuário"""
        return db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.created_at.desc()).offset(skip).limit(limit).all()