"""Utility functions and common helpers"""

import logging
from enum import Enum
from pathlib import Path
from typing import Optional

from bidoc.constants import PBIX_EXTENSION, TWB_EXTENSION, TWBX_EXTENSION


class FileType(Enum):
    """Supported BI file types"""

    POWER_BI = PBIX_EXTENSION
    TABLEAU_TWB = TWB_EXTENSION
    TABLEAU_TWBX = TWBX_EXTENSION
    UNKNOWN = "unknown"


def detect_file_type(file_path: Path) -> FileType:
    """Detect the type of BI file based on extension"""
    suffix = file_path.suffix.lower()

    file_type_mapping = {
        ".pbix": FileType.POWER_BI,
        ".twb": FileType.TABLEAU_TWB,
        ".twbx": FileType.TABLEAU_TWBX,
    }

    return file_type_mapping.get(suffix, FileType.UNKNOWN)


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename by removing/replacing invalid characters"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")
    return filename.strip()


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    size_float = float(size_bytes)
    while size_float >= 1024 and i < len(size_names) - 1:
        size_float /= 1024.0
        i += 1

    return f"{size_float:.1f} {size_names[i]}"


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to a maximum length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


class MetadataExtractor:
    """Base class for metadata extraction"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def extract_metadata(self, file_path: Path) -> dict:
        """Extract metadata from a BI file - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement extract_metadata method")

    def log_extraction_progress(self, step: str, count: Optional[int] = None):
        """Log progress during metadata extraction"""
        if count is not None:
            self.logger.debug(f"{step}: {count} items")
        else:
            self.logger.debug(step)
