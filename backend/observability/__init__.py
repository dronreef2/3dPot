"""
3dPot Backend - Observability Module
Sprint 6: Logging, Metrics, and Tracing for Production Readiness
Sprint 7: Security - Rate Limiting and Audit Logging
Sprint 9: Extended with Trace ID support for distributed tracing
"""

from .logging_config import configure_logging, get_logger
from .logging_middleware import LoggingMiddleware
from .metrics import metrics, setup_metrics, MetricsMiddleware, get_metrics_content_type
from .request_id import RequestIDMiddleware, get_request_id, get_trace_id
from .rate_limiting import RateLimiter, RateLimitMiddleware, create_rate_limit_middleware
from .audit import (
    log_audit, audit_login, audit_logout, audit_resource_created,
    audit_resource_updated, audit_resource_deleted, audit_security_event,
    audit_permission_denied, AuditAction, AuditLevel
)

__all__ = [
    # Sprint 6 - Observability
    "configure_logging",
    "get_logger",
    "LoggingMiddleware",
    "metrics",
    "setup_metrics",
    "MetricsMiddleware",
    "get_metrics_content_type",
    "RequestIDMiddleware",
    "get_request_id",
    "get_trace_id",  # Sprint 9
    # Sprint 7 - Security
    "RateLimiter",
    "RateLimitMiddleware",
    "create_rate_limit_middleware",
    "log_audit",
    "audit_login",
    "audit_logout",
    "audit_resource_created",
    "audit_resource_updated",
    "audit_resource_deleted",
    "audit_security_event",
    "audit_permission_denied",
    "AuditAction",
    "AuditLevel",
]
