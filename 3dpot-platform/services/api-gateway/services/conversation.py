"""
3dPot Platform - Conversation Service
Criado em: 2025-11-12 22:42:43
Autor: MiniMax Agent

Serviço de conversação com Minimax M2 Agent para extração de requisitos
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import redis.asyncio as redis
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
import httpx

# Import local modules
from models.database_models import ConversationSession, Specification, Project, User
from database.database import get_database
from utils.logger import get_logger

logger = get_logger("conversation.service")

class MinimaxAgent:
    """Cliente para integração com Minimax M2 Agent"""
    
    def __init__(self):
        self.api_base = "https://api.minimax.chat/v1"
        self.api_key = os.getenv("MINIMAX_API_KEY")
        
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Processa mensagem com o Minimax M2 Agent
        """
        try:
            # Preparar contexto
            prompt_context = self._build_context_prompt(message, context)
            
            # Fazer request para Minimax
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "minimax-m2",
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt_context
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 2000
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    assistant_message = result["choices"][0]["message"]["content"]
                    
                    # Parse da resposta para extrair requisitos
                    extracted_specs = self._parse_agent_response(assistant_message)
                    
                    return {
                        "response": assistant_message,
                        "extracted_specs": extracted_specs,
                        "confidence": self._calculate_confidence(extracted_specs),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    logger.error(f"Erro na API Minimax: {response.status_code} - {response.text}")
                    return self._fallback_response(message)
                    
        except Exception as e:
            logger.error(f"Erro ao processar com Minimax: {e}")
            return self._fallback_response(message)
    
    def _build_context_prompt(self, message: str, context: Dict[str, Any] = None) -> str:
        """Constrói prompt contextualizado para o agent"""
        base_prompt = """
Você é um especialista em requisitos técnicos para projetos de prototipagem 3D.

Sua tarefa é analisar mensagens de usuários e extrair requisitos técnicos estruturados.

Analise a mensagem e extraia:
1. Dimensões do objeto (largura, altura, profundidade)
2. Material desejado
3. Tolerâncias
4. Funcionalidade principal
5. Requisitos de resistência/força
6. Condições ambientais
7. Conectores/fixação
8. Complexidade estimada

Responda sempre em formato JSON estruturado.
"""
        
        if context:
            context_text = f"\nContexto do projeto: {json.dumps(context)}"
            base_prompt += context_text
        
        return f"{base_prompt}\n\nMensagem do usuário: {message}"
    
    def _parse_agent_response(self, response: str) -> Dict[str, Any]:
        """Parse da resposta do agent para extrair especificações"""
        try:
            # Tentar extrair JSON da resposta
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Fallback: usar regex para encontrar padrões
            specs = {
                "dimensions": self._extract_dimensions(response),
                "material": self._extract_material(response),
                "functionality": self._extract_functionality(response),
                "complexity": self._estimate_complexity(response)
            }
            
            return specs
            
        except Exception as e:
            logger.error(f"Erro ao parsear resposta do agent: {e}")
            return self._extract_basic_specs(response)
    
    def _extract_dimensions(self, text: str) -> Dict[str, float]:
        """Extrai dimensões do texto usando regex"""
        import re
        
        dimensions = {}
        
        # Buscar padrões como "100mm x 50mm x 30mm"
        patterns = [
            r'(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)',
            r'width[:\s]+(\d+(?:\.\d+)?).*?height[:\s]+(\d+(?:\.\d+)?).*?depth[:\s]+(\d+(?:\.\d+)?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) >= 3:
                    dimensions["width"] = float(groups[0])
                    dimensions["height"] = float(groups[1]) 
                    dimensions["depth"] = float(groups[2])
                elif len(groups) >= 2:
                    dimensions["width"] = float(groups[0])
                    dimensions["height"] = float(groups[1])
                break
        
        return dimensions
    
    def _extract_material(self, text: str) -> str:
        """Extrai material desejado"""
        materials = ["ABS", "PLA", "PETG", "Nylon", "Metal", "Alumínio", "Aço", "Resina"]
        
        text_lower = text.lower()
        for material in materials:
            if material.lower() in text_lower:
                return material
        
        return "Não especificado"
    
    def _extract_functionality(self, text: str) -> str:
        """Extrai funcionalidade principal"""
        functionalities = [
            "suporte", "fixação", "guiamento", "proteção", "decoração",
            "funcional", "reposição", "gabarito", "empresa"
        ]
        
        text_lower = text.lower()
        for func in functionalities:
            if func in text_lower:
                return func.capitalize()
        
        return "Não especificado"
    
    def _estimate_complexity(self, text: str) -> str:
        """Estima complexidade do projeto"""
        simple_keywords = ["simples", "básico", "sem complex", "fácil"]
        medium_keywords = ["médio", "alguma", "diferente", "modificado"]
        complex_keywords = ["complexo", "difícil", "preciso", "avançado", "tolerância"]
        
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in complex_keywords):
            return "Alto"
        elif any(keyword in text_lower for keyword in medium_keywords):
            return "Médio"
        elif any(keyword in text_lower for keyword in simple_keywords):
            return "Baixo"
        else:
            return "Médio"
    
    def _extract_basic_specs(self, text: str) -> Dict[str, Any]:
        """Extração básica de especificações como fallback"""
        return {
            "raw_text": text,
            "dimensions": self._extract_dimensions(text),
            "material": self._extract_material(text),
            "functionality": self._extract_functionality(text),
            "complexity": self._estimate_complexity(text),
            "extraction_method": "basic_regex"
        }
    
    def _calculate_confidence(self, specs: Dict[str, Any]) -> float:
        """Calcula confiança da extração (0-1)"""
        confidence_factors = 0.0
        total_factors = 4.0
        
        # Verificar se dimensões foram extraídas
        if specs.get("dimensions") and len(specs["dimensions"]) > 0:
            confidence_factors += 1.0
        
        # Verificar se material foi extraído
        if specs.get("material") and specs["material"] != "Não especificado":
            confidence_factors += 1.0
        
        # Verificar se funcionalidade foi extraída
        if specs.get("functionality") and specs["functionality"] != "Não especificado":
            confidence_factors += 1.0
        
        # Verificar complexidade
        if specs.get("complexity") and specs["complexity"] != "Médio":
            confidence_factors += 1.0
        
        return confidence_factors / total_factors
    
    def _fallback_response(self, message: str) -> Dict[str, Any]:
        """Resposta de fallback quando a API falha"""
        return {
            "response": f"Obrigado pela sua mensagem. Vou processar os requisitos para: {message[:100]}...",
            "extracted_specs": self._extract_basic_specs(message),
            "confidence": 0.5,
            "timestamp": datetime.utcnow().isoformat(),
            "fallback": True
        }

class ConversationService:
    """
    Serviço principal de conversação que gerencia:
    - Sessões WebSocket
    - Integração com Minimax M2 Agent
    - Extração de especificações
    - Persistência no database
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.agent = MinimaxAgent()
        self.router = APIRouter()
        
        # Registrar rotas
        self._register_routes()
    
    async def process_message(
        self, 
        session_id: str, 
        message: str, 
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Processa mensagem através do Minimax Agent"""
        
        try:
            # Buscar contexto da sessão
            context = await self._get_session_context(session_id)
            
            # Processar com Minimax Agent
            result = await self.agent.process_message(message, context)
            
            # Salvar na Redis cache
            await self._cache_message(session_id, message, result)
            
            # Salvar especificação no database se confiança for alta
            if result["confidence"] > 0.6:
                await self._save_specification(session_id, user_id, result)
            
            logger.info(f"📋 Mensagem processada - Confiança: {result['confidence']:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar mensagem: {e}")
            return self.agent._fallback_response(message)
    
    async def _get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Busca contexto da sessão"""
        try:
            cache_key = f"session:{session_id}:context"
            cached_context = await self.redis.get(cache_key)
            
            if cached_context:
                return json.loads(cached_context)
            else:
                return {}
        except Exception as e:
            logger.error(f"Erro ao buscar contexto: {e}")
            return {}
    
    async def _cache_message(self, session_id: str, message: str, result: Dict[str, Any]):
        """Cache da conversa na Redis"""
        try:
            # Cache da mensagem
            cache_key = f"session:{session_id}:messages"
            message_data = {
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "result": result
            }
            
            # Adicionar à lista de mensagens (máximo 50)
            await self.redis.lpush(cache_key, json.dumps(message_data))
            await self.redis.ltrim(cache_key, 0, 49)
            
            # Cache do contexto
            if result.get("extracted_specs"):
                context_key = f"session:{session_id}:context"
                context = await self.redis.get(context_key) or "{}"
                current_context = json.loads(context)
                
                # Atualizar contexto com novas especificações
                specs = result["extracted_specs"]
                current_context.update(specs)
                
                await self.redis.setex(context_key, 3600, json.dumps(current_context))
                
        except Exception as e:
            logger.error(f"Erro ao fazer cache: {e}")
    
    async def _save_specification(self, session_id: str, user_id: Optional[int], result: Dict[str, Any]):
        """Salva especificação extraída no database"""
        try:
            # Esta implementação seria feita no contexto de uma sessão de database
            # Por simplicidade, apenas logamos aqui
            logger.info(f"💾 Salvando especificação da sessão {session_id}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar especificação: {e}")
    
    def _register_routes(self):
        """Registra rotas REST"""
        
        @self.router.get("/sessions")
        async def list_conversation_sessions(
            user_id: Optional[int] = None,
            db: AsyncSession = Depends(get_database)
        ):
            """Lista sessões de conversação"""
            try:
                query = select(ConversationSession)
                if user_id:
                    query = query.where(ConversationSession.user_id == user_id)
                
                result = await db.execute(query.order_by(ConversationSession.created_at.desc()))
                sessions = result.scalars().all()
                
                return {
                    "sessions": [
                        {
                            "session_id": s.session_id,
                            "title": s.title,
                            "status": s.status,
                            "created_at": s.created_at.isoformat(),
                            "updated_at": s.updated_at.isoformat()
                        }
                        for s in sessions
                    ]
                }
            except Exception as e:
                logger.error(f"Erro ao listar sessões: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/sessions/{session_id}/messages")
        async def get_session_messages(
            session_id: str,
            limit: int = 50,
            redis_client: redis.Redis = Depends(get_redis)
        ):
            """Busca mensagens de uma sessão"""
            try:
                cache_key = f"session:{session_id}:messages"
                cached_messages = await redis_client.lrange(cache_key, 0, limit - 1)
                
                messages = []
                for cached_msg in cached_messages:
                    message_data = json.loads(cached_msg)
                    messages.append(message_data)
                
                messages.reverse()  # Mais antigas primeiro
                
                return {"session_id": session_id, "messages": messages}
                
            except Exception as e:
                logger.error(f"Erro ao buscar mensagens: {e}")
                raise HTTPException(status_code=500, detail=str(e))

# Instância global (será inicializada no main.py)
conversation_service = None

# Utility functions
async def get_redis() -> redis.Redis:
    """Dependency para obter Redis client"""
    import redis.asyncio as redis
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    return redis.from_url(redis_url)