"""
Testes unitários para health checks
Sistema de Prototipagem Sob Demanda
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException, status

from app.routers import health
from app.models.health import HealthStatus, ComponentHealth


class TestHealthRouter:
    """Testes para o router de health checks"""
    
    @pytest.mark.unit
    async def test_basic_health_check(self):
        """Testa health check básico"""
        # Act
        result = await health.health_check()
        
        # Assert
        assert result["status"] == "healthy"
        assert "timestamp" in result
        assert "version" in result
        assert "uptime" in result
    
    @pytest.mark.unit
    async def test_detailed_health_check(self):
        """Testa health check detalhado com todos os componentes"""
        # Arrange
        mock_redis = MagicMock()
        mock_redis.ping = AsyncMock(return_value=True)
        
        mock_mqtt = MagicMock()
        mock_mqtt.connect = AsyncMock(return_value=0)
        
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value.scalar.return_value = 1)
        
        # Act
        with patch('app.routers.health.redis_client', mock_redis), \
             patch('app.routers.health.mqtt_client', mock_mqtt), \
             patch('app.routers.health.get_db', return_value=mock_db):
            
            result = await health.detailed_health_check()
            
            # Assert
            assert result["status"] == "healthy"
            assert "components" in result
            assert "database" in result["components"]
            assert "redis" in result["components"]
            assert "mqtt" in result["components"]
            assert "prometheus" in result["components"]
            assert "grafana" in result["components"]
    
    @pytest.mark.unit
    async def test_database_health_check_success(self, mock_database_session):
        """Testa health check do banco com sucesso"""
        # Arrange
        mock_db = mock_database_session
        mock_db.execute.return_value.scalar.return_value = 1
        
        # Act
        result = await health.check_database_health(mock_db)
        
        # Assert
        assert result["status"] == "healthy"
        assert "database" in result
        assert result["database"]["status"] == "healthy"
        assert "response_time_ms" in result["database"]
    
    @pytest.mark.unit
    async def test_database_health_check_failure(self, mock_database_session):
        """Testa health check do banco com falha"""
        # Arrange
        mock_db = mock_database_session
        mock_db.execute.side_effect = Exception("Database connection failed")
        
        # Act
        result = await health.check_database_health(mock_db)
        
        # Assert
        assert result["status"] == "unhealthy"
        assert "database" in result
        assert result["database"]["status"] == "unhealthy"
        assert "error" in result["database"]
    
    @pytest.mark.unit
    async def test_redis_health_check_success(self):
        """Testa health check do Redis com sucesso"""
        # Arrange
        mock_redis = MagicMock()
        mock_redis.ping = AsyncMock(return_value=True)
        
        # Act
        with patch('app.routers.health.redis_client', mock_redis):
            result = await health.check_redis_health()
        
        # Assert
        assert result["status"] == "healthy"
        assert "redis" in result
        assert result["redis"]["status"] == "healthy"
    
    @pytest.mark.unit
    async def test_redis_health_check_failure(self):
        """Testa health check do Redis com falha"""
        # Arrange
        mock_redis = MagicMock()
        mock_redis.ping = AsyncMock(side_effect=Exception("Redis connection failed"))
        
        # Act
        with patch('app.routers.health.redis_client', mock_redis):
            result = await health.check_redis_health()
        
        # Assert
        assert result["status"] == "unhealthy"
        assert "redis" in result
        assert result["redis"]["status"] == "unhealthy"
    
    @pytest.mark.unit
    async def test_mqtt_health_check_success(self):
        """Testa health check do MQTT com sucesso"""
        # Arrange
        mock_mqtt = MagicMock()
        mock_mqtt.connect = AsyncMock(return_value=0)
        mock_mqtt.is_connected.return_value = True
        
        # Act
        with patch('app.routers.health.mqtt_client', mock_mqtt):
            result = await health.check_mqtt_health()
        
        # Assert
        assert result["status"] == "healthy"
        assert "mqtt" in result
        assert result["mqtt"]["status"] == "healthy"
    
    @pytest.mark.unit
    async def test_mqtt_health_check_failure(self):
        """Testa health check do MQTT com falha"""
        # Arrange
        mock_mqtt = MagicMock()
        mock_mqtt.connect = AsyncMock(return_value=1)  # Connection failed
        
        # Act
        with patch('app.routers.health.mqtt_client', mock_mqtt):
            result = await health.check_mqtt_health()
        
        # Assert
        assert result["status"] == "degraded"
        assert "mqtt" in result
        assert result["mqtt"]["status"] == "disconnected"
    
    @pytest.mark.unit
    async def test_external_services_health_check(self):
        """Testa health check de serviços externos"""
        # Arrange
        mock_httpx = AsyncMock()
        mock_httpx.get.return_value.status_code = 200
        mock_httpx.post.return_value.status_code = 200
        
        # Act
        with patch('app.routers.health.httpx_client', mock_httpx):
            result = await health.check_external_services()
        
        # Assert
        assert "external_services" in result
        assert "slant3d" in result["external_services"]
        assert "minimax" in result["external_services"]
    
    @pytest.mark.unit
    async def test_system_metrics_health_check(self):
        """Testa health check de métricas do sistema"""
        # Arrange
        mock_psutil = MagicMock()
        mock_psutil.cpu_percent.return_value = 45.2
        mock_psutil.virtual_memory.return_value.percent = 62.1
        mock_psutil.disk_usage.return_value.percent = 78.3
        
        # Act
        with patch('app.routers.health.psutil', mock_psutil):
            result = await health.get_system_metrics()
        
        # Assert
        assert "system" in result
        assert "cpu_percent" in result["system"]
        assert "memory_percent" in result["system"]
        assert "disk_percent" in result["system"]
    
    @pytest.mark.unit
    async def test_prometheus_metrics_health_check(self):
        """Testa health check das métricas do Prometheus"""
        # Arrange
        mock_requests = MagicMock()
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.text = "prometheus metrics"
        
        # Act
        with patch('app.routers.health.requests', mock_requests):
            result = await health.check_prometheus_health()
        
        # Assert
        assert "prometheus" in result
        assert result["prometheus"]["status"] == "healthy"
    
    @pytest.mark.unit
    async def test_grafana_metrics_health_check(self):
        """Testa health check do Grafana"""
        # Arrange
        mock_requests = MagicMock()
        mock_requests.get.return_value.status_code = 200
        
        # Act
        with patch('app.routers.health.requests', mock_requests):
            result = await health.check_grafana_health()
        
        # Assert
        assert "grafana" in result
        assert result["grafana"]["status"] == "healthy"
    
    @pytest.mark.unit
    async def test_aggregated_health_status_all_healthy(self):
        """Testa agregação de status com todos os componentes saudáveis"""
        # Arrange
        components = {
            "database": {"status": "healthy"},
            "redis": {"status": "healthy"},
            "mqtt": {"status": "healthy"},
            "prometheus": {"status": "healthy"},
            "grafana": {"status": "healthy"}
        }
        
        # Act
        result = health.aggregate_health_status(components)
        
        # Assert
        assert result == "healthy"
    
    @pytest.mark.unit
    async def test_aggregated_health_status_with_degraded(self):
        """Testa agregação de status com componentes degradados"""
        # Arrange
        components = {
            "database": {"status": "healthy"},
            "redis": {"status": "healthy"},
            "mqtt": {"status": "disconnected"},  # Degradado
            "prometheus": {"status": "healthy"},
            "grafana": {"status": "healthy"}
        }
        
        # Act
        result = health.aggregate_health_status(components)
        
        # Assert
        assert result == "degraded"
    
    @pytest.mark.unit
    async def test_aggregated_health_status_with_unhealthy(self):
        """Testa agregação de status com componentes não saudáveis"""
        # Arrange
        components = {
            "database": {"status": "unhealthy"},  # Não saudável
            "redis": {"status": "healthy"},
            "mqtt": {"status": "healthy"},
            "prometheus": {"status": "healthy"},
            "grafana": {"status": "healthy"}
        }
        
        # Act
        result = health.aggregate_health_status(components)
        
        # Assert
        assert result == "unhealthy"


class TestHealthEndpoints:
    """Testes para endpoints HTTP de health check"""
    
    @pytest.mark.unit
    async def test_health_endpoint(self, client):
        """Testa endpoint de health check básico"""
        # Act
        response = client.get("/health")
        
        # Assert
        assert response.status_code == 200
        assert "status" in response.json()
    
    @pytest.mark.unit
    async def test_health_detailed_endpoint(self, client):
        """Testa endpoint de health check detalhado"""
        # Act
        response = client.get("/health/detailed")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "components" in data
    
    @pytest.mark.unit
    async def test_health_ready_endpoint(self, client):
        """Testa endpoint de readiness check"""
        # Act
        response = client.get("/health/ready")
        
        # Assert
        assert response.status_code == 200
        assert "ready" in response.json()
    
    @pytest.mark.unit
    async def test_health_live_endpoint(self, client):
        """Testa endpoint de liveness check"""
        # Act
        response = client.get("/health/live")
        
        # Assert
        assert response.status_code == 200
        assert "alive" in response.json()
    
    @pytest.mark.unit
    async def test_metrics_endpoint(self, client):
        """Testa endpoint de métricas do Prometheus"""
        # Act
        response = client.get("/health/metrics")
        
        # Assert
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]


class TestHealthModels:
    """Testes para os modelos de health check"""
    
    @pytest.mark.unit
    def test_component_health_model(self):
        """Testa modelo ComponentHealth"""
        # Act
        component = ComponentHealth(
            name="database",
            status=HealthStatus.HEALTHY,
            response_time_ms=45.2,
            details={"connections": 10}
        )
        
        # Assert
        assert component.name == "database"
        assert component.status == HealthStatus.HEALTHY
        assert component.response_time_ms == 45.2
        assert component.details["connections"] == 10
    
    @pytest.mark.unit
    def test_health_status_enum(self):
        """Testa enumeração HealthStatus"""
        # Assert
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"
        assert HealthStatus.UNKNOWN.value == "unknown"
    
    @pytest.mark.unit
    def test_health_status_comparison(self):
        """Testa comparação de status de saúde"""
        # Assert
        assert HealthStatus.HEALTHY > HealthStatus.DEGRADED
        assert HealthStatus.DEGRADED > HealthStatus.UNHEALTHY
        assert HealthStatus.UNHEALTHY > HealthStatus.UNKNOWN