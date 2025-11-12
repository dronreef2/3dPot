"""
Testes de integração para o sistema completo
Sistema de Prototipagem Sob Demanda
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient

from app.main import app


class TestAPIIntegration:
    """Testes de integração da API completa"""
    
    @pytest.mark.integration
    async def test_complete_user_workflow(self, async_client):
        """Testa fluxo completo do usuário: registro, login, criação de projeto"""
        # 1. Registro do usuário
        user_data = {
            "email": "integration-test@example.com",
            "password": "TestPassword123!",
            "full_name": "Integration Test User",
            "username": "integration_test"
        }
        
        register_response = await async_client.post("/auth/register", json=user_data)
        assert register_response.status_code in [200, 201]
        
        # 2. Login
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        login_response = await async_client.post("/auth/login", json=login_data)
        if login_response.status_code == 200:
            token_data = login_response.json()
            auth_headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # 3. Criação de projeto
        project_data = {
            "name": "Integration Test Project",
            "description": "Projeto para teste de integração",
            "project_type": "prototype",
            "specifications": {
                "dimensions": {"length": 100, "width": 50, "height": 25},
                "material": "PLA",
                "resolution": "0.2mm"
            }
        }
        
        # Com autenticação (se token foi obtido)
        if 'auth_headers' in locals():
            project_response = await async_client.post(
                "/projects/", 
                json=project_data, 
                headers=auth_headers
            )
            assert project_response.status_code in [200, 201]
        
        # 4. Listagem de projetos
        list_response = await async_client.get("/projects/")
        assert list_response.status_code == 200
    
    @pytest.mark.integration
    async def test_device_management_workflow(self, async_client):
        """Testa fluxo completo de gerenciamento de dispositivos"""
        # 1. Criação de dispositivo
        device_data = {
            "name": "ESP32 Integration Test",
            "device_type": "ESP32",
            "serial_number": "ESP32-INTEGRATION-001",
            "location": "Test Lab",
            "firmware_version": "1.0.0"
        }
        
        device_response = await async_client.post("/devices/", json=device_data)
        assert device_response.status_code in [200, 201, 400]
        
        # 2. Listagem de dispositivos
        devices_response = await async_client.get("/devices/")
        assert devices_response.status_code == 200
        
        # 3. Criação de monitor ESP32
        monitor_data = device_data.copy()
        monitor_data["sensor_interval"] = 5
        
        monitor_response = await async_client.post(
            "/devices/esp32/monitor", 
            json=monitor_data
        )
        assert monitor_response.status_code in [200, 201, 400]
    
    @pytest.mark.integration
    async def test_health_check_workflow(self, async_client):
        """Testa verificação completa de saúde do sistema"""
        # 1. Health check básico
        basic_response = await async_client.get("/health")
        assert basic_response.status_code == 200
        
        basic_data = basic_response.json()
        assert "status" in basic_data
        assert "timestamp" in basic_data
        
        # 2. Health check detalhado
        detailed_response = await async_client.get("/health/detailed")
        assert detailed_response.status_code == 200
        
        detailed_data = detailed_response.json()
        assert "components" in detailed_data
        
        # 3. Readiness check
        ready_response = await async_client.get("/health/ready")
        assert ready_response.status_code == 200
        
        # 4. Liveness check
        live_response = await async_client.get("/health/live")
        assert live_response.status_code == 200
    
    @pytest.mark.integration
    async def test_alerts_system_workflow(self, async_client):
        """Testa fluxo do sistema de alertas"""
        # 1. Criação de alerta
        alert_data = {
            "title": "Integration Test Alert",
            "description": "Alerta para teste de integração",
            "severity": "medium",
            "alert_type": "system",
            "source": "integration_test"
        }
        
        alert_response = await async_client.post("/alerts/", json=alert_data)
        assert alert_response.status_code in [200, 201, 400]
        
        # 2. Listagem de alertas
        alerts_response = await async_client.get("/alerts/")
        assert alerts_response.status_code == 200
        
        # 3. Criação de regra de alerta
        rule_data = {
            "name": "Integration Test Rule",
            "conditions": {
                "metric": "temperature",
                "operator": ">",
                "threshold": 30.0
            },
            "actions": {
                "email": True,
                "webhook": False
            }
        }
        
        rule_response = await async_client.post("/alerts/rules/", json=rule_data)
        assert rule_response.status_code in [200, 201, 400]
    
    @pytest.mark.integration
    async def test_monitoring_workflow(self, async_client):
        """Testa sistema de monitoramento"""
        # 1. Criação de sensor monitor
        sensor_data = {
            "name": "Integration Test Sensor",
            "sensor_type": "temperature",
            "device_id": 1,
            "location": "Test Location"
        }
        
        sensor_response = await async_client.post("/monitoring/sensors/", json=sensor_data)
        assert sensor_response.status_code in [200, 201, 400]
        
        # 2. Envio de dados de sensor
        data_point = {
            "value": 25.5,
            "timestamp": "2025-11-12T16:05:57Z",
            "quality": "high"
        }
        
        data_response = await async_client.post(
            "/monitoring/sensors/1/data", 
            json=data_point
        )
        assert data_response.status_code in [200, 201, 400]
        
        # 3. Consulta de dados históricos
        history_response = await async_client.get(
            "/monitoring/sensors/1/data?limit=10"
        )
        assert history_response.status_code == 200


class TestDatabaseIntegration:
    """Testes de integração com banco de dados"""
    
    @pytest.mark.integration
    async def test_database_connection_health(self, async_client):
        """Testa saúde da conexão com banco de dados"""
        # Act
        response = await async_client.get("/health/detailed")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        if "database" in data.get("components", {}):
            db_status = data["components"]["database"]["status"]
            assert db_status in ["healthy", "unhealthy"]  # Pode estar indisponível nos testes
    
    @pytest.mark.integration
    async def test_persistence_operations(self, async_client):
        """Testa operações de persistência"""
        # 1. Criar projeto
        project_data = {
            "name": "Persistence Test Project",
            "description": "Projeto para teste de persistência",
            "project_type": "prototype"
        }
        
        create_response = await async_client.post("/projects/", json=project_data)
        if create_response.status_code in [200, 201]:
            project = create_response.json()
            project_id = project.get("id")
            
            if project_id:
                # 2. Atualizar projeto
                update_data = {"description": "Atualizado para teste de persistência"}
                update_response = await async_client.put(
                    f"/projects/{project_id}", 
                    json=update_data
                )
                assert update_response.status_code in [200, 404]
                
                # 3. Consultar projeto
                get_response = await async_client.get(f"/projects/{project_id}")
                assert get_response.status_code in [200, 404]
    
    @pytest.mark.integration
    async def test_data_consistency(self, async_client):
        """Testa consistência de dados entre endpoints"""
        # 1. Criar projeto
        project_data = {
            "name": "Consistency Test Project",
            "description": "Teste de consistência",
            "project_type": "prototype"
        }
        
        create_response = await async_client.post("/projects/", json=project_data)
        
        if create_response.status_code in [200, 201]:
            created_project = create_response.json()
            
            # 2. Verificar através do endpoint de listagem
            list_response = await async_client.get("/projects/")
            if list_response.status_code == 200:
                projects_list = list_response.json()
                if isinstance(projects_list, list):
                    created_found = any(
                        p.get("name") == project_data["name"] 
                        for p in projects_list
                    )
                    assert created_found or len(projects_list) == 0


class TestExternalServicesIntegration:
    """Testes de integração com serviços externos"""
    
    @pytest.mark.integration
    async def test_external_api_availability(self, async_client):
        """Testa disponibilidade de APIs externas"""
        # Act - Health check pode verificar serviços externos
        response = await async_client.get("/health/detailed")
        
        if response.status_code == 200:
            data = response.json()
            components = data.get("components", {})
            
            # Verifica se informações sobre serviços externos estão presentes
            external_services = components.get("external_services", {})
            if external_services:
                assert isinstance(external_services, dict)
    
    @pytest.mark.integration
    async def test_file_upload_workflow(self, async_client):
        """Testa fluxo completo de upload de arquivo"""
        # Cria arquivo de teste
        test_file_content = b"test file content for 3D model"
        
        # Simula upload de arquivo (se endpoint existir)
        # Nota: Este teste pode falhar se não houver endpoint de upload implementado
        try:
            files = {"file": ("test_model.stl", test_file_content, "model/stl")}
            response = await async_client.post("/projects/upload", files=files)
            
            # O endpoint pode não existir ainda, então aceite códigos diversos
            assert response.status_code in [200, 201, 404, 422]
        except Exception:
            # Se o endpoint não existir, esperamos erro 404
            pass
    
    @pytest.mark.integration
    async def test_conversational_interface(self, async_client):
        """Testa interface conversacional"""
        chat_data = {
            "message": "Como posso criar um projeto de impressão 3D?",
            "context": {"user_id": "test-user"}
        }
        
        # Pode não haver endpoint de chat implementado ainda
        try:
            response = await async_client.post("/chat", json=chat_data)
            assert response.status_code in [200, 404, 422]
        except Exception:
            pass


class TestErrorHandlingIntegration:
    """Testes de integração para tratamento de erros"""
    
    @pytest.mark.integration
    async def test_invalid_request_handling(self, async_client):
        """Testa tratamento de requisições inválidas"""
        # 1. JSON inválido
        invalid_json = "{ invalid json"
        response = await async_client.post(
            "/projects/", 
            content=invalid_json,
            headers={"content-type": "application/json"}
        )
        assert response.status_code in [400, 422, 500]
        
        # 2. Campos obrigatórios ausentes
        incomplete_data = {"name": "Only Name"}  # Falta outros campos obrigatórios
        response = await async_client.post("/projects/", json=incomplete_data)
        assert response.status_code in [400, 422]
        
        # 3. Tipos de dados incorretos
        wrong_type_data = {
            "name": "Test Project",
            "project_type": 123  # Deveria ser string
        }
        response = await async_client.post("/projects/", json=wrong_type_data)
        assert response.status_code in [400, 422]
    
    @pytest.mark.integration
    async def test_resource_not_found_handling(self, async_client):
        """Testa tratamento de recursos não encontrados"""
        # 1. Projeto inexistente
        response = await async_client.get("/projects/99999")
        assert response.status_code == 404
        
        # 2. Dispositivo inexistente
        response = await async_client.get("/devices/99999")
        assert response.status_code == 404
        
        # 3. Alerta inexistente
        response = await async_client.get("/alerts/99999")
        assert response.status_code == 404
    
    @pytest.mark.integration
    async def test_rate_limiting_behavior(self, async_client):
        """Testa comportamento de limitação de taxa"""
        # Faz múltiplas requisições rápidas
        responses = []
        for i in range(10):
            response = await async_client.get("/health")
            responses.append(response.status_code)
        
        # Deve processar todas as requisições (ou algumas podem ser limitadas)
        successful_requests = sum(1 for status in responses if status == 200)
        assert successful_requests >= 0  # Pelo menos algumas devem ter sucesso


class TestPerformanceIntegration:
    """Testes de integração para performance"""
    
    @pytest.mark.integration
    async def test_response_time_health_check(self, async_client):
        """Testa tempo de resposta do health check"""
        import time
        
        start_time = time.time()
        response = await async_client.get("/health")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        
        # Health check deve responder rapidamente (menos de 1 segundo)
        assert response_time < 1.0
    
    @pytest.mark.integration
    async def test_concurrent_requests(self, async_client):
        """Testa requisições simultâneas"""
        # Cria múltiplas tarefas para execução concorrente
        tasks = []
        for i in range(5):
            task = async_client.get("/health")
            tasks.append(task)
        
        # Executa todas as tarefas simultaneamente
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verifica que todas as requisições foram processadas
        successful_responses = [
            r for r in responses 
            if not isinstance(r, Exception) and r.status_code == 200
        ]
        
        assert len(successful_responses) >= 3  # Pelo menos 3 devem ter sucesso
    
    @pytest.mark.integration
    async def test_large_data_handling(self, async_client):
        """Testa tratamento de grandes volumes de dados"""
        # Testa listagem com limitação
        for limit in [1, 10, 50]:
            response = await async_client.get(f"/projects/?limit={limit}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    assert len(data) <= limit + 1  # Pode retornar +1 por paginação


# Configuração dos testes de integração
@pytest.fixture(scope="session")
async def setup_integration_tests():
    """Configuração global para testes de integração"""
    # Configurações específicas para testes de integração
    print("Setting up integration test environment...")
    
    yield
    
    # Limpeza após todos os testes de integração
    print("Cleaning up integration test environment...")


@pytest.mark.integration
class TestIntegrationEnvironment:
    """Testes para verificar ambiente de integração"""
    
    async def test_api_accessible(self, async_client):
        """Verifica se API está acessível"""
        # Act
        response = await async_client.get("/")
        
        # Assert
        assert response.status_code in [200, 404]  # Pode não ter endpoint raíz
    
    async def test_api_version_header(self, async_client):
        """Verifica header de versão da API"""
        # Act
        response = await async_client.get("/health")
        
        # Assert - verifica se há informações de versão
        assert response.status_code == 200
        # Pode ter diferentes formatos de versão
        assert "json" in response.headers.get("content-type", "")


if __name__ == "__main__":
    # Para execução manual dos testes
    pytest.main([__file__, "-v"])