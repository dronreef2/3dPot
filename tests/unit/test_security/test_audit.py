"""
Tests for Audit Logging - Sprint 7
"""

import pytest
from unittest.mock import Mock, patch, call
from datetime import datetime

from backend.observability.audit import (
    log_audit, audit_login, audit_logout, audit_resource_created,
    audit_resource_updated, audit_resource_deleted, audit_security_event,
    audit_permission_denied, AuditAction, AuditLevel, _sanitize_details
)


class TestSanitizeDetails:
    """Test sanitization of sensitive data"""
    
    def test_sanitize_password_fields(self):
        """Test that password fields are redacted"""
        details = {
            "username": "john",
            "password": "secret123",
            "email": "john@example.com"
        }
        
        sanitized = _sanitize_details(details)
        
        assert sanitized["username"] == "john"
        assert sanitized["email"] == "john@example.com"
        assert sanitized["password"] == "[REDACTED]"
    
    def test_sanitize_token_fields(self):
        """Test that token fields are redacted"""
        details = {
            "access_token": "jwt-token-here",
            "refresh_token": "refresh-token-here",
            "api_key": "api-key-here",
            "data": "public-data"
        }
        
        sanitized = _sanitize_details(details)
        
        assert sanitized["access_token"] == "[REDACTED]"
        assert sanitized["refresh_token"] == "[REDACTED]"
        assert sanitized["api_key"] == "[REDACTED]"
        assert sanitized["data"] == "public-data"
    
    def test_sanitize_nested_dict(self):
        """Test that nested dictionaries are sanitized"""
        details = {
            "user": {
                "username": "john",
                "hashed_password": "hash-here"
            },
            "public": "data"
        }
        
        sanitized = _sanitize_details(details)
        
        assert sanitized["user"]["username"] == "john"
        assert sanitized["user"]["hashed_password"] == "[REDACTED]"
        assert sanitized["public"] == "data"
    
    def test_sanitize_preserves_safe_fields(self):
        """Test that safe fields are preserved"""
        details = {
            "name": "John Doe",
            "email": "john@example.com",
            "role": "admin",
            "timestamp": "2024-01-01T00:00:00"
        }
        
        sanitized = _sanitize_details(details)
        
        # All fields should be preserved
        assert sanitized == details


class TestLogAudit:
    """Test main audit logging function"""
    
    @patch('backend.observability.audit.audit_logger')
    def test_log_audit_basic(self, mock_logger):
        """Test basic audit logging"""
        log_audit(
            action=AuditAction.LOGIN_SUCCESS,
            user_id="user-123",
            username="john",
            status="success",
            level=AuditLevel.INFO
        )
        
        # Verify logger was called
        mock_logger.info.assert_called_once()
        
        # Check the logged data
        call_args = mock_logger.info.call_args
        assert call_args[0][0] == "audit_log"
        
        kwargs = call_args[1]
        assert kwargs["audit"] is True
        assert kwargs["action"] == AuditAction.LOGIN_SUCCESS
        assert kwargs["user_id"] == "user-123"
        assert kwargs["username"] == "john"
        assert kwargs["status"] == "success"
        assert kwargs["level"] == AuditLevel.INFO
    
    @patch('backend.observability.audit.audit_logger')
    def test_log_audit_with_resource(self, mock_logger):
        """Test audit log with resource information"""
        log_audit(
            action=AuditAction.PROJECT_CREATED,
            resource_type="project",
            resource_id="project-456",
            user_id="user-123",
            status="success"
        )
        
        call_args = mock_logger.info.call_args[1]
        assert call_args["resource_type"] == "project"
        assert call_args["resource_id"] == "project-456"
    
    @patch('backend.observability.audit.audit_logger')
    def test_log_audit_with_request_context(self, mock_logger):
        """Test audit log with request context"""
        log_audit(
            action=AuditAction.LOGIN_SUCCESS,
            user_id="user-123",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            request_id="req-789"
        )
        
        call_args = mock_logger.info.call_args[1]
        assert call_args["ip_address"] == "192.168.1.1"
        assert call_args["user_agent"] == "Mozilla/5.0"
        assert call_args["request_id"] == "req-789"
    
    @patch('backend.observability.audit.audit_logger')
    def test_log_audit_with_details(self, mock_logger):
        """Test audit log with details"""
        details = {
            "old_role": "user",
            "new_role": "admin",
            "password": "should-be-redacted"
        }
        
        log_audit(
            action=AuditAction.ROLE_CHANGED,
            user_id="user-123",
            details=details
        )
        
        call_args = mock_logger.info.call_args[1]
        assert call_args["details"]["old_role"] == "user"
        assert call_args["details"]["new_role"] == "admin"
        assert call_args["details"]["password"] == "[REDACTED]"
    
    @patch('backend.observability.audit.audit_logger')
    def test_log_audit_critical_level(self, mock_logger):
        """Test audit log with critical level"""
        log_audit(
            action=AuditAction.SUSPICIOUS_ACTIVITY,
            level=AuditLevel.CRITICAL,
            user_id="user-123"
        )
        
        # Should use critical logger
        mock_logger.critical.assert_called_once()
        mock_logger.info.assert_not_called()
    
    @patch('backend.observability.audit.audit_logger')
    def test_log_audit_warning_level(self, mock_logger):
        """Test audit log with warning level"""
        log_audit(
            action=AuditAction.LOGIN_FAILED,
            level=AuditLevel.WARNING,
            user_id="user-123"
        )
        
        # Should use warning logger
        mock_logger.warning.assert_called_once()
        mock_logger.info.assert_not_called()


