"""Unified logging configuration for ontomem using structlog."""

import logging
import sys
from typing import Optional

import structlog


def configure_logging(
    level: str = "WARNING",
    json_output: bool = False,
    output_file: Optional[str] = None,
) -> None:
    """Configure structlog for ontomem.
    
    Args:
        level: Log level ("DEBUG", "INFO", "WARNING", "ERROR").
        json_output: If True, output JSON format (for production).
        output_file: Optional file path to write logs.
    """
    level_value = getattr(logging, level.upper(), logging.WARNING)
    
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    if json_output:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(
            structlog.dev.ConsoleRenderer(
                colors=True,
                exception_formatter=structlog.dev.plain_traceback,
            )
        )
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    handlers = []
    
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level_value)
    console_handler.setFormatter(structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
        ],
        processors=[
            structlog.processors.UnicodeDecoder(),
            structlog.dev.ConsoleRenderer(colors=True) if not json_output 
            else structlog.processors.JSONRenderer(),
        ],
    ))
    handlers.append(console_handler)
    
    if output_file:
        file_handler = logging.FileHandler(output_file, encoding="utf-8")
        file_handler.setLevel(level_value)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        handlers.append(file_handler)
    
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    for handler in handlers:
        root_logger.addHandler(handler)
    root_logger.setLevel(level_value)


def get_logger(name: str = None) -> structlog.stdlib.BoundLogger:
    """Get a configured structlog logger.
    
    Args:
        name: Logger name (typically __name__).
        
    Returns:
        A structlog bound logger instance.
    """
    return structlog.get_logger(name)


def set_log_level(level: str) -> None:
    """Dynamically set log level at runtime.
    
    Args:
        level: Log level ("DEBUG", "INFO", "WARNING", "ERROR").
    """
    level_value = getattr(logging, level.upper(), logging.WARNING)
    logging.getLogger().setLevel(level_value)
