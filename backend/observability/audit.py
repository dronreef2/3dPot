"""
Audit Logging - 3dPot Sprint 7
Sistema de auditoria para rastreamento de ações críticas e mudanças de estado
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from backend.observability.logging_config import get_logger

# Get structured logger for audit
audit_logger = get_logger("audit")


class AuditAction:
    """Constantes para ações auditáveis"""
    
    # Authentication & Authorization
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    REGISTER = "user_register"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    PASSWORD_RESET_COMPLETE = "password_reset_complete"
    EMAIL_VERIFIED = "email_verified"
    
    # User Management
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_ACTIVATED = "user_activated"
    USER_DEACTIVATED = "user_deactivated"
    ROLE_CHANGED = "role_changed"
    PERMISSIONS_CHANGED = "permissions_changed"
    
    # Projects & Models
    PROJECT_CREATED = "project_created"
    PROJECT_UPDATED = "project_updated"
    PROJECT_DELETED = "project_deleted"
    MODEL_CREATED = "model_created"
    MODEL_UPDATED = "model_updated"
    MODEL_DELETED = "model_deleted"
    MODEL_SHARED = "model_shared"
    
    # Printing & Manufacturing
    PRINT_JOB_CREATED = "print_job_created"
    PRINT_JOB_STARTED = "print_job_started"
    PRINT_JOB_COMPLETED = "print_job_completed"
    PRINT_JOB_FAILED = "print_job_failed"
    PRINT_JOB_CANCELLED = "print_job_cancelled"
    
    # Cloud Rendering
    RENDER_JOB_CREATED = "render_job_created"
    RENDER_JOB_STARTED = "render_job_started"
    RENDER_JOB_COMPLETED = "render_job_completed"
    RENDER_JOB_FAILED = "render_job_failed"
    
    # Marketplace
    PRODUCT_LISTED = "product_listed"
    PRODUCT_UNLISTED = "product_unlisted"
    ORDER_CREATED = "order_created"
    ORDER_COMPLETED = "order_completed"
    ORDER_CANCELLED = "order_cancelled"
    PAYMENT_PROCESSED = "payment_processed"
    PAYMENT_FAILED = "payment_failed"
    
    # Simulation
    SIMULATION_CREATED = "simulation_created"
    SIMULATION_COMPLETED = "simulation_completed"
    SIMULATION_FAILED = "simulation_failed"
    
    # Configuration & Settings
    CONFIG_CHANGED = "config_changed"
    SETTINGS_UPDATED = "settings_updated"
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"
    
    # Security Events
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    PERMISSION_DENIED = "permission_denied"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"


class AuditLevel:
    """Níveis de criticidade para audit logs"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


