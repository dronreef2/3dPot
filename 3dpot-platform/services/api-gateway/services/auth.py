"""
3dPot Platform - Authentication Service
Criado em: 2025-11-12 22:42:43
Autor: MiniMax Agent

Serviço de autenticação com JWT e hash de senhas
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from models.database_models import User
from database.database import get_database

# Configuração de segurança
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class AuthConfig:
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET", "your-super-secret-key-change-in-production-must-be-32-chars-minimum")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24h
        self.refresh_token_expire_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))  # 7 dias

config = AuthConfig()

class AuthService:
    def __init__(self, db: AsyncSession, secret_key: str):
        self.db = db
        self.secret_key = secret_key
        
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica se a senha está correta"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Gera hash da senha"""
        return pwd_context.hash(password)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Autentica usuário por email e senha"""
        try:
            result = await self.db.execute(
                select(User).where(User.email == email, User.is_active == True)
            )
            user = result.scalar_one_or_none()
            
            if user and self.verify_password(password, user.password_hash):
                return user
            return None
        except Exception:
            return None
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Busca usuário por ID"""
        try:
            result = await self.db.execute(
                select(User).where(User.id == user_id, User.is_active == True)
            )
            return result.scalar_one_or_none()
        except Exception:
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Busca usuário por email"""
        try:
            result = await self.db.execute(
                select(User).where(User.email == email, User.is_active == True)
            )
            return result.scalar_one_or_none()
        except Exception:
            return None
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Cria token de acesso JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=config.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=config.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Cria token de refresh JWT"""
        expire = datetime.utcnow() + timedelta(days=config.refresh_token_expire_days)
        to_encode = data.copy()
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=config.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verifica e decodifica token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[config.algorithm])
            if payload.get("type") != token_type:
                return None
            return payload
        except JWTError:
            return None
    
    async def update_last_login(self, user_id: int):
        """Atualiza última data de login do usuário"""
        try:
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(last_login=datetime.utcnow())
            )
            await self.db.commit()
        except Exception:
            await self.db.rollback()

# Dependency para obter usuário atual
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_database)
) -> User:
    """Dependency para obter usuário autenticado"""
    auth_service = AuthService(db, config.secret_key)
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verificar token
        payload = auth_service.verify_token(credentials.credentials, "access")
        if payload is None:
            raise credentials_exception
        
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Buscar usuário no database
    user = await auth_service.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    
    return user

# Dependency para verificar role
def require_role(required_role: str):
    """Decorator para verificar role do usuário"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        roles_order = ["viewer", "operator", "user", "admin"]
        user_role_index = roles_order.index(current_user.role)
        required_role_index = roles_order.index(required_role)
        
        if user_role_index < required_role_index:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Required: {required_role}, Current: {current_user.role}"
            )
        return current_user
    return role_checker