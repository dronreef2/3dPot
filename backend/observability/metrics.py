"""
3dPot Backend - Metrics Collection with Prometheus
Sprint 6: Production metrics for monitoring and alerting

This module provides:
- HTTP request/response metrics (counter, histogram)
- Error counters by type
- Service-level metrics
- /metrics endpoint for Prometheus scraping
"""

import time
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
)
from prometheus_client.multiprocess import MultiProcessCollector
import os


# Create registry
if "PROMETHEUS_MULTIPROC_DIR" in os.environ:
    # Multi-process mode (for production with Gunicorn)
    registry = CollectorRegistry()
    MultiProcessCollector(registry)
else:
    # Single-process mode (for development)
    from prometheus_client import REGISTRY
    registry = REGISTRY


# === HTTP Metrics ===

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
    registry=registry,
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    registry=registry,
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests currently being processed",
    ["method", "endpoint"],
    registry=registry,
)


# === Error Metrics ===

errors_total = Counter(
    "errors_total",
    "Total errors by type",
    ["error_type", "endpoint"],
    registry=registry,
)

exceptions_total = Counter(
    "exceptions_total",
    "Total unhandled exceptions",
    ["exception_type"],
    registry=registry,
)


# === Business Metrics (examples) ===

models_created_total = Counter(
    "models_created_total",
    "Total 3D models created",
    ["model_type"],
    registry=registry,
)

simulations_run_total = Counter(
    "simulations_run_total",
    "Total simulations executed",
    ["simulation_type"],
    registry=registry,
)

budget_calculations_total = Counter(
    "budget_calculations_total",
    "Total budget calculations performed",
    registry=registry,
)


# === Security Metrics (Sprint 8) ===

rate_limit_hits_total = Counter(
    "rate_limit_hits_total",
    "Total rate limit violations",
    ["endpoint", "client_type"],
    registry=registry,
)

auth_failures_total = Counter(
    "auth_failures_total",
    "Total authentication failures",
    ["failure_type", "endpoint"],
    registry=registry,
)

audit_events_total = Counter(
    "audit_events_total",
    "Total audit events logged",
    ["action", "level"],
    registry=registry,
)

permission_denied_total = Counter(
    "permission_denied_total",
    "Total permission denied events",
    ["resource_type", "action"],
    registry=registry,
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to collect HTTP metrics automatically.
    
    Tracks:
    - Request count by method, endpoint, and status
    - Request duration (latency)
    - Requests in progress
    
    Usage:
        from backend.observability import MetricsMiddleware
        app.add_middleware(MetricsMiddleware)
    """
    
    def __init__(
        self,
        app: ASGIApp,
        skip_paths: Optional[list[str]] = None,
    ):
        super().__init__(app)
        # Don't track metrics for these paths to avoid noise
        self.skip_paths = skip_paths or ["/metrics", "/health", "/healthz", "/ping"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip metrics collection for certain paths
        if request.url.path in self.skip_paths:
            return await call_next(request)
        
        method = request.method
        endpoint = request.url.path
        
        # Track in-progress requests
        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()
        
        # Track request duration
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            status = response.status_code
            
            # Record metrics
            duration = time.time() - start_time
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=status
            ).inc()
            
            # Track errors (4xx, 5xx)
            if status >= 400:
                error_type = "client_error" if status < 500 else "server_error"
                errors_total.labels(
                    error_type=error_type,
                    endpoint=endpoint
                ).inc()
            
            return response
            
        except Exception as exc:
            # Track exceptions
            exception_type = type(exc).__name__
            exceptions_total.labels(exception_type=exception_type).inc()
            errors_total.labels(
                error_type="exception",
                endpoint=endpoint
            ).inc()
            raise
            
        finally:
            # Decrement in-progress counter
            http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()


class Metrics:
    """
    Wrapper class for easy access to metrics.
    
    Usage:
        from backend.observability import metrics
        
        # Increment business metrics
        metrics.model_created("cadquery")
        metrics.simulation_run("structural")
        metrics.budget_calculated()
    """
    
    @staticmethod
    def model_created(model_type: str) -> None:
        """Record a 3D model creation"""
        models_created_total.labels(model_type=model_type).inc()
    
    @staticmethod
    def simulation_run(simulation_type: str) -> None:
        """Record a simulation execution"""
        simulations_run_total.labels(simulation_type=simulation_type).inc()
    
    @staticmethod
    def budget_calculated() -> None:
        """Record a budget calculation"""
        budget_calculations_total.inc()
    
    @staticmethod
    def error(error_type: str, endpoint: str) -> None:
        """Record an error"""
        errors_total.labels(error_type=error_type, endpoint=endpoint).inc()
    
    @staticmethod
    def exception(exception_type: str) -> None:
        """Record an exception"""
        exceptions_total.labels(exception_type=exception_type).inc()
    
    # Sprint 8: Security metrics
    
    @staticmethod
    def rate_limit_hit(endpoint: str, client_type: str = "ip") -> None:
        """Record a rate limit violation"""
        rate_limit_hits_total.labels(endpoint=endpoint, client_type=client_type).inc()
    
    @staticmethod
    def auth_failure(failure_type: str, endpoint: str = "/api/auth/login") -> None:
        """Record an authentication failure"""
        auth_failures_total.labels(failure_type=failure_type, endpoint=endpoint).inc()
    
    @staticmethod
    def audit_event(action: str, level: str = "info") -> None:
        """Record an audit event"""
        audit_events_total.labels(action=action, level=level).inc()
    
    @staticmethod
    def permission_denied(resource_type: str, action: str) -> None:
        """Record a permission denied event"""
        permission_denied_total.labels(resource_type=resource_type, action=action).inc()


# Singleton instance
metrics = Metrics()


def setup_metrics() -> bytes:
    """
    Generate metrics output for Prometheus.
    
    Returns:
        Metrics in Prometheus text format
    
    This is used by the /metrics endpoint.
    """
    return generate_latest(registry)


def get_metrics_content_type() -> str:
    """Get the content type for Prometheus metrics"""
    return CONTENT_TYPE_LATEST
