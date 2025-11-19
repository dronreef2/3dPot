"""
3dPot Backend - Request ID / Correlation ID Middleware
Sprint 6: Request tracing for production debugging

This middleware:
- Generates unique request IDs for each HTTP request
- Accepts existing X-Request-ID headers for distributed tracing
- Adds request IDs to response headers
- Makes request IDs available via context for logging
"""

import uuid
from contextvars import ContextVar
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


# Context variable to store request ID across async calls
_request_id_ctx_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


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


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle request ID generation and propagation.
    
    This middleware:
    1. Checks for existing X-Request-ID header
    2. Generates new UUID if not present
    3. Sets request ID in context for logging
    4. Adds X-Request-ID to response headers
    
    Usage:
        from backend.observability import RequestIDMiddleware
        app.add_middleware(RequestIDMiddleware)
    """
    
    def __init__(
        self,
        app: ASGIApp,
        header_name: str = "X-Request-ID",
    ):
        super().__init__(app)
        self.header_name = header_name
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get or generate request ID
        request_id = request.headers.get(self.header_name)
        
        if not request_id:
            # Generate new UUID for this request
            request_id = str(uuid.uuid4())
        
        # Set in context for access in handlers and services
        set_request_id(request_id)
        
        # Store in request state for easy access
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Add request ID to response headers
        response.headers[self.header_name] = request_id
        
        return response
