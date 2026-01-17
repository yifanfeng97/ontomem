"""Unified logging configuration for ontomem."""

import logging
import sys
from typing import Optional

try:
    from loguru import logger as loguru_logger
    HAS_LOGURU = True
except ImportError:
    HAS_LOGURU = False


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance.
    
    If loguru is available, uses it for enhanced formatting.
    Otherwise falls back to standard logging.
    
    Args:
        name: Logger name (typically __name__).
        
    Returns:
        Configured logger instance.
    """
    if HAS_LOGURU:
        return loguru_logger
    else:
        return logging.getLogger(name)


def configure_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
) -> None:
    """Configure root logger for ontomem.
    
    Args:
        level: Logging level ("DEBUG", "INFO", "WARNING", "ERROR").
        format_string: Custom format string (ignored if using loguru).
    """
    if HAS_LOGURU:
        loguru_logger.remove()  # Remove default handler
        loguru_logger.add(
            sys.stderr,
            format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
            level=level,
        )
    else:
        logging.basicConfig(
            level=level,
            format=format_string or "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stderr)],
        )
