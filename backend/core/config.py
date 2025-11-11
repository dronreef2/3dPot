"""
Backend FastAPI Evolutivo - 3dPot v2.0
Sistema de Prototipagem Sob Demanda
Configurações completas para Sprint 1
"""

import os
from pathlib import Path
from typing import Optional, List
from pydantic import BaseSettings, validator

# Build paths
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

# API Configuration
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"

# Security & JWT Configuration
SECRET_KEY = os.environ.get("SECRET_KEY", "CHANGE_ME_IN_PRODUCTION")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password validation
PASSWORD_MIN_LENGTH = int(os.environ.get("PASSWORD_MIN_LENGTH", "8"))
PASSWORD_REQUIRE_UPPERCASE = os.environ.get("PASSWORD_REQUIRE_UPPERCASE", "true").lower() == "true"
PASSWORD_REQUIRE_LOWERCASE = os.environ.get("PASSWORD_REQUIRE_LOWERCASE", "true").lower() == "true"
PASSWORD_REQUIRE_NUMBERS = os.environ.get("PASSWORD_REQUIRE_NUMBERS", "true").lower() == "true"
PASSWORD_REQUIRE_SPECIAL = os.environ.get("PASSWORD_REQUIRE_SPECIAL", "true").lower() == "true"

# Rate limiting
RATE_LIMIT_PER_MINUTE = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "60"))
RATE_LIMIT_PER_HOUR = int(os.environ.get("RATE_LIMIT_PER_HOUR", "1000"))

# Database
POSTGRES_SERVER = os.environ.get("POSTGRES_SERVER", "localhost")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "password")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "3dpot_v2")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")

DATABASE_URL = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# Redis (for Celery and caching)
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_DB = int(os.environ.get("REDIS_DB", "0"))

# Storage (S3/MinIO)
S3_ENDPOINT_URL = os.environ.get("S3_ENDPOINT_URL", "http://localhost:9000")
S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY", "minioadmin")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "3dpot-models")
S3_SECURE = os.environ.get("S3_SECURE", "false").lower() == "true"

# External APIs
MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "")
OCTOPART_API_KEY = os.environ.get("OCTOPART_API_KEY", "")
DIGIKEY_API_KEY = os.environ.get("DIGIKEY_API_KEY", "")
SLANT3D_API_KEY = os.environ.get("SLANT3D_API_KEY", "sl-cc497e90df04027eed2468af328a2d00fa99ca5e3b57893394f6cd6012aba3d4")

# File Upload
UPLOAD_SIZE_LIMIT = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {".stl", ".obj", ".3mf", ".gcode", ".scad", ".py"}

# Celery Configuration
CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# Logging
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Project Paths
MODELS_STORAGE_PATH = ROOT_DIR / "storage" / "models"
TEMP_STORAGE_PATH = ROOT_DIR / "storage" / "temp"
LOGS_PATH = ROOT_DIR / "logs"
CACHE_PATH = ROOT_DIR / "cache"

# Ensure directories exist
for path in [MODELS_STORAGE_PATH, TEMP_STORAGE_PATH, LOGS_PATH, CACHE_PATH]:
    path.mkdir(parents=True, exist_ok=True)