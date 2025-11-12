"""
3dPot Platform - WebSocket Manager
Criado em: 2025-11-12 22:42:43
Autor: MiniMax Agent

Gerenciador de conexões WebSocket para conversação real-time
"""

from typing import Dict, List, Optional
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import json
from datetime import datetime

from utils.logger import get_logger

logger = get_logger("websocket.manager")

class WebSocketManager:
    """
    Gerenciador de conexões WebSocket para múltiplas sessões simultâneas
    """
    
    def __init__(self):
        # Mapeamento session_id -> List[WebSocket]
        self.connections: Dict[str, List[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, session_id: str):
        """Aceita conexão WebSocket"""
        await websocket.accept()
        
        if session_id not in self.connections:
            self.connections[session_id] = []
        
        self.connections[session_id].append(websocket)
        
        logger.info(f"🔌 WebSocket conectado: session_id={session_id}, total_connections={len(self.connections[session_id])}")
        
        # Enviar confirmação de conexão
        await websocket.send_json({
            "type": "connection_established",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def disconnect(self, session_id: str):
        """Remove WebSocket da lista"""
        if session_id in self.connections:
            logger.info(f"🔌 WebSocket desconectado: session_id={session_id}, remaining_connections={len(self.connections[session_id])}")
            
            if len(self.connections[session_id]) == 0:
                del self.connections[session_id]
    
    async def broadcast_to_session(self, session_id: str, message: Dict[str, any]):
        """Envia mensagem para todos os WebSockets de uma sessão"""
        if session_id not in self.connections:
            logger.warning(f"⚠️ Tentativa de broadcast para sessão inexistente: {session_id}")
            return
        
        disconnected_websockets = []
        
        for websocket in self.connections[session_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"❌ Erro ao enviar mensagem via WebSocket: {e}")
                disconnected_websockets.append(websocket)
        
        # Remover WebSockets desconectados
        for websocket in disconnected_websockets:
            self.connections[session_id].remove(websocket)
        
        # Limpar sessão vazia
        if not self.connections[session_id]:
            del self.connections[session_id]
        
        logger.info(f"📡 Broadcast enviado para sessão {session_id}: {len(self.connections[session_id])} conexões")
    
    async def send_to_specific_websocket(self, websocket: WebSocket, message: Dict[str, any]):
        """Envia mensagem para WebSocket específico"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mensagem: {e}")
            raise
    
    def get_connection_count(self, session_id: Optional[str] = None) -> int:
        """Retorna número de conexões ativas"""
        if session_id:
            return len(self.connections.get(session_id, []))
        else:
            return sum(len(connections) for connections in self.connections.values())
    
    def get_active_sessions(self) -> List[str]:
        """Retorna lista de sessões ativas"""
        return list(self.connections.keys())