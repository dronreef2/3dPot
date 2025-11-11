"""
Rotas de Autenticação - 3dPot v2.0
JWT OAuth2 completo com registro, login, refresh tokens e gerenciamento de sessões
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text

from core.config import settings
from database import get_db
from models import User, RefreshToken
from schemas import (
    UserRegister, UserLogin, UserLoginResponse, UserPublic, 
    PasswordResetRequest, PasswordResetConfirm, ChangePasswordRequest,
    RefreshTokenRequest, EmailVerificationRequest,
    SessionList, RevokeSessionRequest, RevokeAllSessionsRequest,
    UserProfileUpdate, AuthResponse, AuthMessage
)
from services.auth_service import auth_service, AuthenticationError, RateLimitError
from middleware.auth import (
    get_current_user, get_current_active_user, log_authentication_attempt,
    log_authentication_logout, create_auth_response, create_error_response,
    extract_token_from_header
)

# Configurar logging
logger = logging.getLogger(__name__)

# Router
auth_router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

# ==================== REGISTRO DE USUÁRIOS ====================

@auth_router.post("/register", response_model=AuthResponse)
async def register_user(
    user_data: UserRegister,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Registra novo usuário no sistema
    """
    try:
        # Informações para auditoria
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent", "Unknown")
        
        # Registra usuário
        user = auth_service.register_user(user_data, db, ip_address)
        
        # Log do registro
        logger.info(f"USER_REGISTER | {user.username} | {user.email} | {ip_address}")
        
        # Retorna resposta
        return AuthResponse(
            success=True,
            message="Usuário registrado com sucesso. Verifique seu email para ativar a conta.",
            data={"user_id": str(user.id), "email": user.email}
        )
        
    except AuthenticationError as e:
        return AuthResponse(
            success=False,
            message=str(e),
            error="REGISTRATION_FAILED"
        )
    except Exception as e:
        logger.error(f"Erro no registro: {str(e)}")
        return AuthResponse(
            success=False,
            message="Erro interno do servidor",
            error="INTERNAL_ERROR"
        )

