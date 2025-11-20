"""
Security Configuration - 3dPot Sprint 7
Gestão segura de configurações e validação de secrets
"""

import os
import re
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from pydantic import BaseModel, Field, validator, ValidationError

from backend.observability.logging_config import get_logger

logger = get_logger(__name__)


class ConfigValidationError(Exception):
    """Exceção para erros de validação de configuração"""
    pass


class SecurityConfig(BaseModel):
    """
    Configuração de segurança com validação.
    Todas as configurações sensíveis devem vir de variáveis de ambiente.
    """
    
    # Environment
    environment: str = Field(default="development", pattern="^(development|staging|production)$")
    debug: bool = Field(default=False)
    
    # Security Keys (MUST be set in production)
    secret_key: str = Field(min_length=32)
    algorithm: str = Field(default="HS256")
    
    # Database (connection string should not contain plaintext password in logs)
    database_url: str = Field(min_length=10)
    
    # Redis (for rate limiting and caching in production)
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379, ge=1, le=65535)
    redis_password: Optional[str] = Field(default=None)
    
    # External API Keys (optional, but validated if present)
    minimax_api_key: Optional[str] = Field(default=None)
    slant3d_api_key: Optional[str] = Field(default=None)
    
    # Rate Limiting
    rate_limiting_enabled: bool = Field(default=True)
    rate_limit_default: int = Field(default=60, ge=1)
    rate_limit_auth: int = Field(default=10, ge=1)
    
    # CORS
    allowed_origins: List[str] = Field(default=["*"])
    
    # Session/Token Configuration
    access_token_expire_minutes: int = Field(default=30, ge=5, le=1440)
    refresh_token_expire_days: int = Field(default=7, ge=1, le=90)
    
    # Password Policy
    password_min_length: int = Field(default=8, ge=8)
    password_require_uppercase: bool = Field(default=True)
    password_require_lowercase: bool = Field(default=True)
    password_require_numbers: bool = Field(default=True)
    password_require_special: bool = Field(default=True)
    
    @validator("secret_key")
    def validate_secret_key(cls, v, values):
        """Validate that secret key is not a default/insecure value"""
        insecure_values = [
            "CHANGE_ME",
            "CHANGE_ME_IN_PRODUCTION",
            "secret",
            "password",
            "12345678",
            "your-secret-key-here"
        ]
        
        env = values.get("environment", "development")
        
        if env == "production":
            # In production, secret key MUST be strong
            if len(v) < 64:
                raise ValueError("In production, secret_key must be at least 64 characters")
            
            if any(insecure in v for insecure in insecure_values):
                raise ValueError("secret_key cannot contain common/insecure values in production")
        
        return v
    
    @validator("database_url")
    def validate_database_url(cls, v):
        """Validate database URL format"""
        # Basic validation - should start with postgresql://
        if not (v.startswith("postgresql://") or v.startswith("postgresql+psycopg2://")):
            raise ValueError("database_url must be a valid PostgreSQL connection string")
        
        return v
    
    @validator("allowed_origins")
    def validate_cors_origins(cls, v, values):
        """Validate CORS origins - warn if using '*' in production"""
        env = values.get("environment", "development")
        
        if env == "production" and "*" in v:
            logger.warning(
                "security_warning",
                message="CORS configured with '*' in production - this is insecure!",
                recommendation="Set specific allowed origins"
            )
        
        return v
    
    @validator("debug")
    def validate_debug_mode(cls, v, values):
        """Ensure debug is disabled in production"""
        env = values.get("environment", "development")
        
        if env == "production" and v:
            raise ValueError("DEBUG mode must be disabled in production")
        
        return v
    
    class Config:
        """Pydantic config"""
        env_prefix = ""
        case_sensitive = False


def load_security_config() -> SecurityConfig:
    """
    Load and validate security configuration from environment variables.
    
    Returns:
        Validated SecurityConfig instance
        
    Raises:
        ConfigValidationError: If configuration is invalid
    """
    try:
        # Load from environment
        config_dict = {
            "environment": os.getenv("ENVIRONMENT", "development"),
            "debug": os.getenv("DEBUG", "false").lower() == "true",
            "secret_key": os.getenv("SECRET_KEY", "CHANGE_ME_IN_PRODUCTION"),
            "algorithm": os.getenv("ALGORITHM", "HS256"),
            
            # Database
            "database_url": _build_database_url(),
            
            # Redis
            "redis_host": os.getenv("REDIS_HOST", "localhost"),
            "redis_port": int(os.getenv("REDIS_PORT", "6379")),
            "redis_password": os.getenv("REDIS_PASSWORD"),
            
            # API Keys
            "minimax_api_key": os.getenv("MINIMAX_API_KEY"),
            "slant3d_api_key": os.getenv("SLANT3D_API_KEY"),
            
            # Rate Limiting
            "rate_limiting_enabled": os.getenv("RATE_LIMITING_ENABLED", "true").lower() == "true",
            "rate_limit_default": int(os.getenv("RATE_LIMIT_DEFAULT", "60")),
            "rate_limit_auth": int(os.getenv("RATE_LIMIT_AUTH", "10")),
            
            # CORS
            "allowed_origins": _parse_allowed_origins(),
            
            # Tokens
            "access_token_expire_minutes": int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
            "refresh_token_expire_days": int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")),
            
            # Password Policy
            "password_min_length": int(os.getenv("PASSWORD_MIN_LENGTH", "8")),
            "password_require_uppercase": os.getenv("PASSWORD_REQUIRE_UPPERCASE", "true").lower() == "true",
            "password_require_lowercase": os.getenv("PASSWORD_REQUIRE_LOWERCASE", "true").lower() == "true",
            "password_require_numbers": os.getenv("PASSWORD_REQUIRE_NUMBERS", "true").lower() == "true",
            "password_require_special": os.getenv("PASSWORD_REQUIRE_SPECIAL", "true").lower() == "true",
        }
        
        # Validate and create config
        config = SecurityConfig(**config_dict)
        
        logger.info(
            "security_config_loaded",
            environment=config.environment,
            rate_limiting_enabled=config.rate_limiting_enabled,
            debug=config.debug
        )
        
        return config
        
    except ValidationError as e:
        logger.error("security_config_validation_failed", errors=str(e))
        raise ConfigValidationError(f"Configuration validation failed: {e}")
    except Exception as e:
        logger.error("security_config_load_failed", error=str(e))
        raise ConfigValidationError(f"Failed to load configuration: {e}")


