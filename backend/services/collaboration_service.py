"""
3dPot v2.0 - Serviço de Colaboração em Tempo Real (Sprint 6+)
============================================================

Serviço para colaboração em tempo real via WebRTC e Socket.IO, incluindo:
- Gestão de sessões de colaboração (CollaborationSession)
- Participantes e permissões (Participant)
- Chat e mensagens (Message)
- Video chamadas e áudio (VideoCall)
- Compartilhamento de tela (ScreenShare)
- Versionamento colaborativo (FileVersion)

Autor: MiniMax Agent
Data: 2025-11-13
Versão: 2.0.0 - Sprint 6+
"""

import os
import json
import logging
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from uuid import UUID
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from sqlalchemy.orm import joinedload

from backend.core.config import settings
from backend.models import (
    CollaborationSession, Participant, Message, VideoCall, VideoCallParticipant,
    ScreenShare, FileVersion, CollaborationSetting,
    User, Project
)

logger = logging.getLogger(__name__)


class CollaborationService:
    """Serviço principal de colaboração em tempo real"""
    
    def __init__(self):
        # Socket.IO rooms ativas (em memória para demo)
        self.active_rooms = {}
        self.webrtc_connections = {}
        self.websocket_connections = {}
        
        # ICE servers para WebRTC
        self.ice_servers = [
            {"urls": "stun:stun.l.google.com:19302"},
            {"urls": "stun:stun1.l.google.com:19302"}
        ]
        
        # Configurações padrão para novos usuários
        self.default_user_settings = {
            'microfone_padrao': None,
            'camera_padrao': None,
            'autofalar': False,
            'video_automatico': False,
            'qualidade_video_padrao': 'medium',
            'framerate_padrao': 30,
            'notificacoes_audios': True,
            'notificacoes_video': True,
            'notificacoes_mensagens': True,
            'som_notificacao': 'default',
            'perfil_visivel': True,
            'status_online_visivel': True,
            'permitir_convites_publicos': False,
            'auto_desconectar_inativo': True,
            'limite_minutos_inativo': 30,
            'gravacao_automatica': False,
            'tema_interface': 'light',
            'tamanho_fonte': 'medium'
        }
    
    # =============================================================================
    # GESTÃO DE SESSÕES DE COLABORAÇÃO
    # =============================================================================
    
    async def create_session(
        self,
        db: Session,
        creator_id: UUID,
        session_data: Dict[str, Any]
    ) -> CollaborationSession:
        """Criar nova sessão de colaboração"""
        try:
            # Gerar room_id único
            room_id = f"room_{uuid.uuid4().hex[:16]}"
            
            # Verificar se projeto existe (se fornecido)
            project = None
            if session_data.get('project_id'):
                project = db.query(Project).filter(
                    and_(
                        Project.id == session_data['project_id'],
                        Project.owner_id == creator_id
                    )
                ).first()
                
                if not project:
                    raise ValueError("Projeto não encontrado")
            
            # Criar sessão
            session = CollaborationSession(
                creator_id=creator_id,
                project_id=session_data.get('project_id'),
                room_id=room_id,
                nome=session_data['nome'],
                descricao=session_data.get('descricao', ''),
                tipo_sessao=session_data.get('tipo_sessao', 'private'),
                max_participantes=session_data.get('max_participantes', 10),
                senha_acesso=session_data.get('senha_acesso'),
                permitir_chat=session_data.get('permitir_chat', True),
                permitir_video=session_data.get('permitir_video', True),
                permitir_audio=session_data.get('permitir_audio', True),
                permitir_compartilhamento_tela=session_data.get('permitir_compartilhamento_tela', True),
                permitir_edicao_colaborativa=session_data.get('permitir_edicao_colaborativa', True),
                moderacao_ativa=session_data.get('moderacao_ativa', False),
                requer_aproacao_entrada=session_data.get('requer_aproacao_entrada', False),
                ice_servers=self.ice_servers,
                duracao_maxima_horas=session_data.get('duracao_maxima_horas', 8)
            )
            
            # Definir expiração se fornecida
            if session_data.get('expira_em'):
                session.expira_em = session_data['expira_em']
            else:
                session.expira_em = datetime.utcnow() + timedelta(hours=session.duracao_maxima_horas)
            
            db.add(session)
            db.commit()
            db.refresh(session)
            
            # Adicionar criador como participante ativo
            creator_participant = await self._add_participant(
                db, session.id, creator_id, 'active', can_moderate=True
            )
            
            # Inicializar room em memória
            self._initialize_room(room_id, session.id)
            
            logger.info(f"Sessão de colaboração criada: {session.id} por {creator_id}")
            return session
            
        except Exception as e:
            logger.error(f"Erro ao criar sessão de colaboração: {e}")
            raise
    
    async def get_session(
        self,
        db: Session,
        session_id: UUID,
        user_id: UUID
    ) -> Optional[CollaborationSession]:
        """Obter detalhes da sessão"""
        try:
            session = db.query(CollaborationSession).filter(
                CollaborationSession.id == session_id
            ).options(
                joinedload(CollaborationSession.participants).joinedload(Participant.user),
                joinedload(CollaborationSession.messages).joinedload(Message.participant),
                joinedload(CollaborationSession.video_calls),
                joinedload(CollaborationSession.screen_shares)
            ).first()
            
            if not session:
                raise ValueError("Sessão não encontrada")
            
            # Verificar permissões de acesso
            if not await self._check_session_access(db, session, user_id):
                raise ValueError("Acesso negado à sessão")
            
            return session
            
        except Exception as e:
            logger.error(f"Erro ao obter sessão: {e}")
            raise
    
    async def list_user_sessions(
        self,
        db: Session,
        user_id: UUID,
        include_ended: bool = False
    ) -> List[CollaborationSession]:
        """Listar sessões do usuário"""
        try:
            # Sessões onde o usuário é participante
            participant_sessions = db.query(CollaborationSession).join(Participant).filter(
                Participant.user_id == user_id
            )
            
            # Sessões criadas pelo usuário
            created_sessions = db.query(CollaborationSession).filter(
                CollaborationSession.creator_id == user_id
            )
            
            # Combinar e remover duplicatas
            all_sessions = participant_sessions.union(created_sessions)
            
            if not include_ended:
                all_sessions = all_sessions.filter(
                    CollaborationSession.status != 'ended'
                )
            
            sessions = all_sessions.order_by(desc(CollaborationSession.created_at)).all()
            return sessions
            
        except Exception as e:
            logger.error(f"Erro ao listar sessões do usuário: {e}")
            raise
    
    async def end_session(
        self,
        db: Session,
        session_id: UUID,
        user_id: UUID
    ) -> bool:
        """Encerrar sessão de colaboração"""
        try:
            session = db.query(CollaborationSession).filter(
                CollaborationSession.id == session_id
            ).first()
            
            if not session:
                raise ValueError("Sessão não encontrada")
            
            # Verificar permissões
            if session.creator_id != user_id:
                # Verificar se usuário pode moderar
                participant = db.query(Participant).filter(
                    and_(
                        Participant.session_id == session_id,
                        Participant.user_id == user_id,
                        Participant.pode_moderar == True
                    )
                ).first()
                
                if not participant:
                    raise ValueError("Permissão negada para encerrar sessão")
            
            # Atualizar status
            session.status = 'ended'
            session.ended_at = datetime.utcnow()
            session.updated_at = datetime.utcnow()
            
            # Atualizar todos os participantes
            db.query(Participant).filter(
                Participant.session_id == session_id
            ).update({
                'status': 'left',
                'left_at': datetime.utcnow()
            })
            
            db.commit()
            
            # Limpar room da memória
            if session.room_id in self.active_rooms:
                del self.active_rooms[session.room_id]
            
            logger.info(f"Sessão {session_id} encerrada por {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao encerrar sessão: {e}")
            raise
    
    # =============================================================================
    # GESTÃO DE PARTICIPANTES
    # =============================================================================
    
    async def add_participant(
        self,
        db: Session,
        session_id: UUID,
        user_id: UUID,
        invited_by_id: UUID,
        permissions: Optional[Dict] = None
    ) -> Participant:
        """Adicionar participante à sessão"""
        try:
            # Verificar se sessão existe
            session = db.query(CollaborationSession).filter(
                CollaborationSession.id == session_id
            ).first()
            
            if not session:
                raise ValueError("Sessão não encontrada")
            
            # Verificar se usuário já está na sessão
            existing_participant = db.query(Participant).filter(
                and_(
                    Participant.session_id == session_id,
                    Participant.user_id == user_id
                )
            ).first()
            
            if existing_participant:
                if existing_participant.status == 'left':
                    # Reativar participante
                    existing_participant.status = 'invited'
                    existing_participant.invited_at = datetime.utcnow()
                    existing_participant.last_activity = datetime.utcnow()
                    db.commit()
                    return existing_participant
                else:
                    raise ValueError("Usuário já é participante da sessão")
            
            # Verificar limite de participantes
            current_participants = db.query(Participant).filter(
                and_(
                    Participant.session_id == session_id,
                    Participant.status != 'left'
                )
            ).count()
            
            if current_participants >= session.max_participantes:
                raise ValueError("Sessão está cheia")
            
            # Criar participante
            default_permissions = {
                'pode_moderar': False,
                'pode_compartilhar_tela': True,
                'pode_usar_microfone': True,
                'pode_usar_camera': True,
                'pode_enviar_mensagens': True
            }
            
            if permissions:
                default_permissions.update(permissions)
            
            participant = Participant(
                session_id=session_id,
                user_id=user_id,
                status='invited',
                invited_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                **default_permissions
            )
            
            db.add(participant)
            db.commit()
            db.refresh(participant)
            
            logger.info(f"Participante {user_id} adicionado à sessão {session_id}")
            return participant
            
        except Exception as e:
            logger.error(f"Erro ao adicionar participante: {e}")
            raise
    
    async def join_session(
        self,
        db: Session,
        session_id: UUID,
        user_id: UUID,
        device_info: Optional[Dict] = None
    ) -> Participant:
        """Participante entrando na sessão"""
        try:
            participant = db.query(Participant).filter(
                and_(
                    Participant.session_id == session_id,
                    Participant.user_id == user_id
                )
            ).first()
            
            if not participant:
                raise ValueError("Participante não encontrado nesta sessão")
            
            # Atualizar status
            participant.status = 'joined'
            participant.joined_at = datetime.utcnow()
            participant.last_activity = datetime.utcnow()
            participant.ip_address = device_info.get('ip_address') if device_info else None
            participant.user_agent = device_info.get('user_agent') if device_info else None
            participant.dispositivo = device_info.get('device') if device_info else None
            
            db.commit()
            db.refresh(participant)
            
            # Notificar outros participantes via WebSocket
            await self._notify_participant_joined(session_id, participant)
            
            logger.info(f"Participante {user_id} entrou na sessão {session_id}")
            return participant
            
        except Exception as e:
            logger.error(f"Erro ao participante entrar na sessão: {e}")
            raise
    
    async def leave_session(
        self,
        db: Session,
        session_id: UUID,
        user_id: UUID
    ) -> bool:
        """Participante saindo da sessão"""
        try:
            participant = db.query(Participant).filter(
                and_(
                    Participant.session_id == session_id,
                    Participant.user_id == user_id
                )
            ).first()
            
            if not participant:
                raise ValueError("Participante não encontrado")
            
            # Atualizar status
            participant.status = 'left'
            participant.left_at = datetime.utcnow()
            participant.last_activity = datetime.utcnow()
            
            db.commit()
            
            # Notificar outros participantes
            await self._notify_participant_left(session_id, participant)
            
            logger.info(f"Participante {user_id} saiu da sessão {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao participante sair: {e}")
            raise
    
    async def update_participant_status(
        self,
        db: Session,
        session_id: UUID,
        user_id: UUID,
        status: str,
        additional_data: Optional[Dict] = None
    ) -> Participant:
        """Atualizar status do participante"""
        try:
            participant = db.query(Participant).filter(
                and_(
                    Participant.session_id == session_id,
                    Participant.user_id == user_id
                )
            ).first()
            
            if not participant:
                raise ValueError("Participante não encontrado")
            
            # Atualizar status
            participant.status = status
            participant.last_activity = datetime.utcnow()
            
            # Atualizar dados adicionais
            if additional_data:
                if 'latencia_ms' in additional_data:
                    participant.latencia_ms = additional_data['latencia_ms']
                if 'conexao_estavel' in additional_data:
                    participant.conexao_estavel = additional_data['conexao_estavel']
            
            db.commit()
            db.refresh(participant)
            
            # Notificar via WebSocket
            await self._notify_participant_status_changed(session_id, participant)
            
            return participant
            
        except Exception as e:
            logger.error(f"Erro ao atualizar status do participante: {e}")
            raise
    
    # =============================================================================
    # CHAT E MENSAGENS
    # =============================================================================
    
    async def send_message(
        self,
        db: Session,
        session_id: UUID,
        participant_id: UUID,
        message_data: Dict[str, Any]
    ) -> Message:
        """Enviar mensagem no chat"""
        try:
            # Verificar se participante existe e pode enviar mensagens
            participant = db.query(Participant).filter(
                Participant.id == participant_id
            ).first()
            
            if not participant:
                raise ValueError("Participante não encontrado")
            
            if not participant.pode_enviar_mensagens:
                raise ValueError("Participante não pode enviar mensagens")
            
            # Criar mensagem
            message = Message(
                session_id=session_id,
                participant_id=participant_id,
                tipo=message_data.get('tipo', 'text'),
                conteudo=message_data['conteudo'],
                arquivo_path=message_data.get('arquivo_path'),
                arquivo_tamanho=message_data.get('arquivo_tamanho'),
                mime_type=message_data.get('mime_type'),
                reply_to_message_id=message_data.get('reply_to_message_id'),
                mencoes=message_data.get('mencoes', []),
                created_at=datetime.utcnow()
            )
            
            db.add(message)
            db.commit()
            db.refresh(message)
            
            # Buscar dados completos da mensagem
            message = db.query(Message).filter(Message.id == message.id).options(
                joinedload(Message.participant).joinedload(Participant.user)
            ).first()
            
            # Notificar outros participantes via WebSocket
            await self._notify_new_message(session_id, message)
            
            logger.info(f"Mensagem enviada na sessão {session_id}")
            return message
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
            raise
    
    async def get_messages(
        self,
        db: Session,
        session_id: UUID,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0
    ) -> List[Message]:
        """Obter mensagens da sessão"""
        try:
            # Verificar acesso
            session = await self._get_session_with_access_check(db, session_id, user_id)
            
            messages = db.query(Message).filter(
                Message.session_id == session_id
            ).order_by(desc(Message.created_at)).limit(limit).offset(offset).options(
                joinedload(Message.participant).joinedload(Participant.user)
            ).all()
            
            return list(reversed(messages))  # Retornar em ordem cronológica
            
        except Exception as e:
            logger.error(f"Erro ao obter mensagens: {e}")
            raise
    
    async def edit_message(
        self,
        db: Session,
        message_id: UUID,
        user_id: UUID,
        new_content: str
    ) -> Optional[Message]:
        """Editar mensagem"""
        try:
            message = db.query(Message).filter(Message.id == message_id).first()
            
            if not message:
                raise ValueError("Mensagem não encontrada")
            
            # Verificar se usuário é o autor
            participant = db.query(Participant).filter(
                Participant.id == message.participant_id
            ).first()
            
            if not participant or participant.user_id != user_id:
                raise ValueError("Permissão negada para editar mensagem")
            
            # Verificar se mensagem pode ser editada (não muito antiga)
            time_diff = datetime.utcnow() - message.created_at
            if time_diff.total_seconds() > 3600:  # 1 hora
                raise ValueError("Mensagem muito antiga para editar")
            
            # Salvar versão original
            if not message.versao_original:
                message.versao_original = message.conteudo
            
            # Atualizar conteúdo
            message.conteudo = new_content
            message.editado_em = datetime.utcnow()
            
            db.commit()
            db.refresh(message)
            
            # Notificar outros participantes
            await self._notify_message_edited(message.session_id, message)
            
            return message
            
        except Exception as e:
            logger.error(f"Erro ao editar mensagem: {e}")
            raise
    
    # =============================================================================
    # VIDEO CHAMADAS
    # =============================================================================
    
    async def start_video_call(
        self,
        db: Session,
        session_id: UUID,
        initiator_id: UUID,
        call_config: Dict[str, Any]
    ) -> VideoCall:
        """Iniciar chamada de vídeo"""
        try:
            # Verificar se sessão existe
            session = db.query(CollaborationSession).filter(
                CollaborationSession.id == session_id
            ).first()
            
            if not session:
                raise ValueError("Sessão não encontrada")
            
            if not session.permitir_video:
                raise ValueError("Vídeo não permitido nesta sessão")
            
            # Criar chamada
            video_call = VideoCall(
                session_id=session_id,
                tipo=call_config.get('tipo', 'video'),
                configuracao_audio=call_config.get('configuracao_audio', {}),
                configuracao_video=call_config.get('configuracao_video', {}),
                qualidade_video=call_config.get('qualidade_video', 'medium'),
                framerate=call_config.get('framerate', 30),
                resolucao=call_config.get('resolucao', '1280x720'),
                status='initializing',
                created_at=datetime.utcnow()
            )
            
            db.add(video_call)
            db.commit()
            db.refresh(video_call)
            
            # Adicionar iniciador como participante da chamada
            initiator_participant = db.query(Participant).filter(
                and_(
                    Participant.session_id == session_id,
                    Participant.user_id == initiator_id
                )
            ).first()
            
            if initiator_participant:
                call_participant = VideoCallParticipant(
                    video_call_id=video_call.id,
                    participant_id=initiator_participant.id,
                    status='connecting',
                    microfone_ativo=call_config.get('microfone_ativo', True),
                    camera_ativa=call_config.get('camera_ativa', True)
                )
                
                db.add(call_participant)
                db.commit()
            
            # Notificar início da chamada
            await self._notify_video_call_started(session_id, video_call)
            
            logger.info(f"Chamada de vídeo iniciada: {video_call.id}")
            return video_call
            
        except Exception as e:
            logger.error(f"Erro ao iniciar chamada de vídeo: {e}")
            raise
    
    async def end_video_call(
        self,
        db: Session,
        video_call_id: UUID,
        user_id: UUID
    ) -> bool:
        """Encerrar chamada de vídeo"""
        try:
            video_call = db.query(VideoCall).filter(VideoCall.id == video_call_id).first()
            
            if not video_call:
                raise ValueError("Chamada não encontrada")
            
            # Verificar se usuário tem permissão (criador da sessão ou participante ativo)
            session = db.query(CollaborationSession).filter(
                CollaborationSession.id == video_call.session_id
            ).first()
            
            if session.creator_id != user_id:
                participant = db.query(Participant).filter(
                    and_(
                        Participant.session_id == video_call.session_id,
                        Participant.user_id == user_id,
                        Participant.status == 'active'
                    )
                ).first()
                
                if not participant:
                    raise ValueError("Permissão negada")
            
            # Atualizar status da chamada
            video_call.status = 'ended'
            video_call.ended_at = datetime.utcnow()
            
            # Calcular duração
            if video_call.started_at:
                duration = (video_call.ended_at - video_call.started_at).total_seconds()
                video_call.duracao_segundos = int(duration)
            
            # Atualizar participantes
            db.query(VideoCallParticipant).filter(
                VideoCallParticipant.video_call_id == video_call_id
            ).update({
                'status': 'disconnected',
                'left_at': datetime.utcnow()
            })
            
            db.commit()
            
            # Notificar encerramento
            await self._notify_video_call_ended(video_call.session_id, video_call)
            
            logger.info(f"Chamada de vídeo encerrada: {video_call_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao encerrar chamada: {e}")
            raise
    
    # =============================================================================
    # COMPARTILHAMENTO DE TELA
    # =============================================================================
    
    async def start_screen_share(
        self,
        db: Session,
        session_id: UUID,
        sharer_id: UUID,
        share_config: Dict[str, Any]
    ) -> ScreenShare:
        """Iniciar compartilhamento de tela"""
        try:
            # Verificar sessão
            session = db.query(CollaborationSession).filter(
                CollaborationSession.id == session_id
            ).first()
            
            if not session:
                raise ValueError("Sessão não encontrada")
            
            if not session.permitir_compartilhamento_tela:
                raise ValueError("Compartilhamento não permitido")
            
            # Obter participante
            sharer_participant = db.query(Participant).filter(
                and_(
                    Participant.session_id == session_id,
                    Participant.user_id == sharer_id
                )
            ).first()
            
            if not sharer_participant:
                raise ValueError("Participante não encontrado")
            
            if not sharer_participant.pode_compartilhar_tela:
                raise ValueError("Participante não pode compartilhar tela")
            
            # Verificar se já há compartilhamento ativo
            active_share = db.query(ScreenShare).filter(
                and_(
                    ScreenShare.session_id == session_id,
                    ScreenShare.status == 'active'
                )
            ).first()
            
            if active_share:
                raise ValueError("Já há compartilhamento ativo nesta sessão")
            
            # Criar compartilhamento
            screen_share = ScreenShare(
                session_id=session_id,
                sharer_id=sharer_participant.id,
                tipo=share_config.get('tipo', 'screen'),
                aplicacao_nome=share_config.get('aplicacao_nome'),
                window_title=share_config.get('window_title'),
                url_browser=share_config.get('url_browser'),
                qualidade=share_config.get('qualidade', 'medium'),
                framerate=share_config.get('framerate', 30),
                mouse_cursor_visivel=share_config.get('mouse_cursor_visivel', True),
                status='active',
                started_at=datetime.utcnow()
            )
            
            db.add(screen_share)
            db.commit()
            db.refresh(screen_share)
            
            # Notificar início
            await self._notify_screen_share_started(session_id, screen_share)
            
            logger.info(f"Compartilhamento iniciado: {screen_share.id}")
            return screen_share
            
        except Exception as e:
            logger.error(f"Erro ao iniciar compartilhamento: {e}")
            raise
    
    # =============================================================================
    # MÉTODOS PRIVADOS DE ASSISTÊNCIA
    # =============================================================================
    
    def _initialize_room(self, room_id: str, session_id: UUID):
        """Inicializar room em memória"""
        self.active_rooms[room_id] = {
            'session_id': session_id,
            'participants': {},
            'webrtc_connections': {},
            'created_at': datetime.utcnow()
        }
    
    async def _add_participant(
        self,
        db: Session,
        session_id: UUID,
        user_id: UUID,
        status: str,
        can_moderate: bool = False
    ) -> Participant:
        """Adicionar participante interno (para criador da sessão)"""
        participant = Participant(
            session_id=session_id,
            user_id=user_id,
            status=status,
            invited_at=datetime.utcnow(),
            joined_at=datetime.utcnow() if status == 'active' else None,
            last_activity=datetime.utcnow(),
            pode_moderar=can_moderate,
            pode_compartilhar_tela=True,
            pode_usar_microfone=True,
            pode_usar_camera=True,
            pode_enviar_mensagens=True
        )
        
        db.add(participant)
        db.commit()
        db.refresh(participant)
        
        return participant
    
    async def _check_session_access(
        self,
        db: Session,
        session: CollaborationSession,
        user_id: UUID
    ) -> bool:
        """Verificar se usuário tem acesso à sessão"""
        # Criador sempre tem acesso
        if session.creator_id == user_id:
            return True
        
        # Verificar se é participante
        participant = db.query(Participant).filter(
            and_(
                Participant.session_id == session.id,
                Participant.user_id == user_id
            )
        ).first()
        
        if participant and participant.status != 'left':
            return True
        
        # Sessão pública (implementar lógica específica)
        if session.tipo_sessao == 'public':
            return True
        
        return False
    
    async def _get_session_with_access_check(
        self,
        db: Session,
        session_id: UUID,
        user_id: UUID
    ) -> CollaborationSession:
        """Obter sessão verificando acesso"""
        session = db.query(CollaborationSession).filter(
            CollaborationSession.id == session_id
        ).first()
        
        if not session:
            raise ValueError("Sessão não encontrada")
        
        if not await self._check_session_access(db, session, user_id):
            raise ValueError("Acesso negado")
        
        return session
    
    # =============================================================================
    # NOTIFICAÇÕES WEBSOCKET (Placeholder)
    # =============================================================================
    
    async def _notify_participant_joined(
        self,
        session_id: UUID,
        participant: Participant
    ):
        """Notificar que participante entrou"""
        # Implementar envio via Socket.IO
        logger.info(f"Notificação: participante {participant.user_id} entrou na sessão {session_id}")
    
    async def _notify_participant_left(
        self,
        session_id: UUID,
        participant: Participant
    ):
        """Notificar que participante saiu"""
        # Implementar envio via Socket.IO
        logger.info(f"Notificação: participante {participant.user_id} saiu da sessão {session_id}")
    
    async def _notify_participant_status_changed(
        self,
        session_id: UUID,
        participant: Participant
    ):
        """Notificar mudança de status do participante"""
        # Implementar envio via Socket.IO
        logger.info(f"Notificação: status do participante mudou para {participant.status}")
    
    async def _notify_new_message(
        self,
        session_id: UUID,
        message: Message
    ):
        """Notificar nova mensagem"""
        # Implementar envio via Socket.IO
        logger.info(f"Notificação: nova mensagem na sessão {session_id}")
    
    async def _notify_message_edited(
        self,
        session_id: UUID,
        message: Message
    ):
        """Notificar mensagem editada"""
        # Implementar envio via Socket.IO
        logger.info(f"Notificação: mensagem editada na sessão {session_id}")
    
    async def _notify_video_call_started(
        self,
        session_id: UUID,
        video_call: VideoCall
    ):
        """Notificar início de chamada de vídeo"""
        # Implementar envio via Socket.IO
        logger.info(f"Notificação: chamada de vídeo iniciada na sessão {session_id}")
    
    async def _notify_video_call_ended(
        self,
        session_id: UUID,
        video_call: VideoCall
    ):
        """Notificar fim de chamada de vídeo"""
        # Implementar envio via Socket.IO
        logger.info(f"Notificação: chamada de vídeo encerrada na sessão {session_id}")
    
    async def _notify_screen_share_started(
        self,
        session_id: UUID,
        screen_share: ScreenShare
    ):
        """Notificar início de compartilhamento"""
        # Implementar envio via Socket.IO
        logger.info(f"Notificação: compartilhamento iniciado na sessão {session_id}")
    
    # =============================================================================
    # CONFIGURAÇÕES DE USUÁRIO
    # =============================================================================
    
    async def get_user_settings(
        self,
        db: Session,
        user_id: UUID
    ) -> CollaborationSetting:
        """Obter configurações de colaboração do usuário"""
        try:
            settings = db.query(CollaborationSetting).filter(
                CollaborationSetting.user_id == user_id
            ).first()
            
            if not settings:
                # Criar configurações padrão
                settings = CollaborationSetting(
                    user_id=user_id,
                    **self.default_user_settings
                )
                
                db.add(settings)
                db.commit()
                db.refresh(settings)
            
            return settings
            
        except Exception as e:
            logger.error(f"Erro ao obter configurações do usuário: {e}")
            raise
    
    async def update_user_settings(
        self,
        db: Session,
        user_id: UUID,
        settings_data: Dict[str, Any]
    ) -> CollaborationSetting:
        """Atualizar configurações de colaboração do usuário"""
        try:
            settings = await self.get_user_settings(db, user_id)
            
            # Atualizar campos
            for field, value in settings_data.items():
                if hasattr(settings, field):
                    setattr(settings, field, value)
            
            settings.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(settings)
            
            logger.info(f"Configurações de colaboração atualizadas para usuário {user_id}")
            return settings
            
        except Exception as e:
            logger.error(f"Erro ao atualizar configurações: {e}")
            raise
    
    # =============================================================================
    # ESTATÍSTICAS E RELATÓRIOS
    # =============================================================================
    
    async def get_session_statistics(
        self,
        db: Session,
        session_id: UUID,
        user_id: UUID
    ) -> Dict[str, Any]:
        """Obter estatísticas da sessão"""
        try:
            # Verificar acesso
            session = await self._get_session_with_access_check(db, session_id, user_id)
            
            # Contar participantes
            total_participants = db.query(Participant).filter(
                Participant.session_id == session_id
            ).count()
            
            active_participants = db.query(Participant).filter(
                and_(
                    Participant.session_id == session_id,
                    Participant.status == 'active'
                )
            ).count()
            
            # Contar mensagens
            total_messages = db.query(Message).filter(
                Message.session_id == session_id
            ).count()
            
            # Contar chamadas
            total_calls = db.query(VideoCall).filter(
                VideoCall.session_id == session_id
            ).count()
            
            active_calls = db.query(VideoCall).filter(
                and_(
                    VideoCall.session_id == session_id,
                    VideoCall.status == 'active'
                )
            ).count()
            
            # Contar compartilhamentos
            total_shares = db.query(ScreenShare).filter(
                ScreenShare.session_id == session_id
            ).count()
            
            active_shares = db.query(ScreenShare).filter(
                and_(
                    ScreenShare.session_id == session_id,
                    ScreenShare.status == 'active'
                )
            ).count()
            
            # Calcular duração da sessão
            session_duration = 0
            if session.started_at and session.ended_at:
                session_duration = (session.ended_at - session.started_at).total_seconds()
            elif session.started_at:
                session_duration = (datetime.utcnow() - session.started_at).total_seconds()
            
            return {
                'session_id': session_id,
                'total_participants': total_participants,
                'active_participants': active_participants,
                'total_messages': total_messages,
                'total_calls': total_calls,
                'active_calls': active_calls,
                'total_shares': total_shares,
                'active_shares': active_shares,
                'session_duration_seconds': int(session_duration),
                'session_status': session.status,
                'created_at': session.created_at,
                'started_at': session.started_at,
                'ended_at': session.ended_at
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas da sessão: {e}")
            raise