"""Application-wide logger.

Writes to data/smartdesk.log with rotation. Falls back to stderr when the
log file cannot be opened (read-only install dir, permission errors, etc.).
"""
from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.config import APP_NAME, DATA_DIR

LOG_PATH = DATA_DIR / "smartdesk.log"

_LOGGER: logging.Logger | None = None


def get_logger() -> logging.Logger:
    """Return the configured application logger (idempotent)."""
    global _LOGGER
    if _LOGGER is not None:
        return _LOGGER

    logger = logging.getLogger(APP_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler with rotation
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            LOG_PATH, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except OSError:
        pass

    # Stderr handler (for dev mode and as fallback)
    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    _LOGGER = logger
    return logger


def log_exception(message: str) -> None:
    """Log an exception with full traceback under the application logger."""
    get_logger().exception(message)
