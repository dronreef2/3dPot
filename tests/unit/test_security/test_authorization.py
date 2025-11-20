"""
Tests for Authorization and RBAC - 3dPot Sprint 8
Unit tests for role-based access control and ownership validation
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from fastapi import HTTPException, Request

from backend.core.authorization import (
    Role,
    Permission,
    ROLE_PERMISSIONS,
    has_role,
    has_permission,
    is_owner,
    is_admin,
    require_role,
    require_permission,
    check_resource_ownership,
    get_user_permissions,
)


@pytest.fixture
def mock_user():
    """Create a mock user"""
    user = Mock()
    user.id = "user123"
    user.username = "testuser"
    user.role = Role.USER
    user.permissions = []
    return user


@pytest.fixture
def mock_admin():
    """Create a mock admin user"""
    user = Mock()
    user.id = "admin123"
    user.username = "admin"
    user.role = Role.ADMIN
    user.permissions = []
    return user


@pytest.fixture
def mock_request():
    """Create a mock FastAPI request"""
    request = Mock(spec=Request)
    request.url.path = "/api/test"
    request.method = "GET"
    request.client.host = "192.168.1.1"
    request.state = Mock()
    request.state.request_id = "req123"
    return request


@pytest.fixture
def mock_resource():
    """Create a mock resource with ownership"""
    resource = Mock()
    resource.id = "resource123"
    resource.owner_id = "user123"
    return resource


class TestRolePermissions:
    """Tests for role and permission constants"""
    
    def test_role_constants(self):
        """Test that role constants are defined"""
        assert Role.USER == "user"
        assert Role.PREMIUM == "premium"
        assert Role.ADMIN == "admin"
        assert Role.OPERATOR == "operator"
    
    def test_permission_constants(self):
        """Test that permission constants are defined"""
        assert Permission.PROJECT_CREATE == "project:create"
        assert Permission.PROJECT_DELETE == "project:delete"
        assert Permission.ADMIN_USERS == "admin:users"
    
    def test_role_permissions_mapping(self):
        """Test that all roles have permission mappings"""
        assert Role.USER in ROLE_PERMISSIONS
        assert Role.PREMIUM in ROLE_PERMISSIONS
        assert Role.ADMIN in ROLE_PERMISSIONS
        assert Role.OPERATOR in ROLE_PERMISSIONS
    
    def test_user_role_permissions(self):
        """Test basic user role permissions"""
        user_perms = ROLE_PERMISSIONS[Role.USER]
        assert Permission.PROJECT_CREATE in user_perms
        assert Permission.PROJECT_READ in user_perms
        assert Permission.PROJECT_DELETE not in user_perms
        assert Permission.ADMIN_USERS not in user_perms
    
    def test_admin_role_permissions(self):
        """Test admin role has all permissions"""
        admin_perms = ROLE_PERMISSIONS[Role.ADMIN]
        assert Permission.PROJECT_DELETE in admin_perms
        assert Permission.ADMIN_USERS in admin_perms
        assert Permission.ADMIN_SYSTEM in admin_perms


class TestHelperFunctions:
    """Tests for helper functions"""
    
    def test_has_role_single_role(self):
        """Test has_role with single role"""
        assert has_role(Role.USER, [Role.USER]) is True
        assert has_role(Role.USER, [Role.ADMIN]) is False
    
    def test_has_role_multiple_roles(self):
        """Test has_role with multiple acceptable roles"""
        assert has_role(Role.USER, [Role.USER, Role.PREMIUM]) is True
        assert has_role(Role.ADMIN, [Role.USER, Role.PREMIUM]) is False
        assert has_role(Role.ADMIN, [Role.ADMIN, Role.OPERATOR]) is True
    
    def test_has_permission_role_based(self):
        """Test has_permission with role-based permissions"""
        # User can create projects
        assert has_permission(Role.USER, Permission.PROJECT_CREATE) is True
        # User cannot delete projects
        assert has_permission(Role.USER, Permission.PROJECT_DELETE) is False
        # Admin can delete projects
        assert has_permission(Role.ADMIN, Permission.PROJECT_DELETE) is True
    
    def test_has_permission_custom_permissions(self):
        """Test has_permission with custom user permissions"""
        # User normally can't delete, but has custom permission
        custom_perms = [Permission.PROJECT_DELETE]
        assert has_permission(Role.USER, Permission.PROJECT_DELETE, custom_perms) is True
    
    def test_is_owner_same_user(self):
        """Test is_owner when IDs match"""
        assert is_owner("user123", "user123") is True
    
    def test_is_owner_different_user(self):
        """Test is_owner when IDs don't match"""
        assert is_owner("user123", "user456") is False
    
    def test_is_owner_uuid_conversion(self):
        """Test is_owner with UUID conversion"""
        from uuid import UUID
        user_id = UUID("12345678-1234-5678-1234-567812345678")
        owner_id = "12345678-1234-5678-1234-567812345678"
        assert is_owner(user_id, owner_id) is True
    
    def test_is_admin_true(self):
        """Test is_admin returns True for admin role"""
        assert is_admin(Role.ADMIN) is True
    
    def test_is_admin_false(self):
        """Test is_admin returns False for non-admin roles"""
        assert is_admin(Role.USER) is False
        assert is_admin(Role.PREMIUM) is False
        assert is_admin(Role.OPERATOR) is False


