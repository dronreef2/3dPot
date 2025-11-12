"""
Configurações globais e fixtures para os testes
Sistema de Prototipagem Sob Demanda
"""
import asyncio
import os
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Adiciona o diretório app ao path do Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Importações condicionais para evitar erros de dependências
try:
    from app.main import app
    from app.config import Settings
    from app.database import get_session
    APP_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import app modules: {e}")
    APP_AVAILABLE = False
    
    # Mock classes quando app não está disponível
    class MockApp:
        pass
    
    class MockSettings:
        pass
    
    app = MockApp()
    Settings = MockSettings
    get_session = None


# ===== CONFIGURAÇÕES DE TESTE =====
@pytest.fixture(scope="session")
def event_loop():
    """Cria event loop para testes async"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings():
    """Configurações para ambiente de teste"""
    return Settings(
        # Database
        DATABASE_URL="postgresql://test:test@localhost:5432/test_db",
        
        # Security
        SECRET_KEY="test-secret-key-for-testing-only",
        ACCESS_TOKEN_EXPIRE_MINUTES=30,
        
        # API Keys (testes)
        SLANT3D_API_KEY="test-slant3d-key",
        MINIMAX_API_KEY="test-minimax-key",
        
        # Redis (mock)
        REDIS_URL="redis://localhost:6379/0",
        REDIS_PASSWORD="test-redis",
        
        # RabbitMQ (mock)
        RABBITMQ_URL="amqp://test:test@localhost:5672/",
        RABBITMQ_USER="test",
        RABBITMQ_PASSWORD="test",
        
        # MinIO (mock)
        MINIO_ENDPOINT="localhost:9000",
        MINIO_ACCESS_KEY="test-minio",
        MINIO_SECRET_KEY="test-minio-secret",
        MINIO_BUCKET_NAME="test-bucket",
        
        # Email (mock)
        SMTP_SERVER="smtp.test.com",
        SMTP_PORT=587,
        SMTP_USERNAME="test@test.com",
        SMTP_PASSWORD="test-password",
        
        # Monitoring (disabled for tests)
        PROMETHEUS_ENABLED=False,
        GRAFANA_ENABLED=False,
        
        # Simulation (enabled for tests)
        SIMULATION_MODE=True,
    )


# ===== CLIENTS DE TESTE =====
@pytest.fixture
def client():
    """Cliente FastAPI para testes HTTP"""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Cliente AsyncHTTP para testes assíncronos"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# ===== MOCKS PARA SERVIÇOS EXTERNOS =====
@pytest.fixture
def mock_database_session():
    """Mock da sessão do banco de dados"""
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.close = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.refresh = MagicMock()
    return mock_session


@pytest.fixture
def mock_database():
    """Mock completo do banco de dados"""
    with patch('app.database.get_session') as mock_get_session:
        mock_get_session.return_value = AsyncMock()
        yield mock_get_session


@pytest.fixture
def mock_httpx_client():
    """Mock do cliente HTTPX"""
    mock_client = AsyncMock()
    mock_client.get.return_value.json.return_value = {"status": "ok"}
    mock_client.post.return_value.json.return_value = {"result": "success"}
    mock_client.put.return_value.json.return_value = {"updated": True}
    mock_client.delete.return_value.status_code = 204
    return mock_client


@pytest.fixture
def mock_redis():
    """Mock do Redis"""
    redis_mock = MagicMock()
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.set = AsyncMock(return_value=True)
    redis_mock.delete = AsyncMock(return_value=1)
    redis_mock.exists = AsyncMock(return_value=False)
    return redis_mock


@pytest.fixture
def mock_slant3d_api():
    """Mock da API Slant3D"""
    with patch('app.services.slant3d_service.Slant3DService') as mock_service:
        mock_instance = AsyncMock()
        mock_instance.submit_project.return_value = {"project_id": "test-123"}
        mock_instance.get_project_status.return_value = {"status": "completed"}
        mock_instance.get_download_url.return_value = {"url": "https://test.com/download"}
        mock_service.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_minimax_api():
    """Mock da API Minimax"""
    with patch('app.services.minimax_service.MinimaxService') as mock_service:
        mock_instance = AsyncMock()
        mock_instance.chat_completion.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        mock_service.return_value = mock_instance
        yield mock_instance


# ===== DADOS DE TESTE =====
@pytest.fixture
def test_user_data():
    """Dados de usuário para testes"""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
        "username": "testuser"
    }


@pytest.fixture
def test_device_data():
    """Dados de dispositivo para testes"""
    return {
        "name": "ESP32 Test Device",
        "device_type": "ESP32",
        "serial_number": "ESP32-123456",
        "location": "Laboratory",
        "firmware_version": "1.0.0",
        "calibration_data": {"temperature_offset": 0.5}
    }


@pytest.fixture
def test_project_data():
    """Dados de projeto para testes"""
    return {
        "name": "Test Project",
        "description": "Projeto para testes automatizados",
        "project_type": "prototype",
        "specifications": {
            "dimensions": {"length": 100, "width": 50, "height": 25},
            "material": "PLA",
            "resolution": "0.2mm"
        }
    }


@pytest.fixture
def test_sensor_data():
    """Dados de sensor para testes"""
    return {
        "sensor_type": "temperature",
        "value": 25.5,
        "unit": "celsius",
        "timestamp": "2025-11-12T16:05:57Z",
        "quality": "high",
        "calibration": {"offset": 0.0, "scale": 1.0}
    }


# ===== FIXTURES DE AUTENTICAÇÃO =====
@pytest.fixture
def mock_jwt_token():
    """Mock de token JWT para testes"""
    import jwt
    
    payload = {
        "sub": "test-user-123",
        "email": "test@example.com",
        "exp": 9999999999  # Token válido por muito tempo
    }
    return jwt.encode(payload, "test-secret-key", algorithm="HS256")


@pytest.fixture
def mock_current_user():
    """Mock do usuário atual autenticado"""
    return {
        "id": 1,
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "is_active": True,
        "is_admin": False,
        "created_at": "2025-11-12T16:05:57Z"
    }


# ===== FIXTURES PARA WEBSOCKET =====
@pytest.fixture
def mock_websocket():
    """Mock para WebSocket"""
    mock_ws = MagicMock()
    mock_ws.send_json = MagicMock()
    mock_ws.receive_json = AsyncMock(return_value={"type": "test"})
    mock_ws.close = MagicMock()
    return mock_ws


# ===== FIXTURES PARA MQTT =====
@pytest.fixture
def mock_mqtt_client():
    """Mock do cliente MQTT"""
    mock_client = MagicMock()
    mock_client.connect = AsyncMock(return_value=0)
    mock_client.publish = MagicMock(return_value=AsyncMock())
    mock_client.subscribe = MagicMock(return_value=(0, 1))
    mock_client.loop_start = MagicMock()
    mock_client.loop_stop = MagicMock()
    mock_client.disconnect = MagicMock()
    return mock_client


# ===== HELPER FUNCTIONS =====
def create_test_db():
    """Cria banco de dados de teste (opcional)"""
    # Implementar criação de banco de teste se necessário
    pass


def cleanup_test_db():
    """Limpa banco de dados de teste (opcional)"""
    # Implementar limpeza do banco de teste se necessário
    pass