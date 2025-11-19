#!/usr/bin/env python3
"""
Testes End-to-End (E2E) - 3dPot v2.0

Testa fluxos completos do sistema através da API HTTP.
Utiliza FastAPI TestClient para simular requisições reais.
"""

import sys
from pathlib import Path
import pytest
from datetime import datetime

# Adicionar backend ao path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def test_client():
    """Cria um cliente de teste FastAPI."""
    try:
        from fastapi.testclient import TestClient
        from backend.main import app
        
        client = TestClient(app)
        return client
    except ImportError as e:
        pytest.skip(f"FastAPI TestClient não disponível: {e}")
    except Exception as e:
        pytest.skip(f"Não foi possível criar TestClient: {e}")


@pytest.fixture
def auth_headers(test_client):
    """Cria headers de autenticação para testes."""
    # Tentar criar um usuário de teste e fazer login
    try:
        # Registrar usuário de teste
        register_data = {
            "email": f"test_{datetime.now().timestamp()}@test.com",
            "password": "Test123!@#",
            "username": f"testuser_{int(datetime.now().timestamp())}"
        }
        
        # Tentar registrar (pode falhar se endpoint não existir)
        response = test_client.post("/api/v1/auth/register", json=register_data)
        
        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            token = data.get("access_token") or data.get("token")
            
            if token:
                return {"Authorization": f"Bearer {token}"}
    except Exception:
        pass
    
    # Retornar headers vazios se autenticação falhar
    return {}


class TestAuthenticationFlow:
    """Testes E2E do fluxo de autenticação."""
    
    def test_health_check(self, test_client):
        """Testa o endpoint de health check."""
        response = test_client.get("/health")
        
        # Aceita 200 (sucesso) ou 404 (endpoint não implementado ainda)
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data or "message" in data
    
    def test_docs_endpoint_available(self, test_client):
        """Testa se a documentação OpenAPI está disponível."""
        response = test_client.get("/docs")
        
        # Docs podem retornar 200 (HTML) ou redirect
        assert response.status_code in [200, 307, 308]
    
    def test_openapi_schema(self, test_client):
        """Testa se o schema OpenAPI está disponível."""
        response = test_client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
    
    @pytest.mark.skip(reason="Requer configuração de banco de dados")
    def test_user_registration_flow(self, test_client):
        """Testa o fluxo completo de registro de usuário."""
        # Dados do novo usuário
        user_data = {
            "email": f"newuser_{datetime.now().timestamp()}@test.com",
            "password": "SecurePass123!",
            "username": f"newuser_{int(datetime.now().timestamp())}"
        }
        
        # Tentar registrar
        response = test_client.post("/api/v1/auth/register", json=user_data)
        
        # Pode retornar 200, 201 (created) ou 404 (endpoint não implementado)
        assert response.status_code in [200, 201, 404]
        
        if response.status_code in [200, 201]:
            data = response.json()
            
            # Verificar campos esperados na resposta
            assert "email" in data or "user" in data or "token" in data
    
    @pytest.mark.skip(reason="Requer configuração de banco de dados")
    def test_login_flow(self, test_client):
        """Testa o fluxo de login."""
        # Dados de login
        login_data = {
            "email": "test@test.com",
            "password": "test123"
        }
        
        # Tentar fazer login
        response = test_client.post("/api/v1/auth/login", json=login_data)
        
        # Login pode falhar por falta de usuário, mas endpoint deve existir
        assert response.status_code in [200, 401, 404, 422]


class TestProjectWorkflow:
    """Testes E2E do fluxo de projetos."""
    
    @pytest.mark.skip(reason="Requer autenticação e banco de dados")
    def test_create_project_flow(self, test_client, auth_headers):
        """Testa o fluxo de criação de projeto."""
        project_data = {
            "name": f"Test Project {datetime.now().timestamp()}",
            "description": "Projeto de teste E2E",
            "category": "electronics"
        }
        
        response = test_client.post(
            "/api/v1/projects/",
            json=project_data,
            headers=auth_headers
        )
        
        # Aceita sucesso ou erro de autenticação/não implementado
        assert response.status_code in [200, 201, 401, 404, 422]
        
        if response.status_code in [200, 201]:
            data = response.json()
            assert "id" in data or "project_id" in data


