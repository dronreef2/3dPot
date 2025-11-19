"""
Router WebSocket para comunicação em tempo real
Sistema de Prototipagem Sob Demanda
"""
import asyncio
import logging
from typing import Dict, Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.websocket.manager import WebSocketManager, get_websocket_manager
from app.websocket.handlers import (
    DeviceWebSocketHandler,
    ProjectWebSocketHandler, 
    SystemWebSocketHandler
)

# Logger
ws_logger = logging.getLogger("websocket.router")

# Security
security = HTTPBearer()

# Router principal
websocket_router = APIRouter(prefix="/ws", tags=["websocket"])

# Handlers globais
device_handler = DeviceWebSocketHandler()
project_handler = ProjectWebSocketHandler()
system_handler = SystemWebSocketHandler()


@websocket_router.websocket("/connect")
async def websocket_connect(
    websocket: WebSocket,
    user_id: str = Query(None, description="ID do usuário autenticado"),
    device_id: str = Query(None, description="ID do dispositivo"),
    manager: WebSocketManager = Depends(get_websocket_manager)
):
    """
    Endpoint principal de conexão WebSocket
    
    Suporta:
    - Usuários autenticados
    - Dispositivos IoT
    - Conexões anônimas (limitadas)
    """
    try:
        # Extrai parâmetros da query
        metadata = {
            "user_agent": websocket.headers.get("user-agent", ""),
            "remote_addr": websocket.client.host if websocket.client else "",
            "query_params": {
                "user_id": user_id,
                "device_id": device_id
            }
        }
        
        # Estabelece conexão
        connection_id = await manager.connect(
            websocket=websocket,
            user_id=user_id,
            device_id=device_id,
            metadata=metadata
        )
        
        ws_logger.info(f"WebSocket connection established: {connection_id}")
        
        # Loop principal de comunicação
        await websocket_communication_loop(websocket, connection_id, manager)
        
    except WebSocketDisconnect:
        ws_logger.info(f"WebSocket disconnected: {connection_id}")
    except Exception as e:
        ws_logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass


async def websocket_communication_loop(
    websocket: WebSocket,
    connection_id: str,
    manager: WebSocketManager
):
    """
    Loop principal de comunicação WebSocket
    
    Args:
        websocket: Conexão WebSocket
        connection_id: ID da conexão
        manager: Gerenciador WebSocket
    """
    try:
        while True:
            # Recebe mensagem
            data = await websocket.receive_text()
            
            try:
                # Parse do JSON
                message = parse_message(data)
                
                # Processa mensagem
                await process_websocket_message(websocket, message, connection_id, manager)
                
            except Exception as e:
                ws_logger.error(f"Error processing message: {e}")
                await send_error(websocket, f"Error processing message: {str(e)}")
                
    except WebSocketDisconnect:
        # Conexão perdida
        await manager.disconnect(connection_id)
        raise
    except Exception as e:
        ws_logger.error(f"Communication loop error: {e}")
        await manager.disconnect(connection_id)
        raise


def parse_message(data: str) -> Dict[str, Any]:
    """
    Parse e validação de mensagem JSON
    
    Args:
        data: Dados JSON brutos
        
    Returns:
        Dict[str, Any]: Mensagem processada
        
    Raises:
        ValueError: Se mensagem inválida
    """
    try:
        message = __import__('json').loads(data)
        
        # Validação básica
        if not isinstance(message, dict):
            raise ValueError("Message must be a JSON object")
        
        if "type" not in message:
            raise ValueError("Message must have 'type' field")
        
        # Garante que existe campo data
        if "data" not in message:
            message["data"] = {}
        
        return message
        
    except ValueError as e:
        raise ValueError(f"Invalid JSON message: {e}")


async def process_websocket_message(
    websocket: WebSocket,
    message: Dict[str, Any],
    connection_id: str,
    manager: WebSocketManager
):
    """
    Processa mensagem WebSocket e envia para handler apropriado
    
    Args:
        websocket: Conexão WebSocket
        message: Mensagem processada
        connection_id: ID da conexão
        manager: Gerenciador WebSocket
    """
    message_type = message.get("type")
    message_data = message.get("data", {})
    
    ws_logger.debug(f"Processing message type: {message_type}")
    
    # Dispatch para handler apropriado
    if message_type.startswith("device_"):
        await device_handler.handle_message(websocket, message, connection_id)
    elif message_type.startswith("project_"):
        await project_handler.handle_message(websocket, message, connection_id)
    elif message_type.startswith(("system_", "user_", "broadcast_")):
        await system_handler.handle_message(websocket, message, connection_id)
    else:
        # Mensagens gerais
        await handle_general_message(websocket, message, connection_id, manager)


