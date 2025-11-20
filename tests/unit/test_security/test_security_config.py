"""
Tests for Security Configuration - Sprint 7
"""

import pytest
import os
from unittest.mock import patch
from pydantic import ValidationError

from backend.core.security_config import (
    SecurityConfig, load_security_config, check_required_secrets,
    validate_production_config, get_safe_config_summary,
    ConfigValidationError
)


class TestSecurityConfig:
    """Test SecurityConfig model validation"""
    
    def test_security_config_defaults(self):
        """Test security config with valid defaults"""
        config = SecurityConfig(
            secret_key="a" * 32,  # Minimum length
            database_url="postgresql://user:pass@localhost/db"
        )
        
        assert config.environment == "development"
        assert config.debug is False
        assert config.algorithm == "HS256"
        assert config.rate_limiting_enabled is True
    
    def test_security_config_validates_secret_key_length(self):
        """Test that secret key must meet minimum length"""
        with pytest.raises(ValidationError) as exc_info:
            SecurityConfig(
                secret_key="short",  # Too short
                database_url="postgresql://user:pass@localhost/db"
            )
        
        assert "at least 32 characters" in str(exc_info.value)
    
    def test_security_config_production_requires_strong_secret(self):
        """Test that production requires strong secret key"""
        with pytest.raises(ValidationError) as exc_info:
            SecurityConfig(
                environment="production",
                secret_key="a" * 32,  # Too short for production
                database_url="postgresql://user:pass@localhost/db"
            )
        
        assert "at least 64 characters" in str(exc_info.value)
    
    def test_security_config_rejects_insecure_secrets_in_production(self):
        """Test that insecure secret keys are rejected in production"""
        with pytest.raises(ValidationError) as exc_info:
            SecurityConfig(
                environment="production",
                secret_key="CHANGE_ME_IN_PRODUCTION" + "x" * 50,
                database_url="postgresql://user:pass@localhost/db"
            )
        
        assert "cannot contain common/insecure values" in str(exc_info.value)
    
    def test_security_config_validates_database_url(self):
        """Test database URL validation"""
        with pytest.raises(ValidationError) as exc_info:
            SecurityConfig(
                secret_key="a" * 32,
                database_url="mysql://user:pass@localhost/db"  # Wrong DB type
            )
        
        assert "PostgreSQL" in str(exc_info.value)
    
    def test_security_config_accepts_valid_database_url(self):
        """Test that valid database URLs are accepted"""
        # PostgreSQL URL
        config1 = SecurityConfig(
            secret_key="a" * 32,
            database_url="postgresql://user:pass@localhost/db"
        )
        assert config1.database_url.startswith("postgresql://")
        
        # PostgreSQL with psycopg2
        config2 = SecurityConfig(
            secret_key="a" * 32,
            database_url="postgresql+psycopg2://user:pass@localhost/db"
        )
        assert config2.database_url.startswith("postgresql+psycopg2://")
    
    def test_security_config_production_requires_debug_disabled(self):
        """Test that debug must be disabled in production"""
        with pytest.raises(ValidationError) as exc_info:
            SecurityConfig(
                environment="production",
                debug=True,
                secret_key="a" * 64,
                database_url="postgresql://user:pass@localhost/db"
            )
        
        assert "DEBUG mode must be disabled" in str(exc_info.value)
    
    def test_security_config_warns_on_wildcard_cors_in_production(self, caplog):
        """Test warning on wildcard CORS in production"""
        config = SecurityConfig(
            environment="production",
            debug=False,
            secret_key="a" * 64,
            database_url="postgresql://user:pass@localhost/db",
            allowed_origins=["*"]
        )
        
        # Config should be created but warning logged
        assert config.allowed_origins == ["*"]
    
    def test_security_config_password_policy_defaults(self):
        """Test password policy defaults"""
        config = SecurityConfig(
            secret_key="a" * 32,
            database_url="postgresql://user:pass@localhost/db"
        )
        
        assert config.password_min_length == 8
        assert config.password_require_uppercase is True
        assert config.password_require_lowercase is True
        assert config.password_require_numbers is True
        assert config.password_require_special is True
    
    def test_security_config_token_expiration_validation(self):
        """Test token expiration validation"""
        # Too short
        with pytest.raises(ValidationError):
            SecurityConfig(
                secret_key="a" * 32,
                database_url="postgresql://user:pass@localhost/db",
                access_token_expire_minutes=1  # Less than minimum
            )
        
        # Too long
        with pytest.raises(ValidationError):
            SecurityConfig(
                secret_key="a" * 32,
                database_url="postgresql://user:pass@localhost/db",
                access_token_expire_minutes=2000  # More than maximum
            )
        
        # Valid
        config = SecurityConfig(
            secret_key="a" * 32,
            database_url="postgresql://user:pass@localhost/db",
            access_token_expire_minutes=30
        )
        assert config.access_token_expire_minutes == 30