class TestAuditConvenienceFunctions:
    """Test convenience functions for common audit events"""
    
    @patch('backend.observability.audit.log_audit')
    def test_audit_login_success(self, mock_log_audit):
        """Test audit_login for successful login"""
        audit_login(
            user_id="user-123",
            username="john",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            success=True,
            request_id="req-789"
        )
        
        mock_log_audit.assert_called_once()
        call_kwargs = mock_log_audit.call_args[1]
        
        assert call_kwargs["action"] == AuditAction.LOGIN_SUCCESS
        assert call_kwargs["user_id"] == "user-123"
        assert call_kwargs["username"] == "john"
        assert call_kwargs["status"] == "success"
        assert call_kwargs["level"] == AuditLevel.INFO
    
    @patch('backend.observability.audit.log_audit')
    def test_audit_login_failed(self, mock_log_audit):
        """Test audit_login for failed login"""
        audit_login(
            user_id="user-123",
            username="john",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            success=False,
            reason="invalid_password"
        )
        
        call_kwargs = mock_log_audit.call_args[1]
        
        assert call_kwargs["action"] == AuditAction.LOGIN_FAILED
        assert call_kwargs["status"] == "failed"
        assert call_kwargs["level"] == AuditLevel.WARNING
        assert call_kwargs["details"]["reason"] == "invalid_password"
    
    @patch('backend.observability.audit.log_audit')
    def test_audit_logout(self, mock_log_audit):
        """Test audit_logout"""
        audit_logout(
            user_id="user-123",
            username="john",
            ip_address="192.168.1.1",
            request_id="req-789"
        )
        
        call_kwargs = mock_log_audit.call_args[1]
        assert call_kwargs["action"] == AuditAction.LOGOUT
        assert call_kwargs["status"] == "success"
    
    @patch('backend.observability.audit.log_audit')
    def test_audit_resource_created_project(self, mock_log_audit):
        """Test audit_resource_created for project"""
        audit_resource_created(
            resource_type="project",
            resource_id="project-456",
            user_id="user-123",
            username="john",
            details={"name": "My Project"}
        )
        
        call_kwargs = mock_log_audit.call_args[1]
        assert call_kwargs["action"] == AuditAction.PROJECT_CREATED
        assert call_kwargs["resource_type"] == "project"
        assert call_kwargs["resource_id"] == "project-456"
    
    @patch('backend.observability.audit.log_audit')
    def test_audit_resource_updated(self, mock_log_audit):
        """Test audit_resource_updated"""
        changes = {"name": "New Name"}
        
        audit_resource_updated(
            resource_type="user",
            resource_id="user-123",
            user_id="admin-456",
            changes=changes
        )
        
        call_kwargs = mock_log_audit.call_args[1]
        assert call_kwargs["action"] == AuditAction.USER_UPDATED
        assert call_kwargs["details"]["changes"] == changes
    
    @patch('backend.observability.audit.log_audit')
    def test_audit_resource_deleted(self, mock_log_audit):
        """Test audit_resource_deleted"""
        audit_resource_deleted(
            resource_type="model",
            resource_id="model-789",
            user_id="user-123"
        )
        
        call_kwargs = mock_log_audit.call_args[1]
        assert call_kwargs["action"] == AuditAction.MODEL_DELETED
        assert call_kwargs["level"] == AuditLevel.WARNING  # Deletion is higher severity
    
    @patch('backend.observability.audit.log_audit')
    def test_audit_security_event(self, mock_log_audit):
        """Test audit_security_event"""
        audit_security_event(
            event_type=AuditAction.RATE_LIMIT_EXCEEDED,
            user_id="user-123",
            ip_address="192.168.1.1",
            details={"endpoint": "/api/auth/login"}
        )
        
        call_kwargs = mock_log_audit.call_args[1]
        assert call_kwargs["action"] == AuditAction.RATE_LIMIT_EXCEEDED
        assert call_kwargs["level"] == AuditLevel.CRITICAL
        assert call_kwargs["status"] == "alert"
    
    @patch('backend.observability.audit.log_audit')
    def test_audit_permission_denied(self, mock_log_audit):
        """Test audit_permission_denied"""
        audit_permission_denied(
            user_id="user-123",
            username="john",
            resource_type="project",
            resource_id="project-456",
            action_attempted="delete",
            ip_address="192.168.1.1"
        )
        
        call_kwargs = mock_log_audit.call_args[1]
        assert call_kwargs["action"] == AuditAction.PERMISSION_DENIED
        assert call_kwargs["status"] == "denied"
        assert call_kwargs["level"] == AuditLevel.WARNING
        assert call_kwargs["details"]["action_attempted"] == "delete"


class TestAuditActions:
    """Test audit action constants"""
    
    def test_audit_action_constants_exist(self):
        """Test that key audit action constants are defined"""
        # Authentication
        assert hasattr(AuditAction, 'LOGIN_SUCCESS')
        assert hasattr(AuditAction, 'LOGIN_FAILED')
        assert hasattr(AuditAction, 'LOGOUT')
        
        # Resource management
        assert hasattr(AuditAction, 'PROJECT_CREATED')
        assert hasattr(AuditAction, 'MODEL_CREATED')
        
        # Security events
        assert hasattr(AuditAction, 'RATE_LIMIT_EXCEEDED')
        assert hasattr(AuditAction, 'UNAUTHORIZED_ACCESS')
        assert hasattr(AuditAction, 'PERMISSION_DENIED')


class TestAuditLevels:
    """Test audit level constants"""
    
    def test_audit_level_constants(self):
        """Test that audit level constants are defined"""
        assert AuditLevel.INFO == "info"
        assert AuditLevel.WARNING == "warning"
        assert AuditLevel.CRITICAL == "critical"