async def handle_general_message(
    websocket: WebSocket,
    message: Dict[str, Any],
    connection_id: str,
    manager: WebSocketManager
):
    """
    Handler para mensagens gerais
    
    Args:
        websocket: Conexão WebSocket
        message: Mensagem
        connection_id: ID da conexão
        manager: Gerenciador WebSocket
    """
    message_type = message.get("type")
    data = message.get("data", {})
    
    if message_type == "ping":
        # Resposta para ping
        await send_success(websocket, "pong", {"timestamp": data.get("timestamp")})
        
    elif message_type == "join_room":
        # Entrar em sala
        room_name = data.get("room_name")
        if room_name:
            await manager.join_room(connection_id, room_name)
            await send_success(websocket, f"Joined room: {room_name}")
        else:
            await send_error(websocket, "room_name is required")
            
    elif message_type == "leave_room":
        # Sair de sala
        room_name = data.get("room_name")
        if room_name:
            await manager.leave_room(connection_id, room_name)
            await send_success(websocket, f"Left room: {room_name}")
        else:
            await send_error(websocket, "room_name is required")
            
    elif message_type == "get_connection_info":
        # Informações da conexão
        info = await manager.get_connection_info(connection_id)
        await send_success(websocket, "Connection info", info)
        
    elif message_type == "get_stats":
        # Estatísticas do servidor
        stats = await manager.get_stats()
        await send_success(websocket, "Server stats", stats)
        
    elif message_type == "subscribe_device":
        # Inscrever para atualizações de dispositivo
        device_id = data.get("device_id")
        if device_id:
            room_name = f"device_{device_id}"
            await manager.join_room(connection_id, room_name)
            await send_success(websocket, f"Subscribed to device {device_id}")
        else:
            await send_error(websocket, "device_id is required")
            
    elif message_type == "unsubscribe_device":
        # Desinscrever de dispositivo
        device_id = data.get("device_id")
        if device_id:
            room_name = f"device_{device_id}"
            await manager.leave_room(connection_id, room_name)
            await send_success(websocket, f"Unsubscribed from device {device_id}")
        else:
            await send_error(websocket, "device_id is required")
    
    else:
        await send_error(websocket, f"Unknown message type: {message_type}")


async def send_success(websocket: WebSocket, message: str, data: Dict[str, Any] = None):
    """Envia mensagem de sucesso"""
    response = {
        "type": "success",
        "data": {
            "message": message
        }
    }
    if data:
        response["data"].update(data)
    
    try:
        await websocket.send_json(response)
    except Exception as e:
        ws_logger.error(f"Error sending success message: {e}")


async def send_error(websocket: WebSocket, error_message: str):
    """Envia mensagem de erro"""
    try:
        await websocket.send_json({
            "type": "error",
            "data": {
                "message": error_message
            }
        })
    except Exception as e:
        ws_logger.error(f"Error sending error message: {e}")


# ===== ENDPOINTS HTTP PARA WEBSOCKET MANAGEMENT =====

@websocket_router.get("/status")
async def websocket_status(manager: WebSocketManager = Depends(get_websocket_manager)):
    """
    Status do servidor WebSocket
    """
    stats = await manager.get_stats()
    return {
        "status": "online",
        "websocket": stats,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }


@websocket_router.get("/devices/connected")
async def get_connected_devices(manager: WebSocketManager = Depends(get_websocket_manager)):
    """
    Lista dispositivos conectados
    """
    devices = device_handler.get_all_devices()
    return {
        "devices": devices,
        "count": len(devices),
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }


@websocket_router.get("/devices/{device_id}/status")
async def get_device_status(
    device_id: str,
    manager: WebSocketManager = Depends(get_websocket_manager)
):
    """
    Status de dispositivo específico
    """
    status = device_handler.get_device_status(device_id)
    if not status:
        return {
            "device_id": device_id,
            "status": "not_found",
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }
    
    return {
        "device_id": device_id,
        "status": status,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }


@websocket_router.post("/broadcast")
async def broadcast_message(
    message: Dict[str, Any],
    manager: WebSocketManager = Depends(get_websocket_manager)
):
    """
    Envia mensagem broadcast para todas as conexões
    """
    await manager.broadcast(message)
    return {
        "status": "broadcast_sent",
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }


@websocket_router.post("/devices/{device_id}/command")
async def send_device_command(
    device_id: str,
    command_data: Dict[str, Any],
    manager: WebSocketManager = Depends(get_websocket_manager)
):
    """
    Envia comando para dispositivo específico
    """
    command = command_data.get("command")
    parameters = command_data.get("parameters", {})
    
    if not command:
        return {
            "error": "command is required",
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }
    
    # Envia comando para dispositivo
    sent_count = await manager.send_to_device(device_id, {
        "type": "device_command",
        "data": {
            "command": command,
            "parameters": parameters,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }
    })
    
    return {
        "device_id": device_id,
        "command": command,
        "sent_to": sent_count,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }


@websocket_router.post("/users/{user_id}/notify")
async def send_user_notification(
    user_id: str,
    notification: Dict[str, Any],
    manager: WebSocketManager = Depends(get_websocket_manager)
):
    """
    Envia notificação para usuário específico
    """
    sent_count = await manager.send_to_user(user_id, {
        "type": "user_notification",
        "data": notification
    })
    
    return {
        "user_id": user_id,
        "notification": notification,
        "sent_to": sent_count,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }


# ===== WEBSOCKET ROOMS MANAGEMENT =====

@websocket_router.get("/rooms")
async def list_rooms(manager: WebSocketManager = Depends(get_websocket_manager)):
    """
    Lista todas as salas ativas
    """
    rooms_info = {}
    for room_name, connections in manager.rooms.items():
        rooms_info[room_name] = {
            "member_count": len(connections),
            "members": list(connections)
        }
    
    return {
        "rooms": rooms_info,
        "total_rooms": len(rooms_info),
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }


@websocket_router.post("/rooms/{room_name}/broadcast")
async def broadcast_to_room(
    room_name: str,
    message: Dict[str, Any],
    manager: WebSocketManager = Depends(get_websocket_manager)
):
    """
    Envia mensagem para sala específica
    """
    await manager.send_to_room(room_name, message)
    return {
        "room": room_name,
        "message": message,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }


# ===== HEALTH CHECKS =====

@websocket_router.get("/health")
async def websocket_health(manager: WebSocketManager = Depends(get_websocket_manager)):
    """
    Health check para WebSocket
    """
    stats = await manager.get_stats()
    
    return {
        "status": "healthy",
        "stats": stats,
        "features": [
            "real_time_communication",
            "device_monitoring", 
            "project_updates",
            "system_notifications"
        ],
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }