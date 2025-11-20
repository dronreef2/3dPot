"""
3dPot Backend - Structured Logging Configuration
Sprint 6: Production-ready logging with structlog
Sprint 9: Extended with trace_id support

This module provides centralized, structured logging configuration that:
- Uses structlog for structured logging with JSON output
- Includes timestamp, level, service, request_id, trace_id, and custom fields
- Configurable via environment variables
- Compatible with log aggregation systems (e.g., ELK, Loki)
"""

import logging
import sys
import os
from typing import Optional
import structlog
from structlog.types import EventDict, Processor


# Log level configuration from environment
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "json")  # json or console


def add_app_context(logger: logging.Logger, method_name: str, event_dict: EventDict) -> EventDict:
    """Add application-wide context to log events"""
    event_dict["service"] = "3dpot-backend"
    event_dict["version"] = "2.0.0"
    return event_dict


def add_trace_context(logger: logging.Logger, method_name: str, event_dict: EventDict) -> EventDict:
    """
    Add trace_id and request_id to log events (Sprint 9).
    Pulls from context vars if available.
    """
    from .request_id import get_request_id, get_trace_id
    
    request_id = get_request_id()
    trace_id = get_trace_id()
    
    if request_id and "request_id" not in event_dict:
        event_dict["request_id"] = request_id
    
    if trace_id and "trace_id" not in event_dict:
        event_dict["trace_id"] = trace_id
    
    return event_dict


def configure_logging(level: Optional[str] = None, format_type: Optional[str] = None) -> None:
    """
    Configure structured logging for the application.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Defaults to LOG_LEVEL env var.
        format_type: Output format ("json" or "console"). Defaults to LOG_FORMAT env var.
    
    Example:
        configure_logging(level="DEBUG", format_type="console")
    """
    log_level = level or LOG_LEVEL
    log_format = format_type or LOG_FORMAT
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level, logging.INFO),
    )
    
    # Build processor chain
    processors: list[Processor] = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        add_app_context,
        add_trace_context,  # Sprint 9: Add trace/request IDs
        structlog.processors.UnicodeDecoder(),
    ]
    
    # Add renderer based on format
    if log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Console-friendly format for development
        processors.append(
            structlog.dev.ConsoleRenderer(colors=True)
        )
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Configured structlog logger
    
    Example:
        logger = get_logger(__name__)
        logger.info("user_login", user_id=123, email="user@example.com")
    """
    return structlog.get_logger(name)


# Default configuration on module import
# This can be overridden by calling configure_logging() explicitly
if not structlog.is_configured():
    configure_logging()
