"""Logging system for MaFin Terminal."""

import os
import sys
from pathlib import Path
from typing import Optional
from loguru import logger as _logger


class LogManager:
    """Log manager for MaFin Terminal."""

    _initialized = False

    @classmethod
    def init(cls, log_file: Optional[str] = None, level: str = "INFO"):
        """Initialize logging."""
        if cls._initialized:
            return

        _logger.remove()

        _logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=level,
            colorize=True
        )

        if log_file:
            log_dir = os.path.dirname(log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            
            _logger.add(
                log_file,
                rotation="10 MB",
                retention="7 days",
                level=level,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
            )

        cls._initialized = True

    @classmethod
    def debug(cls, message: str):
        """Log debug message."""
        _logger.debug(message)

    @classmethod
    def info(cls, message: str):
        """Log info message."""
        _logger.info(message)

    @classmethod
    def warning(cls, message: str):
        """Log warning message."""
        _logger.warning(message)

    @classmethod
    def error(cls, message: str):
        """Log error message."""
        _logger.error(message)

    @classmethod
    def critical(cls, message: str):
        """Log critical message."""
        _logger.critical(message)


def init_logger(log_file: Optional[str] = None, level: str = "INFO"):
    """Initialize logger."""
    LogManager.init(log_file, level)


def get_logger():
    """Get logger instance."""
    return LogManager
