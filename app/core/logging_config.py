"""Logging configuration for the application."""
import logging
import sys
from typing import Any

from app.core.config import settings


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""

    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    FORMATS = {
        logging.DEBUG: grey + "%(levelname)s" + reset + " - %(message)s",
        logging.INFO: blue + "%(levelname)s" + reset + " - %(message)s",
        logging.WARNING: yellow + "%(levelname)s" + reset + " - %(message)s",
        logging.ERROR: red + "%(levelname)s" + reset + " - %(message)s",
        logging.CRITICAL: bold_red + "%(levelname)s" + reset + " - %(message)s",
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors."""
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(
            f"%(asctime)s - %(name)s - {log_fmt}", datefmt="%Y-%m-%d %H:%M:%S"
        )
        return formatter.format(record)


def setup_logging() -> None:
    """Configure application logging."""
    # Get log level from settings
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(ColoredFormatter())
    root_logger.addHandler(console_handler)

    # Set specific log levels for third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)

    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {settings.LOG_LEVEL}")
    logger.info(f"Debug mode: {settings.DEBUG}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module.
    
    Args:
        name: The name of the module (usually __name__)
        
    Returns:
        A configured logger instance
    """
    return logging.getLogger(name)



