"""
3dPot Backend - Logging Middleware
Sprint 6: Automatic request/response logging

This middleware automatically logs:
- Incoming requests with method, path, request_id
- Outgoing responses with status, duration
- Exceptions and errors
"""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .logging_config import get_logger
from .request_id import get_request_id


logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically log HTTP requests and responses.
    
    Logs:
    - Request: method, path, request_id, client IP
    - Response: status, duration, request_id
    - Errors: exception type, details, request_id
    
    Usage:
        from backend.observability import LoggingMiddleware
        app.add_middleware(LoggingMiddleware)
    """
    
    def __init__(
        self,
        app: ASGIApp,
        skip_paths: list[str] = None,
    ):
        super().__init__(app)
        # Don't log these paths to reduce noise
        self.skip_paths = skip_paths or ["/health", "/healthz", "/ping", "/metrics"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip logging for certain paths
        if request.url.path in self.skip_paths:
            return await call_next(request)
        
        # Get request metadata
        method = request.method
        path = request.url.path
        request_id = get_request_id()
        client_host = request.client.host if request.client else "unknown"
        
        # Log incoming request
        logger.info(
            "http_request_started",
            method=method,
            path=path,
            request_id=request_id,
            client_ip=client_host,
        )
        
        # Track timing
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Log successful response
            logger.info(
                "http_request_completed",
                method=method,
                path=path,
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2),
                request_id=request_id,
            )
            
            # Log warning for 4xx/5xx errors
            if response.status_code >= 400:
                log_level = "warning" if response.status_code < 500 else "error"
                getattr(logger, log_level)(
                    "http_request_error",
                    method=method,
                    path=path,
                    status_code=response.status_code,
                    duration_ms=round(duration * 1000, 2),
                    request_id=request_id,
                )
            
            return response
            
        except Exception as exc:
            duration = time.time() - start_time
            
            # Log exception
            logger.error(
                "http_request_exception",
                method=method,
                path=path,
                exception_type=type(exc).__name__,
                exception_message=str(exc),
                duration_ms=round(duration * 1000, 2),
                request_id=request_id,
                exc_info=True,
            )
            
            raise
