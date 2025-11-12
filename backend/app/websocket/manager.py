"""
Gerenciador de WebSocket para comunicação em tempo real
Sistema de Prototipagem Sob Demanda
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Set, Any
from datetime import datetime
import uuid

from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Logger específico para WebSocket
ws_logger = logging.getLogger("websocket.manager")


class WebSocketManager:
    """Gerenciador principal de conexões WebSocket"""
    
    def __init__(self):
        # Mapeamento de conexões ativas
        self.connections: Dict[str, WebSocket] = {}
        
        # Mapeamento de usuário -> conexões
        self.user_connections: Dict[str, Set[str]] = {}
        
        # Mapeamento de dispositivo -> conexões  
        self.device_connections: Dict[str, Set[str]] = {}
        
        # Salas de comunicação
        self.rooms: Dict[str, Set[str]] = {}
        
        # Configurações de heartbeat
        self.heartbeat_interval = 30  # segundos
        self.connection_timeout = 90  # segundos
        
        # Estatísticas
        self.stats = {
            "total_connections": 0,
            "active_connections": 0,
            "total_messages": 0,
            "messages_per_minute": 0
        }
    
    async def connect(
        self, 
        websocket: WebSocket,
        user_id: Optional[str] = None,
        device_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Estabelece nova conexão WebSocket
        
        Args:
            websocket: Conexão WebSocket
            user_id: ID do usuário (opcional)
            device_id: ID do dispositivo (opcional)
            metadata: Metadados adicionais
            
        Returns:
            str: ID único da conexão
        """
        # Aceita a conexão
        await websocket.accept()
        
        # Gera ID único para a conexão
        connection_id = str(uuid.uuid4())
        
        # Registra a conexão
        self.connections[connection_id] = websocket
        
        # Registra usuário se fornecido
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(connection_id)
            ws_logger.info(f"User {user_id} connected via WebSocket {connection_id}")
        
        # Registra dispositivo se fornecido
        if device_id:
            if device_id not in self.device_connections:
                self.device_connections[device_id] = set()
            self.device_connections[device_id].add(connection_id)
            ws_logger.info(f"Device {device_id} connected via WebSocket {connection_id}")
        
        # Atualiza estatísticas
        self.stats["total_connections"] += 1
        self.stats["active_connections"] = len(self.connections)
        
        # Inicia heartbeat para esta conexão
        asyncio.create_task(self._heartbeat_task(connection_id))
        
        # Envia mensagem de boas-vindas
        await self.send_message(connection_id, {
            "type": "connection_established",
            "data": {
                "connection_id": connection_id,
                "timestamp": datetime.utcnow().isoformat(),
                "server_info": {
                    "version": "1.0.0",
                    "features": ["heartbeat", "rooms", "broadcast"]
                }
            }
        })
        
        ws_logger.info(f"WebSocket connection established: {connection_id}")
        return connection_id
    
    async def disconnect(self, connection_id: str):
        """Desconecta WebSocket e limpa recursos"""
        if connection_id not in self.connections:
            return
        
        # Remove de todas as estruturas
        websocket = self.connections.pop(connection_id, None)
        
        # Remove de conexões de usuário
        for user_id, connections in self.user_connections.items():
            if connection_id in connections:
                connections.remove(connection_id)
                if not connections:
                    del self.user_connections[user_id]
                break
        
        # Remove de conexões de dispositivo
        for device_id, connections in self.device_connections.items():
            if connection_id in connections:
                connections.remove(connection_id)
                if not connections:
                    del self.device_connections[device_id]
                break
        
        # Remove de todas as salas
        for room_name, connections in self.rooms.items():
            if connection_id in connections:
                connections.remove(connection_id)
        
        # Fecha websocket se ainda ativo
        try:
            await websocket.close()
        except:
            pass  # WebSocket já pode estar fechado
        
        # Atualiza estatísticas
        self.stats["active_connections"] = len(self.connections)
        
        ws_logger.info(f"WebSocket connection closed: {connection_id}")
    
    async def send_message(self, connection_id: str, message: Dict[str, Any]) -> bool:
        """
        Envia mensagem para conexão específica
        
        Args:
            connection_id: ID da conexão
            message: Dados da mensagem
            
        Returns:
            bool: True se enviado com sucesso
        """
        if connection_id not in self.connections:
            return False
        
        try:
            websocket = self.connections[connection_id]
            await websocket.send_json(message)
            self.stats["total_messages"] += 1
            return True
        except WebSocketDisconnect:
            # Conexão perdida, remove da lista
            await self.disconnect(connection_id)
            return False
        except Exception as e:
            ws_logger.error(f"Error sending message to {connection_id}: {e}")
            return False
    
    async def broadcast(self, message: Dict[str, Any], exclude_connection: Optional[str] = None):
        """
        Envia mensagem para todas as conexões ativas
        
        Args:
            message: Dados da mensagem
            exclude_connection: ID da conexão a excluir (opcional)
        """
        disconnected = []
        
        for connection_id in list(self.connections.keys()):
            if connection_id != exclude_connection:
                success = await self.send_message(connection_id, message)
                if not success:
                    disconnected.append(connection_id)
        
        # Remove conexões perdidas
        for connection_id in disconnected:
            await self.disconnect(connection_id)
    
    async def send_to_user(self, user_id: str, message: Dict[str, Any]) -> int:
        """
        Envia mensagem para todas as conexões de um usuário
        
        Args:
            user_id: ID do usuário
            message: Dados da mensagem
            
        Returns:
            int: Número de mensagens enviadas
        """
        if user_id not in self.user_connections:
            return 0
        
        sent_count = 0
        disconnected = []
        
        for connection_id in self.user_connections[user_id]:
            success = await self.send_message(connection_id, message)
            if success:
                sent_count += 1
            else:
                disconnected.append(connection_id)
        
        # Remove conexões perdidas
        for connection_id in disconnected:
            await self.disconnect(connection_id)
        
        return sent_count
    
    async def send_to_device(self, device_id: str, message: Dict[str, Any]) -> int:
        """
        Envia mensagem para todas as conexões de um dispositivo
        
        Args:
            device_id: ID do dispositivo
            message: Dados da mensagem
            
        Returns:
            int: Número de mensagens enviadas
        """
        if device_id not in self.device_connections:
            return 0
        
        sent_count = 0
        disconnected = []
        
        for connection_id in self.device_connections[device_id]:
            success = await self.send_message(connection_id, message)
            if success:
                sent_count += 1
            else:
                disconnected.append(connection_id)
        
        # Remove conexões perdidas
        for connection_id in disconnected:
            await self.disconnect(connection_id)
        
        return sent_count
    
    async def join_room(self, connection_id: str, room_name: str):
        """
        Adiciona conexão a uma sala
        
        Args:
            connection_id: ID da conexão
            room_name: Nome da sala
        """
        if room_name not in self.rooms:
            self.rooms[room_name] = set()
        
        self.rooms[room_name].add(connection_id)
        
        # Notifica outros membros da sala
        await self.send_to_room(room_name, {
            "type": "user_joined_room",
            "data": {
                "connection_id": connection_id,
                "room_name": room_name,
                "timestamp": datetime.utcnow().isoformat()
            }
        }, exclude_connection=connection_id)
        
        ws_logger.info(f"Connection {connection_id} joined room {room_name}")
    
    async def leave_room(self, connection_id: str, room_name: str):
        """
        Remove conexão de uma sala
        
        Args:
            connection_id: ID da conexão
            room_name: Nome da sala
        """
        if room_name in self.rooms and connection_id in self.rooms[room_name]:
            self.rooms[room_name].remove(connection_id)
            
            # Remove sala vazia
            if not self.rooms[room_name]:
                del self.rooms[room_name]
            else:
                # Notifica outros membros
                await self.send_to_room(room_name, {
                    "type": "user_left_room",
                    "data": {
                        "connection_id": connection_id,
                        "room_name": room_name,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }, exclude_connection=connection_id)
            
            ws_logger.info(f"Connection {connection_id} left room {room_name}")
    
    async def send_to_room(self, room_name: str, message: Dict[str, Any], exclude_connection: Optional[str] = None):
        """
        Envia mensagem para todos os membros de uma sala
        
        Args:
            room_name: Nome da sala
            message: Dados da mensagem
            exclude_connection: ID da conexão a excluir (opcional)
        """
        if room_name not in self.rooms:
            return
        
        disconnected = []
        
        for connection_id in self.rooms[room_name]:
            if connection_id != exclude_connection:
                success = await self.send_message(connection_id, message)
                if not success:
                    disconnected.append(connection_id)
        
        # Remove conexões perdidas
        for connection_id in disconnected:
            await self.disconnect(connection_id)
    
    async def get_room_members(self, room_name: str) -> List[str]:
        """Retorna lista de membros de uma sala"""
        return list(self.rooms.get(room_name, set()))
    
    async def get_connection_info(self, connection_id: str) -> Dict[str, Any]:
        """Retorna informações sobre uma conexão"""
        if connection_id not in self.connections:
            return {}
        
        user_id = None
        device_id = None
        
        # Encontra usuário associado
        for uid, connections in self.user_connections.items():
            if connection_id in connections:
                user_id = uid
                break
        
        # Encontra dispositivo associado
        for did, connections in self.device_connections.items():
            if connection_id in connections:
                device_id = did
                break
        
        # Encontra salas associadas
        rooms = []
        for room_name, connections in self.rooms.items():
            if connection_id in connections:
                rooms.append(room_name)
        
        return {
            "connection_id": connection_id,
            "user_id": user_id,
            "device_id": device_id,
            "rooms": rooms,
            "connected_at": datetime.utcnow().isoformat()
        }
    
    async def cleanup_stale_connections(self):
        """Remove conexões stale (implementar lógica de timeout)"""
        # Implementar lógica de limpeza baseada em tempo de inatividade
        pass
    
    async def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do gerenciador"""
        return {
            **self.stats,
            "active_rooms": len(self.rooms),
            "connected_users": len(self.user_connections),
            "connected_devices": len(self.device_connections),
            "total_rooms": len(self.rooms)
        }
    
    async def _heartbeat_task(self, connection_id: str):
        """
        Tarefa de heartbeat para manter conexão ativa
        
        Args:
            connection_id: ID da conexão
        """
        try:
            while connection_id in self.connections:
                # Envia ping
                await self.send_message(connection_id, {
                    "type": "heartbeat",
                    "data": {
                        "timestamp": datetime.utcnow().isoformat()
                    }
                })
                
                # Espera intervalo
                await asyncio.sleep(self.heartbeat_interval)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            ws_logger.error(f"Heartbeat error for connection {connection_id}: {e}")
        finally:
            # Cleanup se necessário
            if connection_id in self.connections:
                await self.disconnect(connection_id)


# Instância global do gerenciador
websocket_manager = WebSocketManager()


# Função de dependência para WebSocket
async def get_websocket_manager() -> WebSocketManager:
    """Dependency injection para WebSocket Manager"""
    return websocket_manager


# Função para autenticação WebSocket
async def authenticate_websocket(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
) -> str:
    """
    Autentica conexão WebSocket usando token JWT
    
    Args:
        credentials: Credenciais HTTP Bearer
        
    Returns:
        str: ID do usuário autenticado
        
    Raises:
        HTTPException: Se token inválido
    """
    # TODO: Implementar verificação JWT real
    # Por enquanto, validação simples
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid credentials"
        )
    
    # Simulação de validação (implementar JWT real)
    try:
        # Aqui viria a lógica de verificação do JWT
        # Por enquanto, simula sucesso com user_id extraído
        user_id = "user_123"  # Simulação
        return user_id
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )