"""
MFA Service - 3dPot v2.0
Sprint 9: Two-Factor Authentication (TOTP)

Implementação de autenticação de dois fatores baseada em TOTP (Time-based One-Time Password)
compatível com aplicativos como Google Authenticator, Authy, etc.
"""

import base64
import io
import logging
from datetime import datetime
from typing import Optional, Tuple
from uuid import UUID

import pyotp
import qrcode
from sqlalchemy.orm import Session

from backend.models import User
from backend.core.config import settings

logger = logging.getLogger(__name__)


class MFAError(Exception):
    """Exceção base para erros de MFA"""
    pass


class MFANotEnabledException(MFAError):
    """MFA não está habilitado para este usuário"""
    pass


class MFAInvalidCodeException(MFAError):
    """Código MFA inválido"""
    pass


class MFAService:
    """Serviço de autenticação multi-fator (MFA/2FA)"""
    
    def __init__(self):
        self.issuer_name = getattr(settings, 'MFA_ISSUER_NAME', '3dPot')
    
    def generate_secret(self) -> str:
        """
        Gera um novo secret base32 para TOTP
        
        Returns:
            str: Secret em formato base32
        """
        return pyotp.random_base32()
    
    def get_totp_uri(self, user: User, secret: str) -> str:
        """
        Gera URI para configuração do TOTP (usado em QR code)
        
        Args:
            user: Usuário para configurar MFA
            secret: Secret TOTP do usuário
            
        Returns:
            str: URI otpauth:// para QR code
        """
        return pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email,
            issuer_name=self.issuer_name
        )
    
    def generate_qr_code(self, uri: str) -> str:
        """
        Gera QR code em formato base64 para o URI TOTP
        
        Args:
            uri: URI otpauth:// do TOTP
            
        Returns:
            str: Imagem do QR code em base64
        """
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Converte para base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def verify_totp_code(self, secret: str, code: str, window: int = 1) -> bool:
        """
        Verifica se o código TOTP é válido
        
        Args:
            secret: Secret TOTP do usuário
            code: Código de 6 dígitos fornecido pelo usuário
            window: Janela de tolerância (padrão: 1 = ±30 segundos)
            
        Returns:
            bool: True se o código é válido
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=window)
    
    def enable_mfa(self, user: User, db: Session) -> Tuple[str, str]:
        """
        Habilita MFA para o usuário e retorna secret + QR code
        
        Args:
            user: Usuário para habilitar MFA
            db: Sessão do banco de dados
            
        Returns:
            Tuple[str, str]: (secret, qr_code_base64)
        """
        # Gera novo secret
        secret = self.generate_secret()
        
        # Atualiza usuário no banco
        user.mfa_secret = secret
        user.mfa_enabled = False  # Só habilita após verificação do primeiro código
        db.commit()
        db.refresh(user)
        
        # Gera QR code
        uri = self.get_totp_uri(user, secret)
        qr_code = self.generate_qr_code(uri)
        
        logger.info(f"MFA setup iniciado para usuário {user.username} (id={user.id})")
        
        return secret, qr_code
    
    def confirm_mfa_enrollment(self, user: User, code: str, db: Session) -> bool:
        """
        Confirma o enrollment de MFA verificando o primeiro código
        
        Args:
            user: Usuário confirmando MFA
            code: Código TOTP de 6 dígitos
            db: Sessão do banco de dados
            
        Returns:
            bool: True se MFA foi habilitado com sucesso
            
        Raises:
            MFAInvalidCodeException: Se o código for inválido
        """
        if not user.mfa_secret:
            raise MFAError("MFA setup não iniciado para este usuário")
        
        # Verifica código
        if not self.verify_totp_code(user.mfa_secret, code):
            raise MFAInvalidCodeException("Código MFA inválido")
        
        # Habilita MFA
        user.mfa_enabled = True
        db.commit()
        db.refresh(user)
        
        logger.info(f"MFA habilitado com sucesso para usuário {user.username} (id={user.id})")
        
        return True
    
    def disable_mfa(self, user: User, db: Session) -> bool:
        """
        Desabilita MFA para o usuário
        
        Args:
            user: Usuário para desabilitar MFA
            db: Sessão do banco de dados
            
        Returns:
            bool: True se MFA foi desabilitado
        """
        user.mfa_enabled = False
        user.mfa_secret = None
        db.commit()
        db.refresh(user)
        
        logger.info(f"MFA desabilitado para usuário {user.username} (id={user.id})")
        
        return True
    
    def validate_mfa_code(self, user: User, code: str) -> bool:
        """
        Valida código MFA durante login
        
        Args:
            user: Usuário autenticando
            code: Código TOTP de 6 dígitos
            
        Returns:
            bool: True se código é válido
            
        Raises:
            MFANotEnabledException: Se MFA não está habilitado
            MFAInvalidCodeException: Se código é inválido
        """
        if not user.mfa_enabled or not user.mfa_secret:
            raise MFANotEnabledException("MFA não está habilitado para este usuário")
        
        if not self.verify_totp_code(user.mfa_secret, code):
            raise MFAInvalidCodeException("Código MFA inválido")
        
        logger.info(f"Código MFA validado com sucesso para usuário {user.username}")
        
        return True
    
    def generate_backup_codes(self, count: int = 10) -> list:
        """
        Gera códigos de backup para recuperação
        
        Args:
            count: Número de códigos a gerar
            
        Returns:
            list: Lista de códigos de backup
        """
        import secrets
        return [
            f"{secrets.randbelow(10000):04d}-{secrets.randbelow(10000):04d}"
            for _ in range(count)
        ]
    
    def is_mfa_required(self, user: User) -> bool:
        """
        Verifica se MFA é obrigatório para este usuário
        
        Args:
            user: Usuário a verificar
            
        Returns:
            bool: True se MFA é obrigatório
        """
        # MFA obrigatório para admins se configurado
        mfa_required_for_admin = getattr(settings, 'MFA_REQUIRED_FOR_ADMIN', False)
        if mfa_required_for_admin and (user.is_superuser or user.role == 'admin'):
            return True
        
        # Senão, é opcional
        return False


# Instância global do serviço
mfa_service = MFAService()
