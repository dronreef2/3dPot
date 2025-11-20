"""
Rate Limiting - 3dPot Sprint 7
Implementação de rate limiting para endpoints sensíveis com token bucket algorithm
"""

import time
import os
from typing import Dict, Optional, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from backend.observability.logging_config import get_logger

logger = get_logger(__name__)

# Import metrics (lazy to avoid circular imports)
try:
    from backend.observability.metrics import metrics
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False


class TokenBucket:
    """
    Token Bucket algorithm implementation for rate limiting.
    Allows burst traffic while maintaining average rate limit.
    """
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket.
        
        Args:
            capacity: Maximum number of tokens (burst capacity)
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
    
    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens from bucket.
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens were consumed, False if insufficient tokens
        """
        self._refill()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def get_available_tokens(self) -> int:
        """Get current number of available tokens"""
        self._refill()
        return int(self.tokens)
    
    def time_until_token_available(self) -> float:
        """Get time in seconds until at least one token is available"""
        self._refill()
        if self.tokens >= 1:
            return 0.0
        tokens_needed = 1 - self.tokens
        return tokens_needed / self.refill_rate


class RateLimiter:
    """
    Rate limiter with support for per-IP and per-user limits.
    Uses token bucket algorithm for smooth rate limiting.
    """
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        burst_size: Optional[int] = None,
        enabled: bool = True
    ):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Average requests allowed per minute
            burst_size: Maximum burst size (defaults to 2x requests_per_minute)
            enabled: Whether rate limiting is enabled
        """
        self.enabled = enabled
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size or (requests_per_minute * 2)
        
        # Convert to tokens per second
        self.refill_rate = requests_per_minute / 60.0
        
        # Storage for token buckets per client
        self.buckets: Dict[str, TokenBucket] = {}
        
        # Cleanup old buckets periodically
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5 minutes
        
        logger.info(
            "rate_limiter_initialized",
            enabled=enabled,
            requests_per_minute=requests_per_minute,
            burst_size=self.burst_size,
            refill_rate=self.refill_rate
        )
    
    def _get_client_key(self, request: Request) -> str:
        """
        Get unique key for client (user_id or IP address).
        
        Args:
            request: FastAPI request object
            
        Returns:
            Unique client identifier
        """
        # Try to get authenticated user ID first
        user_id = getattr(request.state, 'user_id', None)
        if user_id:
            return f"user:{user_id}"
        
        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Get first IP in case of multiple proxies
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        return f"ip:{client_ip}"
    
    def _cleanup_old_buckets(self):
        """Remove inactive buckets to prevent memory leak"""
        now = time.time()
        if now - self.last_cleanup < self.cleanup_interval:
            return
        
        # Remove buckets that are full (haven't been used recently)
        to_remove = []
        for key, bucket in self.buckets.items():
            if bucket.get_available_tokens() >= bucket.capacity:
                to_remove.append(key)
        
        for key in to_remove:
            del self.buckets[key]
        
        self.last_cleanup = now
        
        if to_remove:
            logger.debug("rate_limiter_cleanup", buckets_removed=len(to_remove))
    
    def check_rate_limit(self, request: Request) -> Tuple[bool, Optional[int]]:
        """
        Check if request should be rate limited.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Tuple of (allowed, retry_after_seconds)
        """
        if not self.enabled:
            return True, None
        
        client_key = self._get_client_key(request)
        
        # Get or create token bucket for this client
        if client_key not in self.buckets:
            self.buckets[client_key] = TokenBucket(
                capacity=self.burst_size,
                refill_rate=self.refill_rate
            )
        
        bucket = self.buckets[client_key]
        
        # Try to consume a token
        if bucket.consume(tokens=1):
            # Request allowed
            return True, None
        else:
            # Rate limited - calculate retry after
            retry_after = int(bucket.time_until_token_available()) + 1
            
            logger.warning(
                "rate_limit_exceeded",
                client_key=client_key,
                path=request.url.path,
                method=request.method,
                retry_after=retry_after,
                available_tokens=bucket.get_available_tokens()
            )
            
            # Sprint 8: Emit metrics if available
            if METRICS_AVAILABLE:
                try:
                    client_type = "user" if client_key.startswith("user:") else "ip"
                    metrics.rate_limit_hit(endpoint=request.url.path, client_type=client_type)
                except Exception:
                    # Don't fail rate limiting if metrics fail
                    pass
            
            return False, retry_after
        
        # Periodic cleanup
        self._cleanup_old_buckets()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to apply rate limiting to all requests.
    Can be configured with different limits for different endpoints.
    Sprint 8: Support for Redis backend via redis_limiter parameter.
    """
    
    def __init__(
        self,
        app,
        default_limit: int = 60,
        burst_size: Optional[int] = None,
        sensitive_endpoints: Optional[Dict[str, int]] = None,
        redis_limiter = None
    ):
        """
        Initialize rate limit middleware.
        
        Args:
            app: FastAPI application
            default_limit: Default requests per minute for all endpoints
            burst_size: Default burst size
            sensitive_endpoints: Dict mapping endpoint patterns to specific limits
            redis_limiter: Optional Redis rate limiter instance (Sprint 8)
        """
        super().__init__(app)
        
        # Read configuration from environment
        self.enabled = os.getenv("RATE_LIMITING_ENABLED", "true").lower() == "true"
        
        # Sprint 8: Store Redis limiter if provided
        self.redis_limiter = redis_limiter
        self.using_redis = redis_limiter is not None
        
        # Default rate limiter (in-memory)
        self.default_limiter = RateLimiter(
            requests_per_minute=default_limit,
            burst_size=burst_size,
            enabled=self.enabled
        )
        
        # Specific limiters for sensitive endpoints
        self.sensitive_endpoints = sensitive_endpoints or {}
        self.endpoint_limiters: Dict[str, RateLimiter] = {}
        
        for pattern, limit in self.sensitive_endpoints.items():
            self.endpoint_limiters[pattern] = RateLimiter(
                requests_per_minute=limit,
                burst_size=limit * 2,
                enabled=self.enabled
            )
        
        logger.info(
            "rate_limit_middleware_initialized",
            enabled=self.enabled,
            backend="redis" if self.using_redis else "in-memory",
            default_limit=default_limit,
            sensitive_endpoints=list(self.sensitive_endpoints.keys())
        )
    
    def _get_limiter(self, path: str) -> RateLimiter:
        """Get appropriate rate limiter for the given path"""
        # Check if path matches any sensitive endpoint pattern
        for pattern, limiter in self.endpoint_limiters.items():
            if pattern in path:
                return limiter
        
        # Return default limiter
        return self.default_limiter
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        # Skip rate limiting for health checks and metrics
        if request.url.path in ["/health", "/healthz", "/ping", "/metrics"]:
            return await call_next(request)
        
        # Sprint 8: Use Redis limiter if available
        if self.using_redis and self.redis_limiter:
            try:
                allowed, retry_after = self.redis_limiter.check_rate_limit(request)
                
                if not allowed:
                    # Return 429 Too Many Requests
                    from fastapi.responses import JSONResponse
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={
                            "error": "Rate limit exceeded",
                            "message": "Too many requests. Please try again later.",
                            "retry_after": retry_after
                        },
                        headers={"Retry-After": str(retry_after)}
                    )
                
                # Process request normally
                response = await call_next(request)
                
                # Add rate limit info to response headers
                try:
                    remaining = self.redis_limiter.get_remaining_tokens(request)
                    response.headers["X-RateLimit-Limit"] = str(self.redis_limiter.requests_per_minute)
                    response.headers["X-RateLimit-Remaining"] = str(remaining)
                    response.headers["X-RateLimit-Backend"] = "redis"
                except Exception:
                    pass
                
                return response
                
            except Exception as e:
                # Redis failed - log warning and fall back to in-memory
                logger.warning(
                    "rate_limit_redis_error",
                    error=str(e),
                    fallback="in-memory",
                    message="Redis rate limiting failed, using in-memory fallback"
                )
                # Continue to in-memory logic below
        
        # In-memory rate limiting (default or fallback)
        # Get appropriate limiter
        limiter = self._get_limiter(request.url.path)
        
        # Check rate limit
        allowed, retry_after = limiter.check_rate_limit(request)
        
        if not allowed:
            # Return 429 Too Many Requests
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": retry_after
                },
                headers={"Retry-After": str(retry_after)}
            )
        
        # Process request normally
        response = await call_next(request)
        
        # Add rate limit info to response headers
        try:
            client_key = limiter._get_client_key(request)
            if client_key in limiter.buckets:
                remaining = limiter.buckets[client_key].get_available_tokens()
            else:
                remaining = limiter.burst_size
            
            response.headers["X-RateLimit-Limit"] = str(limiter.requests_per_minute)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Backend"] = "in-memory"
        except Exception:
            pass
        
        return response


# Configuration helpers
def get_rate_limit_config() -> Dict[str, int]:
    """
    Get rate limit configuration from environment variables.
    
    Returns:
        Dict with rate limit settings
    """
    return {
        "default": int(os.getenv("RATE_LIMIT_DEFAULT", "60")),
        "auth": int(os.getenv("RATE_LIMIT_AUTH", "10")),
        "api_general": int(os.getenv("RATE_LIMIT_API", "100")),
        "cloud_rendering": int(os.getenv("RATE_LIMIT_CLOUD_RENDERING", "30")),
        "marketplace": int(os.getenv("RATE_LIMIT_MARKETPLACE", "50")),
    }


def create_rate_limit_middleware(app):
    """
    Factory function to create and configure rate limit middleware.
    
    Args:
        app: FastAPI application
    """
    config = get_rate_limit_config()
    
    # Define sensitive endpoints with specific limits
    sensitive_endpoints = {
        "/api/auth/login": config["auth"],
        "/api/auth/register": config["auth"],
        "/api/v1/cloud-rendering": config["cloud_rendering"],
        "/api/v1/marketplace": config["marketplace"],
    }
    
    return RateLimitMiddleware(
        app,
        default_limit=config["default"],
        sensitive_endpoints=sensitive_endpoints
    )
