"""
3dPot Backend - Request ID / Correlation ID / Trace ID Middleware
Sprint 6: Request tracing for production debugging
Sprint 9: Extended with X-Trace-Id support for distributed tracing

This middleware:
- Generates unique request IDs for each HTTP request
- Accepts existing X-Request-ID headers for distributed tracing
- Accepts/generates X-Trace-Id for distributed tracing (Sprint 9)
- Adds request IDs and trace IDs to response headers
- Makes request IDs and trace IDs available via context for logging
"""

import uuid
from contextvars import ContextVar
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


# Context variable to store request ID across async calls
_request_id_ctx_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)

# Sprint 9: Context variable to store trace ID across async calls
_trace_id_ctx_var: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)


def get_request_id() -> Optional[str]:
    """
    Get the current request ID from context.
    
    Returns:
        Current request ID or None if not in request context
    
    Example:
        from backend.observability import get_request_id
        request_id = get_request_id()
        logger.info("processing", request_id=request_id)
    """
    return _request_id_ctx_var.get()


def set_request_id(request_id: str) -> None:
    """Set the request ID in context"""
    _request_id_ctx_var.set(request_id)


def get_trace_id() -> Optional[str]:
    """
    Get the current trace ID from context (Sprint 9).
    
    Returns:
        Current trace ID or None if not in request context
    
    Example:
        from backend.observability import get_trace_id
        trace_id = get_trace_id()
        logger.info("processing", trace_id=trace_id)
    """
    return _trace_id_ctx_var.get()


def set_trace_id(trace_id: str) -> None:
    """Set the trace ID in context (Sprint 9)"""
    _trace_id_ctx_var.set(trace_id)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle request ID and trace ID generation and propagation.
    
    This middleware:
    1. Checks for existing X-Request-ID header
    2. Generates new UUID if not present
    3. Checks for existing X-Trace-Id header (Sprint 9)
    4. Generates new UUID for trace if not present (Sprint 9)
    5. Sets request ID and trace ID in context for logging
    6. Adds X-Request-ID and X-Trace-Id to response headers
    
    Usage:
        from backend.observability import RequestIDMiddleware
        app.add_middleware(RequestIDMiddleware)
    """
    
    def __init__(
        self,
        app: ASGIApp,
        request_header_name: str = "X-Request-ID",
        trace_header_name: str = "X-Trace-Id",
    ):
        super().__init__(app)
        self.request_header_name = request_header_name
        self.trace_header_name = trace_header_name
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get or generate request ID
        request_id = request.headers.get(self.request_header_name)
        
        if not request_id:
            # Generate new UUID for this request
            request_id = str(uuid.uuid4())
        
        # Sprint 9: Get or generate trace ID
        trace_id = request.headers.get(self.trace_header_name)
        
        if not trace_id:
            # Generate new UUID for this trace
            # In a distributed system, this would be propagated across services
            trace_id = str(uuid.uuid4())
        
        # Set in context for access in handlers and services
        set_request_id(request_id)
        set_trace_id(trace_id)
        
        # Store in request state for easy access
        request.state.request_id = request_id
        request.state.trace_id = trace_id
        
        # Process request
        response = await call_next(request)
        
        # Add request ID and trace ID to response headers
        response.headers[self.request_header_name] = request_id
        response.headers[self.trace_header_name] = trace_id
        
        return response
