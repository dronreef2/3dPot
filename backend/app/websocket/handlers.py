"""
Handlers para diferentes tipos de comunicação WebSocket
Sistema de Prototipagem Sob Demanda
"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from fastapi import WebSocket, WebSocketDisconnect

from app.websocket.manager import websocket_manager

# Logger
ws_logger = logging.getLogger("websocket.handlers")


class BaseWebSocketHandler:
    """Classe base para todos os handlers WebSocket"""
    
    def __init__(self, manager=None):
        self.manager = manager or websocket_manager
        self.supported_types = []
    
    async def handle_message(self, websocket: WebSocket, message: Dict[str, Any], connection_id: str):
        """
        Processa mensagem recebida
        
        Args:
            websocket: Conexão WebSocket
            message: Mensagem recebida
            connection_id: ID da conexão
        """
        message_type = message.get("type")
        
        if message_type not in self.supported_types:
            await self.send_error(websocket, f"Unsupported message type: {message_type}")
            return
        
        # Dispatch para método específico
        handler_method = getattr(self, f"handle_{message_type}", self.handle_unknown)
        await handler_method(websocket, message.get("data", {}), connection_id)
    
    async def handle_unknown(self, websocket: WebSocket, data: Dict[str, Any], connection_id: str):
        """Handler para mensagens desconhecidas"""
        await self.send_error(websocket, f"Handler not found for this message type")
    
    async def send_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """Envia mensagem via WebSocket"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            ws_logger.error(f"Error sending message: {e}")
    
    async def send_error(self, websocket: WebSocket, error_message: str):
        """Envia mensagem de erro"""
        await self.send_message(websocket, {
            "type": "error",
            "data": {
                "message": error_message,
                "timestamp": datetime.utcnow().isoformat()
            }
        })
    
    async def send_success(self, websocket: WebSocket, message: str, data: Optional[Dict[str, Any]] = None):
        """Envia mensagem de sucesso"""
        response = {
            "type": "success",
            "data": {
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        if data:
            response["data"].update(data)
        
        await self.send_message(websocket, response)


class DeviceWebSocketHandler(BaseWebSocketHandler):
    """Handler para comunicação com dispositivos IoT"""
    
    def __init__(self, manager=None):
        super().__init__(manager)
        self.supported_types = [
            "device_connect",
            "device_disconnect", 
            "sensor_data",
            "device_status",
            "device_command",
            "keepalive",
            "calibration",
            "firmware_update"
        ]
        
        # Estado dos dispositivos
        self.device_states: Dict[str, Dict[str, Any]] = {}
    
    async def handle_device_connect(self, websocket: WebSocket, data: Dict[str, Any], connection_id: str):
        """Processa conexão de dispositivo"""
        device_id = data.get("device_id")
        device_type = data.get("device_type")
        serial_number = data.get("serial_number")
        
        if not device_id:
            await self.send_error(websocket, "device_id is required")
            return
        
        # Atualiza estado do dispositivo
        self.device_states[device_id] = {
            "device_id": device_id,
            "device_type": device_type,
            "serial_number": serial_number,
            "connection_id": connection_id,
            "status": "connected",
            "last_seen": datetime.utcnow().isoformat(),
            "capabilities": data.get("capabilities", []),
            "metadata": data.get("metadata", {})
        }
        
        # Registra dispositivo no gerenciador
        await self.manager.send_to_device(device_id, {
            "type": "device_connected",
            "data": {
                "device_id": device_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        })
        
        await self.send_success(websocket, "Device connected successfully", {
            "device_id": device_id,
            "server_time": datetime.utcnow().isoformat()
        })
        
        ws_logger.info(f"Device {device_id} connected via WebSocket")
    
    async def handle_device_disconnect(self, websocket: WebSocket, data: Dict[str, Any], connection_id: str):
        """Processa desconexão de dispositivo"""
        device_id = data.get("device_id")
        
        if device_id and device_id in self.device_states:
            # Atualiza estado
            self.device_states[device_id]["status"] = "disconnected"
            self.device_states[device_id]["last_seen"] = datetime.utcnow().isoformat()
            
            # Notifica outros clientes
            await self.manager.broadcast({
                "type": "device_disconnected",
                "data": {
                    "device_id": device_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            })
            
            ws_logger.info(f"Device {device_id} disconnected")
        
        await self.send_success(websocket, "Device disconnected")
    
    async def handle_sensor_data(self, websocket: WebSocket, data: Dict[str, Any], connection_id: str):
        """Processa dados de sensor"""
        device_id = data.get("device_id")
        sensor_type = data.get("sensor_type")
        value = data.get("value")
        unit = data.get("unit")
        timestamp = data.get("timestamp")
        
        if not all([device_id, sensor_type, value]):
            await self.send_error(websocket, "device_id, sensor_type, and value are required")
            return
        
        # Valida dados do sensor
        sensor_data = {
            "device_id": device_id,
            "sensor_type": sensor_type,
            "value": value,
            "unit": unit,
            "timestamp": timestamp or datetime.utcnow().isoformat(),
            "connection_id": connection_id,
            "data_id": str(uuid.uuid4())
        }
        
        # Atualiza estado do dispositivo
        if device_id in self.device_states:
            self.device_states[device_id]["last_seen"] = datetime.utcnow().isoformat()
            self.device_states[device_id]["last_data"] = sensor_data
        
        # Envia dados para clientes订阅
        await self.manager.send_to_room(f"device_{device_id}", {
            "type": "sensor_data",
            "data": sensor_data
        })
        
        # Processa alertas se necessário
        await self._process_sensor_alerts(sensor_data)
        
        # Confirma recebimento
        await self.send_success(websocket, "Sensor data received", {
            "data_id": sensor_data["data_id"]
        })
    
    async def handle_device_status(self, websocket: WebSocket, data: Dict[str, Any], connection_id: str):
        """Processa atualização de status do dispositivo"""
        device_id = data.get("device_id")
        status = data.get("status")
        battery_level = data.get("battery_level")
        signal_strength = data.get("signal_strength")
        
        if not device_id:
            await self.send_error(websocket, "device_id is required")
            return
        
        # Atualiza estado
        if device_id in self.device_states:
            self.device_states[device_id].update({
                "status": status or "unknown",
                "battery_level": battery_level,
                "signal_strength": signal_strength,
                "last_seen": datetime.utcnow().isoformat()
            })
        
        # Notifica订阅s
        await self.manager.broadcast({
            "type": "device_status_update",
            "data": {
                "device_id": device_id,
                "status": status,
                "battery_level": battery_level,
                "signal_strength": signal_strength,
                "timestamp": datetime.utcnow().isoformat()
            }
        })
        
        await self.send_success(websocket, "Status updated")
    
    async def handle_device_command(self, websocket: WebSocket, data: Dict[str, Any], connection_id: str):
        """Processa comando para dispositivo"""
        device_id = data.get("device_id")
        command = data.get("command")
        parameters = data.get("parameters", {})
        
        if not all([device_id, command]):
            await self.send_error(websocket, "device_id and command are required")
            return
        
        # Simula execução de comando
        command_result = await self._execute_device_command(device_id, command, parameters)
        
        # Envia resultado de volta para dispositivo
        await self.manager.send_to_device(device_id, {
            "type": "command_result",
            "data": {
                "command": command,
                "result": command_result,
                "timestamp": datetime.utcnow().isoformat()
            }
        })
        
        await self.send_success(websocket, "Command sent", {
            "command": command,
            "result": command_result
        })
    
    async def handle_keepalive(self, websocket: WebSocket, data: Dict[str, Any], connection_id: str):
        """Processa keepalive/heartbeat"""
        device_id = data.get("device_id")
        
        if device_id and device_id in self.device_states:
            self.device_states[device_id]["last_seen"] = datetime.utcnow().isoformat()
        
        await self.send_success(websocket, "Keepalive acknowledged")
    
    async def handle_calibration(self, websocket: WebSocket, data: Dict[str, Any], connection_id: str):
        """Processa dados de calibração"""
        device_id = data.get("device_id")
        calibration_data = data.get("calibration_data", {})
        
        if not device_id:
            await self.send_error(websocket, "device_id is required")
            return
        
        # Salva dados de calibração
        if device_id in self.device_states:
            self.device_states[device_id]["calibration"] = calibration_data
            self.device_states[device_id]["last_calibration"] = datetime.utcnow().isoformat()
        
        await self.send_success(websocket, "Calibration data saved")
    
    async def handle_firmware_update(self, websocket: WebSocket, data: Dict[str, Any], connection_id: str):
        """Processa solicitação de atualização de firmware"""
        device_id = data.get("device_id")
        firmware_version = data.get("firmware_version")
        
        if not device_id:
            await self.send_error(websocket, "device_id is required")
            return
        
        # Simula verificação de firmware
        update_available = await self._check_firmware_update(device_id, firmware_version)
        
        if update_available:
            await self.manager.send_to_device(device_id, {
                "type": "firmware_update_available",
                "data": {
                    "current_version": firmware_version,
                    "new_version": "1.1.0",
                    "update_url": "https://firmware.example.com/device_1.1.0.bin",
                    "changelog": "Bug fixes and performance improvements"
                }
            })
        
        await self.send_success(websocket, "Firmware update check completed", {
            "update_available": update_available
        })
    
    async def _execute_device_command(self, device_id: str, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Executa comando no dispositivo"""
        # Simulação de execução
        command_map = {
            "restart": {"action": "restart", "delay": 5},
            "reset": {"action": "factory_reset"},
            "calibrate": {"action": "start_calibration", "sensors": parameters.get("sensors", [])},
            "update_config": {"action": "config_update", "config": parameters.get("config", {})},
            "get_status": {"action": "status_request"},
            "test_sensors": {"action": "sensor_test", "duration": parameters.get("duration", 10)}
        }
        
        return command_map.get(command, {"action": "unknown_command"})
    
    async def _check_firmware_update(self, device_id: str, current_version: str) -> bool:
        """Verifica se há atualização de firmware disponível"""
        # Lógica de verificação simulada
        return current_version != "1.1.0"  # Sempre há atualização disponível
    
    async def _process_sensor_alerts(self, sensor_data: Dict[str, Any]):
        """Processa alertas baseados nos dados do sensor"""
        device_id = sensor_data["device_id"]
        sensor_type = sensor_data["sensor_type"]
        value = sensor_data["value"]
        
        # Define limites de alerta (deveria vir do banco de dados)
        alert_thresholds = {
            "temperature": {"min": 18.0, "max": 30.0},
            "humidity": {"min": 30.0, "max": 70.0},
            "pressure": {"min": 900.0, "max": 1100.0}
        }
        
        if sensor_type in alert_thresholds:
            threshold = alert_thresholds[sensor_type]
            
            if value < threshold["min"] or value > threshold["max"]:
                # Envia alerta
                await self.manager.broadcast({
                    "type": "sensor_alert",
                    "data": {
                        "device_id": device_id,
                        "sensor_type": sensor_type,
                        "value": value,
                        "threshold": threshold,
                        "severity": "medium",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                })
    
    def get_device_status(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Retorna status de um dispositivo"""
        return self.device_states.get(device_id)
    
    def get_all_devices(self) -> List[Dict[str, Any]]:
        """Retorna lista de todos os dispositivos conectados"""
        return list(self.device_states.values())


class ProjectWebSocketHandler(BaseWebSocketHandler):
    """Handler para comunicação relacionada a projetos"""
    
    def __init__(self, manager=None):
        super().__init__(manager)
        self.supported_types = [
            "subscribe_project",
            "unsubscribe_project",
            "project_update",
            "printing_progress",
            "project_completed",
            "project_error"
        ]
    
    async def handle_subscribe_project(self, websocket: WebSocket, data: Dict[str, Any], connection_id: str):
        """Inscreve cliente para atualizações de projeto"""
        project_id = data.get("project_id")
        
        if not project_id:
            await self.send_error(websocket, "project_id is required")
            return
        
        # Adiciona à sala do projeto
        room_name = f"project_{project_id}"
        await self.manager.join_room(connection_id, room_name)
        
        await self.send_success(websocket, f"Subscribed to project {project_id}", {
            "project_id": project_id
        })
    
    async def handle_unsubscribe_project(self, websocket: WebSocket, data: Dict[str, Any], connection_id: str):
        """Remove inscrição de atualizações de projeto"""
        project_id = data.get("project_id")
        
        if not project_id:
            await self.send_error(websocket, "project_id is required")
            return
        
        # Remove da sala do projeto
        room_name = f"project_{project_id}"
        await self.manager.leave_room(connection_id, room_name)
        
        await self.send_success(websocket, f"Unsubscribed from project {project_id}")
    
    async def handle_project_update(self, websocket: WebSocket, data: Dict[str, Any], connection_id: str):
        """Processa atualização de projeto"""
        project_id = data.get("project_id")
        status = data.get("status")
        progress = data.get("progress")
        
        if not project_id:
            await self.send_error(websocket, "project_id is required")
            return
        
        # Envia atualização para todos os inscritos
        await self.manager.send_to_room(f"project_{project_id}", {
            "type": "project_status_update",
            "data": {
                "project_id": project_id,
                "status": status,
                "progress": progress,
                "timestamp": datetime.utcnow().isoformat()
            }
        })
        
        await self.send_success(websocket, "Project update sent")
    
    async def handle_printing_progress(self, websocket: WebSocket, data: Dict[str, Any], connection_id: str):
        """Processa progresso de impressão 3D"""
        project_id = data.get("project_id")
        layer_progress = data.get("layer_progress")
        total_layers = data.get("total_layers")
        percentage = data.get("percentage")
        
        if not project_id:
            await self.send_error(websocket, "project_id is required")
            return
        
        # Calcula progresso
        if layer_progress and total_layers:
            percentage = (layer_progress / total_layers) * 100
        
        # Envia progresso para inscritos
        await self.manager.send_to_room(f"project_{project_id}", {
            "type": "printing_progress",
            "data": {
                "project_id": project_id,
                "layer_progress": layer_progress,
                "total_layers": total_layers,
                "percentage": percentage,
                "estimated_time_remaining": data.get("estimated_time_remaining"),
                "current_layer_time": data.get("current_layer_time"),
                "timestamp": datetime.utcnow().isoformat()
            }
        })
    
    async def handle_project_completed(self, websocket: WebSocket, data: Dict[str, Any], connection_id: str):
        """Processa conclusão de projeto"""
        project_id = data.get("project_id")
        download_url = data.get("download_url")
        
        if not project_id:
            await self.send_error(websocket, "project_id is required")
            return
        
        # Envia notificação de conclusão
        await self.manager.send_to_room(f"project_{project_id}", {
            "type": "project_completed",
            "data": {
                "project_id": project_id,
                "status": "completed",
                "download_url": download_url,
                "completed_at": datetime.utcnow().isoformat()
            }
        })
    
    async def handle_project_error(self, websocket: WebSocket, data: Dict[str, Any], connection_id: str):
        """Processa erro em projeto"""
        project_id = data.get("project_id")
        error_type = data.get("error_type")
        error_message = data.get("error_message")
        
        if not project_id:
            await self.send_error(websocket, "project_id is required")
            return
        
        # Envia notificação de erro
        await self.manager.send_to_room(f"project_{project_id}", {
            "type": "project_error",
            "data": {
                "project_id": project_id,
                "error_type": error_type,
                "error_message": error_message,
                "timestamp": datetime.utcnow().isoformat()
            }
        })


class SystemWebSocketHandler(BaseWebSocketHandler):
    """Handler para comunicação do sistema"""
    
    def __init__(self, manager=None):
        super().__init__(manager)
        self.supported_types = [
            "system_alert",
            "system_status",
            "user_notification",
            "broadcast_message"
        ]
    
    async def handle_system_alert(self, websocket: WebSocket, data: Dict[str, Any], connection_id: str):
        """Processa alerta do sistema"""
        alert_data = {
            "alert_id": str(uuid.uuid4()),
            "severity": data.get("severity", "info"),
            "title": data.get("title"),
            "message": data.get("message"),
            "source": data.get("source", "system"),
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": data.get("metadata", {})
        }
        
        # Broadcast para todos os usuários
        await self.manager.broadcast({
            "type": "system_alert",
            "data": alert_data
        })
        
        await self.send_success(websocket, "System alert sent")
    
    async def handle_system_status(self, websocket: WebSocket, data: Dict[str, Any], connection_id: str):
        """Processa atualização de status do sistema"""
        status_data = {
            "component": data.get("component"),
            "status": data.get("status"),
            "response_time": data.get("response_time"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Envia status para inscritos (se houver sistema de status)
        await self.manager.broadcast({
            "type": "system_status",
            "data": status_data
        })
        
        await self.send_success(websocket, "System status sent")
    
    async def handle_user_notification(self, websocket: WebSocket, data: Dict[str, Any], connection_id: str):
        """Processa notificação para usuário específico"""
        user_id = data.get("user_id")
        title = data.get("title")
        message = data.get("message")
        notification_type = data.get("notification_type", "info")
        
        if not user_id:
            await self.send_error(websocket, "user_id is required")
            return
        
        notification_data = {
            "notification_id": str(uuid.uuid4()),
            "title": title,
            "message": message,
            "notification_type": notification_type,
            "timestamp": datetime.utcnow().isoformat(),
            "read": False
        }
        
        # Envia para usuário específico
        sent_count = await self.manager.send_to_user(user_id, {
            "type": "user_notification",
            "data": notification_data
        })
        
        await self.send_success(websocket, "User notification sent", {
            "sent_to": sent_count
        })
    
    async def handle_broadcast_message(self, websocket: WebSocket, data: Dict[str, Any], connection_id: str):
        """Processa mensagem broadcast"""
        message = data.get("message")
        message_type = data.get("message_type", "info")
        
        if not message:
            await self.send_error(websocket, "message is required")
            return
        
        # Broadcast para todos
        await self.manager.broadcast({
            "type": "broadcast_message",
            "data": {
                "message": message,
                "message_type": message_type,
                "timestamp": datetime.utcnow().isoformat(),
                "from": data.get("from", "system")
            }
        })
        
        await self.send_success(websocket, "Broadcast message sent")


# Instâncias globais dos handlers
device_handler = DeviceWebSocketHandler()
project_handler = ProjectWebSocketHandler()
system_handler = SystemWebSocketHandler()