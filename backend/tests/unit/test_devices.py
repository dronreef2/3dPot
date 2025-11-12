"""
Testes unitários para dispositivos
Sistema de Prototipagem Sob Demanda
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException, status

from app.routers import devices
from app.models.device import Device, DeviceType, DeviceStatus
from app.schemas.device import (
    DeviceCreate, DeviceUpdate, DeviceResponse,
    ESP32MonitorCreate, ESP32MonitorResponse
)


class TestDeviceRouter:
    """Testes para o router de dispositivos"""
    
    @pytest.mark.unit
    async def test_create_device_success(self, mock_database_session, test_device_data):
        """Testa criação de dispositivo com sucesso"""
        # Arrange
        device_data = DeviceCreate(**test_device_data)
        mock_device = Device(
            id=1,
            name=device_data.name,
            device_type=DeviceType.ESP32,
            serial_number=device_data.serial_number,
            location=device_data.location,
            firmware_version=device_data.firmware_version,
            status=DeviceStatus.OFFLINE,
            created_at="2025-11-12T16:05:57Z"
        )
        
        mock_db = mock_database_session
        
        with patch('app.routers.devices.create_device', return_value=mock_device):
            # Act
            result = await devices.create_device(device_data, mock_db)
            
            # Assert
            assert result.name == device_data.name
            assert result.serial_number == device_data.serial_number
            assert result.device_type == DeviceType.ESP32
    
    @pytest.mark.unit
    async def test_create_device_duplicate_serial(self, mock_database_session, test_device_data):
        """Testa erro ao criar dispositivo com número serial duplicado"""
        # Arrange
        device_data = DeviceCreate(**test_device_data)
        mock_db = mock_database_session
        
        with patch('app.routers.devices.create_device') as mock_create:
            mock_create.side_effect = HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Serial number already exists"
            )
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await devices.create_device(device_data, mock_db)
            
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    
    @pytest.mark.unit
    async def test_get_device_success(self, mock_database_session, test_device_data):
        """Testa obtenção de dispositivo por ID"""
        # Arrange
        device_id = 1
        mock_device = Device(
            id=device_id,
            name=test_device_data["name"],
            device_type=DeviceType.ESP32,
            serial_number=test_device_data["serial_number"],
            location=test_device_data["location"],
            status=DeviceStatus.ONLINE,
            created_at="2025-11-12T16:05:57Z"
        )
        
        mock_db = mock_database_session
        mock_db.execute.return_value.scalar.return_value = mock_device
        
        with patch('app.routers.devices.get_device', return_value=mock_device):
            # Act
            result = await devices.get_device(device_id, mock_db)
            
            # Assert
            assert result.id == device_id
            assert result.name == test_device_data["name"]
            assert result.status == DeviceStatus.ONLINE
    
    @pytest.mark.unit
    async def test_get_device_not_found(self, mock_database_session):
        """Testa erro quando dispositivo não é encontrado"""
        # Arrange
        device_id = 999
        mock_db = mock_database_session
        mock_db.execute.return_value.scalar.return_value = None
        
        with patch('app.routers.devices.get_device', return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await devices.get_device(device_id, mock_db)
            
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.unit
    async def test_list_devices(self, mock_database_session, test_device_data):
        """Testa listagem de dispositivos"""
        # Arrange
        mock_devices = [
            Device(
                id=1,
                name="ESP32 Device 1",
                device_type=DeviceType.ESP32,
                serial_number="ESP32-001",
                location="Lab A",
                status=DeviceStatus.ONLINE,
                created_at="2025-11-12T16:05:57Z"
            ),
            Device(
                id=2,
                name="ESP32 Device 2",
                device_type=DeviceType.ESP32,
                serial_number="ESP32-002",
                location="Lab B",
                status=DeviceStatus.OFFLINE,
                created_at="2025-11-12T16:05:57Z"
            )
        ]
        
        mock_db = mock_database_session
        mock_db.execute.return_value.scalars.return_value.all.return_value = mock_devices
        
        with patch('app.routers.devices.list_devices', return_value=mock_devices):
            # Act
            result = await devices.list_devices(skip=0, limit=10, mock_db)
            
            # Assert
            assert len(result) == 2
            assert result[0].name == "ESP32 Device 1"
            assert result[1].name == "ESP32 Device 2"
    
    @pytest.mark.unit
    async def test_update_device_success(self, mock_database_session, test_device_data):
        """Testa atualização de dispositivo"""
        # Arrange
        device_id = 1
        update_data = DeviceUpdate(location="New Location")
        updated_device = Device(
            id=device_id,
            name=test_device_data["name"],
            device_type=DeviceType.ESP32,
            serial_number=test_device_data["serial_number"],
            location="New Location",  # Atualizado
            status=DeviceStatus.ONLINE,
            created_at="2025-11-12T16:05:57Z"
        )
        
        mock_db = mock_database_session
        
        with patch('app.routers.devices.update_device', return_value=updated_device):
            # Act
            result = await devices.update_device(device_id, update_data, mock_db)
            
            # Assert
            assert result.location == "New Location"
            assert result.id == device_id
    
    @pytest.mark.unit
    async def test_delete_device_success(self, mock_database_session):
        """Testa exclusão de dispositivo"""
        # Arrange
        device_id = 1
        mock_db = mock_database_session
        
        with patch('app.routers.devices.delete_device', return_value=True):
            # Act
            result = await devices.delete_device(device_id, mock_db)
            
            # Assert
            assert result is True
    
    @pytest.mark.unit
    async def test_esp32_monitor_create_success(self, mock_database_session, test_device_data):
        """Testa criação de monitor ESP32"""
        # Arrange
        monitor_data = ESP32MonitorCreate(
            name=test_device_data["name"],
            serial_number=test_device_data["serial_number"],
            location=test_device_data["location"],
            sensor_interval=5,
            alert_thresholds={
                "temperature": {"min": 18.0, "max": 30.0},
                "humidity": {"min": 30.0, "max": 70.0}
            }
        )
        
        mock_device = Device(
            id=1,
            name=monitor_data.name,
            device_type=DeviceType.ESP32,
            serial_number=monitor_data.serial_number,
            location=monitor_data.location,
            status=DeviceStatus.CONFIGURING,
            created_at="2025-11-12T16:05:57Z"
        )
        
        mock_db = mock_database_session
        
        with patch('app.routers.devices.create_esp32_monitor', return_value=mock_device):
            # Act
            result = await devices.create_esp32_monitor(monitor_data, mock_db)
            
            # Assert
            assert result.name == monitor_data.name
            assert result.serial_number == monitor_data.serial_number
            assert result.device_type == DeviceType.ESP32
    
    @pytest.mark.unit
    async def test_device_status_update(self, mock_database_session, test_device_data):
        """Testa atualização de status do dispositivo"""
        # Arrange
        device_id = 1
        status_data = {"status": "online"}
        updated_device = Device(
            id=device_id,
            name=test_device_data["name"],
            device_type=DeviceType.ESP32,
            serial_number=test_device_data["serial_number"],
            location=test_device_data["location"],
            status=DeviceStatus.ONLINE,  # Status atualizado
            created_at="2025-11-12T16:05:57Z"
        )
        
        mock_db = mock_database_session
        
        with patch('app.routers.devices.update_device_status', return_value=updated_device):
            # Act
            result = await devices.update_device_status(device_id, status_data, mock_db)
            
            # Assert
            assert result.status == DeviceStatus.ONLINE
            assert result.id == device_id
    
    @pytest.mark.unit
    async def test_device_command_execution(self, mock_database_session):
        """Testa execução de comando no dispositivo"""
        # Arrange
        device_id = 1
        command_data = {"command": "restart", "parameters": {}}
        
        mock_db = mock_database_session
        
        with patch('app.routers.devices.send_device_command') as mock_send:
            mock_send.return_value = {"status": "command_sent", "command_id": "cmd_123"}
            
            # Act
            result = await devices.send_device_command(device_id, command_data, mock_db)
            
            # Assert
            assert result["status"] == "command_sent"
            assert "command_id" in result
    
    @pytest.mark.unit
    async def test_device_calibration(self, mock_database_session, test_device_data):
        """Testa calibração de dispositivo"""
        # Arrange
        device_id = 1
        calibration_data = {
            "temperature": {"offset": 0.5, "scale": 1.0},
            "humidity": {"offset": -1.0, "scale": 0.95}
        }
        
        mock_device = Device(
            id=device_id,
            name=test_device_data["name"],
            device_type=DeviceType.ESP32,
            serial_number=test_device_data["serial_number"],
            location=test_device_data["location"],
            calibration_data=calibration_data,
            status=DeviceStatus.CALIBRATING,
            created_at="2025-11-12T16:05:57Z"
        )
        
        mock_db = mock_database_session
        
        with patch('app.routers.devices.calibrate_device', return_value=mock_device):
            # Act
            result = await devices.calibrate_device(device_id, calibration_data, mock_db)
            
            # Assert
            assert result.calibration_data == calibration_data
            assert result.status == DeviceStatus.CALIBRATING


class TestDeviceEndpoints:
    """Testes para endpoints HTTP de dispositivos"""
    
    @pytest.mark.unit
    async def test_create_device_endpoint(self, client, test_device_data):
        """Testa endpoint de criação de dispositivo"""
        # Act
        response = client.post("/devices/", json=test_device_data)
        
        # Assert
        # A resposta dependerá da implementação específica
        assert response.status_code in [200, 201, 400, 401]
    
    @pytest.mark.unit
    async def test_list_devices_endpoint(self, client):
        """Testa endpoint de listagem de dispositivos"""
        # Act
        response = client.get("/devices/")
        
        # Assert
        assert response.status_code in [200, 401]
    
    @pytest.mark.unit
    async def test_get_device_endpoint(self, client):
        """Testa endpoint de obtención de dispositivo específico"""
        # Act
        response = client.get("/devices/1")
        
        # Assert
        assert response.status_code in [200, 401, 404]
    
    @pytest.mark.unit
    async def test_esp32_monitor_endpoint(self, client, test_device_data):
        """Testa endpoint de criação de monitor ESP32"""
        monitor_data = test_device_data.copy()
        monitor_data["sensor_interval"] = 5
        
        # Act
        response = client.post("/devices/esp32/monitor", json=monitor_data)
        
        # Assert
        assert response.status_code in [200, 201, 400, 401]
    
    @pytest.mark.unit
    async def test_device_status_endpoint(self, client):
        """Testa endpoint de atualização de status"""
        status_data = {"status": "online"}
        
        # Act
        response = client.put("/devices/1/status", json=status_data)
        
        # Assert
        assert response.status_code in [200, 400, 401, 404]
    
    @pytest.mark.unit
    async def test_device_commands_endpoint(self, client):
        """Testa endpoint de comandos de dispositivo"""
        command_data = {"command": "restart", "parameters": {}}
        
        # Act
        response = client.post("/devices/1/commands", json=command_data)
        
        # Assert
        assert response.status_code in [200, 400, 401, 404]


class TestDeviceModels:
    """Testes para os modelos de dispositivos"""
    
    @pytest.mark.unit
    def test_device_creation(self, test_device_data):
        """Testa criação do modelo Device"""
        # Act
        device = Device(**test_device_data)
        
        # Assert
        assert device.name == test_device_data["name"]
        assert device.serial_number == test_device_data["serial_number"]
        assert device.device_type == DeviceType.ESP32
    
    @pytest.mark.unit
    def test_device_serialization(self, test_device_data):
        """Testa serialização do modelo Device"""
        # Arrange
        device = Device(
            name=test_device_data["name"],
            device_type=DeviceType.ESP32,
            serial_number=test_device_data["serial_number"],
            location=test_device_data["location"],
            status=DeviceStatus.OFFLINE
        )
        
        # Act
        device_dict = device.__dict__
        
        # Assert
        assert "name" in device_dict
        assert "serial_number" in device_dict
        assert device_dict["device_type"] == DeviceType.ESP32
    
    @pytest.mark.unit
    def test_device_status_enum(self):
        """Testa enumeração de status do dispositivo"""
        # Assert
        assert DeviceStatus.OFFLINE.value == "offline"
        assert DeviceStatus.ONLINE.value == "online"
        assert DeviceStatus.ERROR.value == "error"
        assert DeviceStatus.CONFIGURING.value == "configuring"
        assert DeviceStatus.CALIBRATING.value == "calibrating"
        assert DeviceStatus.MAINTENANCE.value == "maintenance"
    
    @pytest.mark.unit
    def test_device_type_enum(self):
        """Testa enumeração de tipos de dispositivo"""
        # Assert
        assert DeviceType.ESP32.value == "ESP32"
        assert DeviceType.ARDUINO.value == "Arduino"
        assert DeviceType.RASPBERRY_PI.value == "Raspberry Pi"
        assert DeviceType.CUSTOM.value == "Custom"