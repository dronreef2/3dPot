"""
Tests for Redis Rate Limiting - 3dPot Sprint 8
Unit tests for distributed rate limiting with Redis backend
"""

import pytest
import time
from unittest.mock import Mock, MagicMock, patch
from fastapi import Request, HTTPException

# Mock Redis before importing
redis_mock = MagicMock()
with patch.dict('sys.modules', {'redis': redis_mock}):
    from backend.observability.rate_limiting_redis import (
        RedisTokenBucket,
        RedisRateLimiter,
        create_redis_rate_limiter,
        REDIS_AVAILABLE
    )


@pytest.fixture
def mock_redis_client():
    """Mock Redis client for testing"""
    client = MagicMock()
    
    # Mock pipeline behavior
    pipe = MagicMock()
    pipe.execute.return_value = [None, None]  # No data initially
    client.pipeline.return_value = pipe
    
    # Mock ping
    client.ping.return_value = True
    
    return client


@pytest.fixture
def redis_bucket(mock_redis_client):
    """Create a RedisTokenBucket for testing"""
    return RedisTokenBucket(
        redis_client=mock_redis_client,
        key_prefix="test_rate_limit",
        capacity=10,
        refill_rate=1.0,  # 1 token per second
        ttl=3600
    )


@pytest.fixture
def mock_request():
    """Create a mock FastAPI request"""
    request = Mock(spec=Request)
    request.url.path = "/api/test"
    request.method = "GET"
    request.client.host = "192.168.1.1"
    request.headers = {}
    request.state = Mock()
    return request


class TestRedisTokenBucket:
    """Tests for RedisTokenBucket class"""
    
    def test_initialization(self, redis_bucket, mock_redis_client):
        """Test that RedisTokenBucket initializes correctly"""
        assert redis_bucket.capacity == 10
        assert redis_bucket.refill_rate == 1.0
        assert redis_bucket.ttl == 3600
        assert redis_bucket.redis_client == mock_redis_client
    
    def test_get_redis_key(self, redis_bucket):
        """Test Redis key generation"""
        key = redis_bucket._get_redis_key("client123")
        assert key == "test_rate_limit:client123"
    
    def test_get_bucket_state_new_bucket(self, redis_bucket, mock_redis_client):
        """Test getting state for a new bucket (no Redis data)"""
        # Mock pipeline to return None (no data)
        pipe = MagicMock()
        pipe.execute.return_value = [None, None]
        mock_redis_client.pipeline.return_value = pipe
        
        tokens, last_refill = redis_bucket._get_bucket_state("client123")
        
        # Should return capacity and current time
        assert tokens == 10  # capacity
        assert isinstance(last_refill, float)
    
    def test_get_bucket_state_existing_bucket(self, redis_bucket, mock_redis_client):
        """Test getting state for an existing bucket"""
        # Mock pipeline to return existing data
        pipe = MagicMock()
        pipe.execute.return_value = ["5.5", "1234567890.0"]
        mock_redis_client.pipeline.return_value = pipe
        
        tokens, last_refill = redis_bucket._get_bucket_state("client123")
        
        assert tokens == 5.5
        assert last_refill == 1234567890.0
    
    def test_set_bucket_state(self, redis_bucket, mock_redis_client):
        """Test setting bucket state in Redis"""
        pipe = MagicMock()
        mock_redis_client.pipeline.return_value = pipe
        
        redis_bucket._set_bucket_state("client123", 7.5, 1234567890.0)
        
        # Verify pipeline commands
        pipe.hset.assert_any_call("test_rate_limit:client123", "tokens", "7.5")
        pipe.hset.assert_any_call("test_rate_limit:client123", "last_refill", "1234567890.0")
        pipe.expire.assert_called_once_with("test_rate_limit:client123", 3600)
        pipe.execute.assert_called_once()
    
    def test_consume_sufficient_tokens(self, redis_bucket, mock_redis_client):
        """Test consuming tokens when sufficient tokens available"""
        # Mock existing state: 5 tokens, recent refill
        pipe = MagicMock()
        pipe.execute.return_value = ["5.0", str(time.time())]
        mock_redis_client.pipeline.return_value = pipe
        
        # Should succeed
        result = redis_bucket.consume("client123", tokens=3)
        assert result is True
    
    def test_consume_insufficient_tokens(self, redis_bucket, mock_redis_client):
        """Test consuming tokens when insufficient tokens available"""
        # Mock existing state: 2 tokens, recent refill
        pipe = MagicMock()
        pipe.execute.return_value = ["2.0", str(time.time())]
        mock_redis_client.pipeline.return_value = pipe
        
        # Should fail (trying to consume 5 tokens)
        result = redis_bucket.consume("client123", tokens=5)
        assert result is False
    
    def test_get_available_tokens(self, redis_bucket, mock_redis_client):
        """Test getting available tokens count"""
        # Mock state: 8 tokens
        pipe = MagicMock()
        pipe.execute.return_value = ["8.0", str(time.time())]
        mock_redis_client.pipeline.return_value = pipe
        
        available = redis_bucket.get_available_tokens("client123")
        assert available == 8
    
    def test_time_until_token_available_tokens_available(self, redis_bucket, mock_redis_client):
        """Test time until token available when tokens are available"""
        # Mock state: 5 tokens
        pipe = MagicMock()
        pipe.execute.return_value = ["5.0", str(time.time())]
        mock_redis_client.pipeline.return_value = pipe
        
        wait_time = redis_bucket.time_until_token_available("client123")
        assert wait_time == 0.0
    
    def test_time_until_token_available_no_tokens(self, redis_bucket, mock_redis_client):
        """Test time until token available when no tokens available"""
        # Mock state: 0.5 tokens (less than 1)
        pipe = MagicMock()
        pipe.execute.return_value = ["0.5", str(time.time())]
        mock_redis_client.pipeline.return_value = pipe
        
        wait_time = redis_bucket.time_until_token_available("client123")
        # Should be approximately (1 - 0.5) / 1.0 = 0.5 seconds
        assert 0.4 <= wait_time <= 0.6


