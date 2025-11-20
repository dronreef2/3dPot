"""
MFA Schemas - 3dPot v2.0
Sprint 9: Schemas for Multi-Factor Authentication
"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator


class MFAEnableRequest(BaseModel):
    """Request para iniciar enrollment de MFA"""
    pass


class MFAEnableResponse(BaseModel):
    """Response com QR code e secret para MFA enrollment"""
    secret: str = Field(..., description="Secret TOTP (backup manual)")
    qr_code: str = Field(..., description="QR code em base64 para escanear")
    backup_codes: List[str] = Field(default_factory=list, description="Códigos de backup")
    
    class Config:
        json_schema_extra = {
            "example": {
                "secret": "JBSWY3DPEHPK3PXP",
                "qr_code": "data:image/png;base64,iVBORw0KG...",
                "backup_codes": ["1234-5678", "9012-3456"]
            }
        }


class MFAConfirmRequest(BaseModel):
    """Request para confirmar MFA enrollment"""
    code: str = Field(..., min_length=6, max_length=6, description="Código TOTP de 6 dígitos")
    
    @validator('code')
    def code_must_be_numeric(cls, v):
        if not v.isdigit():
            raise ValueError('Código deve conter apenas dígitos')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "123456"
            }
        }


class MFADisableRequest(BaseModel):
    """Request para desabilitar MFA"""
    password: str = Field(..., description="Senha atual para confirmação")
    code: Optional[str] = Field(None, min_length=6, max_length=6, description="Código MFA (se habilitado)")


class MFAVerifyRequest(BaseModel):
    """Request para verificar código MFA durante login"""
    code: str = Field(..., min_length=6, max_length=6, description="Código TOTP de 6 dígitos")
    
    @validator('code')
    def code_must_be_numeric(cls, v):
        if not v.isdigit():
            raise ValueError('Código deve conter apenas dígitos')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "123456"
            }
        }


class MFAStatusResponse(BaseModel):
    """Response com status de MFA do usuário"""
    enabled: bool = Field(..., description="MFA está habilitado")
    required: bool = Field(..., description="MFA é obrigatório para este usuário")
    
    class Config:
        json_schema_extra = {
            "example": {
                "enabled": True,
                "required": False
            }
        }


class MFABackupCodesResponse(BaseModel):
    """Response com códigos de backup regenerados"""
    backup_codes: List[str] = Field(..., description="Novos códigos de backup")
    
    class Config:
        json_schema_extra = {
            "example": {
                "backup_codes": ["1234-5678", "9012-3456", "4567-8901"]
            }
        }
