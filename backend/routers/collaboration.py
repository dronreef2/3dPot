"""
Routers FastAPI - Collaborative Features (Sprint 6+)
==================================================

Rotas para colaboração em tempo real, incluindo:
- Sessões de colaboração (CollaborationSession)
- Participantes (Participant)
- Mensagens de chat (Message)
- Video chamadas (VideoCall)
- Compartilhamento de tela (ScreenShare)

Autor: MiniMax Agent
Data: 2025-11-13
Versão: 2.0.0 - Sprint 6+
"""

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID
import json
import logging

from ..database import get_db
from ..core.config import settings
from ..services.collaboration_service import CollaborationService
from ..middleware.auth import get_current_user
from ..models import User

router = APIRouter()

# Instância do serviço
collaboration_service = CollaborationService()

# WebSocket manager para colaboração em tempo real
class CollaborationWebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str, user_id: str):
        await websocket.accept()
        
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
        
        self.active_connections[room_id][user_id] = websocket
        logging.info(f"WebSocket conectado: room {room_id}, user {user_id}")
    
    def disconnect(self, room_id: str, user_id: str):
        if room_id in self.active_connections:
            if user_id in self.active_connections[room_id]:
                del self.active_connections[room_id][user_id]
                logging.info(f"WebSocket desconectado: room {room_id}, user {user_id}")
            
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
    
    async def send_personal_message(self, message: str, room_id: str, user_id: str):
        if room_id in self.active_connections and user_id in self.active_connections[room_id]:
            await self.active_connections[room_id][user_id].send_text(message)
    
    async def broadcast(self, message: str, room_id: str):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id].values():
                await connection.send_text(message)

# Instância global do WebSocket manager
ws_manager = CollaborationWebSocketManager()

# =============================================================================
# ROTAS DE SESSÕES DE COLABORAÇÃO
# =============================================================================

