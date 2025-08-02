"""Retry utilities for handling transient failures."""

import logging
import time
from functools import wraps
from typing import Any, Callable, Optional, Tuple, Type, Union

from .exceptions import RetryableError, is_retryable_error


def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    logger: Optional[logging.Logger] = None
):
    """
    Decorator to retry function calls on failure.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exception types to catch and retry
        logger: Optional logger for retry messages
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            _logger = logger or logging.getLogger(func.__module__)
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    # Don't retry on the last attempt
                    if attempt == max_retries:
                        break
                    
                    # Check if this specific error should be retried
                    if not is_retryable_error(e):
                        _logger.debug(f"Error not retryable, skipping retries: {e}")
                        break
                    
                    _logger.warning(
                        f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {e}. "
                        f"Retrying in {current_delay:.1f}s..."
                    )
                    
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            # All retries exhausted, raise the last exception
            _logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}")
            raise last_exception
        
        return wrapper
    return decorator


def retry_file_operation(
    max_retries: int = 3,
    delay: float = 0.5,
    logger: Optional[logging.Logger] = None
):
    """
    Specialized retry decorator for file operations.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
        logger: Optional logger for retry messages
        
    Returns:
        Decorated function with file operation retry logic
    """
    return retry_on_failure(
        max_retries=max_retries,
        delay=delay,
        backoff=1.5,  # Gentle backoff for file operations
        exceptions=(OSError, IOError, PermissionError),
        logger=logger
    )


def retry_network_operation(
    max_retries: int = 5,
    delay: float = 2.0,
    logger: Optional[logging.Logger] = None
):
    """
    Specialized retry decorator for network operations.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        logger: Optional logger for retry messages
        
    Returns:
        Decorated function with network operation retry logic
    """
    return retry_on_failure(
        max_retries=max_retries,
        delay=delay,
        backoff=2.0,  # Exponential backoff for network operations
        exceptions=(ConnectionError, TimeoutError, OSError),
        logger=logger
    )


class RetryContext:
    """Context manager for manual retry logic."""
    
    def __init__(
        self,
        max_retries: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize retry context.
        
        Args:
            max_retries: Maximum number of retry attempts
            delay: Initial delay between retries in seconds
            backoff: Multiplier for delay after each retry
            logger: Optional logger for retry messages
        """
        self.max_retries = max_retries
        self.delay = delay
        self.backoff = backoff
        self.logger = logger or logging.getLogger(__name__)
        
        self.attempt = 0
        self.current_delay = delay
        self.last_exception = None
    
    def __enter__(self):
        """Enter the retry context."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the retry context."""
        if exc_type is None:
            return True  # Success, suppress any exceptions
        
        self.last_exception = exc_val
        
        # Check if we should retry
        if self.attempt < self.max_retries and is_retryable_error(exc_val):
            self.logger.warning(
                f"Attempt {self.attempt + 1}/{self.max_retries + 1} failed: {exc_val}. "
                f"Retrying in {self.current_delay:.1f}s..."
            )
            
            time.sleep(self.current_delay)
            self.current_delay *= self.backoff
            self.attempt += 1
            
            return True  # Suppress the exception to allow retry
        
        # No more retries or not retryable
        self.logger.error(f"All {self.max_retries + 1} attempts failed")
        return False  # Let the exception propagate
    
    def should_continue(self) -> bool:
        """Check if we should continue with another attempt."""
        return self.attempt <= self.max_retries


def execute_with_retry(
    func: Callable,
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    logger: Optional[logging.Logger] = None,
    *args,
    **kwargs
) -> Any:
    """
    Execute a function with retry logic.
    
    Args:
        func: Function to execute
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        logger: Optional logger for retry messages
        *args: Arguments to pass to function
        **kwargs: Keyword arguments to pass to function
        
    Returns:
        Result of successful function execution
        
    Raises:
        Last exception if all retries fail
    """
    _logger = logger or logging.getLogger(__name__)
    
    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries or not is_retryable_error(e):
                _logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}")
                raise
            
            current_delay = delay * (backoff ** attempt)
            _logger.warning(
                f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                f"Retrying in {current_delay:.1f}s..."
            )
            time.sleep(current_delay)