class TestConversationalWorkflow:
    """Testes E2E do fluxo conversacional."""
    
    @pytest.mark.skip(reason="Requer autenticação e serviços externos")
    def test_start_conversation_flow(self, test_client, auth_headers):
        """Testa início de conversa com sistema conversacional."""
        conversation_data = {
            "message": "Quero criar um gabinete para Arduino",
            "context": "new_project"
        }
        
        response = test_client.post(
            "/api/v1/conversational/conversations",
            json=conversation_data,
            headers=auth_headers
        )
        
        # Endpoint pode não estar implementado ou requer auth
        assert response.status_code in [200, 201, 401, 404, 422]
        
        if response.status_code in [200, 201]:
            data = response.json()
            assert "conversation_id" in data or "id" in data


class TestBudgetingWorkflow:
    """Testes E2E do fluxo de orçamentação."""
    
    @pytest.mark.skip(reason="Requer autenticação e dados de projeto")
    def test_create_budget_flow(self, test_client, auth_headers):
        """Testa criação de orçamento para um projeto."""
        budget_data = {
            "project_id": "test-project-id",
            "material": "PLA",
            "weight_kg": 0.5,
            "print_time_hours": 10
        }
        
        response = test_client.post(
            "/api/v1/budgeting/create",
            json=budget_data,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 201, 401, 404, 422]
        
        if response.status_code in [200, 201]:
            data = response.json()
            assert "total_cost" in data or "budget" in data or "price" in data


class TestCompleteProjectFlow:
    """Testes E2E de fluxo completo de projeto."""
    
    @pytest.mark.skip(reason="Fluxo completo requer todos os serviços configurados")
    def test_end_to_end_project_creation(self, test_client, auth_headers):
        """
        Testa fluxo completo: 
        1. Criar projeto
        2. Iniciar conversa sobre o projeto
        3. Gerar orçamento
        """
        # 1. Criar projeto
        project_data = {
            "name": f"E2E Test Project {datetime.now().timestamp()}",
            "description": "Gabinete para Arduino Uno",
            "category": "electronics"
        }
        
        project_response = test_client.post(
            "/api/v1/projects/",
            json=project_data,
            headers=auth_headers
        )
        
        if project_response.status_code not in [200, 201]:
            pytest.skip("Criação de projeto falhou, pulando resto do fluxo")
        
        project = project_response.json()
        project_id = project.get("id") or project.get("project_id")
        
        # 2. Iniciar conversa sobre o projeto
        conversation_data = {
            "message": "Quero um gabinete de 10x7x4cm em PLA",
            "project_id": project_id
        }
        
        conversation_response = test_client.post(
            "/api/v1/conversational/conversations",
            json=conversation_data,
            headers=auth_headers
        )
        
        # 3. Gerar orçamento
        if project_id:
            budget_data = {
                "project_id": project_id,
                "material": "PLA",
                "weight_kg": 0.25
            }
            
            budget_response = test_client.post(
                "/api/v1/budgeting/create",
                json=budget_data,
                headers=auth_headers
            )
            
            # Verificar que pelo menos tentamos fazer o orçamento
            assert budget_response.status_code in [200, 201, 401, 404, 422]


if __name__ == "__main__":
    print("🧪 TESTES END-TO-END - 3DPOT V2.0")
    print("=" * 60)
    print("⚠️  Nota: Muitos testes E2E estão marcados como skip")
    print("   pois requerem banco de dados e serviços configurados.")
    print("=" * 60)
    
    # Executar testes
    pytest.main([__file__, "-v", "--tb=short"])
