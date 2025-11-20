"""
Rate Limiting with Redis - 3dPot Sprint 8
Implementação de rate limiting distribuído usando Redis como backend
Permite escalabilidade horizontal com múltiplos workers/instâncias
"""

import time
import os
from typing import Dict, Optional, Tuple
from datetime import datetime
from fastapi import Request

from backend.observability.logging_config import get_logger

logger = get_logger(__name__)

# Lazy import Redis to make it optional
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("redis_not_available", message="Redis library not installed. Redis rate limiting will not be available.")


class RedisTokenBucket:
    """
    Token Bucket algorithm implementation using Redis for distributed rate limiting.
    Allows burst traffic while maintaining average rate limit across multiple instances.
    """
    
    def __init__(
        self, 
        redis_client,
        key_prefix: str,
        capacity: int, 
        refill_rate: float,
        ttl: int = 3600
    ):
        """
        Initialize Redis-backed token bucket.
        
        Args:
            redis_client: Redis client instance
            key_prefix: Prefix for Redis keys (e.g., "rate_limit:auth")
            capacity: Maximum number of tokens (burst capacity)
            refill_rate: Tokens added per second
            ttl: Time to live for Redis keys in seconds (default: 1 hour)
        """
        self.redis_client = redis_client
        self.key_prefix = key_prefix
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.ttl = ttl
    
    def _get_redis_key(self, client_key: str) -> str:
        """Generate Redis key for a client"""
        return f"{self.key_prefix}:{client_key}"
    
    def _get_bucket_state(self, client_key: str) -> Tuple[float, float]:
        """
        Get current bucket state from Redis.
        
        Returns:
            Tuple of (tokens, last_refill_timestamp)
        """
        redis_key = self._get_redis_key(client_key)
        
        # Use pipeline for atomic read
        pipe = self.redis_client.pipeline()
        pipe.hget(redis_key, "tokens")
        pipe.hget(redis_key, "last_refill")
        results = pipe.execute()
        
        tokens = float(results[0]) if results[0] else self.capacity
        last_refill = float(results[1]) if results[1] else time.time()
        
        return tokens, last_refill
    
    def _set_bucket_state(self, client_key: str, tokens: float, last_refill: float):
        """
        Set bucket state in Redis.
        
        Args:
            client_key: Client identifier
            tokens: Current token count
            last_refill: Last refill timestamp
        """
        redis_key = self._get_redis_key(client_key)
        
        # Use pipeline for atomic write
        pipe = self.redis_client.pipeline()
        pipe.hset(redis_key, "tokens", str(tokens))
        pipe.hset(redis_key, "last_refill", str(last_refill))
        pipe.expire(redis_key, self.ttl)
        pipe.execute()
    
    def consume(self, client_key: str, tokens: int = 1) -> bool:
        """
        Try to consume tokens from bucket for a specific client.
        
        Args:
            client_key: Client identifier (IP or user ID)
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens were consumed, False if insufficient tokens
        """
        # Get current state
        current_tokens, last_refill = self._get_bucket_state(client_key)
        
        # Calculate refill
        now = time.time()
        elapsed = now - last_refill
        tokens_to_add = elapsed * self.refill_rate
        
        # Refill tokens
        current_tokens = min(self.capacity, current_tokens + tokens_to_add)
        
        # Try to consume
        if current_tokens >= tokens:
            current_tokens -= tokens
            self._set_bucket_state(client_key, current_tokens, now)
            return True
        else:
            # Update last_refill even if we can't consume
            self._set_bucket_state(client_key, current_tokens, now)
            return False
    
    def get_available_tokens(self, client_key: str) -> int:
        """Get current number of available tokens for a client"""
        current_tokens, last_refill = self._get_bucket_state(client_key)
        
        # Calculate refill
        now = time.time()
        elapsed = now - last_refill
        tokens_to_add = elapsed * self.refill_rate
        
        current_tokens = min(self.capacity, current_tokens + tokens_to_add)
        return int(current_tokens)
    
    def time_until_token_available(self, client_key: str) -> float:
        """Get time in seconds until at least one token is available"""
        available = self.get_available_tokens(client_key)
        
        if available >= 1:
            return 0.0
        
        tokens_needed = 1 - available
        return tokens_needed / self.refill_rate


