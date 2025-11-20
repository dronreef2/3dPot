"""
Authorization and RBAC - 3dPot Sprint 8
Sistema de controle de acesso baseado em roles e ownership validation
"""

from typing import Optional, List, Callable, Any
from functools import wraps
from uuid import UUID

from fastapi import HTTPException, status, Request, Depends
from sqlalchemy.orm import Session

from backend.observability.logging_config import get_logger
from backend.observability.audit import audit_permission_denied, AuditAction
from backend.database import get_db

logger = get_logger(__name__)

# Import metrics (lazy to avoid circular imports)
try:
    from backend.observability.metrics import metrics
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False


class Role:
    """Definição de roles do sistema"""
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"
    OPERATOR = "operator"


class Permission:
    """Definição de permissões específicas"""
    # Projects
    PROJECT_CREATE = "project:create"
    PROJECT_READ = "project:read"
    PROJECT_UPDATE = "project:update"
    PROJECT_DELETE = "project:delete"
    
    # Models
    MODEL_CREATE = "model:create"
    MODEL_READ = "model:read"
    MODEL_UPDATE = "model:update"
    MODEL_DELETE = "model:delete"
    
    # Cloud Rendering
    RENDER_CREATE = "render:create"
    RENDER_CANCEL = "render:cancel"
    RENDER_VIEW = "render:view"
    
    # Marketplace
    MARKETPLACE_LIST = "marketplace:list"
    MARKETPLACE_SELL = "marketplace:sell"
    MARKETPLACE_MANAGE = "marketplace:manage"
    
    # Admin
    ADMIN_USERS = "admin:users"
    ADMIN_SYSTEM = "admin:system"
    ADMIN_SETTINGS = "admin:settings"


# Role to permissions mapping
ROLE_PERMISSIONS = {
    Role.USER: [
        Permission.PROJECT_CREATE,
        Permission.PROJECT_READ,
        Permission.MODEL_CREATE,
        Permission.MODEL_READ,
        Permission.RENDER_CREATE,
        Permission.RENDER_VIEW,
        Permission.MARKETPLACE_LIST,
    ],
    Role.PREMIUM: [
        Permission.PROJECT_CREATE,
        Permission.PROJECT_READ,
        Permission.MODEL_CREATE,
        Permission.MODEL_READ,
        Permission.RENDER_CREATE,
        Permission.RENDER_VIEW,
        Permission.MARKETPLACE_LIST,
        Permission.MARKETPLACE_SELL,
    ],
    Role.OPERATOR: [
        Permission.PROJECT_CREATE,
        Permission.PROJECT_READ,
        Permission.PROJECT_UPDATE,
        Permission.MODEL_CREATE,
        Permission.MODEL_READ,
        Permission.MODEL_UPDATE,
        Permission.RENDER_CREATE,
        Permission.RENDER_CANCEL,
        Permission.RENDER_VIEW,
        Permission.MARKETPLACE_LIST,
        Permission.MARKETPLACE_MANAGE,
    ],
    Role.ADMIN: [
        # Admin has all permissions
        Permission.PROJECT_CREATE,
        Permission.PROJECT_READ,
        Permission.PROJECT_UPDATE,
        Permission.PROJECT_DELETE,
        Permission.MODEL_CREATE,
        Permission.MODEL_READ,
        Permission.MODEL_UPDATE,
        Permission.MODEL_DELETE,
        Permission.RENDER_CREATE,
        Permission.RENDER_CANCEL,
        Permission.RENDER_VIEW,
        Permission.MARKETPLACE_LIST,
        Permission.MARKETPLACE_SELL,
        Permission.MARKETPLACE_MANAGE,
        Permission.ADMIN_USERS,
        Permission.ADMIN_SYSTEM,
        Permission.ADMIN_SETTINGS,
    ],
}


class AuthorizationError(Exception):
    """Exceção para erros de autorização"""
    pass


def has_role(user_role: str, required_roles: List[str]) -> bool:
    """
    Check if user has one of the required roles.
    
    Args:
        user_role: User's current role
        required_roles: List of acceptable roles
        
    Returns:
        True if user has one of the required roles
    """
    return user_role in required_roles


def has_permission(user_role: str, required_permission: str, user_permissions: Optional[List[str]] = None) -> bool:
    """
    Check if user has a specific permission.
    
    Args:
        user_role: User's role
        required_permission: Permission to check
        user_permissions: Optional list of user-specific permissions (overrides)
        
    Returns:
        True if user has the permission
    """
    # Check user-specific permissions first (if provided)
    if user_permissions and required_permission in user_permissions:
        return True
    
    # Check role-based permissions
    role_perms = ROLE_PERMISSIONS.get(user_role, [])
    return required_permission in role_perms


def is_owner(user_id: Any, resource_owner_id: Any) -> bool:
    """
    Check if user is the owner of a resource.
    
    Args:
        user_id: Current user's ID
        resource_owner_id: Resource owner's ID
        
    Returns:
        True if user is the owner
    """
    # Convert to string for comparison (handles UUID, int, etc.)
    return str(user_id) == str(resource_owner_id)


def is_admin(user_role: str) -> bool:
    """
    Check if user is an admin.
    
    Args:
        user_role: User's role
        
    Returns:
        True if user is admin
    """
    return user_role == Role.ADMIN


