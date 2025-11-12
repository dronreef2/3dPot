"""
3dPot Backend - Configurações da Aplicação
Sistema de Prototipagem Sob Demanda
"""

from typing import Optional, List, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Configurações da aplicação usando pydantic-settings"""
    
    # === ENVIRONMENT ===
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # === API CONFIGURATION ===
    API_V1_STR: str = Field(default="/api/v1", env="API_V1_STR")
    PROJECT_NAME: str = Field(default="3dPot Backend API", env="PROJECT_NAME")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    ALLOWED_HOSTS: str = Field(default="*", env="ALLOWED_HOSTS")
    FRONTEND_URL: str = Field(default="http://localhost:3000", env="FRONTEND_URL")
    
    # === DATABASE ===
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    POSTGRES_USER: str = Field(default="3dpot", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="3dpot123", env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(default="3dpot_dev", env="POSTGRES_DB")
    POSTGRES_HOST: str = Field(default="localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(default=5432, env="POSTGRES_PORT")
    
    # Database Pool Settings
    DB_POOL_SIZE: int = Field(default=20, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=30, env="DB_MAX_OVERFLOW")
    DB_POOL_TIMEOUT: int = Field(default=30, env="DB_POOL_TIMEOUT")
    DB_POOL_RECYCLE: int = Field(default=3600, env="DB_POOL_RECYCLE")
    
    # === SECURITY & JWT ===
    SECRET_KEY: str = Field(
        default="your-super-secret-key-change-in-production-must-be-32-chars-minimum",
        env="SECRET_KEY"
    )
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # JWT Settings
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Password Policy
    PASSWORD_MIN_LENGTH: int = Field(default=8, env="PASSWORD_MIN_LENGTH")
    PASSWORD_REQUIRE_UPPERCASE: bool = Field(default=True, env="PASSWORD_REQUIRE_UPPERCASE")
    PASSWORD_REQUIRE_LOWERCASE: bool = Field(default=True, env="PASSWORD_REQUIRE_LOWERCASE")
    PASSWORD_REQUIRE_NUMBERS: bool = Field(default=True, env="PASSWORD_REQUIRE_NUMBERS")
    PASSWORD_REQUIRE_SPECIAL: bool = Field(default=True, env="PASSWORD_REQUIRE_SPECIAL")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")
    
    # === REDIS ===
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    
    # Cache Settings
    CACHE_TTL: int = Field(default=3600, env="CACHE_TTL")
    SESSION_TTL: int = Field(default=1800, env="SESSION_TTL")
    
    # === RABBITMQ / CELERY ===
    RABBITMQ_USER: str = Field(default="3dpot", env="RABBITMQ_USER")
    RABBITMQ_PASSWORD: str = Field(default="3dpot123", env="RABBITMQ_PASSWORD")
    RABBITMQ_HOST: str = Field(default="localhost", env="RABBITMQ_HOST")
    RABBITMQ_PORT: int = Field(default=5672, env="RABBITMQ_PORT")
    
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")
    
    # === MQTT ===
    MQTT_BROKER_URL: str = Field(default="localhost", env="MQTT_BROKER_URL")
    MQTT_BROKER_PORT: int = Field(default=1883, env="MQTT_BROKER_PORT")
    MQTT_CLIENT_ID: str = Field(default="3dpot_backend", env="MQTT_CLIENT_ID")
    MQTT_USERNAME: Optional[str] = Field(default=None, env="MQTT_USERNAME")
    MQTT_PASSWORD: Optional[str] = Field(default=None, env="MQTT_PASSWORD")
    
    # === WEBSOCKET ===
    WS_MAX_CONNECTIONS: int = Field(default=100, env="WS_MAX_CONNECTIONS")
    WS_PING_INTERVAL: int = Field(default=20, env="WS_PING_INTERVAL")
    WS_PING_TIMEOUT: int = Field(default=10, env="WS_PING_TIMEOUT")
    
    # === DEVICE MONITORING ===
    MONITORING_INTERVAL: int = Field(default=30, env="MONITORING_INTERVAL")
    MAX_DATA_POINTS: int = Field(default=1000, env="MAX_DATA_POINTS")
    ALERT_THRESHOLDS: Dict[str, Any] = Field(
        default={"temperature": 70, "humidity": 80, "vibration": 5},
        env="ALERT_THRESHOLDS"
    )
    
    # === STORAGE ===
    MODELS_STORAGE_PATH: str = Field(default="/workspace/backend/storage/models", env="MODELS_STORAGE_PATH")
    TEMP_STORAGE_PATH: str = Field(default="/workspace/backend/storage/temp", env="TEMP_STORAGE_PATH")
    
    # File Uploads
    MAX_FILE_SIZE: int = Field(default=104857600, env="MAX_FILE_SIZE")  # 100MB
    
    # === EXTERNAL APIs ===
    SLANT3D_API_KEY: str = Field(..., env="SLANT3D_API_KEY")
    SLANT3D_BASE_URL: str = Field(default="https://api.slant3d.com/v1", env="SLANT3D_BASE_URL")
    
    MINIMAX_API_KEY: str = Field(default="your-minimax-api-key-here", env="MINIMAX_API_KEY")
    MINIMAX_BASE_URL: str = Field(default="https://api.minimax.chat/v1", env="MINIMAX_BASE_URL")
    MINIMAX_MODEL: str = Field(default="abab6.5s-chat", env="MINIMAX_MODEL")
    MINIMAX_MAX_TOKENS: int = Field(default=4000, env="MINIMAX_MAX_TOKENS")
    MINIMAX_TEMPERATURE: float = Field(default=0.7, env="MINIMAX_TEMPERATURE")
    
    # === MONITORING ===
    PROMETHEUS_ENABLED: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    GRAFANA_ENABLED: bool = Field(default=True, env="GRAFANA_ENABLED")
    HEALTH_CHECK_INTERVAL: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    
    # === CORS ===
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="ALLOWED_ORIGINS"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = "utf-8"


# Instância global das configurações
settings = Settings()


def get_settings() -> Settings:
    """Retorna a instância das configurações"""
    return settings