class TestRequireRoleDecorator:
    """Tests for require_role decorator"""
    
    @pytest.mark.asyncio
    async def test_require_role_success(self, mock_user, mock_request):
        """Test require_role allows access with correct role"""
        @require_role(Role.USER, Role.PREMIUM)
        async def test_endpoint(current_user=None, request=None):
            return {"status": "success"}
        
        result = await test_endpoint(current_user=mock_user, request=mock_request)
        assert result == {"status": "success"}
    
    @pytest.mark.asyncio
    async def test_require_role_forbidden(self, mock_user, mock_request):
        """Test require_role denies access with incorrect role"""
        @require_role(Role.ADMIN)
        async def test_endpoint(current_user=None, request=None):
            return {"status": "success"}
        
        with pytest.raises(HTTPException) as exc_info:
            await test_endpoint(current_user=mock_user, request=mock_request)
        
        assert exc_info.value.status_code == 403
        assert "Access denied" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_require_role_unauthenticated(self, mock_request):
        """Test require_role denies access without authentication"""
        @require_role(Role.USER)
        async def test_endpoint(current_user=None, request=None):
            return {"status": "success"}
        
        with pytest.raises(HTTPException) as exc_info:
            await test_endpoint(current_user=None, request=mock_request)
        
        assert exc_info.value.status_code == 401
        assert "Authentication required" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_require_role_admin_access(self, mock_admin, mock_request):
        """Test admin can access admin-only endpoint"""
        @require_role(Role.ADMIN)
        async def test_endpoint(current_user=None, request=None):
            return {"status": "admin_access"}
        
        result = await test_endpoint(current_user=mock_admin, request=mock_request)
        assert result == {"status": "admin_access"}


class TestRequirePermissionDecorator:
    """Tests for require_permission decorator"""
    
    @pytest.mark.asyncio
    async def test_require_permission_success(self, mock_user, mock_request):
        """Test require_permission allows access with correct permission"""
        @require_permission(Permission.PROJECT_CREATE)
        async def test_endpoint(current_user=None, request=None):
            return {"status": "success"}
        
        result = await test_endpoint(current_user=mock_user, request=mock_request)
        assert result == {"status": "success"}
    
    @pytest.mark.asyncio
    async def test_require_permission_forbidden(self, mock_user, mock_request):
        """Test require_permission denies access without permission"""
        @require_permission(Permission.PROJECT_DELETE)
        async def test_endpoint(current_user=None, request=None):
            return {"status": "success"}
        
        with pytest.raises(HTTPException) as exc_info:
            await test_endpoint(current_user=mock_user, request=mock_request)
        
        assert exc_info.value.status_code == 403
        assert "Access denied" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_require_permission_custom_permission(self, mock_user, mock_request):
        """Test require_permission with custom user permission"""
        # Add custom permission to user
        mock_user.permissions = [Permission.PROJECT_DELETE]
        
        @require_permission(Permission.PROJECT_DELETE)
        async def test_endpoint(current_user=None, request=None):
            return {"status": "success"}
        
        result = await test_endpoint(current_user=mock_user, request=mock_request)
        assert result == {"status": "success"}
    
    @pytest.mark.asyncio
    async def test_require_permission_admin_bypass(self, mock_admin, mock_request):
        """Test admin has all permissions"""
        @require_permission(Permission.PROJECT_DELETE)
        async def test_endpoint(current_user=None, request=None):
            return {"status": "admin_success"}
        
        result = await test_endpoint(current_user=mock_admin, request=mock_request)
        assert result == {"status": "admin_success"}