@router.post("/sessions/", response_model=dict)
async def create_session(
    session_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar nova sessão de colaboração"""
    try:
        session = await collaboration_service.create_session(db, current_user.id, session_data)
        return {
            "success": True,
            "message": "Sessão de colaboração criada",
            "data": {
                "id": str(session.id),
                "nome": session.nome,
                "room_id": session.room_id,
                "status": session.status,
                "created_at": session.created_at.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sessions/", response_model=dict)
async def list_sessions(
    include_ended: bool = Query(False, description="Incluir sessões encerradas"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar sessões do usuário"""
    try:
        sessions = await collaboration_service.list_user_sessions(db, current_user.id, include_ended)
        return {
            "success": True,
            "data": {
                "sessions": [
                    {
                        "id": str(s.id),
                        "nome": s.nome,
                        "descricao": s.descricao,
                        "status": s.status,
                        "tipo_sessao": s.tipo_sessao,
                        "participant_count": len(s.participants),
                        "max_participantes": s.max_participantes,
                        "created_at": s.created_at.isoformat(),
                        "started_at": s.started_at.isoformat() if s.started_at else None,
                        "ended_at": s.ended_at.isoformat() if s.ended_at else None
                    }
                    for s in sessions
                ],
                "total": len(sessions)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sessions/{session_id}", response_model=dict)
async def get_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter detalhes da sessão de colaboração"""
    try:
        session = await collaboration_service.get_session(db, session_id, current_user.id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Sessão não encontrada")
        
        return {
            "success": True,
            "data": {
                "id": str(session.id),
                "nome": session.nome,
                "descricao": session.descricao,
                "room_id": session.room_id,
                "status": session.status,
                "tipo_sessao": session.tipo_sessao,
                "max_participantes": session.max_participantes,
                "configuracoes": {
                    "permitir_chat": session.permitir_chat,
                    "permitir_video": session.permitir_video,
                    "permitir_audio": session.permitir_audio,
                    "permitir_compartilhamento_tela": session.permitir_compartilhamento_tela,
                    "permitir_edicao_colaborativa": session.permitir_edicao_colaborativa,
                    "gravacao_ativa": session.gravacao_ativa,
                    "moderacao_ativa": session.moderacao_ativa,
                    "requer_aproacao_entrada": session.requer_aproacao_entrada
                },
                "participantes": [
                    {
                        "id": str(p.id),
                        "user_id": str(p.user.id),
                        "nome_exibicao": p.nome_exibicao,
                        "status": p.status,
                        "pode_moderar": p.pode_moderar,
                        "pode_compartilhar_tela": p.pode_compartilhar_tela,
                        "joined_at": p.joined_at.isoformat() if p.joined_at else None,
                        "last_activity": p.last_activity.isoformat() if p.last_activity else None
                    }
                    for p in session.participants
                ],
                "estatisticas": {
                    "total_messages": len(session.messages),
                    "total_video_calls": len(session.video_calls),
                    "total_screen_shares": len(session.screen_shares)
                },
                "timestamps": {
                    "created_at": session.created_at.isoformat(),
                    "started_at": session.started_at.isoformat() if session.started_at else None,
                    "ended_at": session.ended_at.isoformat() if session.ended_at else None
                }
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/sessions/{session_id}/end", response_model=dict)
async def end_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Encerrar sessão de colaboração"""
    try:
        success = await collaboration_service.end_session(db, session_id, current_user.id)
        return {
            "success": success,
            "message": "Sessão encerrada com sucesso"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =============================================================================
# ROTAS DE PARTICIPANTES
# =============================================================================

@router.post("/sessions/{session_id}/participants/", response_model=dict)
async def add_participant(
    session_id: UUID,
    participant_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Adicionar participante à sessão"""
    try:
        participant = await collaboration_service.add_participant(
            db, session_id, participant_data['user_id'], current_user.id, 
            participant_data.get('permissions')
        )
        return {
            "success": True,
            "message": "Participante adicionado com sucesso",
            "data": {
                "participant_id": str(participant.id),
                "user_id": str(participant.user_id),
                "status": participant.status
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sessions/{session_id}/join", response_model=dict)
async def join_session(
    session_id: UUID,
    device_info: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Participar de uma sessão"""
    try:
        participant = await collaboration_service.join_session(db, session_id, current_user.id, device_info)
        return {
            "success": True,
            "message": "Entrou na sessão com sucesso",
            "data": {
                "participant_id": str(participant.id),
                "user_id": str(participant.user_id),
                "status": participant.status,
                "joined_at": participant.joined_at.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sessions/{session_id}/leave", response_model=dict)
async def leave_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sair de uma sessão"""
    try:
        success = await collaboration_service.leave_session(db, session_id, current_user.id)
        return {
            "success": success,
            "message": "Saiu da sessão com sucesso"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/sessions/{session_id}/participants/{participant_id}/status", response_model=dict)
async def update_participant_status(
    session_id: UUID,
    participant_id: UUID,
    status_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualizar status do participante"""
    try:
        participant = await collaboration_service.update_participant_status(
            db, session_id, current_user.id, status_data['status'], status_data.get('additional_data')
        )
        return {
            "success": True,
            "message": "Status atualizado com sucesso",
            "data": {
                "participant_id": str(participant.id),
                "status": participant.status,
                "last_activity": participant.last_activity.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =============================================================================
# ROTAS DE CHAT E MENSAGENS
# =============================================================================

@router.get("/sessions/{session_id}/messages", response_model=dict)
async def get_messages(
    session_id: UUID,
    limit: int = Query(100, description="Limite de mensagens"),
    offset: int = Query(0, description="Offset para paginação"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter mensagens da sessão"""
    try:
        messages = await collaboration_service.get_messages(db, session_id, current_user.id, limit, offset)
        return {
            "success": True,
            "data": {
                "messages": [
                    {
                        "id": str(m.id),
                        "tipo": m.tipo,
                        "conteudo": m.conteudo,
                        "arquivo_path": m.arquivo_path,
                        "mime_type": m.mime_type,
                        "status": m.status,
                        "editado_em": m.editado_em.isoformat() if m.editado_em else None,
                        "participant": {
                            "id": str(m.participant.id),
                            "nome_exibicao": m.participant.nome_exibicao
                        },
                        "timestamp": m.created_at.isoformat()
                    }
                    for m in messages
                ],
                "total": len(messages)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sessions/{session_id}/messages/", response_model=dict)
async def send_message(
    session_id: UUID,
    message_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enviar mensagem no chat"""
    try:
        # Obter participant_id baseado no user_id
        participant = db.query(User).filter(User.id == current_user.id).first()
        if not participant:
            raise HTTPException(status_code=404, detail="Participante não encontrado")
        
        message = await collaboration_service.send_message(db, session_id, str(participant.id), message_data)
        return {
            "success": True,
            "message": "Mensagem enviada",
            "data": {
                "id": str(message.id),
                "tipo": message.tipo,
                "conteudo": message.conteudo,
                "timestamp": message.created_at.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/sessions/{session_id}/messages/{message_id}/edit", response_model=dict)
async def edit_message(
    session_id: UUID,
    message_id: UUID,
    edit_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Editar mensagem"""
    try:
        message = await collaboration_service.edit_message(db, message_id, current_user.id, edit_data['new_content'])
        return {
            "success": True,
            "message": "Mensagem editada com sucesso",
            "data": {
                "id": str(message.id),
                "conteudo": message.conteudo,
                "editado_em": message.editado_em.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =============================================================================
# ROTAS DE VIDEO CHAMADAS
# =============================================================================

@router.post("/sessions/{session_id}/video-calls/", response_model=dict)
async def start_video_call(
    session_id: UUID,
    call_config: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Iniciar chamada de vídeo"""
    try:
        video_call = await collaboration_service.start_video_call(db, session_id, current_user.id, call_config)
        return {
            "success": True,
            "message": "Chamada de vídeo iniciada",
            "data": {
                "call_id": str(video_call.id),
                "tipo": video_call.tipo,
                "status": video_call.status,
                "qualidade_video": video_call.qualidade_video,
                "framerate": video_call.framerate,
                "created_at": video_call.created_at.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/video-calls/{call_id}/end", response_model=dict)
async def end_video_call(
    call_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Encerrar chamada de vídeo"""
    try:
        success = await collaboration_service.end_video_call(db, call_id, current_user.id)
        return {
            "success": success,
            "message": "Chamada encerrada com sucesso"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =============================================================================
# ROTAS DE COMPARTILHAMENTO DE TELA
# =============================================================================

@router.post("/sessions/{session_id}/screen-share/", response_model=dict)
async def start_screen_share(
    session_id: UUID,
    share_config: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Iniciar compartilhamento de tela"""
    try:
        screen_share = await collaboration_service.start_screen_share(db, session_id, current_user.id, share_config)
        return {
            "success": True,
            "message": "Compartilhamento de tela iniciado",
            "data": {
                "share_id": str(screen_share.id),
                "tipo": screen_share.tipo,
                "aplicacao_nome": screen_share.aplicacao_nome,
                "window_title": screen_share.window_title,
                "qualidade": screen_share.qualidade,
                "started_at": screen_share.started_at.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =============================================================================
# ROTAS DE CONFIGURAÇÕES
# =============================================================================

@router.get("/settings/", response_model=dict)
async def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter configurações de colaboração do usuário"""
    try:
        settings = await collaboration_service.get_user_settings(db, current_user.id)
        return {
            "success": True,
            "data": {
                "microfone_padrao": settings.microfone_padrao,
                "camera_padrao": settings.camera_padrao,
                "autofalar": settings.autofalar,
                "video_automatico": settings.video_automatico,
                "qualidade_video_padrao": settings.qualidade_video_padrao,
                "framerate_padrao": settings.framerate_padrao,
                "notificacoes": {
                    "audios": settings.notificacoes_audios,
                    "video": settings.notificacoes_video,
                    "mensagens": settings.notificacoes_mensagens,
                    "som_notificacao": settings.som_notificacao
                },
                "privacidade": {
                    "perfil_visivel": settings.perfil_visivel,
                    "status_online_visivel": settings.status_online_visivel,
                    "permitir_convites_publicos": settings.permitir_convites_publicos
                },
                "produtividade": {
                    "auto_desconectar_inativo": settings.auto_desconectar_inativo,
                    "limite_minutos_inativo": settings.limite_minutos_inativo,
                    "gravacao_automatica": settings.gravacao_automatica
                },
                "interface": {
                    "tema_interface": settings.tema_interface,
                    "tamanho_fonte": settings.tamanho_fonte
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/settings/", response_model=dict)
async def update_user_settings(
    settings_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualizar configurações de colaboração"""
    try:
        settings = await collaboration_service.update_user_settings(db, current_user.id, settings_data)
        return {
            "success": True,
            "message": "Configurações atualizadas com sucesso",
            "data": {"updated_at": settings.updated_at.isoformat()}
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =============================================================================
# ROTAS DE ESTATÍSTICAS
# =============================================================================

@router.get("/sessions/{session_id}/statistics", response_model=dict)
async def get_session_statistics(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter estatísticas da sessão"""
    try:
        stats = await collaboration_service.get_session_statistics(db, session_id, current_user.id)
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# =============================================================================
# WEBSOCKET ENDPOINT
# =============================================================================

@router.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    user_id: str
):
    """WebSocket para comunicação em tempo real"""
    try:
        await ws_manager.connect(websocket, room_id, user_id)
        
        while True:
            # Receber dados do cliente
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Processar diferentes tipos de mensagem
            message_type = message_data.get("type")
            
            if message_type == "chat_message":
                # Mensagem de chat
                await ws_manager.broadcast(
                    json.dumps({
                        "type": "chat_message",
                        "user_id": user_id,
                        "message": message_data.get("message"),
                        "timestamp": message_data.get("timestamp")
                    }),
                    room_id
                )
            
            elif message_type == "status_update":
                # Atualização de status
                await ws_manager.broadcast(
                    json.dumps({
                        "type": "status_update",
                        "user_id": user_id,
                        "status": message_data.get("status"),
                        "timestamp": message_data.get("timestamp")
                    }),
                    room_id
                )
            
            elif message_type == "webrtc_offer":
                # Oferta WebRTC
                target_user = message_data.get("target_user")
                await ws_manager.send_personal_message(
                    json.dumps({
                        "type": "webrtc_offer",
                        "from_user": user_id,
                        "offer": message_data.get("offer")
                    }),
                    room_id,
                    target_user
                )
            
            elif message_type == "webrtc_answer":
                # Resposta WebRTC
                target_user = message_data.get("target_user")
                await ws_manager.send_personal_message(
                    json.dumps({
                        "type": "webrtc_answer",
                        "from_user": user_id,
                        "answer": message_data.get("answer")
                    }),
                    room_id,
                    target_user
                )
            
            elif message_type == "ice_candidate":
                # ICE candidate WebRTC
                target_user = message_data.get("target_user")
                await ws_manager.send_personal_message(
                    json.dumps({
                        "type": "ice_candidate",
                        "from_user": user_id,
                        "candidate": message_data.get("candidate")
                    }),
                    room_id,
                    target_user
                )
    
    except WebSocketDisconnect:
        ws_manager.disconnect(room_id, user_id)
        # Notificar outros participantes sobre desconexão
        await ws_manager.broadcast(
            json.dumps({
                "type": "user_disconnected",
                "user_id": user_id
            }),
            room_id
        )
    
    except Exception as e:
        logging.error(f"Erro no WebSocket: {e}")
        ws_manager.disconnect(room_id, user_id)