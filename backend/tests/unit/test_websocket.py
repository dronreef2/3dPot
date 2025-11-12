"""
Testes unitários para WebSocket
Sistema de Prototipagem Sob Demanda
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, call
import json

from app.websocket.manager import WebSocketManager
from app.websocket.handlers import (
    DeviceWebSocketHandler,
    ProjectWebSocketHandler,
    SystemWebSocketHandler
)


class TestWebSocketManager:
    """Testes para o gerenciador de WebSocket"""
    
    @pytest.mark.unit
    @pytest.mark.websocket
    def test_manager_initialization(self):
        """Testa inicialização do gerenciador"""
        # Act
        manager = WebSocketManager()
        
        # Assert
        assert manager.connections == {}
        assert len(manager.rooms) == 0
    
    @pytest.mark.unit
    @pytest.mark.websocket
    async def test_connect_websocket(self):
        """Testa conexão de WebSocket"""
        # Arrange
        manager = WebSocketManager()
        mock_websocket = MagicMock()
        mock_websocket.client = ("127.0.0.1", 12345)
        
        # Act
        connection_id = await manager.connect(mock_websocket)
        
        # Assert
        assert connection_id is not None
        assert connection_id in manager.connections
        assert manager.connections[connection_id] == mock_websocket
    
    @pytest.mark.unit
    @pytest.mark.websocket
    async def test_disconnect_websocket(self):
        """Testa desconexão de WebSocket"""
        # Arrange
        manager = WebSocketManager()
        mock_websocket = MagicMock()
        mock_websocket.client = ("127.0.0.1", 12345)
        
        # Conecta primeiro
        connection_id = await manager.connect(mock_websocket)
        
        # Act
        await manager.disconnect(connection_id)
        
        # Assert
        assert connection_id not in manager.connections
    
    @pytest.mark.unit
    @pytest.mark.websocket
    async def test_send_message_to_connection(self):
        """Testa envio de mensagem para conexão específica"""
        # Arrange
        manager = WebSocketManager()
        mock_websocket = MagicMock()
        mock_websocket.client = ("127.0.0.1", 12345)
        
        connection_id = await manager.connect(mock_websocket)
        message = {
            "type": "device_status",
            "data": {"device_id": 1, "status": "online"}
        }
        
        # Act
        await manager.send_message(connection_id, message)
        
        # Assert
        mock_websocket.send_json.assert_called_once_with(message)
    
    @pytest.mark.unit
    @pytest.mark.websocket
    async def test_broadcast_message(self):
        """Testa broadcast de mensagem para todas as conexões"""
        # Arrange
        manager = WebSocketManager()
        
        # Cria múltiplas conexões
        mock_ws1 = MagicMock()
        mock_ws1.client = ("127.0.0.1", 12345)
        connection_id1 = await manager.connect(mock_ws1)
        
        mock_ws2 = MagicMock()
        mock_ws2.client = ("127.0.0.1", 12346)
        connection_id2 = await manager.connect(mock_ws2)
        
        message = {
            "type": "system_alert",
            "data": {"message": "System restart"}
        }
        
        # Act
        await manager.broadcast(message)
        
        # Assert
        mock_ws1.send_json.assert_called_once_with(message)
        mock_ws2.send_json.assert_called_once_with(message)
    
    @pytest.mark.unit
    @pytest.mark.websocket
    async def test_join_room(self):
        """Testa entrada em sala"""
        # Arrange
        manager = WebSocketManager()
        mock_websocket = MagicMock()
        connection_id = await manager.connect(mock_websocket)
        
        room_name = "device_room_1"
        
        # Act
        await manager.join_room(connection_id, room_name)
        
        # Assert
        assert room_name in manager.rooms
        assert connection_id in manager.rooms[room_name]
    
    @pytest.mark.unit
    @pytest.mark.websocket
    async def test_send_to_room(self):
        """Testa envio de mensagem para sala específica"""
        # Arrange
        manager = WebSocketManager()
        
        mock_ws1 = MagicMock()
        connection_id1 = await manager.connect(mock_ws1)
        
        mock_ws2 = MagicMock()
        connection_id2 = await manager.connect(mock_ws2)
        
        room_name = "test_room"
        await manager.join_room(connection_id1, room_name)
        await manager.join_room(connection_id2, room_name)
        
        message = {
            "type": "room_message",
            "data": {"content": "Hello room!"}
        }
        
        # Act
        await manager.send_to_room(room_name, message)
        
        # Assert
        mock_ws1.send_json.assert_called_once_with(message)
        mock_ws2.send_json.assert_called_once_with(message)
    
    @pytest.mark.unit
    @pytest.mark.websocket
    async def test_leave_room(self):
        """Testa saída de sala"""
        # Arrange
        manager = WebSocketManager()
        mock_websocket = MagicMock()
        connection_id = await manager.connect(mock_websocket)
        
        room_name = "test_room"
        await manager.join_room(connection_id, room_name)
        
        # Act
        await manager.leave_room(connection_id, room_name)
        
        # Assert
        assert connection_id not in manager.rooms[room_name]


class TestDeviceWebSocketHandler:
    """Testes para o handler de dispositivos WebSocket"""
    
    @pytest.mark.unit
    @pytest.mark.websocket
    async def test_handle_device_connection(self, mock_websocket):
        """Testa tratamento de conexão de dispositivo"""
        # Arrange
        handler = DeviceWebSocketHandler()
        mock_websocket.receive_json = AsyncMock(return_value={
            "type": "device_connect",
            "data": {
                "device_id": 1,
                "device_type": "ESP32",
                "serial_number": "ESP32-123456"
            }
        })
        
        # Act
        await handler.handle_connection(mock_websocket)
        
        # Assert
        # Verifica se a mensagem de confirmação foi enviada
        calls = mock_websocket.send_json.call_args_list
        assert len(calls) > 0
        
        # Deve ter enviado confirmação de conexão
        connection_confirmed = any(
            call[0][0].get("type") == "connection_confirmed" 
            for call in calls
        )
        assert connection_confirmed
    
    @pytest.mark.unit
    @pytest.mark.websocket
    async def test_handle_sensor_data(self, mock_websocket):
        """Testa recebimento de dados de sensor"""
        # Arrange
        handler = DeviceWebSocketHandler()
        mock_websocket.receive_json = AsyncMock(return_value={
            "type": "sensor_data",
            "data": {
                "sensor_type": "temperature",
                "value": 25.5,
                "timestamp": "2025-11-12T16:05:57Z",
                "device_id": 1
            }
        })
        
        # Act
        await handler.handle_sensor_data(mock_websocket, {"device_id": 1})
        
        # Assert
        # Verifica se os dados foram processados
        # (a implementação específica pode variar)
        mock_websocket.send_json.assert_called()
    
    @pytest.mark.unit
    @pytest.mark.websocket
    async def test_send_device_command(self, mock_websocket):
        """Testa envio de comando para dispositivo"""
        # Arrange
        handler = DeviceWebSocketHandler()
        command_data = {
            "command": "restart",
            "parameters": {"delay": 5}
        }
        
        # Act
        await handler.send_command(mock_websocket, command_data)
        
        # Assert
        mock_websocket.send_json.assert_called_once_with({
            "type": "device_command",
            "data": command_data
        })
    
    @pytest.mark.unit
    @pytest.mark.websocket
    async def test_handle_device_status_update(self, mock_websocket):
        """Testa atualização de status de dispositivo"""
        # Arrange
        handler = DeviceWebSocketHandler()
        status_data = {
            "device_id": 1,
            "status": "online",
            "battery_level": 85,
            "signal_strength": -45
        }
        
        # Act
        await handler.handle_status_update(mock_websocket, status_data)
        
        # Assert
        mock_websocket.send_json.assert_called()
    
    @pytest.mark.unit
    @pytest.mark.websocket
    async def test_device_keepalive(self, mock_websocket):
        """Testa heartbeat/keepalive de dispositivo"""
        # Arrange
        handler = DeviceWebSocketHandler()
        mock_websocket.receive_json = AsyncMock(return_value={
            "type": "keepalive",
            "data": {
                "device_id": 1,
                "timestamp": "2025-11-12T16:05:57Z"
            }
        })
        
        # Act
        await handler.handle_keepalive(mock_websocket, {"device_id": 1})
        
        # Assert
        mock_websocket.send_json.assert_called_once_with({
            "type": "keepalive_ack",
            "data": {"device_id": 1}
        })


class TestProjectWebSocketHandler:
    """Testes para o handler de projetos WebSocket"""
    
    @pytest.mark.unit
    @pytest.mark.websocket
    async def test_project_status_updates(self, mock_websocket):
        """Testa atualizações de status de projeto"""
        # Arrange
        handler = ProjectWebSocketHandler()
        project_update = {
            "project_id": 1,
            "status": "printing",
            "progress": 45,
            "estimated_completion": "2025-11-13T10:00:00Z"
        }
        
        # Act
        await handler.broadcast_project_update(mock_websocket, project_update)
        
        # Assert
        mock_websocket.send_json.assert_called_once_with({
            "type": "project_status_update",
            "data": project_update
        })
    
    @pytest.mark.unit
    @pytest.mark.websocket
    async def test_3d_printing_progress(self, mock_websocket):
        """Testa progresso de impressão 3D"""
        # Arrange
        handler = ProjectWebSocketHandler()
        progress_data = {
            "project_id": 1,
            "layer_progress": 125,
            "total_layers": 250,
            "percentage": 50.0,
            "current_layer_time": 180,
            "estimated_remaining": 900
        }
        
        # Act
        await handler.broadcast_printing_progress(mock_websocket, progress_data)
        
        # Assert
        mock_websocket.send_json.assert_called_once_with({
            "type": "printing_progress",
            "data": progress_data
        })
    
    @pytest.mark.unit
    @pytest.mark.websocket
    async def test_project_completion_notification(self, mock_websocket):
        """Testa notificação de conclusão de projeto"""
        # Arrange
        handler = ProjectWebSocketHandler()
        completion_data = {
            "project_id": 1,
            "status": "completed",
            "completed_at": "2025-11-12T16:05:57Z",
            "download_url": "https://files.example.com/download/project_1.stl"
        }
        
        # Act
        await handler.broadcast_project_completion(mock_websocket, completion_data)
        
        # Assert
        mock_websocket.send_json.assert_called_once_with({
            "type": "project_completed",
            "data": completion_data
        })


class TestSystemWebSocketHandler:
    """Testes para o handler de sistema WebSocket"""
    
    @pytest.mark.unit
    @pytest.mark.websocket
    async def test_system_alerts(self, mock_websocket):
        """Testa alertas do sistema"""
        # Arrange
        handler = SystemWebSocketHandler()
        alert_data = {
            "alert_id": 1,
            "severity": "high",
            "title": "High Temperature Detected",
            "message": "Temperature exceeded threshold",
            "timestamp": "2025-11-12T16:05:57Z"
        }
        
        # Act
        await handler.broadcast_system_alert(mock_websocket, alert_data)
        
        # Assert
        mock_websocket.send_json.assert_called_once_with({
            "type": "system_alert",
            "data": alert_data
        })
    
    @pytest.mark.unit
    @pytest.mark.websocket
    async def test_system_status_updates(self, mock_websocket):
        """Testa atualizações de status do sistema"""
        # Arrange
        handler = SystemWebSocketHandler()
        status_data = {
            "component": "database",
            "status": "healthy",
            "response_time": 45.2,
            "timestamp": "2025-11-12T16:05:57Z"
        }
        
        # Act
        await handler.broadcast_status_update(mock_websocket, status_data)
        
        # Assert
        mock_websocket.send_json.assert_called_once_with({
            "type": "system_status",
            "data": status_data
        })
    
    @pytest.mark.unit
    @pytest.mark.websocket
    async def test_user_notifications(self, mock_websocket):
        """Testa notificações para usuários"""
        # Arrange
        handler = SystemWebSocketHandler()
        notification_data = {
            "user_id": 1,
            "title": "Project Completed",
            "message": "Your 3D print job is ready for download",
            "notification_type": "success",
            "timestamp": "2025-11-12T16:05:57Z"
        }
        
        # Act
        await handler.send_user_notification(mock_websocket, notification_data)
        
        # Assert
        mock_websocket.send_json.assert_called_once_with({
            "type": "user_notification",
            "data": notification_data
        })


class TestWebSocketProtocol:
    """Testes para protocolo WebSocket"""
    
    @pytest.mark.unit
    @pytest.mark.websocket
    async def test_message_format_validation(self, mock_websocket):
        """Testa validação de formato de mensagem"""
        # Arrange
        handler = SystemWebSocketHandler()
        
        # Teste com mensagem válida
        valid_message = {
            "type": "test_message",
            "data": {"key": "value"}
        }
        
        # Act & Assert - não deve levantar exceção
        try:
            await handler.validate_message(mock_websocket, valid_message)
        except Exception:
            pytest.fail("Valid message should not raise exception")
    
    @pytest.mark.unit
    @pytest.mark.websocket
    async def test_invalid_message_format(self, mock_websocket):
        """Testa mensagem com formato inválido"""
        # Arrange
        handler = SystemWebSocketHandler()
        
        # Teste com mensagem inválida
        invalid_message = {
            # Falta "type"
            "data": {"key": "value"}
        }
        
        # Act & Assert - deve levantar exceção
        with pytest.raises(ValueError):
            await handler.validate_message(mock_websocket, invalid_message)
    
    @pytest.mark.unit
    @pytest.mark.websocket
    async def test_message_routing(self, mock_websocket):
        """Testa roteamento de mensagens"""
        # Arrange
        handler = SystemWebSocketHandler()
        mock_websocket.receive_json = AsyncMock(return_value={
            "type": "system_status",
            "data": {"component": "test"}
        })
        
        # Act
        routed = await handler.route_message(mock_websocket, {
            "type": "system_status",
            "data": {"component": "test"}
        })
        
        # Assert
        assert routed is True  # Deve ser roteado com sucesso


class TestWebSocketIntegration:
    """Testes de integração WebSocket"""
    
    @pytest.mark.integration
    @pytest.mark.websocket
    async def test_real_time_device_monitoring(self):
        """Testa monitoramento em tempo real de dispositivos"""
        # Arrange
        manager = WebSocketManager()
        
        # Cria conexões simulando diferentes dispositivos
        device_connections = []
        for i in range(3):
            mock_ws = MagicMock()
            connection_id = await manager.connect(mock_ws)
            await manager.join_room(connection_id, f"device_room_{i+1}")
            device_connections.append((connection_id, mock_ws))
        
        # Act - Envia atualização para um dispositivo específico
        device_update = {
            "device_id": 1,
            "status": "online",
            "temperature": 25.5
        }
        await manager.send_to_room("device_room_1", {
            "type": "device_update",
            "data": device_update
        })
        
        # Assert
        # Apenas o dispositivo da sala device_room_1 deve receber a mensagem
        device_connections[0][1].send_json.assert_called()
        device_connections[1][1].send_json.assert_not_called()
        device_connections[2][1].send_json.assert_not_called()
    
    @pytest.mark.integration
    @pytest.mark.websocket
    async def test_broadcast_system_wide_notifications(self):
        """Testa broadcast de notificações para todo o sistema"""
        # Arrange
        manager = WebSocketManager()
        
        # Cria múltiplas conexões
        connections = []
        for i in range(5):
            mock_ws = MagicMock()
            connection_id = await manager.connect(mock_ws)
            connections.append((connection_id, mock_ws))
        
        # Act - Broadcast sistema completo
        notification = {
            "type": "system_maintenance",
            "data": {
                "title": "Scheduled Maintenance",
                "message": "System will be down for maintenance in 1 hour",
                "start_time": "2025-11-12T17:00:00Z"
            }
        }
        await manager.broadcast(notification)
        
        # Assert - Todas as conexões devem receber
        for _, mock_ws in connections:
            mock_ws.send_json.assert_called_once_with(notification)
    
    @pytest.mark.integration
    @pytest.mark.websocket
    async def test_websocket_connection_management(self):
        """Testa gerenciamento de conexões WebSocket"""
        # Arrange
        manager = WebSocketManager()
        
        # Act & Assert - Múltiplas conexões e desconexões
        connection_ids = []
        for i in range(10):
            mock_ws = MagicMock()
            connection_id = await manager.connect(mock_ws)
            connection_ids.append(connection_id)
            assert connection_id in manager.connections
        
        # Desconecta metade das conexões
        for i in range(0, 5):
            await manager.disconnect(connection_ids[i])
            assert connection_ids[i] not in manager.connections
        
        # Verifica que as outras 5 ainda estão conectadas
        for i in range(5, 10):
            assert connection_ids[i] in manager.connections