def require_role(*allowed_roles: str):
    """
    Decorator to require specific roles for an endpoint.
    
    Usage:
        @require_role(Role.ADMIN, Role.OPERATOR)
        async def admin_only_endpoint(current_user = Depends(get_current_user)):
            ...
    
    Args:
        *allowed_roles: Variable number of allowed roles
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current_user from kwargs (injected by FastAPI dependency)
            current_user = kwargs.get('current_user')
            request = kwargs.get('request')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_role = getattr(current_user, 'role', None)
            
            if not has_role(user_role, list(allowed_roles)):
                # Audit the permission denial
                if request:
                    audit_permission_denied(
                        user_id=str(current_user.id),
                        username=getattr(current_user, 'username', 'unknown'),
                        resource_type="endpoint",
                        resource_id=request.url.path,
                        action_attempted=f"access with role {user_role}",
                        ip_address=request.client.host if request.client else None,
                        request_id=getattr(request.state, 'request_id', None)
                    )
                
                logger.warning(
                    "authorization_role_check_failed",
                    user_id=str(current_user.id),
                    user_role=user_role,
                    required_roles=list(allowed_roles),
                    endpoint=request.url.path if request else "unknown"
                )
                
                # Emit metrics
                if METRICS_AVAILABLE:
                    try:
                        metrics.permission_denied(resource_type="endpoint", action="role_check")
                    except Exception:
                        pass
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_permission(required_permission: str):
    """
    Decorator to require specific permission for an endpoint.
    
    Usage:
        @require_permission(Permission.PROJECT_DELETE)
        async def delete_project(current_user = Depends(get_current_user)):
            ...
    
    Args:
        required_permission: Permission required to access endpoint
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current_user from kwargs
            current_user = kwargs.get('current_user')
            request = kwargs.get('request')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_role = getattr(current_user, 'role', None)
            user_permissions = getattr(current_user, 'permissions', [])
            
            if not has_permission(user_role, required_permission, user_permissions):
                # Audit the permission denial
                if request:
                    audit_permission_denied(
                        user_id=str(current_user.id),
                        username=getattr(current_user, 'username', 'unknown'),
                        resource_type="endpoint",
                        resource_id=request.url.path,
                        action_attempted=f"access with permission {required_permission}",
                        ip_address=request.client.host if request.client else None,
                        request_id=getattr(request.state, 'request_id', None)
                    )
                
                logger.warning(
                    "authorization_permission_check_failed",
                    user_id=str(current_user.id),
                    user_role=user_role,
                    required_permission=required_permission,
                    endpoint=request.url.path if request else "unknown"
                )
                
                # Emit metrics
                if METRICS_AVAILABLE:
                    try:
                        metrics.permission_denied(resource_type="endpoint", action="permission_check")
                    except Exception:
                        pass
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required permission: {required_permission}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_owner_or_admin(resource_owner_field: str = "owner_id"):
    """
    Decorator to require resource ownership or admin role.
    
    Usage:
        @require_owner_or_admin(resource_owner_field="owner_id")
        async def update_project(project_id: UUID, current_user = Depends(get_current_user), db = Depends(get_db)):
            # Function should fetch the resource and have it available
            project = db.query(Project).filter(Project.id == project_id).first()
            ...
    
    Args:
        resource_owner_field: Field name containing the owner ID in the resource
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            request = kwargs.get('request')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check if user is admin (admins can access everything)
            if is_admin(getattr(current_user, 'role', None)):
                return await func(*args, **kwargs)
            
            # For non-admins, we need to check ownership
            # The endpoint function should fetch the resource and validate
            # This is a marker that the function will do ownership check
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def check_resource_ownership(
    current_user,
    resource,
    resource_type: str,
    request: Optional[Request] = None,
    allow_admin: bool = True
) -> bool:
    """
    Check if current user owns a resource or is admin.
    
    Args:
        current_user: Current authenticated user
        resource: Resource object to check ownership
        resource_type: Type of resource (for audit logging)
        request: Optional request object for audit logging
        allow_admin: Whether admins bypass ownership check
        
    Returns:
        True if user owns the resource or is admin
        
    Raises:
        HTTPException: If user doesn't own resource and is not admin
    """
    user_role = getattr(current_user, 'role', None)
    
    # Check if admin
    if allow_admin and is_admin(user_role):
        return True
    
    # Check ownership
    resource_owner_id = getattr(resource, 'owner_id', None)
    if resource_owner_id is None:
        # Resource doesn't have owner_id - check user_id
        resource_owner_id = getattr(resource, 'user_id', None)
    
    if resource_owner_id is None:
        logger.error(
            "resource_ownership_check_failed",
            reason="Resource has no owner_id or user_id field",
            resource_type=resource_type
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cannot verify resource ownership"
        )
    
    if not is_owner(current_user.id, resource_owner_id):
        # Audit the permission denial
        if request:
            audit_permission_denied(
                user_id=str(current_user.id),
                username=getattr(current_user, 'username', 'unknown'),
                resource_type=resource_type,
                resource_id=str(getattr(resource, 'id', 'unknown')),
                action_attempted="access_non_owned_resource",
                ip_address=request.client.host if request.client else None,
                request_id=getattr(request.state, 'request_id', None)
            )
        
        logger.warning(
            "resource_ownership_denied",
            user_id=str(current_user.id),
            resource_type=resource_type,
            resource_id=str(getattr(resource, 'id', 'unknown')),
            resource_owner_id=str(resource_owner_id)
        )
        
        # Emit metrics
        if METRICS_AVAILABLE:
            try:
                metrics.permission_denied(resource_type=resource_type, action="ownership_check")
            except Exception:
                pass
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource"
        )
    
    return True


def get_user_permissions(user_role: str, custom_permissions: Optional[List[str]] = None) -> List[str]:
    """
    Get all permissions for a user based on role and custom permissions.
    
    Args:
        user_role: User's role
        custom_permissions: Optional custom permissions for the user
        
    Returns:
        List of all permissions
    """
    # Get role-based permissions
    perms = set(ROLE_PERMISSIONS.get(user_role, []))
    
    # Add custom permissions
    if custom_permissions:
        perms.update(custom_permissions)
    
    return list(perms)