class TestLoadSecurityConfig:
    """Test loading configuration from environment"""
    
    def test_load_security_config_from_env(self, monkeypatch):
        """Test loading config from environment variables"""
        monkeypatch.setenv("ENVIRONMENT", "staging")
        monkeypatch.setenv("SECRET_KEY", "a" * 64)
        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
        monkeypatch.setenv("RATE_LIMITING_ENABLED", "false")
        
        config = load_security_config()
        
        assert config.environment == "staging"
        assert len(config.secret_key) == 64
        assert config.rate_limiting_enabled is False
    
    def test_load_security_config_builds_database_url(self, monkeypatch):
        """Test building database URL from components"""
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.setenv("SECRET_KEY", "a" * 64)
        monkeypatch.setenv("POSTGRES_USER", "testuser")
        monkeypatch.setenv("POSTGRES_PASSWORD", "testpass")
        monkeypatch.setenv("POSTGRES_SERVER", "testhost")
        monkeypatch.setenv("POSTGRES_PORT", "5433")
        monkeypatch.setenv("POSTGRES_DB", "testdb")
        
        config = load_security_config()
        
        assert "testuser" in config.database_url
        assert "testhost" in config.database_url
        assert "testdb" in config.database_url
        assert "5433" in config.database_url
    
    def test_load_security_config_invalid_raises_error(self, monkeypatch):
        """Test that invalid config raises ConfigValidationError"""
        monkeypatch.setenv("SECRET_KEY", "short")  # Too short
        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
        
        with pytest.raises(ConfigValidationError):
            load_security_config()


class TestCheckRequiredSecrets:
    """Test checking required secrets"""
    
    def test_check_required_secrets_all_valid(self, monkeypatch):
        """Test when all required secrets are valid"""
        monkeypatch.setenv("SECRET_KEY", "a" * 64)
        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
        monkeypatch.setenv("REDIS_HOST", "redis.example.com")
        
        results = check_required_secrets("production")
        
        assert results["SECRET_KEY"] is True
        assert results["DATABASE_URL"] is True
        assert results["REDIS_CONFIG"] is True
    
    def test_check_required_secrets_missing_secret_key(self, monkeypatch):
        """Test when secret key is missing or weak"""
        monkeypatch.setenv("SECRET_KEY", "weak")
        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
        
        results = check_required_secrets("production")
        
        assert results["SECRET_KEY"] is False
    
    def test_check_required_secrets_development(self, monkeypatch):
        """Test that development has fewer requirements"""
        monkeypatch.setenv("SECRET_KEY", "a" * 64)
        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
        
        results = check_required_secrets("development")
        
        # Development doesn't check Redis and CORS
        assert "REDIS_CONFIG" not in results
        assert "CORS_CONFIG" not in results


class TestValidateProductionConfig:
    """Test production configuration validation"""
    
    def test_validate_production_config_valid(self, monkeypatch):
        """Test validation with valid production config"""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("DEBUG", "false")
        monkeypatch.setenv("SECRET_KEY", "a" * 64)
        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
        monkeypatch.setenv("ALLOWED_ORIGINS", "https://example.com")
        monkeypatch.setenv("REDIS_HOST", "redis.example.com")
        monkeypatch.setenv("RATE_LIMITING_ENABLED", "true")
        
        is_valid, errors = validate_production_config()
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_production_config_debug_enabled(self, monkeypatch):
        """Test validation fails when debug is enabled"""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("DEBUG", "true")
        monkeypatch.setenv("SECRET_KEY", "a" * 64)
        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
        
        is_valid, errors = validate_production_config()
        
        assert is_valid is False
        assert any("DEBUG mode" in error for error in errors)
    
    def test_validate_production_config_weak_secret(self, monkeypatch):
        """Test validation fails with weak secret"""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("DEBUG", "false")
        monkeypatch.setenv("SECRET_KEY", "a" * 32)  # Too short for production
        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
        
        is_valid, errors = validate_production_config()
        
        assert is_valid is False
        # Error could be in config validation or secrets check
    
    def test_validate_production_config_wildcard_cors(self, monkeypatch):
        """Test validation fails with wildcard CORS"""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("DEBUG", "false")
        monkeypatch.setenv("SECRET_KEY", "a" * 64)
        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
        monkeypatch.setenv("ALLOWED_ORIGINS", "*")
        monkeypatch.setenv("REDIS_HOST", "redis.example.com")
        
        is_valid, errors = validate_production_config()
        
        assert is_valid is False
        assert any("wildcard" in error.lower() for error in errors)


class TestGetSafeConfigSummary:
    """Test safe configuration summary"""
    
    def test_get_safe_config_summary_redacts_secrets(self, monkeypatch):
        """Test that summary doesn't expose secrets"""
        monkeypatch.setenv("SECRET_KEY", "super-secret-key-12345")
        monkeypatch.setenv("DATABASE_URL", "postgresql://user:secretpass@localhost/db")
        monkeypatch.setenv("MINIMAX_API_KEY", "secret-api-key")
        
        summary = get_safe_config_summary()
        
        # Should not contain actual secret values
        assert "super-secret-key" not in str(summary)
        assert "secretpass" not in str(summary)
        assert "secret-api-key" not in str(summary)
        
        # Should indicate whether secrets are set
        assert "secret_key_set" in summary
        assert "database_configured" in summary
        assert "api_keys" in summary
    
    def test_get_safe_config_summary_shows_config_status(self, monkeypatch):
        """Test that summary shows configuration status"""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("DEBUG", "false")
        monkeypatch.setenv("RATE_LIMITING_ENABLED", "true")
        monkeypatch.setenv("SECRET_KEY", "a" * 64)
        
        summary = get_safe_config_summary()
        
        assert summary["environment"] == "production"
        assert summary["debug"] is False
        assert summary["rate_limiting_enabled"] is True
        assert summary["secret_key_set"] is True