class TestRedisRateLimiter:
    """Tests for RedisRateLimiter class"""
    
    @patch('backend.observability.rate_limiting_redis.redis.from_url')
    def test_initialization(self, mock_from_url, mock_redis_client):
        """Test that RedisRateLimiter initializes correctly"""
        mock_from_url.return_value = mock_redis_client
        
        limiter = RedisRateLimiter(
            redis_url="redis://localhost:6379/0",
            requests_per_minute=60,
            enabled=True
        )
        
        assert limiter.enabled is True
        assert limiter.requests_per_minute == 60
        assert limiter.burst_size == 120  # 2x requests_per_minute
        assert limiter.refill_rate == 1.0  # 60/60
    
    @patch('backend.observability.rate_limiting_redis.redis.from_url')
    def test_initialization_connection_failure(self, mock_from_url):
        """Test initialization with Redis connection failure"""
        mock_from_url.return_value.ping.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception):
            RedisRateLimiter(redis_url="redis://invalid:6379/0")
    
    def test_get_client_key_authenticated(self, mock_request):
        """Test client key generation for authenticated user"""
        mock_request.state.user_id = "user123"
        
        # Create a minimal limiter just for testing _get_client_key
        limiter = Mock()
        limiter._get_client_key = RedisRateLimiter._get_client_key.__get__(limiter)
        
        key = limiter._get_client_key(mock_request)
        assert key == "user:user123"
    
    def test_get_client_key_ip(self, mock_request):
        """Test client key generation for unauthenticated user (IP)"""
        # No user_id on request
        
        # Create a minimal limiter just for testing _get_client_key
        limiter = Mock()
        limiter._get_client_key = RedisRateLimiter._get_client_key.__get__(limiter)
        
        key = limiter._get_client_key(mock_request)
        assert key == "ip:192.168.1.1"
    
    def test_get_client_key_forwarded(self, mock_request):
        """Test client key generation with X-Forwarded-For header"""
        mock_request.headers = {"X-Forwarded-For": "10.0.0.1, 192.168.1.1"}
        
        limiter = Mock()
        limiter._get_client_key = RedisRateLimiter._get_client_key.__get__(limiter)
        
        key = limiter._get_client_key(mock_request)
        assert key == "ip:10.0.0.1"  # First IP in chain
    
    @patch('backend.observability.rate_limiting_redis.redis.from_url')
    @patch('backend.observability.rate_limiting_redis.RedisTokenBucket')
    def test_check_rate_limit_allowed(self, mock_bucket_class, mock_from_url, mock_redis_client, mock_request):
        """Test rate limit check when request is allowed"""
        mock_from_url.return_value = mock_redis_client
        
        # Mock bucket to allow request
        mock_bucket = MagicMock()
        mock_bucket.consume.return_value = True
        mock_bucket_class.return_value = mock_bucket
        
        limiter = RedisRateLimiter(redis_url="redis://localhost:6379/0")
        allowed, retry_after = limiter.check_rate_limit(mock_request)
        
        assert allowed is True
        assert retry_after is None
    
    @patch('backend.observability.rate_limiting_redis.redis.from_url')
    @patch('backend.observability.rate_limiting_redis.RedisTokenBucket')
    def test_check_rate_limit_exceeded(self, mock_bucket_class, mock_from_url, mock_redis_client, mock_request):
        """Test rate limit check when limit is exceeded"""
        mock_from_url.return_value = mock_redis_client
        
        # Mock bucket to deny request
        mock_bucket = MagicMock()
        mock_bucket.consume.return_value = False
        mock_bucket.time_until_token_available.return_value = 5.0
        mock_bucket.get_available_tokens.return_value = 0
        mock_bucket_class.return_value = mock_bucket
        
        limiter = RedisRateLimiter(redis_url="redis://localhost:6379/0")
        allowed, retry_after = limiter.check_rate_limit(mock_request)
        
        assert allowed is False
        assert retry_after == 6  # 5 + 1
    
    @patch('backend.observability.rate_limiting_redis.redis.from_url')
    def test_check_rate_limit_disabled(self, mock_from_url, mock_redis_client, mock_request):
        """Test rate limit check when rate limiting is disabled"""
        mock_from_url.return_value = mock_redis_client
        
        limiter = RedisRateLimiter(redis_url="redis://localhost:6379/0", enabled=False)
        allowed, retry_after = limiter.check_rate_limit(mock_request)
        
        assert allowed is True
        assert retry_after is None
    
    @patch('backend.observability.rate_limiting_redis.redis.from_url')
    @patch('backend.observability.rate_limiting_redis.RedisTokenBucket')
    def test_get_remaining_tokens(self, mock_bucket_class, mock_from_url, mock_redis_client, mock_request):
        """Test getting remaining tokens for a client"""
        mock_from_url.return_value = mock_redis_client
        
        # Mock bucket to return 15 tokens
        mock_bucket = MagicMock()
        mock_bucket.get_available_tokens.return_value = 15
        mock_bucket_class.return_value = mock_bucket
        
        limiter = RedisRateLimiter(redis_url="redis://localhost:6379/0")
        remaining = limiter.get_remaining_tokens(mock_request)
        
        assert remaining == 15
    
    @patch('backend.observability.rate_limiting_redis.redis.from_url')
    def test_close(self, mock_from_url, mock_redis_client):
        """Test closing Redis connection"""
        mock_from_url.return_value = mock_redis_client
        
        limiter = RedisRateLimiter(redis_url="redis://localhost:6379/0")
        limiter.close()
        
        mock_redis_client.close.assert_called_once()


class TestFactoryFunction:
    """Tests for factory functions"""
    
    @patch('backend.observability.rate_limiting_redis.redis.from_url')
    def test_create_redis_rate_limiter(self, mock_from_url, mock_redis_client):
        """Test factory function for creating Redis rate limiter"""
        mock_from_url.return_value = mock_redis_client
        
        limiter = create_redis_rate_limiter(
            redis_url="redis://localhost:6379/0",
            requests_per_minute=120,
            burst_size=200,
            enabled=True,
            key_prefix="custom_prefix"
        )
        
        assert limiter.requests_per_minute == 120
        assert limiter.burst_size == 200
        assert limiter.enabled is True
        assert limiter.key_prefix == "custom_prefix"
