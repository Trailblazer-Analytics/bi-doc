"""Configuration management for the bidoc application."""

import logging
import sys
from logging import FileHandler, StreamHandler
from pathlib import Path
from typing import Optional

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def setup_logging(level: int = logging.INFO, log_file: Optional[Path] = None) -> None:
    """Set up the root logger."""
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        handlers=[StreamHandler(sys.stdout)],
    )
    if log_file:
        file_handler = FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logging.getLogger().addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)
