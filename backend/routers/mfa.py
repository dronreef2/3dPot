"""
MFA Router - 3dPot v2.0
Sprint 9: Multi-Factor Authentication Endpoints
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.database import get_db
from backend.models import User
from backend.schemas.mfa import (
    MFAEnableRequest, MFAEnableResponse, MFAConfirmRequest,
    MFADisableRequest, MFAVerifyRequest, MFAStatusResponse,
    MFABackupCodesResponse
)
from backend.schemas import AuthResponse
from backend.services.mfa_service import (
    mfa_service, MFAError, MFANotEnabledException, MFAInvalidCodeException
)
from backend.services.auth_service import auth_service
from backend.middleware.auth import get_current_active_user
from backend.observability import audit_security_event, AuditAction, get_request_id

logger = logging.getLogger(__name__)

# Router
mfa_router = APIRouter(prefix="/api/v1/auth/mfa", tags=["mfa"])


@mfa_router.get("/status", response_model=AuthResponse)
async def get_mfa_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    Retorna o status de MFA do usuário atual
    """
    try:
        status_data = MFAStatusResponse(
            enabled=current_user.mfa_enabled or False,
            required=mfa_service.is_mfa_required(current_user)
        )
        
        return AuthResponse(
            success=True,
            message="Status de MFA obtido com sucesso",
            data=status_data.dict()
        )
    except Exception as e:
        logger.error(f"Erro ao obter status de MFA: {str(e)}")
        return AuthResponse(
            success=False,
            message="Erro interno do servidor",
            error="INTERNAL_ERROR"
        )