def log_audit(
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    user_id: Optional[str] = None,
    username: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    request_id: Optional[str] = None,
    status: str = "success",
    level: str = AuditLevel.INFO,
    details: Optional[Dict[str, Any]] = None,
    **kwargs
):
    """
    Log de auditoria estruturado.
    
    Args:
        action: Ação sendo auditada (use constantes de AuditAction)
        resource_type: Tipo de recurso afetado (user, project, model, etc.)
        resource_id: ID do recurso afetado
        user_id: ID do usuário que realizou a ação
        username: Nome do usuário
        ip_address: Endereço IP de origem
        user_agent: User agent do cliente
        request_id: ID da requisição (correlation ID)
        status: Status da ação (success, failed, error)
        level: Nível de criticidade (info, warning, critical)
        details: Detalhes adicionais da ação
        **kwargs: Campos adicionais
    """
    # Prepare audit log entry
    log_entry = {
        "audit": True,
        "action": action,
        "status": status,
        "level": level,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    # Add user information
    if user_id:
        log_entry["user_id"] = str(user_id) if isinstance(user_id, UUID) else user_id
    if username:
        log_entry["username"] = username
    
    # Add resource information
    if resource_type:
        log_entry["resource_type"] = resource_type
    if resource_id:
        log_entry["resource_id"] = str(resource_id) if isinstance(resource_id, UUID) else resource_id
    
    # Add request context
    if ip_address:
        log_entry["ip_address"] = ip_address
    if user_agent:
        log_entry["user_agent"] = user_agent
    if request_id:
        log_entry["request_id"] = request_id
    
    # Add details (sanitize sensitive data)
    if details:
        # Remove sensitive fields
        sanitized_details = _sanitize_details(details)
        log_entry["details"] = sanitized_details
    
    # Add any additional fields
    for key, value in kwargs.items():
        if key not in log_entry:
            log_entry[key] = value
    
    # Log based on level
    if level == AuditLevel.CRITICAL:
        audit_logger.critical("audit_log", **log_entry)
    elif level == AuditLevel.WARNING:
        audit_logger.warning("audit_log", **log_entry)
    else:
        audit_logger.info("audit_log", **log_entry)


def _sanitize_details(details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove campos sensíveis dos detalhes do audit log.
    
    Args:
        details: Dicionário com detalhes da ação
        
    Returns:
        Dicionário sanitizado
    """
    # Campos que nunca devem aparecer em logs
    sensitive_fields = {
        "password", "hashed_password", "secret", "token", "api_key",
        "credit_card", "cvv", "ssn", "private_key", "access_token",
        "refresh_token", "reset_token"
    }
    
    sanitized = {}
    for key, value in details.items():
        # Skip sensitive fields
        if any(sensitive in key.lower() for sensitive in sensitive_fields):
            sanitized[key] = "[REDACTED]"
        elif isinstance(value, dict):
            # Recursively sanitize nested dicts
            sanitized[key] = _sanitize_details(value)
        else:
            sanitized[key] = value
    
    return sanitized


# Convenience functions for common audit events

def audit_login(
    user_id: str,
    username: str,
    ip_address: str,
    user_agent: str,
    success: bool,
    request_id: Optional[str] = None,
    reason: Optional[str] = None
):
    """Audit log para tentativas de login"""
    log_audit(
        action=AuditAction.LOGIN_SUCCESS if success else AuditAction.LOGIN_FAILED,
        resource_type="user",
        resource_id=user_id,
        user_id=user_id,
        username=username,
        ip_address=ip_address,
        user_agent=user_agent,
        request_id=request_id,
        status="success" if success else "failed",
        level=AuditLevel.INFO if success else AuditLevel.WARNING,
        details={"reason": reason} if reason else None
    )


def audit_logout(
    user_id: str,
    username: str,
    ip_address: str,
    request_id: Optional[str] = None
):
    """Audit log para logout"""
    log_audit(
        action=AuditAction.LOGOUT,
        resource_type="user",
        resource_id=user_id,
        user_id=user_id,
        username=username,
        ip_address=ip_address,
        request_id=request_id,
        status="success",
        level=AuditLevel.INFO
    )


def audit_resource_created(
    resource_type: str,
    resource_id: str,
    user_id: str,
    username: Optional[str] = None,
    ip_address: Optional[str] = None,
    request_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """Audit log para criação de recursos"""
    action_map = {
        "user": AuditAction.USER_CREATED,
        "project": AuditAction.PROJECT_CREATED,
        "model": AuditAction.MODEL_CREATED,
        "print_job": AuditAction.PRINT_JOB_CREATED,
        "render_job": AuditAction.RENDER_JOB_CREATED,
        "simulation": AuditAction.SIMULATION_CREATED,
    }
    
    action = action_map.get(resource_type, "resource_created")
    
    log_audit(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        username=username,
        ip_address=ip_address,
        request_id=request_id,
        status="success",
        level=AuditLevel.INFO,
        details=details
    )


def audit_resource_updated(
    resource_type: str,
    resource_id: str,
    user_id: str,
    username: Optional[str] = None,
    ip_address: Optional[str] = None,
    request_id: Optional[str] = None,
    changes: Optional[Dict[str, Any]] = None
):
    """Audit log para atualização de recursos"""
    action_map = {
        "user": AuditAction.USER_UPDATED,
        "project": AuditAction.PROJECT_UPDATED,
        "model": AuditAction.MODEL_UPDATED,
        "config": AuditAction.CONFIG_CHANGED,
    }
    
    action = action_map.get(resource_type, "resource_updated")
    
    log_audit(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        username=username,
        ip_address=ip_address,
        request_id=request_id,
        status="success",
        level=AuditLevel.INFO,
        details={"changes": changes} if changes else None
    )


def audit_resource_deleted(
    resource_type: str,
    resource_id: str,
    user_id: str,
    username: Optional[str] = None,
    ip_address: Optional[str] = None,
    request_id: Optional[str] = None
):
    """Audit log para exclusão de recursos"""
    action_map = {
        "user": AuditAction.USER_DELETED,
        "project": AuditAction.PROJECT_DELETED,
        "model": AuditAction.MODEL_DELETED,
    }
    
    action = action_map.get(resource_type, "resource_deleted")
    
    log_audit(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        username=username,
        ip_address=ip_address,
        request_id=request_id,
        status="success",
        level=AuditLevel.WARNING  # Deletion is higher severity
    )


def audit_security_event(
    event_type: str,
    user_id: Optional[str] = None,
    username: Optional[str] = None,
    ip_address: Optional[str] = None,
    request_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """Audit log para eventos de segurança"""
    log_audit(
        action=event_type,
        user_id=user_id,
        username=username,
        ip_address=ip_address,
        request_id=request_id,
        status="alert",
        level=AuditLevel.CRITICAL,
        details=details
    )


def audit_permission_denied(
    user_id: str,
    username: str,
    resource_type: str,
    resource_id: str,
    action_attempted: str,
    ip_address: Optional[str] = None,
    request_id: Optional[str] = None
):
    """Audit log para tentativas de acesso não autorizado"""
    log_audit(
        action=AuditAction.PERMISSION_DENIED,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        username=username,
        ip_address=ip_address,
        request_id=request_id,
        status="denied",
        level=AuditLevel.WARNING,
        details={"action_attempted": action_attempted}
    )
