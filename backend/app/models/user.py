"""
3dPot Backend - Modelo de Usuário
Sistema de Prototipagem Sob Demanda
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, Integer, Text, Column, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from passlib.context import CryptContext
from jose import jwt

from ..database import Base
from ..config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    """Modelo de Usuário para autenticação e autorização"""
    __tablename__ = "users"
    
    # === PRIMARY KEYS ===
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # === AUTHENTICATION ===
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # === PROFILE ===
    full_name = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    company = Column(String(255), nullable=True)
    role = Column(String(50), default="user", nullable=False)  # admin, user, developer
    
    # === STATUS ===
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # === PREFERENCES ===
    preferred_language = Column(String(10), default="pt-BR", nullable=False)
    timezone = Column(String(50), default="America/Sao_Paulo", nullable=False)
    
    # === METADATA ===
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # === API ACCESS ===
    api_key = Column(String(255), unique=True, index=True, nullable=True)
    api_key_created_at = Column(DateTime(timezone=True), nullable=True)
    
    # === RELATIONSHIPS ===
    # projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    devices = relationship("Device", back_populates="owner", cascade="all, delete-orphan")
    sensor_data = relationship("SensorData", back_populates="user")
    alerts = relationship("Alert", back_populates="user")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"
    
    def verify_password(self, plain_password: str) -> bool:
        """Verifica se a senha fornecida está correta"""
        return pwd_context.verify(plain_password, self.hashed_password)
    
    def hash_password(self, plain_password: str) -> str:
        """Gera o hash da senha"""
        return pwd_context.hash(plain_password)
    
    def create_access_token(self) -> str:
        """Cria um token de acesso JWT"""
        to_encode = {
            "sub": self.email,
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "is_superuser": self.is_superuser
        }
        
        expire = datetime.utcnow() + settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def generate_api_key(self) -> str:
        """Gera uma nova API key para o usuário"""
        import secrets
        import string
        
        # Gera uma chave de 32 caracteres
        characters = string.ascii_letters + string.digits
        api_key = ''.join(secrets.choice(characters) for _ in range(32))
        
        self.api_key = api_key
        self.api_key_created_at = datetime.utcnow()
        
        return api_key
    
    @classmethod
    def create_user(cls, email: str, username: str, password: str, full_name: str = None) -> "User":
        """
        Método helper para criar um novo usuário.
        
        Args:
            email: Email do usuário
            username: Nome de usuário único
            password: Senha em texto plano (será hashada)
            full_name: Nome completo opcional
            
        Returns:
            User: Instância do usuário criado
        """
        hashed_password = pwd_context.hash(password)
        
        return cls(
            email=email,
            username=username,
            full_name=full_name,
            hashed_password=hashed_password
        )
    
    @property
    def is_admin(self) -> bool:
        """Retorna True se o usuário é administrador"""
        return self.is_superuser or self.role == "admin"
    
    @property
    def can_access_api(self) -> bool:
        """Retorna True se o usuário tem acesso à API"""
        return self.is_active and (self.is_superuser or self.role in ["admin", "developer"])
    
    class Config:
        from_attributes = True


# Índices para otimização de performance
Index('idx_users_email', User.email)
Index('idx_users_username', User.username)
Index('idx_users_api_key', User.api_key)
Index('idx_users_is_active', User.is_active)
Index('idx_users_created_at', User.created_at)