@mfa_router.post("/enable", response_model=AuthResponse)
async def enable_mfa(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Inicia o processo de enrollment de MFA
    Retorna QR code e secret para configuração no app autenticador
    """
    try:
        # Verifica se MFA já está habilitado
        if current_user.mfa_enabled:
            return AuthResponse(
                success=False,
                message="MFA já está habilitado para este usuário",
                error="MFA_ALREADY_ENABLED"
            )
        
        # Gera secret e QR code
        secret, qr_code = mfa_service.enable_mfa(current_user, db)
        
        # Gera códigos de backup
        backup_codes = mfa_service.generate_backup_codes()
        current_user.mfa_backup_codes = backup_codes
        db.commit()
        
        # Audit log
        request_id = get_request_id(request)
        audit_security_event(
            event_type=AuditAction.MFA_ENROLLED,
            user_id=str(current_user.id),
            username=current_user.username,
            ip_address=request.client.host,
            request_id=request_id,
            details={"action": "mfa_setup_initiated"}
        )
        
        response_data = MFAEnableResponse(
            secret=secret,
            qr_code=qr_code,
            backup_codes=backup_codes
        )
        
        return AuthResponse(
            success=True,
            message="MFA setup iniciado. Escaneie o QR code e confirme com um código.",
            data=response_data.dict()
        )
        
    except Exception as e:
        logger.error(f"Erro ao habilitar MFA: {str(e)}")
        return AuthResponse(
            success=False,
            message="Erro interno do servidor",
            error="INTERNAL_ERROR"
        )


@mfa_router.post("/confirm", response_model=AuthResponse)
async def confirm_mfa(
    confirm_data: MFAConfirmRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Confirma o enrollment de MFA verificando o primeiro código
    """
    try:
        # Confirma enrollment
        success = mfa_service.confirm_mfa_enrollment(current_user, confirm_data.code, db)
        
        if success:
            # Audit log
            request_id = get_request_id(request)
            audit_security_event(
                event_type=AuditAction.MFA_ENROLLED,
                user_id=str(current_user.id),
                username=current_user.username,
                ip_address=request.client.host,
                request_id=request_id,
                details={"action": "mfa_enrollment_confirmed"}
            )
            
            return AuthResponse(
                success=True,
                message="MFA habilitado com sucesso"
            )
        
    except MFAInvalidCodeException as e:
        # Audit log for failed verification
        request_id = get_request_id(request)
        audit_security_event(
            event_type=AuditAction.MFA_CHALLENGE_FAILED,
            user_id=str(current_user.id),
            username=current_user.username,
            ip_address=request.client.host,
            request_id=request_id,
            details={"action": "mfa_enrollment_confirmation_failed", "reason": str(e)}
        )
        
        return AuthResponse(
            success=False,
            message=str(e),
            error="INVALID_MFA_CODE"
        )
    except MFAError as e:
        return AuthResponse(
            success=False,
            message=str(e),
            error="MFA_ERROR"
        )
    except Exception as e:
        logger.error(f"Erro ao confirmar MFA: {str(e)}")
        return AuthResponse(
            success=False,
            message="Erro interno do servidor",
            error="INTERNAL_ERROR"
        )


@mfa_router.post("/disable", response_model=AuthResponse)
async def disable_mfa(
    disable_data: MFADisableRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Desabilita MFA para o usuário
    Requer senha atual e código MFA (se habilitado)
    """
    try:
        # Verifica senha
        if not auth_service._verify_password(disable_data.password, current_user.hashed_password):
            return AuthResponse(
                success=False,
                message="Senha incorreta",
                error="INVALID_PASSWORD"
            )
        
        # Se MFA está habilitado, requer código
        if current_user.mfa_enabled and disable_data.code:
            try:
                mfa_service.validate_mfa_code(current_user, disable_data.code)
            except MFAInvalidCodeException:
                return AuthResponse(
                    success=False,
                    message="Código MFA inválido",
                    error="INVALID_MFA_CODE"
                )
        
        # Desabilita MFA
        mfa_service.disable_mfa(current_user, db)
        
        # Audit log
        request_id = get_request_id(request)
        audit_security_event(
            event_type=AuditAction.MFA_DISABLED,
            user_id=str(current_user.id),
            username=current_user.username,
            ip_address=request.client.host,
            request_id=request_id,
            details={"action": "mfa_disabled"}
        )
        
        return AuthResponse(
            success=True,
            message="MFA desabilitado com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao desabilitar MFA: {str(e)}")
        return AuthResponse(
            success=False,
            message="Erro interno do servidor",
            error="INTERNAL_ERROR"
        )


@mfa_router.post("/verify", response_model=AuthResponse)
async def verify_mfa_code(
    verify_data: MFAVerifyRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Verifica código MFA (usado durante login ou operações sensíveis)
    """
    try:
        # Valida código
        is_valid = mfa_service.validate_mfa_code(current_user, verify_data.code)
        
        if is_valid:
            # Audit log
            request_id = get_request_id(request)
            audit_security_event(
                event_type=AuditAction.MFA_CHALLENGE_PASSED,
                user_id=str(current_user.id),
                username=current_user.username,
                ip_address=request.client.host,
                request_id=request_id,
                details={"action": "mfa_verification_success"}
            )
            
            return AuthResponse(
                success=True,
                message="Código MFA válido"
            )
        
    except MFANotEnabledException as e:
        return AuthResponse(
            success=False,
            message=str(e),
            error="MFA_NOT_ENABLED"
        )
    except MFAInvalidCodeException as e:
        # Audit log
        request_id = get_request_id(request)
        audit_security_event(
            event_type=AuditAction.MFA_CHALLENGE_FAILED,
            user_id=str(current_user.id),
            username=current_user.username,
            ip_address=request.client.host,
            request_id=request_id,
            details={"action": "mfa_verification_failed"}
        )
        
        return AuthResponse(
            success=False,
            message=str(e),
            error="INVALID_MFA_CODE"
        )
    except Exception as e:
        logger.error(f"Erro ao verificar código MFA: {str(e)}")
        return AuthResponse(
            success=False,
            message="Erro interno do servidor",
            error="INTERNAL_ERROR"
        )


@mfa_router.post("/backup-codes/regenerate", response_model=AuthResponse)
async def regenerate_backup_codes(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Regenera códigos de backup para MFA
    """
    try:
        if not current_user.mfa_enabled:
            return AuthResponse(
                success=False,
                message="MFA não está habilitado",
                error="MFA_NOT_ENABLED"
            )
        
        # Gera novos códigos
        backup_codes = mfa_service.generate_backup_codes()
        current_user.mfa_backup_codes = backup_codes
        db.commit()
        
        # Audit log
        request_id = get_request_id(request)
        audit_security_event(
            event_type=AuditAction.MFA_BACKUP_CODES_REGENERATED,
            user_id=str(current_user.id),
            username=current_user.username,
            ip_address=request.client.host,
            request_id=request_id,
            details={"action": "backup_codes_regenerated"}
        )
        
        response_data = MFABackupCodesResponse(backup_codes=backup_codes)
        
        return AuthResponse(
            success=True,
            message="Códigos de backup regenerados. Guarde-os em local seguro.",
            data=response_data.dict()
        )
        
    except Exception as e:
        logger.error(f"Erro ao regenerar códigos de backup: {str(e)}")
        return AuthResponse(
            success=False,
            message="Erro interno do servidor",
            error="INTERNAL_ERROR"
        )