@auth_router.post("/verify-email", response_model=AuthResponse)
async def verify_email(
    verification_data: EmailVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Solicita reenvio do email de verificação
    """
    try:
        user = db.query(User).filter(User.email == verification_data.email).first()
        
        if not user:
            # Por segurança, não revelamos se email existe
            return AuthResponse(
                success=True,
                message="Se o email estiver cadastrado, você receberá as instruções."
            )
        
        if user.is_verified:
            return AuthResponse(
                success=False,
                message="Email já foi verificado",
                error="ALREADY_VERIFIED"
            )
        
        # Gerar novo token de verificação (implementar envio de email)
        # verification_token = auth_service.generate_verification_token(user)
        
        return AuthResponse(
            success=True,
            message="Instruções de verificação foram enviadas para seu email."
        )
        
    except Exception as e:
        logger.error(f"Erro na verificação de email: {str(e)}")
        return AuthResponse(
            success=False,
            message="Erro interno do servidor",
            error="INTERNAL_ERROR"
        )

# ==================== LOGIN E AUTENTICAÇÃO ====================

@auth_router.post("/login", response_model=AuthResponse)
async def login(
    login_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Autentica usuário e retorna tokens JWT
    """
    try:
        # Informações para auditoria
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent", "Unknown")
        
        # Autentica usuário
        login_response = auth_service.authenticate_user(
            login_data, db, ip_address, user_agent
        )
        
        # Log do login bem-sucedido
        log_authentication_attempt(
            username=login_data.username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=True
        )
        
        # Retorna tokens
        return AuthResponse(
            success=True,
            message="Login realizado com sucesso",
            data=login_response.dict()
        )
        
    except RateLimitError as e:
        log_authentication_attempt(
            username=login_data.username,
            ip_address=request.client.host,
            user_agent=user_agent,
            success=False,
            reason=str(e)
        )
        return AuthResponse(
            success=False,
            message=str(e),
            error="RATE_LIMITED"
        )
    except AuthenticationError as e:
        log_authentication_attempt(
            username=login_data.username,
            ip_address=request.client.host,
            user_agent=user_agent,
            success=False,
            reason=str(e)
        )
        return AuthResponse(
            success=False,
            message=str(e),
            error="AUTHENTICATION_FAILED"
        )
    except Exception as e:
        logger.error(f"Erro no login: {str(e)}")
        return AuthResponse(
            success=False,
            message="Erro interno do servidor",
            error="INTERNAL_ERROR"
        )

@auth_router.post("/refresh", response_model=AuthResponse)
async def refresh_tokens(
    refresh_data: RefreshTokenRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Renova tokens usando refresh token
    """
    try:
        # Informações para auditoria
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent", "Unknown")
        
        # Renova tokens
        login_response = auth_service.refresh_tokens(
            refresh_data.refresh_token, db
        )
        
        return AuthResponse(
            success=True,
            message="Tokens renovados com sucesso",
            data=login_response.dict()
        )
        
    except AuthenticationError as e:
        return AuthResponse(
            success=False,
            message=str(e),
            error="TOKEN_INVALID"
        )
    except Exception as e:
        logger.error(f"Erro na renovação de tokens: {str(e)}")
        return AuthResponse(
            success=False,
            message="Erro interno do servidor",
            error="INTERNAL_ERROR"
        )

# ==================== LOGOUT ====================

@auth_router.post("/logout", response_model=AuthResponse)
async def logout(
    request: Request,
    refresh_data: Optional[RefreshTokenRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Faz logout do usuário
    """
    try:
        # Informações para auditoria
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent", "Unknown")
        
        # Extrai refresh token se fornecido
        refresh_token = None
        if refresh_data:
            refresh_token = refresh_data.refresh_token
        
        # Faz logout
        auth_service.logout(refresh_token=refresh_token, db=db)
        
        # Log do logout
        log_authentication_logout(
            user_id=str(current_user.id),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return AuthResponse(
            success=True,
            message="Logout realizado com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro no logout: {str(e)}")
        return AuthResponse(
            success=False,
            message="Erro interno do servidor",
            error="INTERNAL_ERROR"
        )

@auth_router.post("/logout-all", response_model=AuthResponse)
async def logout_all_sessions(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Faz logout de todas as sessões
    """
    try:
        # Informações para auditoria
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent", "Unknown")
        
        # Faz logout de todas as sessões
        auth_service.logout_all_sessions(current_user.id, db)
        
        # Log do logout
        log_authentication_logout(
            user_id=str(current_user.id),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return AuthResponse(
            success=True,
            message="Logout de todas as sessões realizado com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro no logout de todas as sessões: {str(e)}")
        return AuthResponse(
            success=False,
            message="Erro interno do servidor",
            error="INTERNAL_ERROR"
        )

# ==================== GERENCIAMENTO DE SENHA ====================

@auth_router.post("/reset-password", response_model=AuthResponse)
async def reset_password_request(
    reset_data: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Solicita reset de senha
    """
    try:
        user = db.query(User).filter(User.email == reset_data.email).first()
        
        # Por segurança, sempre retornar sucesso
        if user:
            # Gerar token de reset (implementar envio de email)
            reset_token = auth_service._generate_secure_token()
            expires_at = datetime.utcnow() + timedelta(hours=1)
            
            user.reset_token = reset_token
            user.reset_token_expires = expires_at
            db.commit()
            
            logger.info(f"PASSWORD_RESET_REQUEST | {user.username} | {user.email}")
        
        return AuthResponse(
            success=True,
            message="Se o email estiver cadastrado, você receberá as instruções para resetar sua senha."
        )
        
    except Exception as e:
        logger.error(f"Erro no reset de senha: {str(e)}")
        return AuthResponse(
            success=False,
            message="Erro interno do servidor",
            error="INTERNAL_ERROR"
        )

@auth_router.post("/reset-password/confirm", response_model=AuthResponse)
async def reset_password_confirm(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Confirma reset de senha
    """
    try:
        # Busca usuário com token válido
        user = db.query(User).filter(
            and_(
                User.reset_token == reset_data.token,
                User.reset_token_expires > datetime.utcnow()
            )
        ).first()
        
        if not user:
            return AuthResponse(
                success=False,
                message="Token inválido ou expirado",
                error="INVALID_TOKEN"
            )
        
        # Valida nova senha
        if not auth_service.is_password_strong(reset_data.new_password):
            return AuthResponse(
                success=False,
                message="Senha não atende aos requisitos de segurança",
                error="WEAK_PASSWORD"
            )
        
        # Atualiza senha e limpa token
        user.hashed_password = auth_service._hash_password(reset_data.new_password)
        user.reset_token = None
        user.reset_token_expires = None
        db.commit()
        
        # Log do reset
        logger.info(f"PASSWORD_RESET_COMPLETE | {user.username} | {user.email}")
        
        return AuthResponse(
            success=True,
            message="Senha resetada com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro na confirmação de reset: {str(e)}")
        return AuthResponse(
            success=False,
            message="Erro interno do servidor",
            error="INTERNAL_ERROR"
        )

@auth_router.post("/change-password", response_model=AuthResponse)
async def change_password(
    change_data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Altera senha do usuário logado
    """
    try:
        # Verifica senha atual
        if not auth_service._verify_password(change_data.current_password, current_user.hashed_password):
            return AuthResponse(
                success=False,
                message="Senha atual incorreta",
                error="INVALID_CURRENT_PASSWORD"
            )
        
        # Valida nova senha
        if not auth_service.is_password_strong(change_data.new_password):
            return AuthResponse(
                success=False,
                message="Nova senha não atende aos requisitos de segurança",
                error="WEAK_PASSWORD"
            )
        
        # Atualiza senha
        current_user.hashed_password = auth_service._hash_password(change_data.new_password)
        db.commit()
        
        # Log da alteração
        logger.info(f"PASSWORD_CHANGE | {current_user.username}")
        
        return AuthResponse(
            success=True,
            message="Senha alterada com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro na alteração de senha: {str(e)}")
        return AuthResponse(
            success=False,
            message="Erro interno do servidor",
            error="INTERNAL_ERROR"
        )

# ==================== GERENCIAMENTO DE PERFIL ====================

@auth_router.get("/profile", response_model=AuthResponse)
async def get_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Retorna perfil do usuário atual
    """
    try:
        user_public = UserPublic.from_orm(current_user)
        
        return AuthResponse(
            success=True,
            message="Perfil obtenido com sucesso",
            data=user_public.dict()
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter perfil: {str(e)}")
        return AuthResponse(
            success=False,
            message="Erro interno do servidor",
            error="INTERNAL_ERROR"
        )

@auth_router.put("/profile", response_model=AuthResponse)
async def update_profile(
    profile_data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Atualiza perfil do usuário
    """
    try:
        # Atualiza campos fornecidos
        if profile_data.full_name is not None:
            current_user.full_name = profile_data.full_name
        if profile_data.company is not None:
            current_user.company = profile_data.company
        if profile_data.website is not None:
            current_user.website = profile_data.website
        if profile_data.bio is not None:
            current_user.bio = profile_data.bio
        if profile_data.preferences is not None:
            current_user.preferences = profile_data.preferences
        
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        return AuthResponse(
            success=True,
            message="Perfil atualizado com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro na atualização do perfil: {str(e)}")
        return AuthResponse(
            success=False,
            message="Erro interno do servidor",
            error="INTERNAL_ERROR"
        )

# ==================== GERENCIAMENTO DE SESSÕES ====================

@auth_router.get("/sessions", response_model=AuthResponse)
async def get_user_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lista todas as sessões ativas do usuário
    """
    try:
        sessions = auth_service.get_user_sessions(current_user.id, db)
        
        return AuthResponse(
            success=True,
            message="Sessões obtenidas com sucesso",
            data=SessionList(
                sessions=sessions,
                current_session_id=str(current_user.id)  # Simplificado
            ).dict()
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter sessões: {str(e)}")
        return AuthResponse(
            success=False,
            message="Erro interno do servidor",
            error="INTERNAL_ERROR"
        )

@auth_router.delete("/sessions/{session_id}", response_model=AuthResponse)
async def revoke_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Revoga sessão específica
    """
    try:
        success = auth_service.revoke_session(current_user.id, session_id, db)
        
        if success:
            return AuthResponse(
                success=True,
                message="Sessão revogada com sucesso"
            )
        else:
            return AuthResponse(
                success=False,
                message="Sessão não encontrada",
                error="SESSION_NOT_FOUND"
            )
        
    except Exception as e:
        logger.error(f"Erro ao revogar sessão: {str(e)}")
        return AuthResponse(
            success=False,
            message="Erro interno do servidor",
            error="INTERNAL_ERROR"
        )

# ==================== INFORMAÇÕES DO TOKEN ====================

@auth_router.get("/token/verify", response_model=AuthResponse)
async def verify_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
):
    """
    Verifica se token é válido
    """
    try:
        if not credentials:
            return AuthResponse(
                success=False,
                message="Token não fornecido",
                error="NO_TOKEN"
            )
        
        # Verifica token
        is_valid = auth_service.is_token_valid(credentials.credentials)
        
        if is_valid:
            return AuthResponse(
                success=True,
                message="Token válido"
            )
        else:
            return AuthResponse(
                success=False,
                message="Token inválido ou expirado",
                error="INVALID_TOKEN"
            )
        
    except Exception as e:
        logger.error(f"Erro na verificação de token: {str(e)}")
        return AuthResponse(
            success=False,
            message="Erro interno do servidor",
            error="INTERNAL_ERROR"
        )

# ==================== HEALTH CHECK ====================

@auth_router.get("/health")
async def auth_health():
    """
    Health check do serviço de autenticação
    """
    return {
        "status": "healthy",
        "service": "authentication",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    }