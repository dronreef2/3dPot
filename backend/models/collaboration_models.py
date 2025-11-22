"""
Modelos SQLAlchemy - Collaborative Features (Sprint 6+)
======================================================

Modelos para colaboração em tempo real, incluindo:
- Sessões de colaboração (CollaborationSession)
- Participantes (Participant)
- Mensagens e chat (Message)
- Compartilhamento de tela (ScreenShare)
- Video chamadas (VideoCall)
- Versionamento colaborativo (FileVersion)

Autor: MiniMax Agent
Data: 2025-11-13
Versão: 2.0.0 - Sprint 6+
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Set
from uuid import uuid4, UUID
from enum import Enum

from sqlalchemy import (
    Boolean, Column, DateTime, Enum as SqlEnum, ForeignKey, Integer, 
    JSON, String, Text, Float, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from . import Base


class CollaborationSession(Base):
    """Sessões de colaboração em tempo real"""
    __tablename__ = "collaboration_sessions"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    creator_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(PGUUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    
    # Informações básicas
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    
    # Configurações de acesso
    tipo_sessao = Column(SqlEnum('private', 'public', 'link_based', name='session_type'), 
                        default='private')
    max_participantes = Column(Integer, default=10)
    senha_acesso = Column(String(50), nullable=True)
    
    # Status da sessão
    status = Column(SqlEnum('active', 'paused', 'ended', 'cancelled', name='session_status'), 
                   default='active')
    
    # Configurações de colaboração
    permitir_chat = Column(Boolean, default=True)
    permitir_video = Column(Boolean, default=True)
    permitir_audio = Column(Boolean, default=True)
    permitir_compartilhamento_tela = Column(Boolean, default=True)
    permitir_edicao_colaborativa = Column(Boolean, default=True)
    gravacao_ativa = Column(Boolean, default=False)
    
    # Configurações de segurança
    moderacao_ativa = Column(Boolean, default=False)
    requer_aproacao_entrada = Column(Boolean, default=False)
    bloqueado = Column(Boolean, default=False)
    
    # WebRTC e Socket.IO
    room_id = Column(String(100), nullable=False)  # Para WebRTC/Socket.IO
    webrtc_offer = Column(JSON, default=dict)
    ice_servers = Column(JSON, default=list)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    
    # Configurações de duração
    duracao_maxima_horas = Column(Integer, default=8)
    expira_em = Column(DateTime, nullable=True)
    
    # Relationships
    creator = relationship("User", back_populates="created_collaboration_sessions")
    project = relationship("Project", back_populates="collaboration_sessions")
    participants = relationship("Participant", back_populates="session", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    video_calls = relationship("VideoCall", back_populates="session", cascade="all, delete-orphan")
    screen_shares = relationship("ScreenShare", back_populates="session", cascade="all, delete-orphan")
    file_versions = relationship("FileVersion", back_populates="session", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('room_id', name='uq_session_room_id'),
    )


class Participant(Base):
    """Participantes de uma sessão de colaboração"""
    __tablename__ = "participants"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(PGUUID(as_uuid=True), ForeignKey("collaboration_sessions.id"), 
                       nullable=False)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Status do participante
    status = Column(SqlEnum('invited', 'joined', 'active', 'away', 'banned', 'left', 
                           name='participant_status'), default='invited')
    
    # Permissões
    pode_moderar = Column(Boolean, default=False)
    pode_compartilhar_tela = Column(Boolean, default=True)
    pode_usar_microfone = Column(Boolean, default=True)
    pode_usar_camera = Column(Boolean, default=True)
    pode_enviar_mensagens = Column(Boolean, default=True)
    
    # Informações de conexão
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    dispositivo = Column(String(50), nullable=True)
    
    # Configurações pessoais
    nome_exibicao = Column(String(50), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    status_mensagem = Column(String(100), nullable=True)
    
    # Timestamps
    invited_at = Column(DateTime, default=datetime.utcnow)
    joined_at = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, nullable=True)
    left_at = Column(DateTime, nullable=True)
    
    # Qualidade de conexão
    latencia_ms = Column(Integer, nullable=True)
    conexao_estavel = Column(Boolean, default=False)
    
    # Relationships
    session = relationship("CollaborationSession", back_populates="participants")
    user = relationship("User", back_populates="collaboration_participations")
    messages = relationship("Message", back_populates="participant", cascade="all, delete-orphan")
    video_call_participations = relationship("VideoCallParticipant", 
                                           back_populates="participant", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('session_id', 'user_id', name='uq_participant_session_user'),
    )


class Message(Base):
    """Mensagens de chat na colaboração"""
    __tablename__ = "messages"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(PGUUID(as_uuid=True), ForeignKey("collaboration_sessions.id"), 
                       nullable=False)
    participant_id = Column(PGUUID(as_uuid=True), ForeignKey("participants.id"), 
                           nullable=False)
    
    # Conteúdo da mensagem
    tipo = Column(SqlEnum('text', 'file', 'image', 'link', 'system', name='message_type'), 
                 default='text')
    conteudo = Column(Text, nullable=False)
    
    # Metadados
    arquivo_path = Column(String(500), nullable=True)
    arquivo_tamanho = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    
    # Context
    reply_to_message_id = Column(PGUUID(as_uuid=True), ForeignKey("messages.id"), nullable=True)
    mencoes = Column(JSON, default=list)  # Lista de user_ids mencionados
    
    # Status de entrega
    status = Column(SqlEnum('sending', 'sent', 'delivered', 'read', 'failed', name='message_status'),
                   default='sending')
    
    # Edição e histórico
    editado_em = Column(DateTime, nullable=True)
    versao_original = Column(Text, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    
    # Moderation
    moderado = Column(Boolean, default=False)
    moderador_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    motivo_moderacao = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("CollaborationSession", back_populates="messages")
    participant = relationship("Participant", back_populates="messages")
    parent_message = relationship("Message", remote_side="Message.id", backref="replies")
    moderator = relationship("User", foreign_keys=[moderador_id])
    
    # Indexes para performance
    __table_args__ = (
        Index('idx_messages_session_created', 'session_id', 'created_at'),
        Index('idx_messages_participant', 'participant_id'),
    )


class VideoCall(Base):
    """Chamadas de vídeo em sessões de colaboração"""
    __tablename__ = "video_calls"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(PGUUID(as_uuid=True), ForeignKey("collaboration_sessions.id"), 
                       nullable=False)
    
    # Configurações da chamada
    tipo = Column(SqlEnum('audio', 'video', 'screen_share', 'mixed', name='call_type'), 
                 default='video')
    configuracao_audio = Column(JSON, default=dict)
    configuracao_video = Column(JSON, default=dict)
    
    # Configurações de qualidade
    qualidade_video = Column(SqlEnum('low', 'medium', 'high', 'hd', name='video_quality'), 
                           default='medium')
    framerate = Column(Integer, default=30)
    resolucao = Column(String(20), default='1280x720')
    
    # Status da chamada
    status = Column(SqlEnum('initializing', 'active', 'paused', 'ended', 'failed', name='call_status'),
                   default='initializing')
    
    # Configurações de gravação
    gravando = Column(Boolean, default=False)
    gravacao_path = Column(String(500), nullable=True)
    gravacao_iniciou_em = Column(DateTime, nullable=True)
    
    # Estatísticas
    duracao_segundos = Column(Integer, nullable=True)
    packets_lost = Column(Integer, default=0)
    bandwidth_used = Column(Float, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("CollaborationSession", back_populates="video_calls")
    participants = relationship("VideoCallParticipant", back_populates="video_call", 
                              cascade="all, delete-orphan")
    
    # Statistics helpers
    @property
    def duracao_minutos(self) -> Optional[float]:
        """Retorna duração da chamada em minutos"""
        if self.started_at and self.ended_at:
            return (self.ended_at - self.started_at).total_seconds() / 60
        return None


class VideoCallParticipant(Base):
    """Participantes de chamadas de vídeo"""
    __tablename__ = "video_call_participants"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    video_call_id = Column(PGUUID(as_uuid=True), ForeignKey("video_calls.id"), nullable=False)
    participant_id = Column(PGUUID(as_uuid=True), ForeignKey("participants.id"), nullable=False)
    
    # Status na chamada
    status = Column(SqlEnum('joining', 'connected', 'disconnected', 'muted', 'video_off', 
                           name='call_participant_status'), default='joining')
    
    # Configurações de mídia
    microfone_ativo = Column(Boolean, default=True)
    camera_ativa = Column(Boolean, default=True)
    compartilhando_tela = Column(Boolean, default=False)
    
    # Qualidade de mídia
    qualidade_audio = Column(SqlEnum('poor', 'fair', 'good', 'excellent', name='audio_quality'),
                           default='good')
    qualidade_video = Column(SqlEnum('poor', 'fair', 'good', 'excellent', name='video_quality'),
                           default='good')
    
    # Estatísticas de conexão
    latencia_ms = Column(Integer, nullable=True)
    jitter_ms = Column(Integer, nullable=True)
    packets_lost = Column(Integer, default=0)
    bitrate_kbps = Column(Integer, nullable=True)
    
    # Timestamps
    joined_at = Column(DateTime, default=datetime.utcnow)
    left_at = Column(DateTime, nullable=True)
    
    # Relationships
    video_call = relationship("VideoCall", back_populates="participants")
    participant = relationship("Participant", back_populates="video_call_participations")


class ScreenShare(Base):
    """Sessões de compartilhamento de tela"""
    __tablename__ = "screen_shares"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(PGUUID(as_uuid=True), ForeignKey("collaboration_sessions.id"), 
                       nullable=False)
    
    # Participante que está compartilhando
    sharer_id = Column(PGUUID(as_uuid=True), ForeignKey("participants.id"), nullable=False)
    
    # Configurações do compartilhamento
    tipo = Column(SqlEnum('screen', 'application', 'browser_tab', name='share_type'), 
                 default='screen')
    
    # Informações do que está sendo compartilhado
    aplicacao_nome = Column(String(100), nullable=True)
    window_title = Column(String(200), nullable=True)
    url_browser = Column(String(500), nullable=True)
    
    # Configurações técnicas
    qualidade = Column(SqlEnum('low', 'medium', 'high', name='share_quality'), default='medium')
    framerate = Column(Integer, default=30)
    mouse_cursor_visivel = Column(Boolean, default=True)
    
    # Status
    status = Column(SqlEnum('active', 'paused', 'stopped', 'error', name='share_status'), 
                   default='active')
    
    # Estatísticas
    bandwidth_used = Column(Float, nullable=True)
    viewers_count = Column(Integer, default=0)
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    stopped_at = Column(DateTime, nullable=True)
    
    # Relationships
    session = relationship("CollaborationSession", back_populates="screen_shares")
    sharer = relationship("Participant")


class FileVersion(Base):
    """Versionamento colaborativo de arquivos"""
    __tablename__ = "file_versions"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(PGUUID(as_uuid=True), ForeignKey("collaboration_sessions.id"), 
                       nullable=False)
    uploader_id = Column(PGUUID(as_uuid=True), ForeignKey("participants.id"), nullable=False)
    
    # Informações do arquivo
    nome_arquivo = Column(String(255), nullable=False)
    arquivo_path = Column(String(500), nullable=False)
    arquivo_tamanho = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    
    # Versionamento
    versao = Column(Integer, nullable=False)
    versao_mae = Column(PGUUID(as_uuid=True), ForeignKey("file_versions.id"), nullable=True)
    descricao_alteracoes = Column(Text, nullable=True)
    
    # Status
    status = Column(SqlEnum('uploading', 'processing', 'available', 'archived', 'deleted', 
                           name='file_version_status'), default='uploading')
    
    # Metadados específicos do tipo
    metadata_3d = Column(JSON, default=dict)  # Para modelos 3D
    metadata_image = Column(JSON, default=dict)  # Para imagens
    metadata_document = Column(JSON, default=dict)  # Para documentos
    
    # Permissões de acesso
    download_permitido = Column(Boolean, default=True)
    visualizacao_permitida = Column(Boolean, default=True)
    editavel_por_grupo = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    session = relationship("CollaborationSession", back_populates="file_versions")
    uploader = relationship("Participant")
    parent_version = relationship("FileVersion", remote_side="FileVersion.id")


class CollaborationSetting(Base):
    """Configurações de colaboração por usuário"""
    __tablename__ = "collaboration_settings"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Preferências de áudio/vídeo
    microfone_padrao = Column(String(100), nullable=True)
    camera_padrao = Column(String(100), nullable=True)
    autofalar = Column(Boolean, default=False)
    video_automatico = Column(Boolean, default=False)
    
    # Qualidade de vídeo
    qualidade_video_padrao = Column(SqlEnum('low', 'medium', 'high', 'hd', name='default_video_quality'),
                                  default='medium')
    framerate_padrao = Column(Integer, default=30)
    
    # Configurações de notificação
    notificacoes_audios = Column(Boolean, default=True)
    notificacoes_video = Column(Boolean, default=True)
    notificacoes_mensagens = Column(Boolean, default=True)
    som_notificacao = Column(String(100), default='default')
    
    # Configurações de privacidade
    perfil_visivel = Column(Boolean, default=True)
    status_online_visivel = Column(Boolean, default=True)
    permitir_convites_publicos = Column(Boolean, default=False)
    
    # Configurações de produtividade
    auto_desconectar_inativo = Column(Boolean, default=True)
    limite_minutos_inativo = Column(Integer, default=30)
    gravacao_automatica = Column(Boolean, default=False)
    
    # Interface
    tema_interface = Column(String(20), default='light')
    tamanho_fonte = Column(SqlEnum('small', 'medium', 'large', name='font_size'), default='medium')
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="collaboration_settings")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', name='uq_settings_user'),
    )


# Adicionar relacionamentos às models existentes

# User relationships (adicionar às models existentes)
def add_user_collaboration_relationships():
    """Adicionar relacionamentos ao modelo User"""
    from backend.models import User
    
    if not hasattr(User, 'created_collaboration_sessions'):
        User.created_collaboration_sessions = relationship(
            "CollaborationSession", 
            back_populates="creator",
            foreign_keys="CollaborationSession.creator_id"
        )
    
    if not hasattr(User, 'collaboration_participations'):
        User.collaboration_participations = relationship(
            "Participant",
            back_populates="user"
        )
    
    if not hasattr(User, 'collaboration_settings'):
        User.collaboration_settings = relationship(
            "CollaborationSetting",
            back_populates="user",
            uselist=False
        )


# Project relationships (adicionar às models existentes)
def add_project_collaboration_relationships():
    """Adicionar relacionamentos ao modelo Project"""
    from backend.models import Project
    
    if not hasattr(Project, 'collaboration_sessions'):
        Project.collaboration_sessions = relationship(
            "CollaborationSession",
            back_populates="project"
        )