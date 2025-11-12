"""
3dPot Platform - Utilities
Criado em: 2025-11-12 22:42:43
Autor: MiniMax Agent

Utilitários da plataforma
"""

import os
import sys
import structlog
from typing import Dict, Any, Optional
import json
import asyncio
from contextlib import contextmanager

# Logging utilities
def setup_logging():
    """Configura logging estruturado com Rich"""
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO level
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=True,
    )

def get_logger(name: str):
    """Cria logger com nome"""
    return structlog.get_logger(name)

# OS utilities
def ensure_directory(path: str) -> str:
    """Garante que diretório existe"""
    os.makedirs(path, exist_ok=True)
    return path

# JSON utilities
def load_json_config(path: str) -> Dict[str, Any]:
    """Carrega configuração JSON"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise Exception(f"Erro ao carregar config {path}: {e}")

def save_json_config(data: Dict[str, Any], path: str):
    """Salva configuração JSON"""
    ensure_directory(os.path.dirname(path))
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Async utilities
@contextmanager
async def timeout_context(timeout_seconds: int):
    """Context manager para timeout assíncrono"""
    try:
        yield
    except asyncio.TimeoutError:
        raise Exception(f"Operation timed out after {timeout_seconds} seconds")

# Validation utilities
def validate_email(email: str) -> bool:
    """Valida formato de email"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_required_fields(data: Dict[str, Any], required_fields: list) -> Dict[str, Any]:
    """Valida campos obrigatórios"""
    errors = {}
    
    for field in required_fields:
        if field not in data or not data[field]:
            errors[field] = f"Campo '{field}' é obrigatório"
    
    if errors:
        raise ValueError(f"Campos obrigatórios ausentes: {json.dumps(errors)}")
    
    return data

# File utilities
def get_file_size_mb(file_path: str) -> float:
    """Retorna tamanho do arquivo em MB"""
    try:
        size_bytes = os.path.getsize(file_path)
        return round(size_bytes / (1024 * 1024), 2)
    except OSError:
        return 0.0

def safe_filename(filename: str) -> str:
    """Gera nome de arquivo seguro"""
    import re
    # Remove caracteres especiais e espaços
    safe = re.sub(r'[^\w\-_\.]', '_', filename)
    # Remove underscores duplos
    safe = re.sub(r'_+', '_', safe)
    # Remove pontos duplos
    safe = re.sub(r'\.+', '.', safe)
    return safe.strip('_.')

# Date utilities
def format_timestamp(timestamp) -> str:
    """Formata timestamp para string legível"""
    if isinstance(timestamp, str):
        return timestamp
    return timestamp.isoformat() if hasattr(timestamp, 'isoformat') else str(timestamp)

# Configuration utilities
def get_config_value(key: str, default: Any = None) -> Any:
    """Busca valor de configuração em variáveis de ambiente"""
    return os.getenv(key, default)

def get_required_config_value(key: str) -> Any:
    """Busca valor obrigatório de configuração"""
    value = os.getenv(key)
    if not value:
        raise Exception(f"Variável de ambiente obrigatória não encontrada: {key}")
    return value

# Error handling utilities
def handle_api_error(e: Exception) -> Dict[str, Any]:
    """Formata erro da API"""
    return {
        "error": type(e).__name__,
        "message": str(e),
        "type": "api_error"
    }

def handle_validation_error(e: ValueError) -> Dict[str, Any]:
    """Formata erro de validação"""
    return {
        "error": "ValidationError",
        "message": str(e),
        "type": "validation_error"
    }

# Export commonly used utilities
__all__ = [
    "setup_logging",
    "get_logger",
    "ensure_directory",
    "load_json_config",
    "save_json_config",
    "timeout_context",
    "validate_email",
    "validate_required_fields",
    "get_file_size_mb",
    "safe_filename",
    "format_timestamp",
    "get_config_value",
    "get_required_config_value",
    "handle_api_error",
    "handle_validation_error"
]