def _build_database_url() -> str:
    """Build database URL from environment variables"""
    # Check if DATABASE_URL is provided directly
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL")
    
    # Build from components
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "password")
    host = os.getenv("POSTGRES_SERVER", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "3dpot_v2")
    
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


def _parse_allowed_origins() -> List[str]:
    """Parse CORS allowed origins from environment"""
    origins_str = os.getenv("ALLOWED_ORIGINS", "*")
    
    if origins_str == "*":
        return ["*"]
    
    # Split by comma and strip whitespace
    return [origin.strip() for origin in origins_str.split(",")]


def check_required_secrets(environment: str = "production") -> Dict[str, bool]:
    """
    Check if all required secrets are properly configured.
    
    Args:
        environment: Target environment (production, staging, development)
        
    Returns:
        Dict mapping secret names to whether they are properly set
    """
    results = {}
    
    # Critical secrets (always required)
    results["SECRET_KEY"] = _check_secret_key()
    results["DATABASE_URL"] = _check_database_config()
    
    # Production-specific requirements
    if environment == "production":
        results["REDIS_CONFIG"] = _check_redis_config()
        results["CORS_CONFIG"] = _check_cors_config()
        results["DEBUG_DISABLED"] = not (os.getenv("DEBUG", "false").lower() == "true")
    
    return results


def _check_secret_key() -> bool:
    """Check if SECRET_KEY is properly set"""
    secret_key = os.getenv("SECRET_KEY", "")
    
    # Must be set and not a default value
    if len(secret_key) < 32:
        return False
    
    insecure_values = ["CHANGE_ME", "secret", "password"]
    if any(insecure in secret_key for insecure in insecure_values):
        return False
    
    return True


def _check_database_config() -> bool:
    """Check if database configuration is valid"""
    db_url = os.getenv("DATABASE_URL")
    
    if db_url and db_url.startswith("postgresql"):
        return True
    
    # Check individual components
    required = ["POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_SERVER", "POSTGRES_DB"]
    return all(os.getenv(var) for var in required)


def _check_redis_config() -> bool:
    """Check if Redis configuration is valid"""
    redis_host = os.getenv("REDIS_HOST")
    
    if redis_host and redis_host != "localhost":
        return True
    
    return False


def _check_cors_config() -> bool:
    """Check if CORS is properly configured (not wildcard in production)"""
    origins = os.getenv("ALLOWED_ORIGINS", "*")
    return origins != "*"


def validate_production_config() -> Tuple[bool, List[str]]:
    """
    Validate that production configuration is secure.
    
    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []
    
    try:
        config = load_security_config()
        
        if config.environment == "production":
            # Check critical requirements
            if config.debug:
                errors.append("DEBUG mode is enabled in production")
            
            if len(config.secret_key) < 64:
                errors.append("SECRET_KEY is too short for production (minimum 64 characters)")
            
            if "*" in config.allowed_origins:
                errors.append("CORS is configured with wildcard '*' in production")
            
            if not config.rate_limiting_enabled:
                errors.append("Rate limiting is disabled in production")
            
            # Check secrets
            secrets_check = check_required_secrets("production")
            for secret, is_valid in secrets_check.items():
                if not is_valid:
                    errors.append(f"Required secret/config '{secret}' is not properly set")
        
        return len(errors) == 0, errors
        
    except Exception as e:
        errors.append(f"Configuration validation failed: {str(e)}")
        return False, errors


def get_safe_config_summary() -> Dict[str, Any]:
    """
    Get a summary of current configuration (with sensitive data redacted).
    Safe to log or display.
    
    Returns:
        Dict with configuration summary
    """
    return {
        "environment": os.getenv("ENVIRONMENT", "development"),
        "debug": os.getenv("DEBUG", "false").lower() == "true",
        "secret_key_set": bool(os.getenv("SECRET_KEY")) and len(os.getenv("SECRET_KEY", "")) >= 32,
        "database_configured": bool(os.getenv("DATABASE_URL")) or bool(os.getenv("POSTGRES_SERVER")),
        "redis_configured": bool(os.getenv("REDIS_HOST")),
        "rate_limiting_enabled": os.getenv("RATE_LIMITING_ENABLED", "true").lower() == "true",
        "cors_origins": "wildcard" if os.getenv("ALLOWED_ORIGINS", "*") == "*" else "restricted",
        "api_keys": {
            "minimax": bool(os.getenv("MINIMAX_API_KEY")),
            "slant3d": bool(os.getenv("SLANT3D_API_KEY")),
        }
    }


# Global security config instance (lazy loaded)
_security_config: Optional[SecurityConfig] = None


def get_security_config() -> SecurityConfig:
    """
    Get global security configuration instance.
    
    Returns:
        SecurityConfig instance
    """
    global _security_config
    
    if _security_config is None:
        _security_config = load_security_config()
    
    return _security_config
