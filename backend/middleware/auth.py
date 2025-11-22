"""
Middleware de Autenticação - 3dPot v2.0
Protege rotas com JWT e gerencia autenticação de forma segura
"""

import logging
from typing import Optional, Callable, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import (
    Request, Response, HTTPException, Depends, status
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Import condicional para BaseHTTPMiddleware (FastAPI >= 0.65)
try:
    from fastapi.middleware.base import BaseHTTPMiddleware
    MIDDLEWARE_AVAILABLE = True
except ImportError:
    # Fallback para versões mais antigas do FastAPI
    from fastapi import Request, Response
    BaseHTTPMiddleware = None
    MIDDLEWARE_AVAILABLE = False
    print("⚠️  BaseHTTPMiddleware não disponível nesta versão do FastAPI")

from sqlalchemy.orm import Session
import jwt

from backend.core.config import settings
from backend.models import User
from backend.services.auth_service import auth_service
from backend.schemas import TokenData, UserPublic
from backend.database import get_db

# Configurar logging
logger = logging.getLogger(__name__)

# Esquema de segurança HTTP Bearer
security = HTTPBearer(auto_error=False)

class AuthenticationError(HTTPException):
    """Exceção de autenticação HTTP"""
    def __init__(self, detail: str = "Não autorizado"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

class InsufficientPermissionsError(HTTPException):
    """Exceção para permissões insuficientes"""
    def __init__(self, detail: str = "Permissões insuficientes"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )

class TokenExpiredError(HTTPException):
    """Token expirado"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ==================== DEPENDÊNCIAS ====================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Obtém usuário atual a partir do token JWT
    """
    if not credentials:
        raise AuthenticationError("Token de acesso requerido")
    
    try:
        # Decodifica e verifica token
        payload = auth_service.verify_access_token(credentials.credentials)
        
        # Extrai dados do usuário
        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        
        if user_id is None:
            raise AuthenticationError("Token inválido")
        
        # Busca usuário no banco
        user = db.query(User).filter(User.id == UUID(user_id)).first()
        if user is None:
            raise AuthenticationError("Usuário não encontrado")
        
        # Verifica se usuário está ativo
        if not user.is_active:
            raise AuthenticationError("Usuário inativo")
        
        # Verifica se conta está bloqueada
        if user.is_locked():
            raise AuthenticationError("Conta temporariamente bloqueada")
        
        return user
        
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError()
    except jwt.InvalidTokenError:
        raise AuthenticationError("Token inválido")
    except Exception as e:
        logger.error(f"Erro na autenticação: {str(e)}")
        raise AuthenticationError("Erro na autenticação")

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verifica se usuário está ativo
    """
    if not current_user.is_active:
        raise AuthenticationError("Usuário inativo")
    
    return current_user

async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verifica se usuário é superusuário
    """
    if not current_user.is_superuser:
        raise InsufficientPermissionsError("Superusuário requerido")
    
    return current_user

async def get_current_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verifica se usuário tem email verificado
    """
    if not current_user.is_verified:
        raise AuthenticationError("Email não verificado")
    
    return current_user

def require_role(allowed_roles: list):
    """
    Decorator para verificar roles específicos
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise InsufficientPermissionsError(
                f"Role '{current_user.role}' não autorizado. Required: {allowed_roles}"
            )
        return current_user
    return role_checker

def require_permissions(permissions: list):
    """
    Decorator para verificar permissões específicas
    """
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        user_permissions = current_user.permissions or []
        
        for required_permission in permissions:
            if required_permission not in user_permissions:
                raise InsufficientPermissionsError(
                    f"Permissão '{required_permission}' requerida"
                )
        
        return current_user
    return permission_checker

# ==================== MIDDLEWARE ====================

# Classe de middleware condicional
if MIDDLEWARE_AVAILABLE and BaseHTTPMiddleware:
    class AuthenticationMiddleware(BaseHTTPMiddleware):
        """
        Middleware para log de requisições autenticadas
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Adiciona informações de autenticação ao request state
        request.state.user = None
        request.state.authenticated = False
        
        # Se tem token Bearer, adiciona ao state
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            request.state.bearer_token = token
            
            # Decodifica token para obter info do usuário (sem verificar expiração)
            try:
                payload = jwt.decode(
                    token, 
                    settings.SECRET_KEY, 
                    algorithms=[settings.ALGORITHM],
                    options={"verify_exp": False}
                )
                request.state.user_id = payload.get("sub")
                request.state.username = payload.get("username")
                request.state.role = payload.get("role")
                request.state.authenticated = True
            except jwt.InvalidTokenError:
                pass  # Token inválido será tratado na rota
        
        # Processa requisição
        response = await call_next(request)
        
        return response

else:
    # Placeholder para quando BaseHTTPMiddleware não está disponível
    class AuthenticationMiddleware:
        """
        Placeholder para AuthenticationMiddleware quando BaseHTTPMiddleware não está disponível
        """
        def __init__(self, app):
            self.app = app
    """
    Middleware para rate limiting por usuário
    """
    
    def __init__(self, app, calls_per_minute: int = 60):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        self._request_counts = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Obtém usuário atual (se autenticado)
        user_id = getattr(request.state, 'user_id', None)
        client_ip = request.client.host
        
        # Chave para rate limiting
        if user_id:
            rate_limit_key = f"user_{user_id}"
        else:
            rate_limit_key = f"ip_{client_ip}"
        
        # Verifica rate limiting
        now = datetime.now()
        
        # Limpa requests antigas (mais de 1 minuto)
        if rate_limit_key in self._request_counts:
            self._request_counts[rate_limit_key] = [
                timestamp for timestamp in self._request_counts[rate_limit_key]
                if now - timestamp < timedelta(minutes=1)
            ]
        
        # Inicializa contador se não existe
        if rate_limit_key not in self._request_counts:
            self._request_counts[rate_limit_key] = []
        
        # Verifica se excedeu limite
        if len(self._request_counts[rate_limit_key]) >= self.calls_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Muitas requisições. Tente novamente em alguns minutos."
            )
        
        # Adiciona request atual
        self._request_counts[rate_limit_key].append(now)
        
        # Processa requisição
        response = await call_next(request)
        
        return response

# ==================== UTILITÁRIOS ====================

def extract_token_from_header(auth_header: str) -> Optional[str]:
    """
    Extrai token do header Authorization
    """
    if not auth_header:
        return None
    
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    
    return parts[1]

def create_auth_response(
    user: User,
    access_token: str,
    refresh_token: Optional[str] = None,
    token_type: str = "bearer"
) -> Dict[str, Any]:
    """
    Cria resposta padronizada de autenticação
    """
    response = {
        "access_token": access_token,
        "token_type": token_type,
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": UserPublic.from_orm(user)
    }
    
    if refresh_token:
        response["refresh_token"] = refresh_token
    
    return response

def create_error_response(
    error_type: str,
    message: str,
    status_code: int = 400,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Cria resposta de erro padronizada
    """
    response = {
        "success": False,
        "error": {
            "type": error_type,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    if details:
        response["error"]["details"] = details
    
    return response

def log_authentication_attempt(
    username: str,
    ip_address: str,
    user_agent: str,
    success: bool,
    reason: Optional[str] = None
) -> None:
    """
    Log de tentativas de autenticação
    """
    status = "SUCCESS" if success else "FAILED"
    log_message = f"AUTH_LOGIN | {status} | {username} | {ip_address} | {user_agent}"
    
    if reason:
        log_message += f" | REASON: {reason}"
    
    if success:
        logger.info(log_message)
    else:
        logger.warning(log_message)

def log_authentication_logout(
    user_id: str,
    ip_address: str,
    user_agent: str,
    session_id: Optional[str] = None
) -> None:
    """
    Log de logout
    """
    session_info = f" | SESSION: {session_id}" if session_id else ""
    logger.info(f"AUTH_LOGOUT | {user_id} | {ip_address} | {user_agent}{session_info}")

# ==================== DECORATORS ADICIONAIS ====================

def require_https(require_https: bool = True):
    """
    Decorator para forçar HTTPS (em produção)
    """
    def https_checker(request: Request) -> Request:
        if require_https and not request.url.is_secure():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="HTTPS obrigatório em produção"
            )
        return request
    return https_checker

def cors_allow_credentials():
    """
    Configuração CORS para autenticação
    """
    return {
        "allow_origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        "allow_headers": ["Authorization", "Content-Type", "X-Requested-With"],
        "expose_headers": ["Authorization", "X-Total-Count"],
    }

# ==================== CONFIGURAÇÃO RÁPIDA ====================

def setup_authentication_middleware(app):
    """
    Configura middlewares de autenticação na aplicação
    """
    # Adiciona middleware de autenticação
    app.add_middleware(AuthenticationMiddleware)
    
    # TODO: Implementar RateLimitMiddleware se necessário
    # app.add_middleware(
    #     RateLimitMiddleware,
    #     calls_per_minute=settings.RATE_LIMIT_PER_MINUTE
    # )

# Instância global do security scheme
security = HTTPBearer(auto_error=False)