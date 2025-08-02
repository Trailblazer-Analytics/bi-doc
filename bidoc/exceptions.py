"""Custom exception classes and error handling utilities for BI Documentation Tool."""

import logging
from enum import Enum
from typing import Any, Dict, Optional


class ErrorCode(Enum):
    """Standardized error codes for consistent error reporting."""
    
    # File-related errors (1000-1099)
    FILE_NOT_FOUND = 1001
    FILE_ACCESS_DENIED = 1002
    FILE_CORRUPTED = 1003
    FILE_TOO_LARGE = 1004
    INVALID_FILE_FORMAT = 1005
    
    # Parser errors (1100-1199) 
    PARSER_INITIALIZATION_FAILED = 1101
    PARSER_DEPENDENCY_MISSING = 1102
    PARSER_METADATA_EXTRACTION_FAILED = 1103
    PARSER_UNSUPPORTED_VERSION = 1104
    PARSER_TIMEOUT = 1105
    
    # Data processing errors (1200-1299)
    DATA_VALIDATION_FAILED = 1201
    DATA_TRANSFORMATION_FAILED = 1202
    DATA_SERIALIZATION_FAILED = 1203
    DATA_INCOMPLETE = 1204
    
    # Template/generation errors (1300-1399)
    TEMPLATE_NOT_FOUND = 1301
    TEMPLATE_RENDER_FAILED = 1302
    OUTPUT_GENERATION_FAILED = 1303
    OUTPUT_WRITE_FAILED = 1304
    
    # Configuration errors (1400-1499)
    CONFIG_FILE_INVALID = 1401
    CONFIG_MISSING_REQUIRED = 1402
    CONFIG_VALIDATION_FAILED = 1403
    
    # Network/AI service errors (1500-1599)
    AI_SERVICE_UNAVAILABLE = 1501
    AI_SERVICE_TIMEOUT = 1502
    AI_SERVICE_QUOTA_EXCEEDED = 1503
    AI_SERVICE_AUTHENTICATION_FAILED = 1504
    
    # System errors (1600-1699)
    MEMORY_INSUFFICIENT = 1601
    DISK_SPACE_INSUFFICIENT = 1602
    PERMISSION_DENIED = 1603
    SYSTEM_RESOURCE_UNAVAILABLE = 1604