class TestCheckResourceOwnership:
    """Tests for check_resource_ownership function"""
    
    def test_check_ownership_owner(self, mock_user, mock_resource, mock_request):
        """Test ownership check succeeds for owner"""
        result = check_resource_ownership(
            current_user=mock_user,
            resource=mock_resource,
            resource_type="project",
            request=mock_request
        )
        assert result is True
    
    def test_check_ownership_admin(self, mock_admin, mock_resource, mock_request):
        """Test admin bypasses ownership check"""
        # Resource owned by different user
        mock_resource.owner_id = "different_user"
        
        result = check_resource_ownership(
            current_user=mock_admin,
            resource=mock_resource,
            resource_type="project",
            request=mock_request
        )
        assert result is True
    
    def test_check_ownership_non_owner(self, mock_user, mock_resource, mock_request):
        """Test ownership check fails for non-owner"""
        # Resource owned by different user
        mock_resource.owner_id = "different_user"
        
        with pytest.raises(HTTPException) as exc_info:
            check_resource_ownership(
                current_user=mock_user,
                resource=mock_resource,
                resource_type="project",
                request=mock_request
            )
        
        assert exc_info.value.status_code == 403
        assert "don't have permission" in exc_info.value.detail
    
    def test_check_ownership_user_id_fallback(self, mock_user, mock_request):
        """Test ownership check with user_id field instead of owner_id"""
        resource = Mock()
        resource.id = "resource123"
        resource.user_id = "user123"  # user_id instead of owner_id
        delattr(resource, 'owner_id')  # Simulate no owner_id
        resource.owner_id = None
        
        result = check_resource_ownership(
            current_user=mock_user,
            resource=resource,
            resource_type="project",
            request=mock_request
        )
        assert result is True
    
    def test_check_ownership_no_owner_field(self, mock_user, mock_request):
        """Test ownership check fails when resource has no owner field"""
        resource = Mock()
        resource.id = "resource123"
        resource.owner_id = None
        resource.user_id = None
        
        with pytest.raises(HTTPException) as exc_info:
            check_resource_ownership(
                current_user=mock_user,
                resource=resource,
                resource_type="project",
                request=mock_request
            )
        
        assert exc_info.value.status_code == 500


class TestGetUserPermissions:
    """Tests for get_user_permissions function"""
    
    def test_get_permissions_user_role(self):
        """Test getting permissions for user role"""
        perms = get_user_permissions(Role.USER)
        assert Permission.PROJECT_CREATE in perms
        assert Permission.PROJECT_DELETE not in perms
    
    def test_get_permissions_admin_role(self):
        """Test getting permissions for admin role"""
        perms = get_user_permissions(Role.ADMIN)
        assert Permission.PROJECT_DELETE in perms
        assert Permission.ADMIN_USERS in perms
    
    def test_get_permissions_with_custom(self):
        """Test getting permissions with custom permissions"""
        custom = [Permission.ADMIN_USERS]
        perms = get_user_permissions(Role.USER, custom_permissions=custom)
        
        # Should have user permissions + custom
        assert Permission.PROJECT_CREATE in perms
        assert Permission.ADMIN_USERS in perms
    
    def test_get_permissions_deduplication(self):
        """Test that duplicate permissions are handled correctly"""
        # Add a permission that user already has
        custom = [Permission.PROJECT_CREATE]
        perms = get_user_permissions(Role.USER, custom_permissions=custom)
        
        # Should only appear once (using set internally)
        assert isinstance(perms, list)
        assert Permission.PROJECT_CREATE in perms
