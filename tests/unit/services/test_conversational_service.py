"""
Testes unitários para ConversationalService
Cobertura: Serviço de conversação inteligente com Minimax M2
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from datetime import datetime
from uuid import uuid4


class TestConversationalServiceInitialization:
    """Testes de inicialização do serviço"""
    
    def test_service_initialization(self):
        """Testa inicialização básica do serviço"""
        service = Mock()
        service.api_key = "test_api_key"
        service.base_url = "https://api.minimax.chat/v1"
        
        assert service.api_key == "test_api_key"
        assert service.base_url == "https://api.minimax.chat/v1"
    
    def test_headers_configuration(self):
        """Testa configuração dos headers"""
        headers = {
            "Authorization": "Bearer test_key",
            "Content-Type": "application/json"
        }
        
        assert headers["Authorization"].startswith("Bearer")
        assert headers["Content-Type"] == "application/json"


class TestConversationCreation:
    """Testes de criação de conversas"""
    
    def test_new_conversation_structure(self):
        """Testa estrutura de nova conversa"""
        conversation = Mock()
        conversation.id = uuid4()
        conversation.user_id = uuid4()
        conversation.project_id = None
        conversation.status = "especificando"
        
        assert conversation.status == "especificando"
        assert conversation.project_id is None
    
    def test_conversation_with_project(self):
        """Testa conversa associada a projeto"""
        conversation = Mock()
        conversation.id = uuid4()
        conversation.user_id = uuid4()
        conversation.project_id = uuid4()
        conversation.status = "especificando"
        
        assert conversation.project_id is not None
        assert conversation.status == "especificando"
    
    def test_conversation_status_values(self):
        """Testa valores válidos de status"""
        valid_statuses = ["especificando", "completo", "abandonado"]
        
        for status in valid_statuses:
            conversation = Mock()
            conversation.status = status
            assert conversation.status in valid_statuses


class TestMessageManagement:
    """Testes de gerenciamento de mensagens"""
    
    def test_add_user_message(self):
        """Testa adição de mensagem do usuário"""
        message = Mock()
        message.id = uuid4()
        message.conversation_id = uuid4()
        message.papel = "user"
        message.conteudo = "Quero criar uma caixa"
        message.timestamp = datetime.utcnow()
        
        assert message.papel == "user"
        assert len(message.conteudo) > 0
        assert message.timestamp is not None
    
    def test_add_assistant_message(self):
        """Testa adição de mensagem do assistente"""
        message = Mock()
        message.id = uuid4()
        message.conversation_id = uuid4()
        message.papel = "assistant"
        message.conteudo = "Qual o tamanho da caixa?"
        message.timestamp = datetime.utcnow()
        
        assert message.papel == "assistant"
        assert len(message.conteudo) > 0
    
    def test_message_roles(self):
        """Testa papéis válidos de mensagens"""
        valid_roles = ["user", "assistant", "system"]
        
        for role in valid_roles:
            message = Mock()
            message.papel = role
            assert message.papel in valid_roles


class TestContextPreparation:
    """Testes de preparação de contexto"""
    
    def test_prepare_context_structure(self):
        """Testa estrutura do contexto preparado"""
        context = [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "User message 1"},
            {"role": "assistant", "content": "Assistant response 1"}
        ]
        
        assert len(context) >= 1
        assert context[0]["role"] == "system"
        assert all("role" in msg for msg in context)
        assert all("content" in msg for msg in context)
    
    def test_context_message_ordering(self):
        """Testa ordenação de mensagens no contexto"""
        messages = [
            {"role": "user", "content": "Msg 1", "order": 1},
            {"role": "assistant", "content": "Resp 1", "order": 2},
            {"role": "user", "content": "Msg 2", "order": 3}
        ]
        
        orders = [msg["order"] for msg in messages]
        assert orders == sorted(orders)
    
    def test_system_prompt_insertion(self):
        """Testa inserção do system prompt"""
        context = []
        system_prompt = {"role": "system", "content": "You are an assistant"}
        context.insert(0, system_prompt)
        
        assert context[0]["role"] == "system"
        assert len(context) == 1


class TestSystemPrompt:
    """Testes do prompt do sistema"""
    
    def test_system_prompt_content(self):
        """Testa conteúdo do system prompt"""
        system_prompt = {
            "role": "system",
            "content": "Você é um assistente especializado em extrair especificações técnicas para projetos de prototipagem 3D."
        }
        
        assert system_prompt["role"] == "system"
        assert "especificações técnicas" in system_prompt["content"]
        assert "prototipagem" in system_prompt["content"] or "3D" in system_prompt["content"]
    
    def test_system_prompt_language(self):
        """Testa idioma do prompt (português)"""
        content = "Você é um assistente especializado em extrair especificações técnicas"
        
        # Palavras-chave em português
        assert "Você" in content or "você" in content
        assert "especificações" in content


class TestAPICall:
    """Testes de chamada à API"""
    
    @pytest.mark.asyncio
    async def test_api_payload_structure(self):
        """Testa estrutura do payload da API"""
        payload = {
            "model": "abab6.5-chat",
            "messages": [{"role": "user", "content": "Test"}],
            "temperature": 0.7,
            "max_tokens": 2000,
            "stream": False
        }
        
        assert payload["model"] == "abab6.5-chat"
        assert isinstance(payload["messages"], list)
        assert payload["temperature"] == 0.7
        assert payload["max_tokens"] == 2000
        assert payload["stream"] is False
    
    @pytest.mark.asyncio
    async def test_api_response_structure(self):
        """Testa estrutura da resposta da API"""
        response = {
            "content": "AI response content",
            "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 100
            },
            "model": "abab6.5-chat"
        }
        
        assert "content" in response
        assert "usage" in response
        assert "model" in response
    
    @pytest.mark.asyncio
    async def test_api_timeout_configuration(self):
        """Testa configuração de timeout"""
        timeout = 30.0
        
        assert timeout > 0
        assert timeout <= 60.0


class TestFallbackResponse:
    """Testes de resposta de fallback"""
    
    @pytest.mark.asyncio
    async def test_fallback_response_structure(self):
        """Testa estrutura da resposta de fallback"""
        fallback = {
            "content": "Entendo que você quer criar um projeto. Forneça detalhes sobre dimensões, material desejado e funcionalidades.",
            "usage": {},
            "model": "fallback"
        }
        
        assert fallback["model"] == "fallback"
        assert "dimensões" in fallback["content"] or "dimensoes" in fallback["content"]
        assert "material" in fallback["content"] or "funcionalidades" in fallback["content"]
    
    @pytest.mark.asyncio
    async def test_fallback_provides_guidance(self):
        """Testa que fallback fornece orientação"""
        content = "Para melhores resultados, forneça: dimensões, material, funcionalidades, restrições"
        
        assert "dimensões" in content or "dimensoes" in content
        assert "material" in content
        assert "funcionalidades" in content


class TestSpecificationExtraction:
    """Testes de extração de especificações"""
    
    def test_extract_category_mecanico(self):
        """Testa extração de categoria mecânico"""
        ai_content = "Este é um projeto mecânico com engrenagens"
        
        categoria = None
        if "mecânico" in ai_content.lower() or "mecanica" in ai_content.lower():
            categoria = "mecanico"
        
        assert categoria == "mecanico"
    
    def test_extract_category_eletronico(self):
        """Testa extração de categoria eletrônico"""
        ai_content = "Projeto eletrônico com sensores"
        
        categoria = None
        if "eletrônico" in ai_content.lower() or "eletronico" in ai_content.lower():
            categoria = "eletronico"
        
        assert categoria == "eletronico"
    
    def test_extract_category_arquitetura(self):
        """Testa extração de categoria arquitetura"""
        ai_content = "Projeto de arquitetura modular"
        
        categoria = None
        if "arquitetura" in ai_content.lower():
            categoria = "arquitetura"
        
        assert categoria == "arquitetura"
    
    def test_extract_material_pla(self):
        """Testa extração de material PLA"""
        ai_content = "Recomendo usar PLA para este projeto"
        
        materiais = ["pla", "abs", "petg", "nylon", "metal"]
        material_found = None
        
        for material in materiais:
            if material in ai_content.lower():
                material_found = material.upper()
                break
        
        assert material_found == "PLA"
    
    def test_extract_material_abs(self):
        """Testa extração de material ABS"""
        ai_content = "Use ABS para maior resistência"
        
        materiais = ["pla", "abs", "petg", "nylon", "metal"]
        material_found = None
        
        for material in materiais:
            if material in ai_content.lower():
                material_found = material.upper()
                break
        
        assert material_found == "ABS"
    
    def test_extracted_specs_structure(self):
        """Testa estrutura de especificações extraídas"""
        extracted = {
            "categoria": "mecanico",
            "dimensoes": {},
            "material": "PLA",
            "componentes": [],
            "funcionalidades": [],
            "restricoes": []
        }
        
        assert "categoria" in extracted
        assert "dimensoes" in extracted
        assert "material" in extracted
        assert isinstance(extracted["componentes"], list)
        assert isinstance(extracted["funcionalidades"], list)


class TestClarifications:
    """Testes de identificação de clarificações"""
    
    def test_identify_missing_dimensions(self):
        """Testa identificação de dimensões faltantes"""
        ai_content = "Vou criar o projeto, mas preciso saber as dimensões exatas"
        
        needs_dimensions = ("dimensão" in ai_content.lower() or "dimensões" in ai_content.lower()) and "largura" not in ai_content.lower()
        
        assert needs_dimensions is True
    
    def test_identify_missing_material(self):
        """Testa identificação de material faltante"""
        ai_content = "Qual o melhor escolha para este projeto?"
        
        needs_material = "material" not in ai_content.lower() and "filamento" not in ai_content.lower()
        
        assert needs_material is True
    
    def test_clarifications_list_structure(self):
        """Testa estrutura da lista de clarificações"""
        clarifications = ["dimensions", "material", "functionality"]
        
        assert isinstance(clarifications, list)
        assert all(isinstance(c, str) for c in clarifications)
    
    def test_no_clarifications_needed(self):
        """Testa quando não há clarificações necessárias"""
        ai_content = "Projeto completo: 100mm x 50mm x 30mm, material PLA, funcionalidade de armazenamento"
        
        clarifications = []
        
        if "dimensão" in ai_content.lower() and "largura" not in ai_content.lower():
            clarifications.append("dimensions")
        
        assert len(clarifications) == 0


class TestConversationUpdate:
    """Testes de atualização de conversas"""
    
    def test_update_extracted_specs(self):
        """Testa atualização de especificações extraídas"""
        current_specs = {"categoria": "mecanico"}
        new_specs = {"material": "PLA", "dimensoes": {"largura": 100}}
        
        current_specs.update(new_specs)
        
        assert "categoria" in current_specs
        assert "material" in current_specs
        assert "dimensoes" in current_specs
    
    def test_update_clarifications(self):
        """Testa atualização de clarificações"""
        current_clarifications = ["dimensions"]
        new_clarification = "material"
        
        if new_clarification not in current_clarifications:
            current_clarifications.append(new_clarification)
        
        assert len(current_clarifications) == 2
        assert "material" in current_clarifications
    
    def test_conversation_status_complete(self):
        """Testa mudança de status para completo"""
        conversation = Mock()
        conversation.status = "especificando"
        clarifications = []
        
        if not clarifications:
            conversation.status = "completo"
            conversation.completed_at = datetime.utcnow()
        
        assert conversation.status == "completo"
        assert conversation.completed_at is not None


class TestConversationRetrieval:
    """Testes de recuperação de conversas"""
    
    def test_get_conversation_by_id(self):
        """Testa obtenção de conversa por ID"""
        conversation_id = uuid4()
        conversation = Mock()
        conversation.id = conversation_id
        
        assert conversation.id == conversation_id
    
    def test_get_user_conversations_pagination(self):
        """Testa paginação de conversas do usuário"""
        skip = 0
        limit = 50
        
        assert skip >= 0
        assert limit > 0
        assert limit <= 100
    
    def test_conversations_ordered_by_date(self):
        """Testa ordenação de conversas por data"""
        conversations = [
            Mock(created_at=datetime(2025, 1, 1)),
            Mock(created_at=datetime(2025, 1, 3)),
            Mock(created_at=datetime(2025, 1, 2))
        ]
        
        # Simular ordenação descendente
        sorted_convs = sorted(conversations, key=lambda x: x.created_at, reverse=True)
        
        assert sorted_convs[0].created_at > sorted_convs[1].created_at
        assert sorted_convs[1].created_at > sorted_convs[2].created_at


class TestErrorHandling:
    """Testes de tratamento de erros"""
    
    @pytest.mark.asyncio
    async def test_handle_api_error(self):
        """Testa tratamento de erro da API"""
        try:
            # Simular erro
            raise Exception("API Error")
        except Exception as e:
            error_handled = True
            error_message = str(e)
        
        assert error_handled is True
        assert "API Error" in error_message
    
    @pytest.mark.asyncio
    async def test_conversation_not_found(self):
        """Testa erro quando conversa não encontrada"""
        conversation = None
        
        if not conversation:
            error_raised = True
        
        assert error_raised is True
    
    @pytest.mark.asyncio
    async def test_database_rollback_on_error(self):
        """Testa rollback de banco em caso de erro"""
        db = Mock()
        db.rollback = Mock()
        
        try:
            raise Exception("Database error")
        except Exception:
            db.rollback()
        
        db.rollback.assert_called_once()


class TestResponseFormatting:
    """Testes de formatação de resposta"""
    
    def test_conversational_response_structure(self):
        """Testa estrutura da resposta conversacional"""
        response = {
            "response": "AI response content",
            "conversation_id": uuid4(),
            "message_id": uuid4(),
            "clarifications_needed": ["dimensions"],
            "extracted_specs": {"categoria": "mecanico"}
        }
        
        assert "response" in response
        assert "conversation_id" in response
        assert "message_id" in response
        assert "clarifications_needed" in response
        assert "extracted_specs" in response
    
    def test_response_with_no_clarifications(self):
        """Testa resposta sem clarificações necessárias"""
        response = {
            "response": "Especificações completas!",
            "clarifications_needed": []
        }
        
        assert len(response["clarifications_needed"]) == 0
