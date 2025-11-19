"""
Tests for Rate Limiting - Sprint 7
"""

import pytest
import time
from unittest.mock import Mock, MagicMock
from fastapi import Request, FastAPI
from fastapi.testclient import TestClient

from backend.observability.rate_limiting import (
    TokenBucket, RateLimiter, RateLimitMiddleware, get_rate_limit_config
)


class TestTokenBucket:
    """Test TokenBucket algorithm"""
    
    def test_token_bucket_initialization(self):
        """Test token bucket is initialized correctly"""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        
        assert bucket.capacity == 10
        assert bucket.refill_rate == 1.0
        assert bucket.tokens == 10
    
    def test_consume_tokens_success(self):
        """Test consuming tokens when available"""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        
        # Should succeed
        assert bucket.consume(1) is True
        assert bucket.get_available_tokens() == 9
        
        # Consume more
        assert bucket.consume(5) is True
        assert bucket.get_available_tokens() == 4
    
    def test_consume_tokens_insufficient(self):
        """Test consuming tokens when insufficient"""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        
        # Consume all tokens
        assert bucket.consume(10) is True
        assert bucket.get_available_tokens() == 0
        
        # Try to consume more - should fail
        assert bucket.consume(1) is False
    
    def test_token_refill(self):
        """Test tokens are refilled over time"""
        bucket = TokenBucket(capacity=10, refill_rate=10.0)  # 10 tokens/second
        
        # Consume all tokens
        bucket.consume(10)
        assert bucket.get_available_tokens() == 0
        
        # Wait a bit and check refill
        time.sleep(0.2)  # Should add ~2 tokens
        available = bucket.get_available_tokens()
        assert available >= 1  # At least 1 token should be available
        assert available <= 3  # But not too many
    
    def test_token_bucket_max_capacity(self):
        """Test bucket doesn't exceed max capacity"""
        bucket = TokenBucket(capacity=10, refill_rate=100.0)
        
        # Wait for refill
        time.sleep(0.5)
        
        # Should not exceed capacity
        assert bucket.get_available_tokens() <= 10
    
    def test_time_until_token_available(self):
        """Test calculation of time until token available"""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        
        # When tokens available, should be 0
        assert bucket.time_until_token_available() == 0.0
        
        # Consume all
        bucket.consume(10)
        
        # Should need ~1 second for next token
        wait_time = bucket.time_until_token_available()
        assert wait_time > 0.0
        assert wait_time <= 1.1  # Allow small margin


class TestRateLimiter:
    """Test RateLimiter class"""
    
    def test_rate_limiter_initialization(self):
        """Test rate limiter is initialized correctly"""
        limiter = RateLimiter(requests_per_minute=60)
        
        assert limiter.enabled is True
        assert limiter.requests_per_minute == 60
        assert limiter.burst_size == 120  # 2x by default
        assert limiter.refill_rate == 1.0  # 60/60
    
    def test_rate_limiter_disabled(self):
        """Test rate limiter when disabled"""
        limiter = RateLimiter(enabled=False)
        
        # Create mock request
        request = Mock(spec=Request)
        request.state = Mock()
        request.state.user_id = None
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {}
        
        # Should always allow when disabled
        for _ in range(1000):
            allowed, retry_after = limiter.check_rate_limit(request)
            assert allowed is True
            assert retry_after is None
    
    def test_rate_limiter_allows_within_limit(self):
        """Test rate limiter allows requests within limit"""
        limiter = RateLimiter(requests_per_minute=60, burst_size=10)
        
        # Create mock request
        request = Mock(spec=Request)
        request.state = Mock()
        request.state.user_id = None
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {}
        
        # Should allow first 10 requests (burst size)
        for _ in range(10):
            allowed, retry_after = limiter.check_rate_limit(request)
            assert allowed is True
            assert retry_after is None
    
    def test_rate_limiter_blocks_over_limit(self):
        """Test rate limiter blocks requests over limit"""
        limiter = RateLimiter(requests_per_minute=60, burst_size=5)
        
        # Create mock request
        request = Mock(spec=Request)
        request.state = Mock()
        request.state.user_id = None
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {}
        
        # Allow first 5 requests
        for _ in range(5):
            allowed, _ = limiter.check_rate_limit(request)
            assert allowed is True
        
        # 6th request should be blocked
        allowed, retry_after = limiter.check_rate_limit(request)
        assert allowed is False
        assert retry_after is not None
        assert retry_after > 0
    
    def test_rate_limiter_per_user(self):
        """Test rate limiter differentiates between users"""
        limiter = RateLimiter(requests_per_minute=60, burst_size=5)
        
        # User 1
        request1 = Mock(spec=Request)
        request1.state = Mock()
        request1.state.user_id = "user-1"
        request1.client = Mock()
        request1.client.host = "127.0.0.1"
        request1.headers = {}
        
        # User 2
        request2 = Mock(spec=Request)
        request2.state = Mock()
        request2.state.user_id = "user-2"
        request2.client = Mock()
        request2.client.host = "127.0.0.2"
        request2.headers = {}
        
        # Each user should have independent limits
        for _ in range(5):
            allowed, _ = limiter.check_rate_limit(request1)
            assert allowed is True
        
        # User 1 is now at limit
        allowed, _ = limiter.check_rate_limit(request1)
        assert allowed is False
        
        # But user 2 should still be allowed
        for _ in range(5):
            allowed, _ = limiter.check_rate_limit(request2)
            assert allowed is True
    
    def test_rate_limiter_x_forwarded_for(self):
        """Test rate limiter uses X-Forwarded-For header"""
        limiter = RateLimiter(requests_per_minute=60, burst_size=5)
        
        # Request with X-Forwarded-For
        request = Mock(spec=Request)
        request.state = Mock()
        request.state.user_id = None
        request.client = Mock()
        request.client.host = "192.168.1.1"  # Internal IP
        request.headers = {"X-Forwarded-For": "203.0.113.1, 198.51.100.1"}  # Real IPs
        
        # Should use first IP from X-Forwarded-For
        key = limiter._get_client_key(request)
        assert "203.0.113.1" in key


class TestRateLimitConfig:
    """Test rate limit configuration"""
    
    def test_get_rate_limit_config_defaults(self):
        """Test default rate limit configuration"""
        import os
        
        # Clear env vars
        for key in ["RATE_LIMIT_DEFAULT", "RATE_LIMIT_AUTH", "RATE_LIMIT_API"]:
            os.environ.pop(key, None)
        
        config = get_rate_limit_config()
        
        assert config["default"] == 60
        assert config["auth"] == 10
        assert config["api_general"] == 100
    
    def test_get_rate_limit_config_from_env(self, monkeypatch):
        """Test rate limit configuration from environment"""
        monkeypatch.setenv("RATE_LIMIT_DEFAULT", "100")
        monkeypatch.setenv("RATE_LIMIT_AUTH", "5")
        
        config = get_rate_limit_config()
        
        assert config["default"] == 100
        assert config["auth"] == 5
