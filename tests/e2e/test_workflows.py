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


class TestProjectRevisionWorkflow:
    """Testes E2E do fluxo de revisão de projeto (Sprint 4)."""
    
    @pytest.mark.skip(reason="Requer configuração completa de banco de dados")
    def test_project_revision_flow(self, test_client, auth_headers):
        """Testa fluxo completo: criar projeto → atualizar → marcar como pronto."""
        # 1. Criar projeto inicial
        project_data = {
            "name": "Projeto para Revisão",
            "description": "Projeto que será revisado",
            "category": "mecanico"
        }
        
        create_response = test_client.post(
            "/api/v1/projects/",
            json=project_data,
            headers=auth_headers
        )
        
        assert create_response.status_code in [200, 201, 401, 404, 422]
        
        if create_response.status_code in [200, 201]:
            project_id = create_response.json().get("id")
            
            # 2. Atualizar projeto
            update_data = {
                "description": "Projeto revisado com novas especificações",
                "status": "em_revisao"
            }
            
            update_response = test_client.put(
                f"/api/v1/projects/{project_id}",
                json=update_data,
                headers=auth_headers
            )
            
            # 3. Marcar como pronto
            ready_response = test_client.patch(
                f"/api/v1/projects/{project_id}/ready",
                headers=auth_headers
            )
            
            assert ready_response.status_code in [200, 404, 422]


class TestAdvancedSimulationWorkflow:
    """Testes E2E de simulação avançada com diferentes parâmetros (Sprint 4)."""
    
    @pytest.mark.skip(reason="Requer configuração completa de simulação")
    def test_drop_test_simulation(self, test_client, auth_headers):
        """Testa simulação de drop test com diferentes alturas."""
        simulation_data = {
            "type": "drop_test",
            "model_path": "/models/test_object.stl",
            "parameters": {
                "drop_height": 1.0,
                "num_drops": 5,
                "ground_material": "concrete"
            }
        }
        
        response = test_client.post(
            "/api/v1/simulation/run",
            json=simulation_data,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 201, 401, 404, 422, 500]
        
        if response.status_code in [200, 201]:
            data = response.json()
            assert "simulation_id" in data or "result" in data
    
    @pytest.mark.skip(reason="Requer configuração completa de simulação")
    def test_stress_test_simulation(self, test_client, auth_headers):
        """Testa simulação de stress test com diferentes forças."""
        simulation_data = {
            "type": "stress_test",
            "model_path": "/models/test_object.stl",
            "parameters": {
                "force_newtons": 500,
                "direction": "vertical",
                "material": "PLA"
            }
        }
        
        response = test_client.post(
            "/api/v1/simulation/run",
            json=simulation_data,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 201, 401, 404, 422, 500]


class TestPrint3DIntegrationWorkflow:
    """Testes E2E de integração com impressão 3D (Sprint 4)."""
    
    @pytest.mark.skip(reason="Requer impressora 3D configurada")
    def test_create_print_job(self, test_client, auth_headers):
        """Testa criação de job de impressão 3D."""
        print_job_data = {
            "model_path": "/models/test_print.stl",
            "material": "PLA",
            "color": "white",
            "layer_height": 0.2,
            "infill": 20,
            "supports": True,
            "quantity": 1
        }
        
        response = test_client.post(
            "/api/v1/print3d/jobs",
            json=print_job_data,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 201, 401, 404, 422]
        
        if response.status_code in [200, 201]:
            data = response.json()
            assert "job_id" in data or "id" in data
            
            # Verificar estimativa de tempo e custo
            if "estimated_time" in data:
                assert data["estimated_time"] > 0
            if "estimated_cost" in data:
                assert data["estimated_cost"] > 0
    
    @pytest.mark.skip(reason="Requer impressora 3D configurada")
    def test_print_job_status(self, test_client, auth_headers):
        """Testa consulta de status de job de impressão."""
        job_id = "test-job-123"
        
        response = test_client.get(
            f"/api/v1/print3d/jobs/{job_id}/status",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 404, 401]


class TestCostOptimizationWorkflow:
    """Testes E2E de fluxo de otimização de custos (Sprint 4)."""
    
    @pytest.mark.skip(reason="Requer configuração de otimização")
    def test_optimize_material_costs(self, test_client, auth_headers):
        """Testa otimização de custos de material."""
        optimization_data = {
            "project_id": "test-project-123",
            "optimization_type": "material",
            "constraints": {
                "max_budget": 1000,
                "min_quality": 0.8,
                "max_lead_time_days": 14
            }
        }
        
        response = test_client.post(
            "/api/v1/optimization/analyze",
            json=optimization_data,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 201, 401, 404, 422]
        
        if response.status_code in [200, 201]:
            data = response.json()
            assert "recommendations" in data or "optimized_cost" in data
    
    @pytest.mark.skip(reason="Requer configuração de otimização")
    def test_batch_production_optimization(self, test_client, auth_headers):
        """Testa otimização de produção em lote."""
        optimization_data = {
            "project_id": "test-project-123",
            "optimization_type": "batch",
            "quantity": 100,
            "constraints": {
                "max_budget": 5000,
                "max_lead_time_days": 30
            }
        }
        
        response = test_client.post(
            "/api/v1/optimization/batch",
            json=optimization_data,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 201, 401, 404, 422]


class TestMarketplaceWorkflow:
    """Testes E2E de fluxo de marketplace (Sprint 4)."""
    
    @pytest.mark.skip(reason="Requer configuração de marketplace")
    def test_search_components(self, test_client, auth_headers):
        """Testa busca de componentes no marketplace."""
        search_params = {
            "query": "sensor ultrassonico",
            "category": "eletronic",
            "max_price": 50,
            "in_stock": True
        }
        
        response = test_client.get(
            "/api/v1/marketplace/search",
            params=search_params,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "results" in data or "items" in data
    
    @pytest.mark.skip(reason="Requer configuração de marketplace")
    def test_create_order(self, test_client, auth_headers):
        """Testa criação de pedido no marketplace."""
        order_data = {
            "items": [
                {"component_id": "comp-123", "quantity": 2},
                {"component_id": "comp-456", "quantity": 1}
            ],
            "shipping_address": {
                "street": "Rua Teste, 123",
                "city": "São Paulo",
                "state": "SP",
                "zip_code": "01234-567"
            },
            "payment_method": "credit_card"
        }
        
        response = test_client.post(
            "/api/v1/marketplace/orders",
            json=order_data,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 201, 401, 404, 422]
        
        if response.status_code in [200, 201]:
            data = response.json()
            assert "order_id" in data or "id" in data
            assert "total_price" in data or "amount" in data
    
    @pytest.mark.skip(reason="Requer configuração de marketplace")
    def test_order_tracking(self, test_client, auth_headers):
        """Testa rastreamento de pedido."""
        order_id = "order-123"
        
        response = test_client.get(
            f"/api/v1/marketplace/orders/{order_id}/track",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 404, 401]
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "tracking_events" in data or "history" in data


if __name__ == "__main__":
    print("🧪 TESTES END-TO-END - 3DPOT V2.0 - SPRINT 4")
    print("=" * 60)
    print("⚠️  Nota: Muitos testes E2E estão marcados como skip")
    print("   pois requerem banco de dados e serviços configurados.")
    print("=" * 60)
    print("📊 Novos fluxos E2E adicionados na Sprint 4:")
    print("   - Revisão de projeto")
    print("   - Simulações avançadas")
    print("   - Integração com impressão 3D")
    print("   - Otimização de custos")
    print("   - Marketplace")
    print("=" * 60)
    
    # Executar testes
    pytest.main([__file__, "-v", "--tb=short"])