class BIDocError(Exception):
    """Base exception class for all BI Documentation Tool errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """
        Initialize BIDocError.
        
        Args:
            message: Human-readable error message
            error_code: Standardized error code
            context: Additional context information
            original_exception: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.original_exception = original_exception
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for structured logging."""
        return {
            "error_code": self.error_code.value,
            "error_name": self.error_code.name,
            "message": self.message,
            "context": self.context,
            "original_error": str(self.original_exception) if self.original_exception else None
        }
    
    def __str__(self) -> str:
        """Return formatted error string."""
        return f"[{self.error_code.name}:{self.error_code.value}] {self.message}"


class FileProcessingError(BIDocError):
    """Raised when file processing operations fail."""
    pass


class ParserError(BIDocError):
    """Raised when parsing operations fail."""
    pass


class DataValidationError(BIDocError):
    """Raised when data validation fails."""
    pass


class TemplateError(BIDocError):
    """Raised when template operations fail."""
    pass


class ConfigurationError(BIDocError):
    """Raised when configuration is invalid or missing."""
    pass


class AIServiceError(BIDocError):
    """Raised when AI service operations fail."""
    pass


class SystemResourceError(BIDocError):
    """Raised when system resources are insufficient."""
    pass


def handle_file_error(error: Exception, file_path: str) -> BIDocError:
    """
    Convert file-related exceptions to standardized BIDocError.
    
    Args:
        error: Original exception
        file_path: Path of the file that caused the error
        
    Returns:
        Appropriate BIDocError instance
    """
    context = {"file_path": file_path}
    
    if isinstance(error, FileNotFoundError):
        return FileProcessingError(
            f"File not found: {file_path}",
            ErrorCode.FILE_NOT_FOUND,
            context,
            error
        )
    elif isinstance(error, PermissionError):
        return FileProcessingError(
            f"Access denied to file: {file_path}",
            ErrorCode.FILE_ACCESS_DENIED,
            context,
            error
        )
    elif isinstance(error, OSError) and "corrupted" in str(error).lower():
        return FileProcessingError(
            f"File appears to be corrupted: {file_path}",
            ErrorCode.FILE_CORRUPTED,
            context,
            error
        )
    elif isinstance(error, (OSError, IOError)):
        return FileProcessingError(
            f"File I/O error: {file_path} - {str(error)}",
            ErrorCode.FILE_ACCESS_DENIED,
            context,
            error
        )
    else:
        return FileProcessingError(
            f"Unknown file processing error: {file_path} - {str(error)}",
            ErrorCode.INVALID_FILE_FORMAT,
            context,
            error
        )


def handle_parser_error(error: Exception, parser_type: str, file_path: str) -> BIDocError:
    """
    Convert parser-related exceptions to standardized BIDocError.
    
    Args:
        error: Original exception
        parser_type: Type of parser (e.g., "PowerBI", "Tableau")
        file_path: Path of the file being parsed
        
    Returns:
        Appropriate BIDocError instance
    """
    context = {"parser_type": parser_type, "file_path": file_path}
    
    if isinstance(error, ImportError):
        return ParserError(
            f"{parser_type} parser dependency missing: {str(error)}",
            ErrorCode.PARSER_DEPENDENCY_MISSING,
            context,
            error
        )
    elif isinstance(error, TimeoutError):
        return ParserError(
            f"{parser_type} parser timed out processing: {file_path}",
            ErrorCode.PARSER_TIMEOUT,
            context,
            error
        )
    elif "version" in str(error).lower() or "compatibility" in str(error).lower():
        return ParserError(
            f"{parser_type} parser: unsupported file version - {str(error)}",
            ErrorCode.PARSER_UNSUPPORTED_VERSION,
            context,
            error
        )
    else:
        return ParserError(
            f"{parser_type} parser failed to extract metadata: {str(error)}",
            ErrorCode.PARSER_METADATA_EXTRACTION_FAILED,
            context,
            error
        )


def handle_template_error(error: Exception, template_name: str) -> BIDocError:
    """
    Convert template-related exceptions to standardized BIDocError.
    
    Args:
        error: Original exception
        template_name: Name of the template that failed
        
    Returns:
        Appropriate BIDocError instance
    """
    context = {"template_name": template_name}
    
    if isinstance(error, FileNotFoundError):
        return TemplateError(
            f"Template not found: {template_name}",
            ErrorCode.TEMPLATE_NOT_FOUND,
            context,
            error
        )
    else:
        return TemplateError(
            f"Template rendering failed: {template_name} - {str(error)}",
            ErrorCode.TEMPLATE_RENDER_FAILED,
            context,
            error
        )


def log_structured_error(logger: logging.Logger, error: BIDocError) -> None:
    """
    Log error with structured information.
    
    Args:
        logger: Logger instance
        error: BIDocError to log
    """
    error_dict = error.to_dict()
    
    # Log with appropriate level based on error type
    if error.error_code.value < 1500:  # Non-network errors are usually more serious
        logger.error(
            f"Error {error.error_code.name}({error.error_code.value}): {error.message}",
            extra={"error_details": error_dict}
        )
    else:  # Network/AI service errors might be temporary
        logger.warning(
            f"Service Error {error.error_code.name}({error.error_code.value}): {error.message}",
            extra={"error_details": error_dict}
        )
    
    # Log original exception details if available
    if error.original_exception:
        logger.debug(f"Original exception: {type(error.original_exception).__name__}: {error.original_exception}")


class RetryableError(BIDocError):
    """Base class for errors that might succeed on retry."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        super().__init__(message, error_code, context, original_exception)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retry_count = 0
    
    def should_retry(self) -> bool:
        """Check if this error should be retried."""
        return self.retry_count < self.max_retries
    
    def increment_retry(self) -> None:
        """Increment the retry counter."""
        self.retry_count += 1


def is_retryable_error(error: Exception) -> bool:
    """
    Determine if an error is potentially retryable.
    
    Args:
        error: Exception to check
        
    Returns:
        True if error might succeed on retry
    """
    if isinstance(error, RetryableError):
        return error.should_retry()
    
    # Network-related errors are usually retryable
    if isinstance(error, (ConnectionError, TimeoutError)):
        return True
    
    # Some file system errors might be retryable
    if isinstance(error, OSError) and error.errno in [13, 16, 26]:  # Permission, busy, text file busy
        return True
    
    return False