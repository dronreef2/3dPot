"""
Serviço para interação com a API Minimax M2
Implementa conversação natural para extração de especificações
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

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
        
        # Tentativa de extrair dimensões específicas
        # Pattern: X mm de largura
        import re
        dim_pattern = r"(\d+(?:\.\d+)?)\s*(?:mm|cm|m)\s*(?:de\s*)?(?:largura|altura|profundidade|comprimento)"
        dimensions = re.findall(dim_pattern, ai_response.lower())
        if dimensions:
            extracted["dimensoes"]["valor"] = float(dimensions[0])
        
        return extracted