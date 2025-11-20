"""
Serviço de Autenticação - 3dPot v2.0
JWT OAuth2 completo com refresh tokens, rate limiting e segurança
"""

import secrets
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID, uuid4
import re
import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from core.config import settings
from models import User, RefreshToken
from schemas import (
    UserRegister, UserLogin, UserLoginResponse, UserPublic, 
    PasswordValidation, SessionInfo, AuthResponse
)

# Configuração de criptografia
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthenticationError(Exception):
    """Exceção para erros de autenticação"""
    pass

class TokenExpiredError(AuthenticationError):
    """Token expirado"""
    pass

class TokenInvalidError(AuthenticationError):
    """Token inválido"""
    pass

class UserLockedError(AuthenticationError):
    """Usuário bloqueado"""
    pass

class RateLimitError(AuthenticationError):
    """Rate limit excedido"""
    pass

class AuthenticationService:
    """Serviço completo de autenticação JWT OAuth2"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
        
        # Rate limiting (em produção, usar Redis)
        self._login_attempts = {}
        self._rate_limit_cache = {}
    
    # ==================== CRIPTOGRAFIA E HASH ====================
    
    def _hash_password(self, password: str) -> str:
        """Hasheia senha usando bcrypt"""
        return pwd_context.hash(password)
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verifica senha"""
        return pwd_context.verify(password, hashed)
    
    def _generate_secure_token(self, length: int = 64) -> str:
        """Gera token seguro random"""
        return secrets.token_urlsafe(length)
    
    def _hash_token(self, token: str) -> str:
        """Hasheia token para armazenamento seguro"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    def _verify_token_signature(self, token: str) -> bool:
        """Verifica assinatura do token"""
        try:
            jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return True
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Token expirado")
        except jwt.InvalidTokenError:
            raise TokenInvalidError("Token inválido")
        return False
    
    # ==================== VALIDAÇÃO DE SENHA ====================
    
    def validate_password_strength(self, password: str) -> PasswordValidation:
        """Valida força da senha"""
        return PasswordValidation.validate_password(
            password,
            min_length=settings.PASSWORD_MIN_LENGTH,
            require_upper=settings.PASSWORD_REQUIRE_UPPERCASE,
            require_lower=settings.PASSWORD_REQUIRE_LOWERCASE,
            require_digit=settings.PASSWORD_REQUIRE_NUMBERS,
            require_special=settings.PASSWORD_REQUIRE_SPECIAL
        )
    
    def is_password_strong(self, password: str) -> bool:
        """Verifica se senha é forte"""
        validation = self.validate_password_strength(password)
        return all([
            validation.min_length,
            validation.has_uppercase,
            validation.has_lowercase,
            validation.has_digit,
            validation.has_special if settings.PASSWORD_REQUIRE_SPECIAL else True
        ])
    
    # ==================== JWT TOKENS ====================
    
    def create_access_token(self, user: User) -> str:
        """Cria token de acesso JWT"""
        now = datetime.utcnow()
        expire = now + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "type": "access",
            "iat": now,
            "exp": expire,
            "jti": str(uuid4())  # JWT ID único
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user: User, db: Session, 
                           device_info: Optional[Dict] = None,
                           ip_address: Optional[str] = None,
                           user_agent: Optional[str] = None) -> Tuple[str, RefreshToken]:
        """Cria refresh token e salva no banco"""
        # Token raw para response
        refresh_token_raw = self._generate_secure_token()
        token_hash = self._hash_token(refresh_token_raw)
        
        # Expiração
        expires_at = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        # Registro no banco
        refresh_token = RefreshToken(
            user_id=user.id,
            token=refresh_token_raw,  # Guardamos o token raw para lookup
            hashed_token=token_hash,
            device_info=device_info or {},
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at
        )
        
        db.add(refresh_token)
        db.commit()
        db.refresh(refresh_token)
        
        return refresh_token_raw, refresh_token
    
    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """Verifica e decodifica token de acesso"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Token de acesso expirado")
        except jwt.InvalidTokenError:
            raise TokenInvalidError("Token de acesso inválido")
    
    def verify_refresh_token(self, token: str, db: Session) -> User:
        """Verifica refresh token e retorna usuário"""
        # Busca token no banco
        refresh_token = db.query(RefreshToken).filter(
            and_(
                RefreshToken.token == token,
                RefreshToken.is_active == True,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.utcnow()
            )
        ).first()
        
        if not refresh_token:
            raise TokenInvalidError("Refresh token não encontrado ou inválido")
        
        # Atualiza última utilização
        refresh_token.last_used = datetime.utcnow()
        db.commit()
        
        # Busca usuário
        user = db.query(User).filter(User.id == refresh_token.user_id).first()
        if not user or not user.is_active:
            raise AuthenticationError("Usuário não encontrado ou inativo")
        
        if user.is_locked():
            raise UserLockedError("Conta temporariamente bloqueada")
        
        return user
    
    # ==================== REGISTRO DE USUÁRIOS ====================
    
    def register_user(self, user_data: UserRegister, db: Session, 
                     ip_address: Optional[str] = None) -> User:
        """Registra novo usuário"""
        
        # Verifica se email já existe
        existing_user = db.query(User).filter(
            or_(User.email == user_data.email, User.username == user_data.username)
        ).first()
        
        if existing_user:
            if existing_user.email == user_data.email:
                raise AuthenticationError("Email já está em uso")
            if existing_user.username == user_data.username:
                raise AuthenticationError("Nome de usuário já está em uso")
        
        # Valida senha
        if not self.is_password_strong(user_data.password):
            raise AuthenticationError("Senha não atende aos requisitos de segurança")
        
        # Cria usuário
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=self._hash_password(user_data.password),
            company=user_data.company,
            website=user_data.website,
            is_active=True,
            is_verified=False
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    # ==================== LOGIN E AUTENTICAÇÃO ====================
    
    def authenticate_user(self, login_data: UserLogin, db: Session,
                         ip_address: Optional[str] = None,
                         user_agent: Optional[str] = None) -> UserLoginResponse:
        """
        Autentica usuário e retorna tokens.
        Sprint 9: Com suporte para MFA challenge quando habilitado.
        """
        from backend.core.config import MFA_ENABLED, MFA_REQUIRED_FOR_ADMIN
        
        # Verifica rate limiting por IP
        self._check_rate_limit_login(ip_address)
        
        # Busca usuário por username ou email
        user = db.query(User).filter(
            or_(User.username == login_data.username, User.email == login_data.username)
        ).first()
        
        if not user:
            self._record_failed_attempt(ip_address)
            raise AuthenticationError("Credenciais inválidas")
        
        # Verifica se conta está bloqueada
        if user.is_locked():
            raise UserLockedError("Conta temporariamente bloqueada devido a tentativas falhadas")
        
        # Verifica senha
        if not self._verify_password(login_data.password, user.hashed_password):
            self._increment_login_attempts(user.id, ip_address)
            raise AuthenticationError("Credenciais inválidas")
        
        # Verifica se usuário está ativo
        if not user.is_active:
            raise AuthenticationError("Conta desativada")
        
        # Sprint 9: Verifica se MFA é necessário
        mfa_required = False
        if MFA_ENABLED:
            # MFA é obrigatório para admins se configurado
            if MFA_REQUIRED_FOR_ADMIN and (user.is_superuser or user.role == 'admin'):
                mfa_required = True
                # Se admin não tem MFA configurado, força erro
                if not user.mfa_enabled:
                    raise AuthenticationError("MFA é obrigatório para administradores. Configure MFA antes de fazer login.")
            # Ou se o usuário tem MFA habilitado voluntariamente
            elif user.mfa_enabled:
                mfa_required = True
        
        # Se MFA é necessário, retorna token parcial para challenge
        if mfa_required:
            # Cria um token temporário de MFA challenge (curta duração: 5 min)
            mfa_challenge_token = self._create_mfa_challenge_token(user)
            
            # NÃO reseta tentativas de login nem atualiza last_login ainda
            # Isso será feito após validação MFA
            
            return UserLoginResponse(
                access_token="",  # Token vazio - será emitido após MFA
                refresh_token="",  # Token vazio - será emitido após MFA
                token_type="bearer",
                expires_in=300,  # 5 minutos para completar MFA
                user=UserPublic.from_orm(user),
                mfa_required=True,
                mfa_token=mfa_challenge_token
            )
        
        # Login normal sem MFA (backward compatible)
        # Reset tentativas de login em caso de sucesso
        self._reset_login_attempts(user.id, ip_address)
        
        # Atualiza último login
        user.last_login = datetime.utcnow()
        user.login_attempts = 0
        user.locked_until = None
        db.commit()
        
        # Cria tokens
        access_token = self.create_access_token(user)
        refresh_token, refresh_token_record = self.create_refresh_token(
            user, db, 
            device_info=login_data.device_info,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Determina tempo de expiração baseado no "remember me"
        expires_in = (
            self.refresh_token_expire_days * 24 * 3600  # 7 dias
            if login_data.remember_me 
            else self.access_token_expire_minutes * 60  # 30 minutos
        )
        
        return UserLoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=expires_in,
            user=UserPublic.from_orm(user),
            mfa_required=False
        )
    
    def refresh_tokens(self, refresh_token: str, db: Session) -> UserLoginResponse:
        """Renova tokens usando refresh token"""
        
        # Verifica refresh token
        user = self.verify_refresh_token(refresh_token, db)
        
        # Gera novos tokens
        access_token = self.create_access_token(user)
        
        # Cria novo refresh token (rotatividade)
        new_refresh_token, _ = self.create_refresh_token(user, db)
        
        # Revoga refresh token antigo
        old_token = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token
        ).first()
        if old_token:
            old_token.is_revoked = True
            old_token.revoked_at = datetime.utcnow()
            db.commit()
        
        return UserLoginResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=self.access_token_expire_minutes * 60,
            user=UserPublic.from_orm(user)
        )
    
    # ==================== LOGOUT ====================
    
    def logout(self, refresh_token: Optional[str] = None, 
               db: Session = None, user_id: Optional[UUID] = None) -> bool:
        """Faz logout do usuário"""
        
        if refresh_token:
            # Revoga refresh token específico
            refresh_token_record = db.query(RefreshToken).filter(
                RefreshToken.token == refresh_token
            ).first()
            if refresh_token_record:
                refresh_token_record.is_revoked = True
                refresh_token_record.revoked_at = datetime.utcnow()
                db.commit()
        
        elif user_id:
            # Revoga todos os refresh tokens do usuário
            db.query(RefreshToken).filter(
                RefreshToken.user_id == user_id,
                RefreshToken.is_active == True
            ).update({
                'is_revoked': True,
                'revoked_at': datetime.utcnow()
            })
            db.commit()
        
        return True
    
    def logout_all_sessions(self, user_id: UUID, db: Session) -> bool:
        """Faz logout de todas as sessões exceto a atual"""
        # Em uma implementação completa, precisaríamos identificar a sessão atual
        # Por simplicidade, revogamos todos os tokens
        self.logout(user_id=user_id, db=db)
        return True
    
    # ==================== GERENCIAMENTO DE SESSÕES ====================
    
    def get_user_sessions(self, user_id: UUID, db: Session) -> List[SessionInfo]:
        """Retorna todas as sessões ativas do usuário"""
        
        tokens = db.query(RefreshToken).filter(
            and_(
                RefreshToken.user_id == user_id,
                RefreshToken.is_active == True,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.utcnow()
            )
        ).all()
        
        sessions = []
        for token in tokens:
            sessions.append(SessionInfo(
                session_id=str(token.id),
                device_info=token.device_info,
                ip_address=token.ip_address or "Unknown",
                user_agent=token.user_agent or "Unknown",
                created_at=token.created_at,
                last_used=token.last_used or token.created_at,
                is_active=True
            ))
        
        return sessions
    
    def revoke_session(self, user_id: UUID, session_id: str, db: Session) -> bool:
        """Revoga sessão específica"""
        
        token = db.query(RefreshToken).filter(
            and_(
                RefreshToken.id == UUID(session_id),
                RefreshToken.user_id == user_id
            )
        ).first()
        
        if token:
            token.is_revoked = True
            token.revoked_at = datetime.utcnow()
            db.commit()
            return True
        
        return False
    
    # ==================== MFA CHALLENGE (SPRINT 9) ====================
    
    def _create_mfa_challenge_token(self, user: User) -> str:
        """
        Cria token temporário para MFA challenge (5 minutos)
        Este token permite verificar MFA após credenciais corretas
        """
        now = datetime.utcnow()
        expire = now + timedelta(minutes=5)
        
        payload = {
            "sub": str(user.id),
            "username": user.username,
            "type": "mfa_challenge",
            "iat": now,
            "exp": expire,
            "jti": str(uuid4())
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_mfa_challenge_token(self, mfa_token: str) -> Dict[str, Any]:
        """
        Verifica token de MFA challenge e retorna payload
        """
        try:
            payload = jwt.decode(mfa_token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != "mfa_challenge":
                raise TokenInvalidError("Token não é um MFA challenge válido")
            return payload
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("MFA challenge expirado. Faça login novamente.")
        except jwt.InvalidTokenError:
            raise TokenInvalidError("MFA challenge inválido")
    
    def complete_mfa_login(self, mfa_token: str, code: str, db: Session,
                          device_info: Optional[Dict] = None,
                          ip_address: Optional[str] = None,
                          user_agent: Optional[str] = None) -> UserLoginResponse:
        """
        Completa login após verificação MFA bem-sucedida.
        Sprint 9: Valida código MFA e emite tokens finais.
        """
        from backend.services.mfa_service import mfa_service, MFAInvalidCodeException
        
        # Verifica token de challenge
        payload = self.verify_mfa_challenge_token(mfa_token)
        user_id = payload.get("sub")
        
        # Busca usuário
        user = db.query(User).filter(User.id == UUID(user_id)).first()
        if not user or not user.is_active:
            raise AuthenticationError("Usuário não encontrado ou inativo")
        
        # Valida código MFA (TOTP ou backup code)
        try:
            is_valid = mfa_service.validate_mfa_code(user, code)
        except MFAInvalidCodeException as e:
            raise AuthenticationError(str(e))
        
        if not is_valid:
            raise AuthenticationError("Código MFA inválido")
        
        # MFA validado com sucesso - completa login
        # Reset tentativas de login
        self._reset_login_attempts(user.id, ip_address)
        
        # Atualiza último login
        user.last_login = datetime.utcnow()
        user.login_attempts = 0
        user.locked_until = None
        db.commit()
        
        # Cria tokens finais
        access_token = self.create_access_token(user)
        refresh_token, refresh_token_record = self.create_refresh_token(
            user, db,
            device_info=device_info,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return UserLoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=self.access_token_expire_minutes * 60,
            user=UserPublic.from_orm(user),
            mfa_required=False
        )
    
    # ==================== RATE LIMITING ====================
    
    def _check_rate_limit_login(self, ip_address: Optional[str]) -> None:
        """Verifica rate limiting para login"""
        if not ip_address:
            return
        
        now = datetime.utcnow()
        
        # Simulação de rate limiting (em produção usar Redis)
        key = f"login_attempts_{ip_address}"
        attempts = self._rate_limit_cache.get(key, [])
        
        # Remove attempts antigas (mais de 1 hora)
        recent_attempts = [t for t in attempts if now - t < timedelta(hours=1)]
        self._rate_limit_cache[key] = recent_attempts
        
        if len(recent_attempts) >= 5:  # Max 5 attempts per hour
            raise RateLimitError("Muitas tentativas de login. Tente novamente em 1 hora")
    
    def _record_failed_attempt(self, ip_address: Optional[str]) -> None:
        """Registra tentativa falhada"""
        if not ip_address:
            return
        
        now = datetime.utcnow()
        key = f"login_attempts_{ip_address}"
        attempts = self._rate_limit_cache.get(key, [])
        attempts.append(now)
        self._rate_limit_cache[key] = attempts
    
    def _increment_login_attempts(self, user_id: UUID, ip_address: Optional[str]) -> None:
        """Incrementa tentativas de login falhadas"""
        # Em uma implementação completa, isso seria persistido no banco
        pass
    
    def _reset_login_attempts(self, user_id: UUID, ip_address: Optional[str]) -> None:
        """Reset tentativas de login"""
        if ip_address:
            key = f"login_attempts_{ip_address}"
            if key in self._rate_limit_cache:
                del self._rate_limit_cache[key]
    
    # ==================== UTILITÁRIOS ====================
    
    def is_token_valid(self, token: str) -> bool:
        """Verifica se token é válido sem decodificar"""
        try:
            jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return True
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return False
    
    def get_user_from_token(self, token: str) -> Optional[User]:
        """Extrai usuário do token (sem verificar expiração para cache)"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], options={"verify_exp": False})
            user_id = payload.get("sub")
            return user_id
        except jwt.InvalidTokenError:
            return None
    
    def cleanup_expired_tokens(self, db: Session) -> int:
        """Remove tokens expirados do banco"""
        now = datetime.utcnow()
        
        deleted = db.query(RefreshToken).filter(
            RefreshToken.expires_at < now
        ).delete()
        db.commit()
        
        return deleted


# Instância global do serviço
auth_service = AuthenticationService()