class RedisRateLimiter:
    """
    Distributed rate limiter using Redis.
    Supports per-IP and per-user limits across multiple application instances.
    """
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        requests_per_minute: int = 60,
        burst_size: Optional[int] = None,
        enabled: bool = True,
        key_prefix: str = "rate_limit"
    ):
        """
        Initialize Redis-backed rate limiter.
        
        Args:
            redis_url: Redis connection URL (e.g., redis://localhost:6379/0)
            requests_per_minute: Average requests allowed per minute
            burst_size: Maximum burst size (defaults to 2x requests_per_minute)
            enabled: Whether rate limiting is enabled
            key_prefix: Prefix for Redis keys
        """
        self.enabled = enabled
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size or (requests_per_minute * 2)
        self.key_prefix = key_prefix
        
        # Convert to tokens per second
        self.refill_rate = requests_per_minute / 60.0
        
        # Initialize Redis client
        if not REDIS_AVAILABLE:
            raise ImportError("Redis library is not installed. Install with: pip install redis")
        
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
        try:
            # Parse Redis URL for connection
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            self.redis_client.ping()
            
            logger.info(
                "redis_rate_limiter_initialized",
                enabled=enabled,
                requests_per_minute=requests_per_minute,
                burst_size=self.burst_size,
                redis_url=self.redis_url.split('@')[-1] if '@' in self.redis_url else self.redis_url  # Hide credentials
            )
            
        except Exception as e:
            logger.error(
                "redis_connection_failed",
                error=str(e),
                redis_url=self.redis_url.split('@')[-1] if '@' in self.redis_url else self.redis_url
            )
            raise
    
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
        
        # Create token bucket for this endpoint
        bucket = RedisTokenBucket(
            redis_client=self.redis_client,
            key_prefix=self.key_prefix,
            capacity=self.burst_size,
            refill_rate=self.refill_rate
        )
        
        # Try to consume a token
        if bucket.consume(client_key, tokens=1):
            # Request allowed
            return True, None
        else:
            # Rate limited - calculate retry after
            retry_after = int(bucket.time_until_token_available(client_key)) + 1
            
            logger.warning(
                "rate_limit_exceeded",
                client_key=client_key,
                path=request.url.path,
                method=request.method,
                retry_after=retry_after,
                available_tokens=bucket.get_available_tokens(client_key),
                backend="redis"
            )
            
            return False, retry_after
    
    def get_remaining_tokens(self, request: Request) -> int:
        """
        Get remaining tokens for a client.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Number of remaining tokens
        """
        client_key = self._get_client_key(request)
        
        bucket = RedisTokenBucket(
            redis_client=self.redis_client,
            key_prefix=self.key_prefix,
            capacity=self.burst_size,
            refill_rate=self.refill_rate
        )
        
        return bucket.get_available_tokens(client_key)
    
    def close(self):
        """Close Redis connection"""
        if hasattr(self, 'redis_client'):
            self.redis_client.close()


def create_redis_rate_limiter(
    redis_url: Optional[str] = None,
    requests_per_minute: int = 60,
    burst_size: Optional[int] = None,
    enabled: bool = True,
    key_prefix: str = "rate_limit"
) -> RedisRateLimiter:
    """
    Factory function to create Redis rate limiter.
    
    Args:
        redis_url: Redis connection URL
        requests_per_minute: Average requests allowed per minute
        burst_size: Maximum burst size
        enabled: Whether rate limiting is enabled
        key_prefix: Prefix for Redis keys
        
    Returns:
        RedisRateLimiter instance
    """
    return RedisRateLimiter(
        redis_url=redis_url,
        requests_per_minute=requests_per_minute,
        burst_size=burst_size,
        enabled=enabled,
        key_prefix=key_prefix
    )
